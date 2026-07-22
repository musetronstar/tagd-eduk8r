# Task
Implement the live Google API client authentication flow, credential management, and active HTTPS metadata scraping routines for the archiving pipeline.

## Scope
* Modified files: `bin/classroom-archiver.py`
* New project dependencies: `google-auth-oauthlib`, `google-api-python-client`

## Constraints

### 1. Authentication Invariants
* Use the OAuth 2.0 Desktop Application flow.
* Read client configuration from `.secrets/credentials.json`.
* Save and cache the generated user token locally at `.secrets/token.json` to allow headless subsequent runs.
* Restrict OAuth scopes to the minimum required read-only permissions:
  * `classroom.courses.readonly`
  * `classroom.coursework.me.readonly`
  * `classroom.courseworkmaterials.readonly`
  * `drive.readonly`

### 2. Scraping and Mapping Mechanics
* Implement the concrete `ClassroomScraper` using Google's API discovery client (`build('classroom', 'v1', ...)` and `build('drive', 'v3', ...)`).
* `fetch_courses()` must pull both `ACTIVE` and `ARCHIVED` states.
* Map incoming Google Classroom API payloads cleanly into the existing `Course`, `Assignment`, and `Resource` dataclasses.
* Collect the `materials` arrays from both `courseWork` (assignments) and `courseWorkMaterials` (resources) endpoints.

### 3. Pipeline Isolation
* Do not implement the file-writing logic inside `CorpusWriter` or file conversion mechanics inside `ContentConverter` yet. Keep this slice focused entirely on successful authentication, live API pagination, filtering, and data model mapping.

## Acceptance Criteria
* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --list-classrooms` successfully prompts OAuth authorization on the first run, creates `.secrets/token.json`, fetches live classrooms from the HTTPS API, and prints their real names and slugs to the terminal.
* Running with the `--course {slug}` filter accurately restricts metadata collection to that single matching target.

## Deliverables
1. Concise summary of Google API client integration and token storage verification
2. Suggested git commit message in the format: `<agent>: <commit message>`