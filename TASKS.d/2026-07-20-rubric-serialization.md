# Task
Serialize Google Classroom rubric data as CSV beside its owning coursework entry.

## Scope
* Modified files: `bin/classroom-archiver.py`
* Test files may be modified only to add isolated rubric fixtures and assertions.

## Constraints

### 1. Rubric Retrieval
* Retrieve rubrics through the authenticated Google Classroom coursework rubric endpoint.
* Keep rubric lookup failures isolated so coursework without accessible rubric data remains archivable.
* Do not write test fixtures or generated files into the production `corpus/` directory.

### 2. CSV Output Location
* Write rubric data to `rubric.csv` inside the owning coursework entry directory:

```text
corpus/courses/{course-slug}/{type-subdirectory}/{YYYY-MM-DD}-{assignment-slug}/rubric.csv
```

* Emit `* Rubric: ./rubric.csv` in `index.md` only when that CSV file is written successfully.

### 3. Serialization Contract
* Write this exact header row in the specified order:

```csv
criterion_id,criterion_title,criterion_desc,level_id,level_title,level_desc,level_points
```

* Serialize source fields using this mapping:

| Column | Source field | Value contract |
| --- | --- | --- |
| `criterion_id` | criterion `id` | String identifier. |
| `criterion_title` | criterion `title` | Human-readable criterion title. |
| `criterion_desc` | criterion `description` | Criterion description. |
| `level_id` | level `id` | String identifier. |
| `level_title` | level `title` | Human-readable level title. |
| `level_desc` | level `description` | Level description. |
| `level_points` | level `points` | Numeric point value when present. |

* Emit one row for every level belonging to a criterion. Repeat the `criterion_*` values across those rows and vary the `level_*` values for each level.
* Emit one row for a criterion with no levels. Populate its `criterion_*` fields and leave every `level_*` field empty.
* Use Python's structured CSV APIs so commas, quotes, and newlines in rubric text are escaped correctly.
* Preserve source ordering for criteria and their levels.
* Do not invent values for absent optional rubric fields.

## Acceptance Criteria
* Coursework with an accessible rubric writes a valid `rubric.csv` beside its `index.md`.
* The metadata pointer is omitted when no rubric is available or serialization fails.
* CSV content uses the exact approved header and preserves criterion and level ordering.
* Criteria without levels remain present as rows with empty level fields.
* Rubric and non-rubric fixtures remain isolated under pytest temporary directories.
* `python3 -m pytest` passes completely.

## Deliverables
1. Summary of rubric retrieval, CSV schema, and failure-isolation behavior.
2. Suggested git commit message in the format: `<agent>: <commit message>`
