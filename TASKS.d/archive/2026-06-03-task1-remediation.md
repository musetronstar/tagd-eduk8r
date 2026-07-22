# Task
Re-align `bin/classroom-archiver.py` with established repository documentation constraints, comments policies, and semantic data models.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Constraints

### 1. Invariant Documentation Preservation
Restore the original detailed multi-line module docstring exactly as specified in the original skeleton. It must include the explicit script title, descriptive overview sentence, and the multi-line terminal configuration `Usage:` examples block. Do not truncate or remove architectural headers.

### 2. Interface Contract Restorations
Restore the `sheet_to_csv(self, raw_content: Any) -> str:` abstract method on the `ContentConverter` abstract base class. This method is an explicit prerequisite for handling Google Sheets data processing and cannot be omitted.

### 3. Comment Policy Compliance
Review all new concrete skeleton classes (`SkeletonClassroomScraper`, `SkeletonCorpusWriter`) and argument parsers. Ensure they comply with the new `AGENTS.md` comment policy:
* Ensure code logic remains self-documenting where possible.
* Append highly concise **intent comments** explicitly stating *why* an invariant or specific structure exists (e.g., explaining why dependency injection is enabled inside `main()`, or why the mock classes return stable empty types during initial orchestration passes).

### 4. Preservation of Valid Structure
Preserve the testable execution framework introduced in the last pass (`main` argument plumbing, `build_parser`, dependency injection arguments, and functional step extractions like `archive_courses`).

## Acceptance Criteria
* Running `python3 bin/classroom-archiver.py --help` shows the restored, robust usage documentation.
* The `ContentConverter` class explicitly declares its dual processing properties (`document_to_markdown` and `sheet_to_csv`).
* No structural code logic or testing capability is regressed.

## Deliverables
1. Concise summary of restored definitions and added intent comments
2. Suggested git commit message in the format: `<agent>: <commit message>`
