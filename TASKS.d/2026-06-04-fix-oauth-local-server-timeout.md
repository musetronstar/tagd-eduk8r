# Task
Fix the local WSGI timeout and connection refusal error occurring during the OAuth browser redirect loop.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Context & Root Cause
The script currently crashes with a `WSGITimeoutError` because `flow.run_local_server(port=0)` assigns a random high port that is dropping connections or closing early on the redirect back from Google's servers.

## Constraints

### 1. Hardcode Localhost Bindings
Modify the `flow.run_local_server()` call inside `ClassroomScraper.authenticate()` to explicitly bind to a stable host and port rather than picking randomly:
```python
credentials = flow.run_local_server(
    host="localhost",
    port=8080,
    prompt="consent"
)

```

*Intent Comment Requirement:* Explicitly document *why* `host="localhost"` and a fixed port are used (to avoid dynamic high-port routing blockages and ensure local firewalls do not drop the incoming token landing redirect).

### 2. Verify Redirect URI Compatibility

Ensure that your Google Cloud Console credential allows local loopbacks on this explicit port (Google allows `http://localhost` automatically for Desktop client types, but fixing the port locally ensures exact structural matching).

## Acceptance Criteria

* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --list-classrooms` successfully catches the browser redirect callback on port `8080`.
* The server processes the authorization payload instantly without timing out, creates `.secrets/token.json`, and returns your course list data payload straight to the terminal shell.

## Deliverables

1. Summary of fixed loopback port and host parameter adjustments
2. Suggested git commit message in the format: `<agent>: <commit message>`

