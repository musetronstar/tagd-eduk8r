# Task
Update `bin/classroom-archiver.py` to enforce strict fail-fast validation and error reporting across coursework processing, material mappings, Google Drive attachments, and Google Forms serialization.

## Scope
* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Constraints

### 1. Strict Fail-Fast Policy
If `classroom-archiver.py` encounters any unhandled or unknown asset during archive execution, it must immediately raise a `RuntimeError` and halt execution to prevent silent data loss or partial directory writes.

### 2. Required Fail-Fast Boundaries
The script must validate and trap errors at these specific points:

* **Work Type Trapping:** Any unrecognized Classroom `workType` outside of `ASSIGNMENT`, `QUIZ_ASSIGNMENT`, `QUESTION`, `SHORT_ANSWER_QUESTION`, `MULTIPLE_CHOICE_QUESTION`, or `MATERIAL` must raise:
  `RuntimeError: "Unsupported Classroom work type: [{work_type}] in assignment '{title}' ({id}). Halting execution."`
  * **Attachment Type Trapping:** Any unmapped Google Drive attachment type or unrecognized material dictionary payload outside of recognized files, links, YouTube videos, or Google Forms must raise:
    `RuntimeError: "Unsupported material attachment type: [{source_type}] in assignment '{title}'. Halting execution."`
    * For `driveFile` materials, validate the `mime_type` property obtained from `_fetch_drive_file_metadata()` against this exact allowlist:
      ```python
      SUPPORTED_MIME_TYPES = {
          "application/vnd.google-apps.document",
          "application/vnd.google-apps.spreadsheet",
          "application/vnd.google-apps.presentation",
          "application/pdf",
          "application/zip",
          "application/x-zip-compressed",
          "image/png",
          "image/jpeg",
          "image/gif",
          "image/svg+xml",
          "text/plain",
          "text/csv",
      }
      ```
    * A missing or unsupported Drive MIME type must raise:
      `RuntimeError: "Unsupported Drive file MIME type: [{mime_type}] for file '{title}' in assignment '{assignment_title}'. Halting execution."`
    * **Google Form Item Type Trapping:** During Google Form quiz serialization, any form question or item structure outside `MULTIPLE_CHOICE`, `PARAGRAPH`, `SHORT_ANSWER`, `CHECKBOXES`, `DROPDOWN`, or `MULTIPLE_CHOICE_GRID` must raise:
      `RuntimeError: "Unsupported Google Form question type: [{item_type}] in form '{form_id}'. Halting execution."`
      * Provide this boundary as a standalone, reusable validator for the future Google Forms serializer, such as `validate_form_item_type(item_type: str, form_id: str)`; implementing Forms serialization is outside this task.

### 3. Filename Sanitization Utility
Implement a helper `sanitize_filename(name: str) -> str` for attachment file paths:
* Replace path traversal and OS-unsafe characters (`/`, `\`, `:`, `?`, `*`, `<`, `>`, `|`, `"`) with hyphens (`-`).
* Strip leading and trailing whitespace.
* Strip leading hyphens (`-`) and spaces so filenames never start with unsafe flags/characters.
* Raise `RuntimeError` if sanitization results in an empty string.

## Acceptance Criteria
* `classroom-archiver.py` immediately exits with non-zero status and descriptive error message upon encountering unhandled coursework types, attachment types, or form question types.
* `sanitize_filename` cleans string inputs according to spec and prevents leading spaces/hyphens.
* All existing tests pass, and new unit tests verify error boundary trapping.
* `python3 -m pytest` passes completely.
