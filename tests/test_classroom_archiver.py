import importlib.util
import json
import os
import re
import sys
import types
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "bin" / "classroom-archiver.py"


def load_archiver():
    spec = importlib.util.spec_from_file_location("classroom_archiver", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_help_uses_explicit_long_form_options(capsys):
    archiver = load_archiver()

    try:
        archiver.main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out
    assert "--creds" in output
    assert "--output" in output
    assert "--course" in output
    assert "--teacher-email" in output
    assert "--list-classrooms" in output
    assert "Usage:" in output
    assert "python3 bin/classroom-archiver.py --creds secrets/credentials.json" in output
    assert not re.search(r"(^|[\s,])-[A-Za-z](\b|,)", output)


def test_missing_creds_is_argparse_validation_error(capsys):
    archiver = load_archiver()

    try:
        archiver.main(["--list-classrooms"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("missing --creds should fail argument parsing")

    error = capsys.readouterr().err
    assert "--creds" in error
    assert "required" in error


def test_required_pipeline_abstractions_and_dataclasses_exist():
    archiver = load_archiver()

    for name in ("ClassroomScraper", "ContentConverter", "CorpusWriter"):
        cls = getattr(archiver, name)
        assert cls.__abstractmethods__

    assert archiver.ContentConverter.__abstractmethods__ == {
        "document_to_markdown",
        "sheet_to_csv",
    }

    for name in ("Course", "Assignment", "ClassroomResource"):
        cls = getattr(archiver, name)
        assert hasattr(cls, "__dataclass_fields__")

    assert "materials" in archiver.Assignment.__dataclass_fields__
    assert archiver.Resource is archiver.ClassroomResource


def test_list_classrooms_authenticates_prints_slugs_and_does_not_write(capsys, tmp_path):
    archiver = load_archiver()

    class FakeScraper(archiver.ClassroomScraper):
        def __init__(self):
            self.authenticated_with = None
            self.assignments_fetched = False

        def authenticate(self, creds_path):
            self.authenticated_with = creds_path

        def fetch_courses(self, teacher_email=None):
            assert teacher_email is None
            return [archiver.Course(id="course-1", name="Full Stack Web Development")]

        def fetch_assignments(self, course_id):
            self.assignments_fetched = True
            return []

    class FailingWriter(archiver.CorpusWriter):
        def write_course_structure(self, course):
            raise AssertionError("list mode must not write courses")

        def write_assignment_structure(self, course, assignment):
            raise AssertionError("list mode must not write assignments")

    creds = tmp_path / "credentials.json"
    scraper = FakeScraper()
    writer = FailingWriter(tmp_path / "corpus")

    result = archiver.main(
        ["--creds", str(creds), "--list-classrooms"],
        scraper=scraper,
        writer=writer,
    )

    output = capsys.readouterr().out
    assert result == 0
    assert scraper.authenticated_with == creds
    assert not scraper.assignments_fetched
    assert "course-1-full-stack-web-development" in output


def test_archive_routing_filters_by_course_and_writes_selected_assignments(tmp_path):
    archiver = load_archiver()

    class FakeScraper(archiver.ClassroomScraper):
        def __init__(self):
            self.authenticated_with = None
            self.assignment_fetches = []

        def authenticate(self, creds_path):
            self.authenticated_with = creds_path

        def fetch_courses(self, teacher_email=None):
            assert teacher_email == "teacher@example.test"
            return [
                archiver.Course(id="course-1", name="Full Stack Web Development"),
                archiver.Course(id="course-2", name="Python Programming 101"),
            ]

        def fetch_assignments(self, course_id):
            self.assignment_fetches.append(course_id)
            return [archiver.Assignment(title=f"Assignment for {course_id}")]

    class RecordingWriter(archiver.CorpusWriter):
        def __init__(self, target_root):
            super().__init__(target_root)
            self.courses = []
            self.assignments = []

        def write_course_structure(self, course):
            self.courses.append(course)

        def write_assignment_structure(self, course, assignment):
            self.assignments.append((course, assignment))

    creds = tmp_path / "credentials.json"
    scraper = FakeScraper()
    writer = RecordingWriter(tmp_path / "corpus")

    result = archiver.main(
        [
            "--creds",
            str(creds),
            "--output",
            str(tmp_path / "out"),
            "--course",
            "python-programming-101",
            "--teacher-email",
            "teacher@example.test",
        ],
        scraper=scraper,
        writer=writer,
    )

    assert result == 0
    assert scraper.authenticated_with == creds
    assert scraper.assignment_fetches == ["course-2"]
    assert [course.slug for course in writer.courses] == ["python-programming-101"]
    assert len(writer.assignments) == 1
    assert writer.assignments[0][1].slug == "assignment-for-course-2"


class FakeRequest:
    def __init__(self, response):
        self.response = response

    def execute(self):
        return self.response


class FailingRequest:
    def __init__(self, error):
        self.error = error

    def execute(self):
        raise self.error


class FakeListEndpoint:
    def __init__(self, responses, calls):
        self.responses = list(responses)
        self.calls = calls

    def list(self, **kwargs):
        self.calls.append(kwargs)
        return FakeRequest(self.responses.pop(0))


class FakeDriveFiles:
    def __init__(self, metadata_by_id):
        self.metadata_by_id = metadata_by_id
        self.calls = []

    def get(self, **kwargs):
        self.calls.append(kwargs)
        response = self.metadata_by_id[kwargs["fileId"]]
        if isinstance(response, Exception):
            return FailingRequest(response)
        return FakeRequest(response)


class FakeDriveService:
    def __init__(self, metadata_by_id):
        self.files_endpoint = FakeDriveFiles(metadata_by_id)

    def files(self):
        return self.files_endpoint


class FakeClassroomCourses:
    def __init__(self, course_responses, coursework_responses, material_responses):
        self.course_calls = []
        self.coursework_calls = []
        self.material_calls = []
        self.course_endpoint = FakeListEndpoint(course_responses, self.course_calls)
        self.coursework_endpoint = FakeListEndpoint(
            coursework_responses,
            self.coursework_calls,
        )
        self.material_endpoint = FakeListEndpoint(
            material_responses,
            self.material_calls,
        )

    def list(self, **kwargs):
        return self.course_endpoint.list(**kwargs)

    def courseWork(self):
        return self.coursework_endpoint

    def courseWorkMaterials(self):
        return self.material_endpoint


class FakeClassroomService:
    def __init__(self, course_responses, coursework_responses=None, material_responses=None):
        self.courses_endpoint = FakeClassroomCourses(
            course_responses,
            coursework_responses or [],
            material_responses or [],
        )

    def courses(self):
        return self.courses_endpoint


def test_google_scraper_fetches_active_and_archived_courses_with_pagination():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()
    scraper.classroom_service = FakeClassroomService(
        [
            {
                "courses": [{"id": "active-1", "name": "Active Course"}],
                "nextPageToken": "next-active",
            },
            {"courses": [{"id": "active-2", "name": "Second Active"}]},
            {"courses": [{"id": "archived-1", "name": "Archived Course"}]},
        ]
    )

    courses = scraper.fetch_courses()
    course_endpoint = scraper.classroom_service.courses_endpoint

    assert [course.id for course in courses] == ["active-1", "active-2", "archived-1"]
    assert [course.slug for course in courses] == [
        "active-course",
        "second-active",
        "archived-course",
    ]
    assert course_endpoint.course_calls == [
        {"courseStates": ["ACTIVE"]},
        {"courseStates": ["ACTIVE"], "pageToken": "next-active"},
        {"courseStates": ["ARCHIVED"]},
    ]


def test_google_scraper_passes_teacher_email_as_teacher_id_filter():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()
    scraper.classroom_service = FakeClassroomService(
        [
            {"courses": [{"id": "active-1", "name": "Active Course"}]},
            {"courses": [{"id": "archived-1", "name": "Archived Course"}]},
        ]
    )

    courses = scraper.fetch_courses(teacher_email="teacher@example.test")
    course_endpoint = scraper.classroom_service.courses_endpoint

    assert [course.id for course in courses] == ["active-1", "archived-1"]
    assert course_endpoint.course_calls == [
        {
            "courseStates": ["ACTIVE"],
            "teacherId": "teacher@example.test",
        },
        {
            "courseStates": ["ARCHIVED"],
            "teacherId": "teacher@example.test",
        },
    ]


def test_google_scraper_maps_coursework_and_coursework_material_resources():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()
    scraper.classroom_service = FakeClassroomService(
        [],
        coursework_responses=[
            {
                "courseWork": [
                    {
                        "id": "work-1",
                        "title": "Build a Page",
                        "description": "Use the linked starter.",
                        "materials": [
                            {
                                "driveFile": {
                                    "driveFile": {
                                        "id": "drive-1",
                                        "title": "Starter Doc",
                                        "alternateLink": "https://drive/doc",
                                    }
                                }
                            },
                            {
                                "link": {
                                    "title": "Reference",
                                    "url": "https://example.test/reference",
                                }
                            },
                        ],
                    }
                ]
            }
        ],
        material_responses=[
            {
                "courseWorkMaterial": [
                    {
                        "id": "material-1",
                        "title": "Demo Video",
                        "materials": [
                            {
                                "youtubeVideo": {
                                    "id": "video-1",
                                    "title": "Walkthrough",
                                    "alternateLink": "https://youtube.test/watch",
                                }
                            }
                        ],
                    }
                ]
            }
        ],
    )
    scraper.drive_service = FakeDriveService(
        {
            "drive-1": {
                "id": "drive-1",
                "name": "Starter Doc Metadata",
                "mimeType": "application/vnd.google-apps.document",
                "webViewLink": "https://drive/doc-metadata",
            }
        }
    )

    assignments = scraper.fetch_assignments("course-1")

    assert [assignment.title for assignment in assignments] == [
        "Build a Page",
        "Demo Video",
    ]
    assert [resource.source_type for resource in assignments[0].materials] == [
        "driveFile",
        "link",
    ]
    assert assignments[0].materials[0].title == "Starter Doc Metadata"
    assert assignments[0].materials[0].mime_type == "application/vnd.google-apps.document"
    assert assignments[0].materials[1].source_url == "https://example.test/reference"
    assert assignments[1].materials[0].source_type == "youtubeVideo"
    assert assignments[1].materials[0].source_url == "https://youtube.test/watch"


def test_google_scraper_rejects_missing_empty_or_invalid_credentials(tmp_path):
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()

    missing = tmp_path / "missing.json"
    empty = tmp_path / "empty.json"
    malformed = tmp_path / "malformed.json"
    wrong_shape = tmp_path / "wrong-shape.json"
    empty.touch()
    malformed.write_text("not json", encoding="utf-8")
    wrong_shape.write_text(json.dumps({"client_id": "value"}), encoding="utf-8")

    cases = [
        (missing, "does not exist"),
        (empty, "is empty"),
        (malformed, "is not valid JSON"),
        (wrong_shape, "OAuth client secrets JSON"),
    ]

    for path, expected in cases:
        try:
            scraper._validate_client_credentials_file(path)
        except RuntimeError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"{path} should fail credentials validation")


def test_cli_reports_empty_credentials_without_traceback(capsys, tmp_path):
    archiver = load_archiver()
    creds = tmp_path / "credentials.json"
    creds.touch()

    try:
        archiver.main(["--creds", str(creds), "--list-classrooms"])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("empty credentials should exit with a parser error")

    captured = capsys.readouterr()
    assert "Credentials file is empty" in captured.err
    assert "Traceback" not in captured.err


def test_google_api_scopes_match_oauth_backend_response():
    archiver = load_archiver()

    assert archiver.GOOGLE_API_SCOPES == [
        "https://www.googleapis.com/auth/classroom.courses.readonly",
        "https://www.googleapis.com/auth/classroom.coursework.students.readonly",
        "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
        "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    assert "https://www.googleapis.com/auth/classroom.coursework.me.readonly" not in (
        archiver.GOOGLE_API_SCOPES
    )


def test_authenticate_relaxes_oauth_scope_before_starting_browser_flow(
    monkeypatch,
    tmp_path,
):
    archiver = load_archiver()
    creds = tmp_path / "credentials.json"
    creds.write_text(json.dumps({"installed": {"client_id": "client"}}), encoding="utf-8")
    monkeypatch.delenv("OAUTHLIB_RELAX_TOKEN_SCOPE", raising=False)

    class FakeCredentials:
        valid = True

        def to_json(self):
            return "{}"

    class FakeCredentialsClass:
        @staticmethod
        def from_authorized_user_file(path, scopes):
            return None

    class FakeFlow:
        @staticmethod
        def from_client_secrets_file(path, scopes):
            assert os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] == "1"
            assert scopes == archiver.GOOGLE_API_SCOPES
            return FakeFlow()

        def run_local_server(self, host, port, prompt):
            assert host == "localhost"
            assert port == 8080
            assert prompt == "consent"
            return FakeCredentials()

    def fake_build(service_name, version, credentials):
        return {"service": service_name, "version": version, "credentials": credentials}

    monkeypatch.setitem(sys.modules, "google", types.ModuleType("google"))
    monkeypatch.setitem(sys.modules, "google.auth", types.ModuleType("google.auth"))
    monkeypatch.setitem(
        sys.modules,
        "google.auth.transport",
        types.ModuleType("google.auth.transport"),
    )
    requests_module = types.ModuleType("google.auth.transport.requests")
    requests_module.Request = object
    monkeypatch.setitem(sys.modules, "google.auth.transport.requests", requests_module)
    monkeypatch.setitem(sys.modules, "google.oauth2", types.ModuleType("google.oauth2"))
    credentials_module = types.ModuleType("google.oauth2.credentials")
    credentials_module.Credentials = FakeCredentialsClass
    monkeypatch.setitem(sys.modules, "google.oauth2.credentials", credentials_module)
    monkeypatch.setitem(
        sys.modules,
        "google_auth_oauthlib",
        types.ModuleType("google_auth_oauthlib"),
    )
    flow_module = types.ModuleType("google_auth_oauthlib.flow")
    flow_module.InstalledAppFlow = FakeFlow
    monkeypatch.setitem(sys.modules, "google_auth_oauthlib.flow", flow_module)
    monkeypatch.setitem(
        sys.modules,
        "googleapiclient",
        types.ModuleType("googleapiclient"),
    )
    discovery_module = types.ModuleType("googleapiclient.discovery")
    discovery_module.build = fake_build
    monkeypatch.setitem(sys.modules, "googleapiclient.discovery", discovery_module)

    scraper = archiver.GoogleClassroomScraper()
    scraper.authenticate(creds)

    assert os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] == "1"
    assert scraper.token_path == tmp_path / "token.json"
    assert scraper.classroom_service["service"] == "classroom"
    assert scraper.drive_service["service"] == "drive"


# --- parse_archive_token ---

def test_parse_archive_token_bare_id():
    archiver = load_archiver()
    assert archiver.parse_archive_token("1234567890") == "1234567890"


def test_parse_archive_token_full_token():
    archiver = load_archiver()
    assert archiver.parse_archive_token("1234567890-g8-2-computer-science-2025-2026") == "1234567890"


# --- CLI: --archive-classroom ---

def test_cli_parser_accepts_archive_classroom():
    archiver = load_archiver()
    parser = archiver.build_parser()
    args = parser.parse_args(["--creds", "creds.json", "--archive-classroom", "1234567890-apcsa-2025-2026"])
    assert args.archive_classroom == "1234567890-apcsa-2025-2026"


# --- MarkdownCorpusWriter ---

def test_markdown_writer_creates_course_index(tmp_path):
    archiver = load_archiver()
    writer = archiver.MarkdownCorpusWriter(tmp_path)
    course = archiver.Course(id="c1", name="APCSA 2025-2026", description="AP Computer Science A")
    writer.write_course_structure(course)
    index = tmp_path / "courses" / "apcsa-2025-2026" / "index.md"
    assert index.exists()
    content = index.read_text(encoding="utf-8")
    assert "# APCSA 2025-2026" in content
    assert "AP Computer Science A" in content


def test_markdown_writer_creates_assignment_index(tmp_path):
    archiver = load_archiver()
    writer = archiver.MarkdownCorpusWriter(tmp_path)
    course = archiver.Course(id="c1", name="APCSA 2025-2026")
    assignment = archiver.Assignment(title="Unit 1 Primitive Types", description="Learn primitives.")
    writer.write_assignment_structure(course, assignment)
    index = tmp_path / "courses" / "apcsa-2025-2026" / "assignments" / "unit-1-primitive-types" / "index.md"
    assert index.exists()
    content = index.read_text(encoding="utf-8")
    assert "# Unit 1 Primitive Types" in content
    assert "Learn primitives." in content


def test_markdown_writer_renders_external_links_only_in_links_section(tmp_path):
    archiver = load_archiver()
    writer = archiver.MarkdownCorpusWriter(tmp_path)
    course = archiver.Course(id="c1", name="APCSA 2025-2026")
    assignment = archiver.Assignment(
        title="Unit 1 Primitive Types",
        materials=[
            archiver.ClassroomResource(
                title="Reference",
                source_type="link",
                source_url="https://example.test/reference",
            ),
            archiver.ClassroomResource(
                title="Walkthrough",
                source_type="youtubeVideo",
                source_url="https://youtube.test/watch",
            ),
        ],
    )
    writer.write_assignment_structure(course, assignment)
    index = tmp_path / "courses" / "apcsa-2025-2026" / "assignments" / "unit-1-primitive-types" / "index.md"
    content = index.read_text(encoding="utf-8")
    assert "## Links" in content
    assert "* [Reference](https://example.test/reference)" in content
    assert "* [Walkthrough](https://youtube.test/watch) (YouTube)" in content
    assert "## Materials" not in content


def test_markdown_writer_omits_links_section_without_external_links(tmp_path):
    archiver = load_archiver()
    writer = archiver.MarkdownCorpusWriter(tmp_path)
    course = archiver.Course(id="c1", name="APCSA 2025-2026")
    assignment = archiver.Assignment(
        title="Unit 1 Primitive Types",
        materials=[
            archiver.ClassroomResource(
                title="Starter Doc",
                source_type="driveFile",
                source_url="https://drive.test/doc",
            )
        ],
    )

    writer.write_assignment_structure(course, assignment)

    index = tmp_path / "courses" / "apcsa-2025-2026" / "assignments" / "unit-1-primitive-types" / "index.md"
    content = index.read_text(encoding="utf-8")
    assert "## Links" not in content
    assert "## Materials" in content
    assert "* [Starter Doc](https://drive.test/doc)" in content


def test_drive_metadata_fetch_translates_not_found_and_permission_errors():
    archiver = load_archiver()

    class FakeHttpError(Exception):
        def __init__(self, status):
            super().__init__(f"HTTP {status}")
            self.resp = types.SimpleNamespace(status=status)

    cases = [
        (
            404,
            "Drive file or attachment not found: [drive-404] in assignment "
            "'Lab 1'. Halting execution.",
        ),
        (
            403,
            "Permission denied for Drive file [drive-403] in assignment "
            "'Lab 1'. Check OAuth scopes. Halting execution.",
        ),
    ]

    for status, expected in cases:
        file_id = f"drive-{status}"
        scraper = archiver.GoogleClassroomScraper()
        scraper.drive_service = FakeDriveService({file_id: FakeHttpError(status)})

        try:
            scraper._fetch_drive_file_metadata(file_id, "Lab 1")
        except RuntimeError as exc:
            assert str(exc) == expected
        else:
            raise AssertionError(f"HTTP {status} should fail Drive metadata fetch")


# --- archive_classroom orchestration ---

def test_archive_classroom_selects_course_by_id(tmp_path):
    archiver = load_archiver()

    class FakeScraper(archiver.ClassroomScraper):
        def __init__(self):
            self.fetched_course_ids = []

        def authenticate(self, creds_path):
            pass

        def fetch_courses(self, teacher_email=None):
            return [
                archiver.Course(id="111", name="Math"),
                archiver.Course(id="222", name="Science"),
            ]

        def fetch_assignments(self, course_id):
            self.fetched_course_ids.append(course_id)
            return []

    class RecordingWriter(archiver.CorpusWriter):
        def __init__(self, target_root):
            super().__init__(target_root)
            self.courses = []

        def write_course_structure(self, course):
            self.courses.append(course)

        def write_assignment_structure(self, course, assignment):
            pass

    creds = tmp_path / "credentials.json"
    scraper = FakeScraper()
    writer = RecordingWriter(tmp_path / "corpus")

    result = archiver.main(
        ["--creds", str(creds), "--archive-classroom", "222-science"],
        scraper=scraper,
        writer=writer,
    )

    assert result == 0
    assert [c.id for c in writer.courses] == ["222"]
    assert scraper.fetched_course_ids == ["222"]


def test_archive_classroom_exits_nonzero_if_id_not_found(capsys, tmp_path):
    archiver = load_archiver()

    class FakeScraper(archiver.ClassroomScraper):
        def authenticate(self, creds_path):
            pass

        def fetch_courses(self, teacher_email=None):
            return [archiver.Course(id="111", name="Math")]

        def fetch_assignments(self, course_id):
            return []

    class NullWriter(archiver.CorpusWriter):
        def write_course_structure(self, course):
            pass

        def write_assignment_structure(self, course, assignment):
            pass

    creds = tmp_path / "credentials.json"
    try:
        archiver.main(
            ["--creds", str(creds), "--archive-classroom", "999-not-found"],
            scraper=FakeScraper(),
            writer=NullWriter(tmp_path),
        )
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("missing classroom ID should exit non-zero")

    err = capsys.readouterr().err
    assert "999" in err


# --- strict archive validation ---

def test_sanitize_filename_replaces_unsafe_characters_and_strips_unsafe_prefixes():
    archiver = load_archiver()

    assert (
        archiver.sanitize_filename('  --Unit 1: Selection / Loops?.pdf  ')
        == "Unit 1- Selection - Loops-.pdf"
    )


def test_sanitize_filename_rejects_empty_result():
    archiver = load_archiver()

    try:
        archiver.sanitize_filename(' /\\:?*<>|" ')
    except RuntimeError as exc:
        assert "empty after sanitization" in str(exc)
    else:
        raise AssertionError("an empty sanitized filename must fail")


def test_google_scraper_rejects_unsupported_work_type_with_payload_context():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()

    try:
        scraper._map_course_work(
            {"id": "work-9", "title": "Mystery Work", "workType": "PROJECT"},
            {},
        )
    except RuntimeError as exc:
        assert str(exc) == (
            "Unsupported Classroom work type: [PROJECT] in assignment "
            "'Mystery Work' (work-9). Halting execution."
        )
    else:
        raise AssertionError("an unsupported work type must fail")


def test_google_scraper_rejects_unknown_material_key():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()

    try:
        scraper._map_material({"book": {"id": "book-1"}}, "Lab 1")
    except RuntimeError as exc:
        assert str(exc) == (
            "Unsupported material attachment type: [book] in assignment "
            "'Lab 1'. Halting execution."
        )
    else:
        raise AssertionError("an unsupported material type must fail")


def test_google_scraper_rejects_material_without_identifiable_key():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()

    try:
        scraper._map_material({}, "Lab 1")
    except RuntimeError as exc:
        assert "attachment type: [unknown]" in str(exc)
    else:
        raise AssertionError("an empty material payload must fail")


def test_google_scraper_rejects_malformed_material_payload():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()

    try:
        scraper._map_material(None, "Lab 1")
    except RuntimeError as exc:
        assert str(exc) == (
            "Unsupported material attachment type: [unknown] in assignment "
            "'Lab 1'. Halting execution."
        )
    else:
        raise AssertionError("a malformed material payload must fail contextually")


def test_google_scraper_rejects_unsupported_drive_mime_type():
    archiver = load_archiver()
    scraper = archiver.GoogleClassroomScraper()
    scraper.drive_service = FakeDriveService(
        {
            "drive-9": {
                "name": "Architecture Drawing",
                "mimeType": "application/vnd.google-apps.drawing",
            }
        }
    )

    try:
        scraper._map_drive_file({"id": "drive-9"}, "Lab 1")
    except RuntimeError as exc:
        assert str(exc) == (
            "Unsupported Drive file MIME type: "
            "[application/vnd.google-apps.drawing] for file "
            "'Architecture Drawing' in assignment 'Lab 1'. Halting execution."
        )
    else:
        raise AssertionError("an unsupported Drive MIME type must fail")


def test_validate_form_item_type_accepts_allowlist_and_rejects_unknown_type():
    archiver = load_archiver()

    for item_type in archiver.SUPPORTED_FORM_ITEM_TYPES:
        archiver.validate_form_item_type(item_type, "form-1")

    try:
        archiver.validate_form_item_type("SCALE", "form-1")
    except RuntimeError as exc:
        assert str(exc) == (
            "Unsupported Google Form question type: [SCALE] in form "
            "'form-1'. Halting execution."
        )
    else:
        raise AssertionError("an unsupported Form item type must fail")


def test_markdown_writer_stages_failed_course_without_partial_destination(tmp_path):
    archiver = load_archiver()
    writer = archiver.MarkdownCorpusWriter(tmp_path / "corpus")
    course = archiver.Course(
        id="course-1",
        name="Course One",
        assignments=[archiver.Assignment(title="Unknown", work_type="PROJECT")],
    )

    try:
        writer.write_course(course)
    except RuntimeError as exc:
        assert "Unsupported Classroom work type" in str(exc)
    else:
        raise AssertionError("a failed staged write must propagate its error")

    assert not (tmp_path / "corpus" / "courses" / "course-one").exists()
