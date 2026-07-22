# Task
Prepend creation dates to assignment directory paths and append a clean, optional plain-text metadata section to the bottom of assignment index files.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Constraints

### 1. Update Data Models & Payload Mapping
* Expand the `Assignment` dataclass to capture:
  * `creation_time`: `str` (Default: `""`)
  * `max_points`: `Optional[float]` (Default: `None`)
  * `due_time`: `Optional[str]` (Default: `None`)
* Inside `GoogleClassroomScraper._map_course_work()`, extract:
  * `creationTime` $\rightarrow$ `creation_time`
  * `maxPoints` $\rightarrow$ `max_points`
  * Combine `dueDate` (year/month/day) and `dueTime` (hours/minutes) if present into a single human-readable `YYYY-MM-DD HH:MM` format assigned to `due_time`.

### 2. Chronological Assignment Folders
Modify `MarkdownCorpusWriter.write_assignment_structure()` to prefix directory names:
* Extract the first 10 characters (`YYYY-MM-DD`) from the assignment's `creation_time`.
* If a valid creation date exists, format the directory name exactly as: `{YYYY-MM-DD}-{assignment-slug}`
* Target Path pattern: `corpus/courses/{course-slug}/assignments/{YYYY-MM-DD}-{assignment-slug}/index.md`

### 3. Append Optional Plain-Text Metadata Section
When writing an assignment's `index.md`, append an optional section at the very end of the file following the body prose:

* Formatting Rules:*
* If a metadata field is missing or `None`, do not print its line.
* If there are no details available at all (all fields are missing or empty), omit the `## Assignment Details` header entirely.

Example block format (when all data is present):
```markdown

## Assignment Details
- Created: 2018-10-24
- Due: 2018-10-26 23:59
- Max Points: 100

```

## Acceptance Criteria

* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --archive-classroom 19601548035-2018-g12-ict` completes cleanly.
* Generated folders are prefixed chronologically (e.g., `2018-10-24-assignment-2-student-digital-portfolio`).
* The bottom of assignment `index.md` files contains a clean, plain-text key-value block with no markdown bolding on the keys, and contains zero lines representing missing/None data.

## Deliverables

1. Summary of updated markdown serialization constraints and folder paths
2. Suggested git commit message in the format: `<agent>: <commit message>`

