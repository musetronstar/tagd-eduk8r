# Task
Fix the crash in the authentication loop caused by the Google OAuth backend changing requested scopes on response.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Context & Root Cause
The script currently crashes inside `flow.run_local_server()` with an `oauthlib` Warning raised as an exception because the scopes returned by Google do not perfectly match the order or exact strings requested. Google stripped `classroom.coursework.me.readonly` and appended `classroom.student-submissions.me.readonly`.

## Constraints

### 1. Re-align Scopes
Update the hardcoded scopes array inside the `ClassroomScraper` concrete class authentication logic to request the exact list returned by the server:
* `https://www.googleapis.com/auth/classroom.courses.readonly`
* `https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly`
* `https://www.googleapis.com/auth/classroom.student-submissions.me.readonly`
* `https://www.googleapis.com/auth/drive.readonly`

### 2. Permit Scope Overrides
To make the authentication pipeline resilient against upstream ordering or minor payload drift, inject the `OAUTHLIB_RELAX_TOKEN_SCOPE` variable into the runtime environment directly before initializing the flow:
```python
import os
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

```

*Intent Comment Requirement:* Include a highly concise comment above this line stating that this environment key prevents `oauthlib` from raising a strict parameter mismatch exception if Google modifies the token scopes payload dynamically on response.

## Acceptance Criteria

* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --list-classrooms` completes the browser flow successfully without raising an `oauthlib` parameter exception.
* The script successfully saves a valid `.secrets/token.json` file.
* Subsequent runs load `.secrets/token.json` automatically and list rooms without triggering the browser popup again.

## Deliverables

1. Summary of updated scope list configurations
2. Suggested git commit message in the format: `<agent>: <commit message>`

