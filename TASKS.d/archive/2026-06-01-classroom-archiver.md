# Task
Implement the initial structural skeleton, explicit command-line argument parsing, and core abstractions for the Google Classroom archiving script.

## Scope
* New files: `bin/classroom-archiver.py`
* New configuration/test mock files: `tests/test_archiver_skeleton.py`

## Constraints
* **Location:** The script must reside in `bin/classroom-archiver.py`.
* **CLI Architecture:** Use the standard library `argparse` module. Only use explicit long-form options (`--creds`, `--output`, `--course`, `--list-classrooms`).
* **Explicit Inputs:** The `--creds` option must be explicitly marked as required. No environmental variables or implicit fallbacks are allowed.
* **Architecture:** Separate data extraction from file writing. Implement a pluggable abstract interface (`ContentConverter`) for converting Classroom data into Markdown.
* **Discovery Flag:** Implement the boolean flag `--list-classrooms`. When passed, the script must authenticate, print the human-readable classroom names alongside their clean slugified tokens, and short-circuit execution cleanly without writing files.

## Acceptance Criteria
* Running `python3 bin/classroom-archiver.py --help` shows only long-form options (`--creds`, `--output`, `--course`, `--list-classrooms`).
* Omitting `--creds` results in a clear argument validation error from `argparse`.
* The script contains explicit abstract classes/interfaces for the pipeline (`ClassroomScraper`, `ContentConverter`, `CorpusWriter`).
* Dataclasses are defined to handle data shapes for courses, assignments, and resources safely.

## Deliverables
1. Concise summary of flag behavior and routing checks
2. Verification that the file is syntactically sound
3. Suggested git commit message in the format: `<agent>: <commit message>`