#!/usr/bin/env python3
"""
classroom-archiver.py
Archiving utility to pull courses, assignments, and resources from the Google 
Classroom HTTPS API and write them into a localized static directory structure.

Usage:
    python3 bin/classroom-archiver.py --creds secrets/credentials.json
    python3 bin/classroom-archiver.py --creds secrets/credentials.json --list-classrooms
    python3 bin/classroom-archiver.py --creds secrets/credentials.json --course full-stack-webdev
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse


# --- Configuration & Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CORPUS_ROOT = REPO_ROOT / "corpus"
# Leave headroom below restrictive filesystem component limits such as 143 bytes.
MAX_ASSIGNMENT_DIRECTORY_NAME_LENGTH = 120
GOOGLE_API_SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.students.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
ENTRY_TYPE_DIRECTORIES = {
    "ASSIGNMENT": "assignments",
    "QUIZ_ASSIGNMENT": "assessments",
    "QUESTION": "questions",
    "SHORT_ANSWER_QUESTION": "questions",
    "MULTIPLE_CHOICE_QUESTION": "questions",
    "MATERIAL": "resources",
}
SUPPORTED_WORK_TYPES = frozenset(ENTRY_TYPE_DIRECTORIES)
SUPPORTED_FORM_ITEM_TYPES = frozenset(
    {
        "MULTIPLE_CHOICE",
        "PARAGRAPH",
        "SHORT_ANSWER",
        "CHECKBOXES",
        "DROPDOWN",
        "MULTIPLE_CHOICE_GRID",
    }
)
SUPPORTED_WORKSPACE_MIME_TYPES = frozenset(
    {
        "application/vnd.google-apps.document",
        "application/vnd.google-apps.spreadsheet",
        "application/vnd.google-apps.presentation",
    }
)
GOOGLE_WORKSPACE_MIME_PREFIX = "application/vnd.google-apps."
WORKSPACE_EXPORTS = {
    "application/vnd.google-apps.document": (
        (".md", "text/html"),
        (
            ".docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    ),
    "application/vnd.google-apps.spreadsheet": ((".csv", "text/csv"),),
    "application/vnd.google-apps.presentation": (
        (
            ".pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ),
        (".pdf", "application/pdf"),
    ),
}


# --- Data Models ---

def slugify(value: str) -> str:
    """Return a clean token suitable for selecting a Classroom course."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


def parse_archive_token(token: str) -> str:
    """Extract the Classroom ID from an archive token or bare ID."""
    return token.split("-", 1)[0]


def format_archive_token(course: "Course") -> str:
    """Return the canonical token used to identify a discovered classroom."""
    return f"{course.id}-{course.slug}"


def sanitize_filename(name: str) -> str:
    """Return an attachment filename that cannot escape its target directory."""
    sanitized = re.sub(r'[/\\:?*<>|\"]', "-", name).strip().lstrip("- ")
    if not sanitized:
        raise RuntimeError(
            f"Attachment filename is empty after sanitization: {name!r}. "
            "Halting execution."
        )
    return sanitized


def validate_form_item_type(item_type: str, form_id: str) -> None:
    """Reject form structures that the serializer cannot preserve losslessly."""
    if item_type not in SUPPORTED_FORM_ITEM_TYPES:
        raise RuntimeError(
            f"Unsupported Google Form question type: [{item_type}] "
            f"in form '{form_id}'. Halting execution."
        )


class MissingDriveAttachmentError(RuntimeError):
    """Signal a recoverable missing Drive payload across the download boundary."""

    def __init__(self, file_id: str) -> None:
        super().__init__(file_id)
        self.file_id = file_id


class DriveExportSizeLimitError(RuntimeError):
    """Signal a recoverable Workspace export limit across the download boundary."""

    def __init__(self, file_id: str) -> None:
        super().__init__(file_id)
        self.file_id = file_id


class UnsupportedDriveMimeError(RuntimeError):
    """Mark an already-reported MIME failure that must halt the archive."""


@dataclass
class ClassroomResource:
    """A Classroom resource, material, attachment, or linked asset."""

    title: str
    source_type: str
    source_url: str
    mime_type: str | None = None
    local_filename: str | None = None
    file_id: str | None = None


@dataclass
class Assignment:
    """A Google Classroom coursework item."""

    title: str
    description: str | None = None
    materials: list[ClassroomResource] = field(default_factory=list)
    slug: str = ""
    creation_time: str = ""
    max_points: Optional[float] = None
    due_time: Optional[str] = None
    work_type: str = "ASSIGNMENT"
    topic: str | None = None
    rubric: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.slug:
            self.slug = slugify(self.title)


@dataclass
class Course:
    """A Google Classroom course."""

    id: str
    name: str
    description: str | None = None
    assignments: list[Assignment] = field(default_factory=list)
    slug: str = ""

    def __post_init__(self) -> None:
        if not self.slug:
            self.slug = slugify(self.name)


Resource = ClassroomResource


# --- Core Interfaces (Pluggable Abstractions) ---

class ClassroomScraper(ABC):
    """Authenticates and extracts data from Google Classroom."""

    @abstractmethod
    def authenticate(self, creds_path: Path) -> None:
        """Authenticate using an explicit credentials file path."""

    @abstractmethod
    def fetch_courses(self, teacher_email: str | None = None) -> list[Course]:
        """Fetch available courses."""

    @abstractmethod
    def fetch_assignments(self, course_id: str) -> list[Assignment]:
        """Fetch assignments for a course."""


class ContentConverter(ABC):
    """Converts Classroom source content into corpus-ready local formats."""

    @abstractmethod
    def document_to_markdown(self, raw_content: Any) -> str:
        """Convert document-like content into Markdown."""

    @abstractmethod
    def sheet_to_csv(self, raw_content: Any) -> str:
        """Convert sheet-like content into CSV."""


class CorpusWriter(ABC):
    """Writes converted Classroom content into an output directory."""

    def __init__(self, target_root: Path = DEFAULT_CORPUS_ROOT) -> None:
        self.target_root = target_root

    @abstractmethod
    def write_course_structure(self, course: Course) -> None:
        """Write course-level files."""

    @abstractmethod
    def write_assignment_structure(self, course: Course, assignment: Assignment) -> None:
        """Write assignment-level files."""


class SkeletonClassroomScraper(ClassroomScraper):
    """Placeholder scraper for the structural skeleton.

    The concrete Google API implementation is intentionally left undefined.
    """

    def __init__(self) -> None:
        self.creds_path: Path | None = None

    def authenticate(self, creds_path: Path) -> None:
        self.creds_path = creds_path

    def fetch_courses(self, teacher_email: str | None = None) -> list[Course]:
        # Stable empty results let orchestration tests run before API wiring exists.
        return []

    def fetch_assignments(self, course_id: str) -> list[Assignment]:
        # The skeleton preserves the pipeline contract without inventing fixtures.
        return []


class SkeletonCorpusWriter(CorpusWriter):
    """Placeholder writer that keeps the initial skeleton side-effect free."""

    def __init__(self, target_root: Path = DEFAULT_CORPUS_ROOT) -> None:
        super().__init__(target_root)
        self.written_courses: list[Course] = []
        self.written_assignments: list[tuple[Course, Assignment]] = []

    def write_course_structure(self, course: Course) -> None:
        self.written_courses.append(course)

    def write_assignment_structure(self, course: Course, assignment: Assignment) -> None:
        self.written_assignments.append((course, assignment))


class MarkdownCorpusWriter(CorpusWriter):
    """Writes classroom content as clean Markdown under corpus/courses/."""

    def __init__(self, target_root: Path = DEFAULT_CORPUS_ROOT, downloader: Any = None) -> None:
        super().__init__(target_root)
        self.downloader = downloader

    def write_course(self, course: Course) -> None:
        destination = self.target_root / "courses" / course.slug
        if destination.exists():
            raise RuntimeError(f"Course directory already exists: {destination}")

        # Staging keeps an interrupted course from becoming part of the corpus.
        with tempfile.TemporaryDirectory(prefix=f"tagd-archive-{course.id}-") as temp_dir:
            staging_writer = MarkdownCorpusWriter(Path(temp_dir), self.downloader)
            staging_writer.write_course_structure(course)
            for assignment in course.assignments:
                staging_writer.write_assignment_structure(course, assignment)

            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise RuntimeError(f"Course directory already exists: {destination}")
            shutil.move(str(Path(temp_dir) / "courses" / course.slug), destination)

    def write_course_structure(self, course: Course) -> None:
        course_dir = self.target_root / "courses" / course.slug
        course_dir.mkdir(parents=True, exist_ok=True)
        lines = [f"# {course.name}"]
        if course.description:
            lines.extend(["", course.description])
        (course_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_assignment_structure(self, course: Course, assignment: Assignment) -> None:
        print(f"* Assignment: '{assignment.title}'")
        assignment_dir_name = self._assignment_dir_name(assignment)
        try:
            type_subdirectory = ENTRY_TYPE_DIRECTORIES[assignment.work_type]
        except KeyError as exc:
            # Reject unknown taxonomy rather than placing content in a misleading collection.
            raise RuntimeError(f"Unsupported Classroom work type: {assignment.work_type}") from exc
        assignment_dir = (
            self.target_root
            / "courses"
            / course.slug
            / type_subdirectory
            / assignment_dir_name
        )
        assignment_dir.mkdir(parents=True, exist_ok=True)
        lines = [f"# {assignment.title}"]
        if assignment.description:
            lines.extend(["", assignment.description])
        link_materials = [
            material
            for material in assignment.materials
            if material.source_type in {"link", "youtubeVideo"}
        ]
        file_materials = [
            material
            for material in assignment.materials
            if material.source_type not in {"link", "youtubeVideo"}
        ]
        if link_materials:
            lines.extend(["", "## Links", ""])
            for material in link_materials:
                youtube_suffix = " (YouTube)" if material.source_type == "youtubeVideo" else ""
                lines.append(
                    f"* [{material.title}]({material.source_url}){youtube_suffix}"
                )
        if file_materials:
            lines.extend(["", "## Materials", ""])
            for material in file_materials:
                lines.append(
                    self._write_material(
                        assignment_dir,
                        material,
                    )
                )
        detail_lines = self._assignment_detail_lines(assignment)
        if detail_lines:
            lines.extend(["", "## Assignment Details", *detail_lines])
        (assignment_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_material(
        self,
        assignment_dir: Path,
        material: ClassroomResource,
    ) -> str:
        if material.source_type == "missingDriveFile":
            return self._missing_attachment_stub(material)
        if material.source_type == "unsupportedDriveFile":
            print(
                f"Error: Unsupported Drive MIME type '{material.mime_type}' "
                f"for attachment '{material.title}'.",
                file=sys.stderr,
            )
            raise UnsupportedDriveMimeError(
                f"Unsupported Drive MIME type '{material.mime_type}' "
                f"for attachment '{material.title}'."
            )
        if material.source_type != "driveFile" or not self.downloader or not material.file_id:
            return f"* [{material.title}]({material.source_url})"

        attachments_dir = assignment_dir / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)
        local_paths = self._attachment_paths(material, attachments_dir)
        try:
            for local_path in local_paths:
                self.downloader(material.file_id, local_path)
        except MissingDriveAttachmentError:
            self._remove_incomplete_attachment_paths(local_paths)
            if attachments_dir.exists() and not any(attachments_dir.iterdir()):
                attachments_dir.rmdir()
            return self._missing_attachment_stub(material)
        except DriveExportSizeLimitError:
            self._remove_incomplete_attachment_paths(local_paths)
            if attachments_dir.exists() and not any(attachments_dir.iterdir()):
                attachments_dir.rmdir()
            return self._export_size_limit_stub(material)
        return self._local_material_link(material, local_paths)

    def _missing_attachment_stub(
        self,
        material: ClassroomResource,
    ) -> str:
        print(
            f"Warning: Attachment '{material.file_id}' ('{material.title}') not found "
            "or inaccessible. Skipping attachment download.",
            file=sys.stderr,
        )
        return (
            f"* [Attachment Missing: {material.title} "
            "(File not found or inaccessible on Google Drive)]"
        )

    def _export_size_limit_stub(self, material: ClassroomResource) -> str:
        print(
            f"Warning: Attachment '{material.title}' (ID: '{material.file_id}') "
            "exceeds Google Drive API export size limits. Skipping attachment download.",
            file=sys.stderr,
        )
        return (
            f"* [Attachment Unavailable: {material.title} "
            "(Exceeds Google Drive API export size limits)]"
        )

    def _remove_incomplete_attachment_paths(self, local_paths: list[Path]) -> None:
        for local_path in local_paths:
            local_path.unlink(missing_ok=True)
            sidecar_dir = local_path.parent / f"{local_path.name}-files"
            if sidecar_dir.exists():
                shutil.rmtree(sidecar_dir)

    def _attachment_paths(
        self,
        material: ClassroomResource,
        attachments_dir: Path,
    ) -> list[Path]:
        filename = sanitize_filename(material.title)
        exports = WORKSPACE_EXPORTS.get(material.mime_type)
        if exports:
            return [attachments_dir / f"{filename}{suffix}" for suffix, _ in exports]
        return [attachments_dir / filename]

    def _local_material_link(
        self,
        material: ClassroomResource,
        local_paths: list[Path],
    ) -> str:
        relative_paths = [f"attachments/{path.name}" for path in local_paths]
        if material.mime_type == "application/vnd.google-apps.document":
            return (
                f"* [{material.title}]({relative_paths[0]}) "
                f"([DOCX]({relative_paths[1]}))"
            )
        if material.mime_type == "application/vnd.google-apps.presentation":
            return (
                f"* [{material.title}]({relative_paths[0]}) "
                f"([PDF]({relative_paths[1]}))"
            )
        return f"* [{material.title}]({relative_paths[0]})"

    def _assignment_dir_name(self, assignment: Assignment) -> str:
        creation_date = assignment.creation_time[:10]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", creation_date):
            prefix = f"{creation_date}-"
            return prefix + assignment.slug[
                : MAX_ASSIGNMENT_DIRECTORY_NAME_LENGTH - len(prefix)
            ]
        return assignment.slug[:MAX_ASSIGNMENT_DIRECTORY_NAME_LENGTH]

    def _assignment_detail_lines(self, assignment: Assignment) -> list[str]:
        details: list[str] = []
        creation_date = assignment.creation_time[:10]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", creation_date):
            details.append(f"* Created: {creation_date}")
        if assignment.due_time:
            details.append(f"* Due: {assignment.due_time}")
        if assignment.max_points is not None:
            details.append(f"* Points: {assignment.max_points:g}")
        if assignment.topic:
            details.append(f"* Topic: {assignment.topic}")
        if assignment.rubric is not None:
            details.append("* Rubric: ./rubric.csv")
        return details


class GoogleClassroomScraper(ClassroomScraper):
    """Live Google API-backed Classroom metadata scraper."""

    def __init__(self) -> None:
        self.classroom_service: Any = None
        self.drive_service: Any = None
        self.token_path: Path | None = None
        self.drive_metadata: dict[str, dict[str, Any]] = {}

    def authenticate(self, creds_path: Path) -> None:
        self._validate_client_credentials_file(creds_path)
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "Missing Google API dependencies. Install google-auth-oauthlib "
                "and google-api-python-client."
            ) from exc

        self.token_path = creds_path.parent / "token.json"
        credentials = self._load_cached_credentials(Credentials, self.token_path)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                # Prevent oauthlib from failing if Google rewrites token scopes.
                os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(creds_path),
                    GOOGLE_API_SCOPES,
                )
                # Fixed localhost binding avoids dynamic high-port redirect drops.
                credentials = flow.run_local_server(
                    host="localhost",
                    port=8080,
                    prompt="consent",
                )
            self._save_credentials(credentials, self.token_path)

        self.classroom_service = build("classroom", "v1", credentials=credentials)
        self.drive_service = build("drive", "v3", credentials=credentials)

    def _validate_client_credentials_file(self, creds_path: Path) -> None:
        if not creds_path.exists():
            raise RuntimeError(f"Credentials file does not exist: {creds_path}")
        if creds_path.stat().st_size == 0:
            raise RuntimeError(f"Credentials file is empty: {creds_path}")
        try:
            client_config = json.loads(creds_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Credentials file is not valid JSON: {creds_path}") from exc
        # OAuth Desktop credentials must contain one of Google's recognized roots.
        if "installed" not in client_config and "web" not in client_config:
            raise RuntimeError(
                "Credentials file must be a Google OAuth client secrets JSON file "
                "with an 'installed' application section."
            )

    def fetch_courses(self, teacher_email: str | None = None) -> list[Course]:
        course_filters: dict[str, Any] = {
            "courseStates": ["ACTIVE", "ARCHIVED"],
        }
        if teacher_email:
            course_filters["teacherId"] = teacher_email
        return [
            self._map_course(payload)
            for payload in self._paginate(
                self.classroom_service.courses().list,
                "courses",
                **course_filters,
            )
        ]

    def fetch_assignments(self, course_id: str) -> list[Assignment]:
        try:
            topic_cache = self._fetch_topic_cache(course_id)
            assignments = [
                self._map_course_work(payload, topic_cache)
                for payload in self._paginate(
                    self.classroom_service.courses().courseWork().list,
                    "courseWork",
                    courseId=course_id,
                )
            ]
            assignments.extend(
                self._map_course_work_material(payload, topic_cache)
                for payload in self._paginate(
                    self.classroom_service.courses().courseWorkMaterials().list,
                    "courseWorkMaterial",
                    courseId=course_id,
                )
            )
            return assignments
        except Exception as exc:
            # Course context turns an opaque API denial into actionable archive guidance.
            status = getattr(getattr(exc, "resp", None), "status", None)
            if status == 403:
                raise RuntimeError(
                    f"Permission denied accessing coursework for course '{course_id}'. "
                    "Ensure the authenticated account is an owner/teacher of this course "
                    "(active or archived). Halting execution."
                ) from exc
            raise

    def _fetch_topic_cache(self, course_id: str) -> dict[str, str]:
        try:
            topics = self._paginate(
                self.classroom_service.courses().topics().list,
                "topics",
                courseId=course_id,
            )
        except Exception:
            # Topic access must not make otherwise readable coursework unarchivable.
            return {}
        return {
            topic["topicId"]: topic["name"]
            for topic in topics
            if topic.get("topicId") and topic.get("name")
        }

    def _load_cached_credentials(self, credentials_cls: Any, token_path: Path) -> Any:
        if not token_path.exists():
            return None
        return credentials_cls.from_authorized_user_file(
            str(token_path),
            GOOGLE_API_SCOPES,
        )

    def _save_credentials(self, credentials: Any, token_path: Path) -> None:
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json(), encoding="utf-8")

    def _paginate(self, list_method: Any, response_key: str, **kwargs: Any) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page_token = None
        while True:
            request_kwargs = dict(kwargs)
            if page_token:
                request_kwargs["pageToken"] = page_token
            for attempt in range(3):
                try:
                    response = list_method(**request_kwargs).execute()
                    break
                except Exception as exc:
                    status = getattr(getattr(exc, "resp", None), "status", None)
                    if status not in {500, 502, 503, 504}:
                        raise
                    if attempt == 2:
                        course_id = request_kwargs.get("courseId", "unknown")
                        raise RuntimeError(
                            f"Google API transient error ({status}) on course "
                            f"'{course_id}'. Halting execution."
                        ) from exc
                    # Bounded backoff handles brief Google API faults without hiding failures.
                    time.sleep(2 ** attempt)
            items.extend(response.get(response_key, []))
            page_token = response.get("nextPageToken")
            if not page_token:
                return items

    def _map_course(self, payload: dict[str, Any]) -> Course:
        return Course(
            id=payload["id"],
            name=payload.get("name", payload["id"]),
            description=payload.get("description"),
        )

    def _map_course_work(
        self,
        payload: dict[str, Any],
        topic_cache: dict[str, str],
    ) -> Assignment:
        materials_payload = payload.get("materials", [])
        work_type = payload.get("workType", "ASSIGNMENT")
        title = payload.get("title", payload.get("id", "Untitled coursework"))
        coursework_id = payload.get("id", "unknown")
        if work_type not in SUPPORTED_WORK_TYPES:
            raise RuntimeError(
                f"Unsupported Classroom work type: [{work_type}] in assignment "
                f"'{title}' ({coursework_id}). Halting execution."
            )
        if work_type == "ASSIGNMENT" and self._has_google_form(materials_payload):
            work_type = "QUIZ_ASSIGNMENT"
        return Assignment(
            title=title,
            description=payload.get("description"),
            materials=self._map_materials(materials_payload, title),
            creation_time=payload.get("creationTime", ""),
            max_points=self._map_max_points(payload.get("maxPoints")),
            due_time=self._map_due_time(payload),
            work_type=work_type,
            topic=self._resolve_topic(payload.get("topicId"), topic_cache),
            rubric=payload.get("rubric"),
        )

    def _map_course_work_material(
        self,
        payload: dict[str, Any],
        topic_cache: dict[str, str],
    ) -> Assignment:
        title = payload.get("title", payload.get("id", "Untitled material"))
        return Assignment(
            title=title,
            description=payload.get("description"),
            materials=self._map_materials(payload.get("materials", []), title),
            creation_time=payload.get("creationTime", ""),
            topic=self._resolve_topic(payload.get("topicId"), topic_cache),
            work_type="MATERIAL",
        )

    def _has_google_form(self, materials: list[dict[str, Any]]) -> bool:
        for material in materials:
            if "form" in material:
                return True
            link_url = material.get("link", {}).get("url", "")
            if urlparse(link_url).hostname == "forms.google.com":
                return True
        return False

    def _resolve_topic(
        self,
        topic_id: Any,
        topic_cache: dict[str, str],
    ) -> str | None:
        if not isinstance(topic_id, str) or not topic_id:
            return None
        return topic_cache.get(topic_id)

    def _map_max_points(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _map_due_time(self, payload: dict[str, Any]) -> str | None:
        due_date = payload.get("dueDate")
        due_time = payload.get("dueTime")
        if not due_date or not due_time:
            return None
        try:
            year = int(due_date["year"])
            month = int(due_date["month"])
            day = int(due_date["day"])
            hours = int(due_time.get("hours", 0))
            minutes = int(due_time.get("minutes", 0))
        except (KeyError, TypeError, ValueError):
            return None
        # Zero padding preserves lexical sorting and matches the corpus metadata contract.
        return f"{year:04d}-{month:02d}-{day:02d} {hours:02d}:{minutes:02d}"

    def _map_materials(
        self,
        materials: list[Any],
        assignment_title: str,
    ) -> list[ClassroomResource]:
        return [
            resource
            for material in materials
            for resource in self._map_material(material, assignment_title)
        ]

    def _map_material(
        self,
        material: Any,
        assignment_title: str,
    ) -> list[ClassroomResource]:
        if not isinstance(material, dict):
            raise RuntimeError(
                "Unsupported material attachment type: [unknown] in assignment "
                f"'{assignment_title}'. Halting execution."
            )
        if "driveFile" in material:
            return [
                self._map_drive_file(
                    material["driveFile"].get("driveFile", {}),
                    assignment_title,
                )
            ]
        if "link" in material:
            link = material["link"]
            return [
                ClassroomResource(
                    title=link.get("title", link.get("url", "Untitled link")),
                    source_type="link",
                    source_url=link.get("url", ""),
                )
            ]
        if "youtubeVideo" in material:
            video = material["youtubeVideo"]
            return [
                ClassroomResource(
                    title=video.get("title", video.get("id", "Untitled YouTube video")),
                    source_type="youtubeVideo",
                    source_url=video.get("alternateLink", ""),
                )
            ]
        if "form" in material:
            form = material["form"]
            return [
                ClassroomResource(
                    title=form.get("title", form.get("formUrl", "Untitled form")),
                    source_type="form",
                    source_url=form.get("formUrl", ""),
                )
            ]
        source_type = next(iter(material), "unknown")
        raise RuntimeError(
            f"Unsupported material attachment type: [{source_type}] in assignment "
            f"'{assignment_title}'. Halting execution."
        )

    def _map_drive_file(
        self,
        drive_file: dict[str, Any],
        assignment_title: str,
    ) -> ClassroomResource:
        file_id = drive_file.get("id")
        try:
            metadata = self._fetch_drive_file_metadata(file_id, assignment_title)
        except MissingDriveAttachmentError:
            return ClassroomResource(
                title=drive_file.get("title") or file_id or "Unknown attachment",
                source_type="missingDriveFile",
                source_url="",
                file_id=file_id,
            )
        title = metadata.get("name") or drive_file.get("title") or drive_file.get("id", "")
        source_url = metadata.get("webViewLink") or drive_file.get("alternateLink", "")
        mime_type = metadata.get("mimeType")
        # Uploaded blobs are intrinsically downloadable; only Workspace apps need
        # an explicit export contract to prevent lossy or impossible archives.
        is_supported = bool(mime_type) and (
            mime_type in SUPPORTED_WORKSPACE_MIME_TYPES
            or not mime_type.startswith(GOOGLE_WORKSPACE_MIME_PREFIX)
        )
        source_type = "driveFile" if is_supported else "unsupportedDriveFile"
        return ClassroomResource(
            title=title,
            source_type=source_type,
            source_url=source_url,
            mime_type=mime_type,
            file_id=file_id,
        )

    def _fetch_drive_file_metadata(
        self,
        file_id: str | None,
        assignment_title: str,
    ) -> dict[str, Any]:
        if not file_id or not self.drive_service:
            return {}
        try:
            metadata = (
                self.drive_service.files()
                .get(fileId=file_id, fields="id,name,mimeType,webViewLink")
                .execute()
            )
            self.drive_metadata[file_id] = metadata
            return metadata
        except Exception as exc:
            # Translate only known HTTP failures; unexpected API failures retain their details.
            status = getattr(getattr(exc, "resp", None), "status", None)
            if status == 404:
                raise MissingDriveAttachmentError(file_id) from exc
            if status == 403:
                raise RuntimeError(
                    f"Permission denied for Drive file [{file_id}] in assignment "
                    f"'{assignment_title}'. Check OAuth scopes. Halting execution."
                ) from exc
            raise

    def download_drive_file(self, file_id: str, destination_path: Path) -> None:
        """Stream one mapped Drive attachment or export directly into staging."""
        try:
            metadata = self.drive_metadata.get(file_id)
            if metadata is None:
                metadata = (
                    self.drive_service.files()
                    .get(fileId=file_id, fields="id,name,mimeType,webViewLink")
                    .execute()
                )
                self.drive_metadata[file_id] = metadata
            mime_type = metadata.get("mimeType")
            if (
                mime_type == "application/vnd.google-apps.document"
                and destination_path.suffix == ".md"
            ):
                self._export_google_doc_markdown(file_id, destination_path)
                return
            export_mime_type = self._export_mime_type(
                mime_type,
                destination_path.suffix,
            )
            if export_mime_type:
                request = self.drive_service.files().export_media(
                    fileId=file_id,
                    mimeType=export_mime_type,
                )
            else:
                request = self.drive_service.files().get_media(fileId=file_id)
            self._stream_drive_request(request, destination_path)
        except Exception as exc:
            status = getattr(getattr(exc, "resp", None), "status", None)
            if status == 404:
                raise MissingDriveAttachmentError(file_id) from exc
            if self._is_export_size_limit_error(exc):
                raise DriveExportSizeLimitError(file_id) from exc
            raise

    def _is_export_size_limit_error(self, exc: Exception) -> bool:
        status = getattr(getattr(exc, "resp", None), "status", None)
        if status != 403:
            return False
        # Drive has represented this condition in both structured reasons and text.
        error_text = " ".join(
            (
                str(exc),
                repr(getattr(exc, "content", "")),
                repr(getattr(exc, "error_details", "")),
            )
        )
        return (
            "exportSizeLimitExceeded" in error_text
            or "This file is too large to be exported." in error_text
        )

    def _export_mime_type(self, mime_type: Any, suffix: str) -> str | None:
        for export_suffix, export_mime_type in WORKSPACE_EXPORTS.get(mime_type, ()):
            if export_suffix == suffix:
                return export_mime_type
        return None

    def _stream_drive_request(self, request: Any, destination_path: Path) -> None:
        try:
            from googleapiclient.http import MediaIoBaseDownload
        except ImportError as exc:
            raise RuntimeError(
                "Missing Google API dependency google-api-python-client."
            ) from exc
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        with destination_path.open("wb") as output_file:
            downloader = MediaIoBaseDownload(output_file, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

    def _export_google_doc_markdown(self, file_id: str, destination_path: Path) -> None:
        try:
            from markdownify import markdownify
        except ImportError as exc:
            raise RuntimeError(
                "Missing Google Doc conversion dependency. Install markdownify."
            ) from exc

        with tempfile.TemporaryDirectory(prefix="tagd-google-doc-") as temp_dir:
            export_path = Path(temp_dir) / "document-export"
            request = self.drive_service.files().export_media(
                fileId=file_id,
                mimeType="text/html",
            )
            self._stream_drive_request(request, export_path)
            response_bytes = export_path.read_bytes()
            response_buffer = io.BytesIO(response_bytes)
            if zipfile.is_zipfile(response_buffer):
                response_buffer.seek(0)
                with zipfile.ZipFile(response_buffer) as archive:
                    html_names = [
                        name
                        for name in archive.namelist()
                        if name.lower().endswith(".html")
                    ]
                    if not html_names:
                        raise RuntimeError(
                            f"Google Doc HTML export contained no HTML file: [{file_id}]. "
                            "Halting execution."
                        )
                    html = archive.read(html_names[0]).decode("utf-8")
                    sidecar_name = f"{destination_path.name}-files"
                    sidecar_dir = destination_path.parent / sidecar_name
                    for member in archive.namelist():
                        if member.endswith("/") or not member.startswith("images/"):
                            continue
                        relative_media_path = Path(member).relative_to("images")
                        if any(part == ".." for part in relative_media_path.parts):
                            raise RuntimeError(
                                f"Unsafe media path in Google Doc export: [{member}]. "
                                "Halting execution."
                            )
                        media_path = sidecar_dir / relative_media_path
                        media_path.parent.mkdir(parents=True, exist_ok=True)
                        media_path.write_bytes(archive.read(member))
                        html = html.replace(
                            member,
                            f"{sidecar_name}/{relative_media_path.as_posix()}",
                        )
            else:
                # Text-only Docs may return HTML directly instead of a ZIP container.
                html = response_bytes.decode("utf-8")
            destination_path.write_text(markdownify(html), encoding="utf-8")


# --- Main Orchestration Execution ---

def build_parser() -> argparse.ArgumentParser:
    usage_examples = "\n".join(
        [
            "Usage:",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json --list-classrooms",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json --course full-stack-webdev",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json --archive-classroom 1234567890-apcsa-2025-2026",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json --archive-classrooms-file docs/classrooms-list.txt",
        ]
    )
    parser = argparse.ArgumentParser(
        add_help=False,
        description="Archive Google Classroom courses into a local corpus hierarchy.",
        epilog=usage_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--help",
        action="help",
        help="Show this help message and exit.",
    )
    parser.add_argument(
        "--creds",
        required=True,
        type=Path,
        help="Path to the Google Cloud OAuth2 desktop client credentials JSON file.",
    )
    parser.add_argument(
        "--output",
        default=None,
        type=Path,
        help="Legacy alias for the target corpus root directory.",
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=None,
        help="Path to an external educational corpus root directory.",
    )
    parser.add_argument(
        "--course",
        default="all",
        help="Course slug or ID to archive (default: all).",
    )
    parser.add_argument(
        "--teacher-email",
        type=str,
        default=None,
        help="Filter discovered courses strictly to those taught by this teacher email address.",
    )
    parser.add_argument(
        "--list-classrooms",
        action="store_true",
        help="Print available archive tokens, then exit without writing.",
    )
    parser.add_argument(
        "--archive-classroom",
        default=None,
        metavar="ARCHIVE_TOKEN",
        help="Archive one classroom by archive token (e.g. 1234567890-apcsa-2025-2026).",
    )
    parser.add_argument(
        "--archive-classrooms-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="Archive classroom tokens listed in a text file, skipping existing courses.",
    )
    return parser


def list_classrooms(
    scraper: ClassroomScraper,
    creds_path: Path,
    teacher_email: str | None = None,
) -> None:
    scraper.authenticate(creds_path)
    for course in scraper.fetch_courses(teacher_email=teacher_email):
        print(format_archive_token(course))


def write_course_archive(writer: CorpusWriter, course: Course) -> None:
    """Write one validated course through the writer's strongest available boundary."""
    if isinstance(writer, MarkdownCorpusWriter):
        writer.write_course(course)
        return
    writer.write_course_structure(course)
    for assignment in course.assignments:
        writer.write_assignment_structure(course, assignment)


def archive_classroom(
    scraper: ClassroomScraper,
    writer: CorpusWriter,
    creds_path: Path,
    archive_token: str,
    teacher_email: str | None = None,
) -> None:
    classroom_id = parse_archive_token(archive_token)
    scraper.authenticate(creds_path)
    courses = scraper.fetch_courses(teacher_email=teacher_email)
    course = next((c for c in courses if c.id == classroom_id), None)
    if course is None:
        raise RuntimeError(f"Classroom ID not found: {classroom_id}")
    course_dir = writer.target_root / "courses" / course.slug
    # Refuse an existing course before fetching or writing so archives stay immutable.
    if course_dir.exists():
        raise RuntimeError("course directory already exists")
    course.assignments = scraper.fetch_assignments(course.id)
    write_course_archive(writer, course)


def read_archive_tokens(token_file: Path) -> list[str]:
    """Read actionable archive tokens while preserving their file order."""
    try:
        lines = token_file.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"Unable to read classroom token file: {token_file}") from exc
    return [
        stripped
        for line in lines
        if (stripped := line.strip()) and not stripped.startswith("#")
    ]


def archive_classrooms_file(
    scraper: ClassroomScraper,
    writer: CorpusWriter,
    creds_path: Path,
    token_file: Path,
    teacher_email: str | None = None,
) -> None:
    """Archive listed classrooms sequentially, resuming past completed courses."""
    scraper.authenticate(creds_path)
    courses_by_id = {
        course.id: course
        for course in scraper.fetch_courses(teacher_email=teacher_email)
    }
    archived_count = 0
    for archive_token in read_archive_tokens(token_file):
        classroom_id = parse_archive_token(archive_token)
        course = courses_by_id.get(classroom_id)
        if course is None:
            raise RuntimeError(f"Classroom ID not found: {classroom_id}")
        canonical_token = format_archive_token(course)
        course_dir = writer.target_root / "courses" / course.slug
        if course_dir.exists():
            # Existing directories are completed checkpoints for resumable batch runs.
            print(f"Skipping '{canonical_token}', already exists")
            continue
        print(f"Archiving '{canonical_token}' ...")
        course.assignments = scraper.fetch_assignments(course.id)
        write_course_archive(writer, course)
        archived_count += 1
    print(f"{archived_count} courses archived")


def archive_courses(
    scraper: ClassroomScraper,
    writer: CorpusWriter,
    creds_path: Path,
    course_filter: str,
    teacher_email: str | None = None,
) -> None:
    scraper.authenticate(creds_path)
    for course in scraper.fetch_courses(teacher_email=teacher_email):
        if course_filter != "all" and course_filter not in {course.id, course.slug}:
            continue
        course.assignments = scraper.fetch_assignments(course.id)
        write_course_archive(writer, course)


def main(
    argv: list[str] | None = None,
    scraper: ClassroomScraper | None = None,
    writer: CorpusWriter | None = None,
) -> int:
    # Injection keeps CLI routing verifiable without requiring Google API state.
    parser = build_parser()
    args = parser.parse_args(argv)
    active_scraper = scraper or GoogleClassroomScraper()

    try:
        if args.corpus_dir is not None:
            if not args.corpus_dir.is_dir():
                raise RuntimeError("corpus directory does not exist")
            active_corpus_root = args.corpus_dir
        elif args.output is not None:
            active_corpus_root = args.output
        else:
            active_corpus_root = Path.cwd() / "corpus"

        if args.list_classrooms:
            list_classrooms(active_scraper, args.creds, args.teacher_email)
            return 0

        if writer is None and args.corpus_dir is None and args.output is None:
            # Only the implicit local corpus is safe to create on the user's behalf.
            active_corpus_root.mkdir(parents=True, exist_ok=True)

        active_writer = writer or MarkdownCorpusWriter(
            active_corpus_root,
            getattr(active_scraper, "download_drive_file", None),
        )

        if args.archive_classrooms_file:
            archive_classrooms_file(
                active_scraper,
                active_writer,
                args.creds,
                args.archive_classrooms_file,
                args.teacher_email,
            )
            return 0

        if args.archive_classroom:
            archive_classroom(
                active_scraper,
                active_writer,
                args.creds,
                args.archive_classroom,
                args.teacher_email,
            )
            return 0

        archive_courses(
            active_scraper,
            active_writer,
            args.creds,
            args.course,
            args.teacher_email,
        )
    except UnsupportedDriveMimeError:
        raise SystemExit(1)
    except RuntimeError as exc:
        parser.exit(1, f"classroom-archiver.py: error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
