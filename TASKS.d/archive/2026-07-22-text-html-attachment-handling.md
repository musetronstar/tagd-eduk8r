# Task
Support `text/html` Drive downloads and add fallback handling for unknown attachment MIME types in `bin/classroom-archiver.py`.

## Scope
* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. Direct Download for Standard Text & Web MIME Types
* Ensure `text/html`, `text/css`, `text/javascript`, `text/plain`, `application/json`, and binary files are downloaded directly using `files().get_media(fileId=...)`.

### 2. Workspace Export Mappings
* Maintain standard Google Workspace App export mappings:
  * `application/vnd.google-apps.document` -> `text/plain`
  * `application/vnd.google-apps.spreadsheet` -> `text/csv`
  * `application/vnd.google-apps.presentation` -> `application/pdf`

### 3. Non-Blocking Fallback for Unsupported Types
* If an attachment's MIME type cannot be exported or downloaded:
  * Print a warning to `stderr` / `stdout`:
    `Warning: Skipping unsupported Drive MIME type [{mime_type}] for attachment '{file_name}'.`
  * Append a notation in the assignment's markdown metadata:
    `- [Unsupported Attachment: {file_name} ({mime_type})]`
  * **Do not halt execution or raise SystemExit.**

## Acceptance Criteria
* `py bin/classroom-archiver.py` successfully downloads `text/html` attachments without crashing.
* Any unhandled MIME type logs a clear warning and allows the archiver to continue.
* `python3 -m pytest` passes completely.

