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
    assert "Full Stack Web Development" in output
    assert "full-stack-web-development" in output


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
        return FakeRequest(self.metadata_by_id[kwargs["fileId"]])


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
