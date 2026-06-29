# Task: Implement `--archive-classroom`

## Objective

Implement a command-line option that archives one Google Classroom course into the eduk8r corpus.

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --archive-classroom <archive-token>
```

The archive must produce clean corpus content following `docs/corpus-design.md`.

This is a preservation task. Do not generate Google Classroom provenance artifacts in the human-facing Markdown unless needed to preserve user-authored content.

---

## Archive Token

`--archive-classroom` accepts the archive token printed by `--list-classrooms`.

Token format:

```text
<classroom_id>-<slugified_classroom_name>
```

Example:

```text
1234567890-g8-2-computer-science-2025-2026
```

But can also accept just the `<classroom_id>`:

```text
1234567890
```

The leading Classroom ID is authoritative.

The slug suffix is for human readability only.

Implementation shall identify the classroom by parsing the leading ID:

```python
classroom_id = archive_token.split("-", 1)[0]
```

No de-slugification or name matching is required.

---

## Current Status

The script already supports:

* OAuth authentication
* `--list-classrooms`
* teacher email filtering
* course discovery
* assignment discovery
* classroom material discovery
* Drive/link/YouTube/form material mapping into dataclasses

The missing functionality is corpus writing.

---

## CLI Requirements

Add:

```text
--archive-classroom <archive-token>
```

Behavior:

1. Authenticate with Google.
2. Fetch available classrooms.
3. Locate the classroom whose `course.id` matches the leading ID in `<archive-token>`.
4. Fetch that classroom's assignments and course materials.
5. Write the classroom into the corpus.
6. Exit non-zero with a clear error if the ID is not found.

Preserve existing options:

* `--creds`
* `--output`
* `--teacher-email`
* `--list-classrooms`
* `--help`

`--teacher-email` should continue to filter available courses before archive-token lookup.

---

## Corpus Layout

Write archived classroom content under:

```text
corpus/
└── courses/
    └── <course-slug>/
        ├── index.md
        └── assignments/
            └── <assignment-slug>/
                └── index.md
```

Where:

* `<course-slug>` comes from the Classroom course name.
* `<assignment-slug>` comes from the Classroom assignment or material title.
* Each directory containing `index.md` is a corpus asset.
* `index.md` shall begin with the clean human-facing title.

Example:

```text
corpus/
└── courses/
    └── apcsa-2025-2026/
        ├── index.md
        └── assignments/
            └── unit-1-primitive-types/
                └── index.md
```

---

## Markdown Requirements

Generated Markdown should be clean and useful after the Google account is gone.

Do not include boilerplate such as:

```text
Imported from Google Classroom.
Original Classroom ID: ...
```

Do not expose Google Classroom IDs in normal Markdown content.

Use simple Markdown.

Course `index.md`:

```markdown
# APCSA 2025-2026

Course description if available.
```

Assignment `index.md`:

```markdown
# Unit 1 Primitive Types

Assignment description if available.
```

If the source has no description, the file may contain only the H1 title.

---

## Materials and Attachments

For the initial implementation, preserve attachment references in Markdown.

For each material attached to an assignment or course material, include a section such as:

```markdown
## Materials

- [Resource Title](https://example.com)
```

Do not attempt full Drive export/download in this task unless it is already straightforward from existing code.

Preserving links is sufficient for this task.

Future tasks may implement:

* Google Docs export to Markdown
* Google Sheets export to CSV
* Drive file download
* local attachment mirroring

---

## Course Materials

Google Classroom `courseWorkMaterials` may be archived under the same `assignments/` directory for now, unless the existing datamodel clearly distinguishes them.

Do not introduce a separate corpus taxonomy unless necessary.

The priority is preserving all classroom content in a readable corpus format.

---

## Writer Implementation

Replace or extend the current skeleton writer with a real corpus writer.

Suggested class:

```python
class MarkdownCorpusWriter(CorpusWriter):
    ...
```

It should implement:

* `write_course_structure(course)`
* `write_assignment_structure(course, assignment)`

The implementation should be deterministic and safe to rerun.

Use `mkdir(parents=True, exist_ok=True)`.

When rewriting existing generated `index.md` files, prefer overwriting with the current API content for now.

---

## Non-goals

Do not implement:

* TAGL generation
* `meta.tagl` generation
* full Google Drive export
* Google Docs to Markdown conversion
* Google Sheets to CSV conversion
* HTML generation
* search
* web UI
* semantic relationship inference

This task is only for preserving classroom content into the corpus.

---

## Tests

Update or add tests for:

1. parsing the archive token into a Classroom ID
  + parsing `1234567890` returns `1234567890`
  + parsing `1234567890-g8-2-computer-science-2025-2026` returns `1234567890`
2. CLI parser accepting `--archive-classroom`
3. writer creating course `index.md`
4. writer creating assignment `index.md`
5. writer preserving material links in Markdown
6. archive command selecting the matching course by ID

Existing tests must continue to pass.

---

## Verification

Run:

```bash
python3 -m py_compile bin/classroom-archiver.py
python3 -m pytest tests/test_archiver_skeleton.py
```

If new tests are added, run the full test suite:

```bash
python3 -m pytest
```

Manual live check:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --list-classrooms
```

Then archive one classroom:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --archive-classroom <archive-token>
```

Confirm that readable Markdown appears under:

```text
corpus/courses/
```

---

## Acceptance Criteria

A command of the form:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --archive-classroom 1234567890-apcsa-2025-2026
```

creates a clean eduk8r corpus subtree for that classroom.

The generated Markdown must be readable without Google Classroom access.

The archive must not include Google Classroom provenance boilerplate in human-facing content.

The implementation must conform to `docs/corpus-design.md`.

