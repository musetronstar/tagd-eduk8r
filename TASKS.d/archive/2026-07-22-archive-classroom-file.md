# Task
Add `--archive-classroom-file` CLI flag to batch archive classrooms from a line-separated token list file, skipping already-archived course directories.

## Scope
* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. New CLI Option `--archive-classroom-file <path>`
* Add a command-line argument `--archive-classroom-file` (or `--course-file` alias if appropriate) taking a path to a plain text file containing one course token (e.g., `19601548035-2018-g12-ict`) per line.
* The parser should strip leading/trailing whitespace from each line and ignore blank lines or lines starting with `#` (comments).

### 2. Idempotent Batch Behavior (Skip Existing Courses)
* When processing courses in batch mode via `--archive-classroom-file`:
  * Check whether the target course directory `corpus/courses/{course-slug}` already exists.
  * If it **exists**, do NOT raise a `RuntimeError`. Instead, print an informational status message to `stdout` (e.g., `Skipping course '{slug}' (directory already exists).`) and continue to the next course in the list.
  * If it **does not exist**, proceed with fetching and writing the course archive using the staged writer.
* Note: Single-course mode via `--archive-classroom <TOKEN>` or `--course <slug>` should retain its strict explicit check if desired, or align with skipping if specified.

### 3. Exit Status & Error Handling
* In batch mode (`--archive-classroom-file`), if a course fails mid-archive due to a validation error (e.g., unsupported MIME type or work type), it should halt execution immediately so the user can inspect the error and fix it before resuming.
* The script exits cleanly with status code `0` when all entries in the file have been processed or skipped.

## Acceptance Criteria
* `py bin/classroom-archiver.py --archive-classroom-file classrooms-list.txt` processes tokens sequentially.
* Already-archived courses are reported as skipped and do not cause execution failure.
* Unit tests verify line parsing, comment/empty line handling, and skipping behavior when directories exist.
* `python3 -m pytest` passes completely.

