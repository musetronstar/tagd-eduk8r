# Task: Make `--list-classrooms` Output Archive Tokens

## Objective

Modify `bin/classroom-archiver.py` so that:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --list-classrooms
```

prints one copy/paste-friendly archive token per classroom.

This prepares for a future `--archive-classroom` option.

---

## Current Behavior

`--list-classrooms` currently prints both the Classroom display name and slug.

Example:

```text
G8.2 Computer Science 2025-2026 g8-2-computer-science-2025-2026
```

This is not ideal for scripting because names may contain spaces, punctuation, or tabs.

---

## New Behavior

`--list-classrooms` shall print exactly one archive token per line.

Format:

```text
<classroom_id>-<slugified_classroom_name>
```

Example:

```text
1234567890-g8-2-computer-science-2025-2026
```

The Classroom ID is the authoritative identifier.

The slug suffix is included only for human readability.

---

## Requirements

1. Preserve the existing `--list-classrooms` option name.

2. Change its output to one token per line.

3. The token format shall be:

   ```text
   <course.id>-<course.slug>
   ```

4. Do not print headers.

5. Do not print display names.

6. Do not print extra whitespace.

7. Preserve `--teacher-email` filtering behavior.

8. Keep output suitable for shell scripting, for example:

   ```bash
   python3 bin/classroom-archiver.py \
     --creds .secrets/credentials.json \
     --list-classrooms \
     --teacher-email teacher@example.edu \
     | while read classroom; do
         echo "$classroom"
       done
   ```

---

## Example Output

```text
1234567890-robotics-asa-sem-2-2026
2345678901-apcsp-2025-2026
3456789012-g7-robotics-2025-2026
```

---

## Implementation Notes

The current `Course` dataclass already includes:

* `id`
* `name`
* `slug`

Use:

```python
print(f"{course.id}-{course.slug}")
```

instead of printing the display name.

No reverse lookup or de-slugification is required.

Future archive commands will parse the leading Classroom ID from this token.

---

## Non-goals

Do not implement:

* `--archive-classroom`
* corpus writing
* Google Drive downloads
* Markdown conversion
* TAGL generation
* metadata generation

This task only changes `--list-classrooms` output.

---

## Acceptance Criteria

Running:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --list-classrooms
```

prints one token per line in the form:

```text
<classroom_id>-<slugified_classroom_name>
```

The output contains no display-name column and no header.

Existing tests continue to pass:

```bash
python3 -m py_compile bin/classroom-archiver.py
python3 -m pytest tests/test_archiver_skeleton.py
```

