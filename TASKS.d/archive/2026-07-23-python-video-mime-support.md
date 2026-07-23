# Task: Add Download Support for Standard Drive Binary/Text Files (`text/x-python`, `video/mp4`, etc.)

## Scope

* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. Direct Download Handler for Non-Workspace Drive Files

* Expand attachment handling so standard non-Google Workspace files (e.g., source code like `text/x-python`, media like `video/mp4`, subtitles `application/x-subrip`, PDFs, images, etc.) are downloaded directly using Drive API's `get_media` / `alt=media` stream instead of attempting a Workspace `export`.
* Differentiate between:
* **Google Workspace Documents** (e.g., `application/vnd.google-apps.document`, `.spreadsheet`, `.presentation`) -> Exported via export MIME mappings.
* **Standard Drive Files / Blobs** (e.g., `text/x-python`, `video/mp4`, `application/pdf`, etc.) -> Downloaded directly as media files.
* **Google Workspace Shortcuts / Unsupported Apps** (e.g., `application/vnd.google-apps.form`, `application/vnd.google-apps.site`) -> Fast-fail with `UnsupportedMimeTypeError` if unexportable/unsupported.



### 2. Output & Error Formatting Consistency

* When downloading standard binary/text files, use the existing attachment download pipeline and file naming.
* Retain fast-fail behavior for truly unhandled/unsupported MIME types (e.g. Google Forms or non-downloadable Google Workspace app types).

## Acceptance Criteria

* `repl.py` (`text/x-python`) and other standard uploaded binary/text attachments download successfully without triggering `UnsupportedMimeTypeError`.
* Unhandled Google Workspace app MIME types (e.g. Google Forms) continue to fast-fail with an `Error:` message and immediate exit.
* `python3 -m pytest` passes completely with updated unit and integration tests.

## Deliverables

1. Concise summary of changes.
2. Test execution results (`pytest`).
3. Suggested commit message (`codex: ...`).

