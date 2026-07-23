# Task
Handle missing or deleted Google Drive files/attachments gracefully in `bin/classroom-archiver.py` without halting execution.

## Context & Problem
During course archiving (`Archiving '123033699217-ict-grade-8'`), a Drive file or attachment ID (`1XubvUWhUAVve2Uq2WYtYbr7jXMssiChp`) inside 'Assignment 4 - Fun with Strings' could not be found (e.g., deleted from Drive, broken link, or insufficient permissions). Currently, the archiver raises an unhandled error and halts execution:


```

classroom-archiver.py: error: Drive file or attachment not found: [1XubvUWhUAVve2Uq2WYtYbr7jXMssiChp] in assignment 'Assignment 4 - Fun with Strings'. Halting execution.

```

Per the archive resilience guidelines, missing attachments should produce a non-blocking warning and record an offline stub in the assignment's `index.md`.

## Scope
* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. Graceful Download Exception Handling
* Catch missing file errors (HTTP 404 / Drive API file not found errors) during attachment downloads and Drive exports.
* Do **not** raise `SystemExit` or halt course archiving when a specific attachment payload fails to download or export.

### 2. Warning Output
* Print a clear warning message to `stderr` (or stdout status output) identifying the missing attachment and course context:
  ```text
  Warning: Attachment '[{file_id}]' ({filename}) not found or inaccessible in assignment '{assignment_title}'. Skipping attachment download.

```

### 3. Record Offline Stub in `index.md`

* In the assignment's `index.md` under `## Materials`, record a non-linked offline stub for the missing file:
```markdown
* [Attachment Missing: {filename} (File not found or inaccessible on Google Drive)]

```


* Do **not** generate broken local relative links to non-existent files inside `attachments/`.

### 4. Course Staging & Completion Integrity

* Ensure the rest of the assignment structure and any remaining valid materials continue to download cleanly.
* The overall course should report `, success` if all available resources process, or continue to report `, failed` only for fatal structural/course-level API errors.

## Acceptance Criteria

* Encountering a missing Drive file ID (HTTP 404) logs a warning and continues processing remaining materials.
* The assignment's `index.md` includes an `[Attachment Missing: ...]` entry for missing attachments.
* Running batch archiving against course `123033699217-ict-grade-8` completes successfully past 'Assignment 4 - Fun with Strings'.
* `python3 -m pytest` passes completely with regression unit tests simulating HTTP 404 / missing file downloads.

