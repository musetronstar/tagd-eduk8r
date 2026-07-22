# Task
Fix the HttpError 403 permission crash when invoking courseWork().list by restoring the required coursework read-only scopes.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Context & Root Cause
When archiving a classroom, `scraper.fetch_assignments()` executes both `courseWork().list()` and `courseWorkMaterials().list()`. The script crashes with a 403 Forbidden error because `GOOGLE_API_SCOPES` contains `classroom.courseworkmaterials.readonly` but is missing the corresponding coursework permission scope required for the assignment list endpoint.

## Constraints

### 1. Update API Scopes
Expand the `GOOGLE_API_SCOPES` array at the top of `bin/classroom-archiver.py` to include the standard coursework read-only scope:
```python
GOOGLE_API_SCOPES = [
    "[https://www.googleapis.com/auth/classroom.courses.readonly](https://www.googleapis.com/auth/classroom.courses.readonly)",
    "[https://www.googleapis.com/auth/classroom.coursework.students.readonly](https://www.googleapis.com/auth/classroom.coursework.students.readonly)",
    "[https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly](https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly)",
    "[https://www.googleapis.com/auth/classroom.student-submissions.me.readonly](https://www.googleapis.com/auth/classroom.student-submissions.me.readonly)",
    "[https://www.googleapis.com/auth/drive.readonly](https://www.googleapis.com/auth/drive.readonly)",
]
```

### 2. Environment Resiliency Invariant

Ensure `os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"` remains fully active inside `authenticate()` right before the authorization flow runs. This safely prevents the local library from crashing if the Google OAuth backend performs any runtime scope reduction or re-ordering during testing.

## Acceptance Criteria

* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --archive-classroom <token>` after deleting any old `.secrets/token.json` successfully prompts for re-authorization in the browser.
* The browser consent screen explicitly requests permission to view coursework/assignments.
* The script successfully bypasses the 403 error and outputs the course layout and files into the `corpus/` directory structure cleanly.

## Deliverables

1. Summary of updated `GOOGLE_API_SCOPES` values
2. Suggested git commit message in the format: `<agent>: <commit message>`

