# Task
Implement a configurable `--corpus-dir` command-line option with explicit folder existence validation guards to prevent accidental course overwrites.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Constraints

### 1. Argument Parser Updates
Modify the initialization blocks inside `build_parser()` to register the new optional parameter:
* **Flag:** `--corpus-dir`
* **Type:** `Path`
* **Default:** `None`
* **Help:** "Path to an external educational corpus root directory."

### 2. Output & Target Path Selection Logic
Update the engine inside `main()` and `MarkdownCorpusWriter` initialization to dynamically resolve the active target root:
* **Case A (No `--corpus-dir` provided):** 
  * Default to creating and targeting a `./corpus/` subdirectory relative to the current working directory (`Path.cwd() / "corpus"`).
  * If this default `./corpus/` folder does not exist at runtime, automatically create it using `mkdir(parents=True, exist_ok=True)`.
* **Case B (`--corpus-dir` is provided):**
  * Check if the provided directory exists on disk.
  * If the path **does not exist**, immediately halt execution and fail with a clear message: `"corpus directory does not exist"`.
  * Do not auto-generate missing directories if explicitly passed by the user.

### 3. Duplicate Overwrite Guard Invariant
Implement a strict check inside `archive_classroom()` before writing files:
* Locate the derived `course-slug` identifier folder target.
* If the specific target course directory (`{active_corpus_root}/courses/{course-slug}`) **already exists** on disk, do not overwrite or append duplicate data.
* Immediately stop execution and raise a `RuntimeError` that formats to: `"course directory already exists"`.

## Acceptance Criteria
* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --archive-classroom 19601548035-2018-g12-ict` automatically creates `./corpus/` in the working directory if missing and dumps data successfully.
* Running the command a second time against that same directory errors out cleanly with `"course directory already exists"`.
* Running the command with `--corpus-dir ~/non-existent-path/` terminates execution immediately with `"corpus directory does not exist"`.
* All existing functionality, tests, and metadata formatting blocks remain fully intact and operational (`python3 -m pytest` passes completely).

## Deliverables
1. Summary of argument expansion validations and directory existence protection logic.
2. Suggested git commit message in the format: `<agent>: <commit message>`

