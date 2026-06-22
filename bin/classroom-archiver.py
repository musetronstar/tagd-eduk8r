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
import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# --- Configuration & Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CORPUS_ROOT = REPO_ROOT / "corpus"
GOOGLE_API_SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


# --- Data Models ---

def slugify(value: str) -> str:
    """Return a clean token suitable for selecting a Classroom course."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


@dataclass
class ClassroomResource:
    """A Classroom resource, material, attachment, or linked asset."""

    title: str
    source_type: str
    source_url: str
    mime_type: str | None = None
    local_filename: str | None = None


@dataclass
class Assignment:
    """A Google Classroom coursework item."""

    title: str
    description: str | None = None
    materials: list[ClassroomResource] = field(default_factory=list)
    slug: str = ""

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


class GoogleClassroomScraper(ClassroomScraper):
    """Live Google API-backed Classroom metadata scraper."""

    def __init__(self) -> None:
        self.classroom_service: Any = None
        self.drive_service: Any = None
        self.token_path: Path | None = None

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
        courses: list[Course] = []
        for state in ("ACTIVE", "ARCHIVED"):
            course_filters: dict[str, Any] = {"courseStates": [state]}
            if teacher_email:
                course_filters["teacherId"] = teacher_email
            for payload in self._paginate(
                self.classroom_service.courses().list,
                "courses",
                **course_filters,
            ):
                courses.append(self._map_course(payload))
        return courses

    def fetch_assignments(self, course_id: str) -> list[Assignment]:
        assignments = [
            self._map_course_work(payload)
            for payload in self._paginate(
                self.classroom_service.courses().courseWork().list,
                "courseWork",
                courseId=course_id,
            )
        ]
        assignments.extend(
            self._map_course_work_material(payload)
            for payload in self._paginate(
                self.classroom_service.courses().courseWorkMaterials().list,
                "courseWorkMaterial",
                courseId=course_id,
            )
        )
        return assignments

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
            response = list_method(**request_kwargs).execute()
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

    def _map_course_work(self, payload: dict[str, Any]) -> Assignment:
        return Assignment(
            title=payload.get("title", payload.get("id", "Untitled coursework")),
            description=payload.get("description"),
            materials=self._map_materials(payload.get("materials", [])),
        )

    def _map_course_work_material(self, payload: dict[str, Any]) -> Assignment:
        return Assignment(
            title=payload.get("title", payload.get("id", "Untitled material")),
            description=payload.get("description"),
            materials=self._map_materials(payload.get("materials", [])),
        )

    def _map_materials(self, materials: list[dict[str, Any]]) -> list[ClassroomResource]:
        return [resource for material in materials for resource in self._map_material(material)]

    def _map_material(self, material: dict[str, Any]) -> list[ClassroomResource]:
        if "driveFile" in material:
            return [self._map_drive_file(material["driveFile"].get("driveFile", {}))]
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
        return []

    def _map_drive_file(self, drive_file: dict[str, Any]) -> ClassroomResource:
        metadata = self._fetch_drive_file_metadata(drive_file.get("id"))
        title = metadata.get("name") or drive_file.get("title") or drive_file.get("id", "")
        source_url = metadata.get("webViewLink") or drive_file.get("alternateLink", "")
        return ClassroomResource(
            title=title,
            source_type="driveFile",
            source_url=source_url,
            mime_type=metadata.get("mimeType"),
        )

    def _fetch_drive_file_metadata(self, file_id: str | None) -> dict[str, Any]:
        if not file_id or not self.drive_service:
            return {}
        return (
            self.drive_service.files()
            .get(fileId=file_id, fields="id,name,mimeType,webViewLink")
            .execute()
        )


# --- Main Orchestration Execution ---

def build_parser() -> argparse.ArgumentParser:
    usage_examples = "\n".join(
        [
            "Usage:",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json --list-classrooms",
            "    python3 bin/classroom-archiver.py --creds secrets/credentials.json --course full-stack-webdev",
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
        default=DEFAULT_CORPUS_ROOT,
        type=Path,
        help=f"Target output root directory (default: {DEFAULT_CORPUS_ROOT}).",
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
        help="Print available course names and slug tokens, then exit without writing.",
    )
    return parser


def list_classrooms(
    scraper: ClassroomScraper,
    creds_path: Path,
    teacher_email: str | None = None,
) -> None:
    scraper.authenticate(creds_path)
    for course in scraper.fetch_courses(teacher_email=teacher_email):
        print(f"{course.name}\t{course.slug}")


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
        writer.write_course_structure(course)
        for assignment in course.assignments:
            writer.write_assignment_structure(course, assignment)


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
        if args.list_classrooms:
            list_classrooms(active_scraper, args.creds, args.teacher_email)
            return 0

        active_writer = writer or SkeletonCorpusWriter(args.output)
        archive_courses(
            active_scraper,
            active_writer,
            args.creds,
            args.course,
            args.teacher_email,
        )
    except RuntimeError as exc:
        parser.exit(1, f"classroom-archiver.py: error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
