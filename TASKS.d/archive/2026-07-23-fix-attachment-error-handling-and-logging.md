# Task: Implement Assignment Progress Headings, Simplify Course Status, and Fast-Fail Unsupported MIME Types

## Scope

* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. Classroom Output Formatting

* Change course progress output to a simple un-flushed heading with an ellipsis and symmetrical single quotes around the course token:
```text
Archiving '123033699217-ict-grade-8' ...

```


* Remove trailing status completion text (` success` / `, failed`) on the classroom line. Success is indicated by the absence of fatal errors.

### 2. Hierarchical Assignment Progress Output & Quoting Consistency

* Before processing each assignment (fetching metadata, downloading attachments, or writing structure), print an explicit progress marker for that assignment using symmetrical single quotes (`'...'`):
```text
* Assignment: 'Assignment 4 - Fun with Strings'

```


* Use the asterisk bullet (`*`) prefix so log outputs are easily scannable and grepable (e.g., `grep "^\* Assignment:"`).
* Because the assignment context is now established by this heading immediately preceding any actions, warning/error messages do **not** need to redundantly repeat the assignment name.

### 3. Fast-Fail Unsupported Drive MIME Types

* Replace non-fatal warning skips for unsupported/unhandled Drive MIME types (`text/x-python`, `video/mp4`, `application/x-subrip`, etc.) with a fatal exception.
* When an unsupported MIME type is encountered:
* Print an `Error:` message to `stderr`/`stdout` using consistent single quoting for dynamic parameters.
* Raise a fatal exception (or exit) immediately, halting the script.


* **Missing Attachments (404s):** Remain non-fatal. Log a `Warning:` message, write the offline stub into `index.md`, and proceed with the assignment.

### 4. Example Output Flow (Quoting & Layout Standard)

#### Success / Non-Fatal Warning Path:

```text
Archiving '123033699217-ict-grade-8' ...
* Assignment: 'Assignment 4 - Fun with Strings'
Warning: Attachment '1XubvUWhUAVve2Uq2WYtYbr7jXMssiChp' ('1XubvUWhUAVve2Uq2WYtYbr7jXMssiChp') not found or inaccessible. Skipping attachment download.
* Assignment: 'REPL Command Line (Checkpoint)'

```

#### Fast-Fail Path:

```text
Archiving '123033699217-ict-grade-8' ...
* Assignment: 'Assignment 4 - Fun with Strings'
* Assignment: 'REPL Command Line (Checkpoint)'
Error: Unsupported Drive MIME type 'text/x-python' for attachment 'repl.py'.

```

*(Script exits immediately following the `Error:` line)*

## Acceptance Criteria

* Course start output matches `Archiving '<token>' ...` on its own line.
* Each assignment logs `* Assignment: '<Title>'` before downloading/processing its resources.
* All dynamic log tokens use symmetrical single quotes (`'...'`).
* Unsupported MIME types log an `Error:` and raise a fatal exception immediately.
* Missing attachments log a `Warning:` and continue execution.
* `python3 -m pytest` passes completely with updated tests covering output formatting, quoting standards, and fast-fail behavior.

## Deliverables

1. Concise summary of changes.
2. Test execution results (`pytest`).
3. Suggested commit message (`codex: ...`).

