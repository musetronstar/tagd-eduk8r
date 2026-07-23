# Task: Handle `exportSizeLimitExceeded` Gracefully for Large Google Docs

## Scope

* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. Catch `exportSizeLimitExceeded` (403 Export Size Limit)

* In Google Doc export calls (`_export_google_doc_markdown` / `_stream_drive_request`), catch `googleapiclient.errors.HttpError`.
* If the error status is `403` and the reason/message contains `exportSizeLimitExceeded` or `"This file is too large to be exported."`:
* Treat the file as an un-exportable attachment.
* Print a clean warning matching our existing warning format:
```text
Warning: Attachment '{title}' (ID: '{file_id}') exceeds Google Drive API export size limits. Skipping attachment download.

```


* Write an offline stub link in the markdown output indicating the document exceeded Google's export limits.
* **Do not halt execution.** Continue archiving the rest of the assignment.



### 2. Unit Test Coverage

* Add a unit test simulating a `403 HttpError` with `exportSizeLimitExceeded` during Google Doc export.
* Verify that a warning is logged, an offline stub is written, and no unhandled exception is raised.

## Acceptance Criteria

* Encountering `exportSizeLimitExceeded` logs a `Warning:` and continues processing without crashing.
* `python3 -m pytest` passes completely.

## Deliverables

1. Concise summary of changes.
2. Test execution results (`pytest`).
3. Suggested commit message (`codex: ...`).

