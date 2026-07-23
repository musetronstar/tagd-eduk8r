# Task
Fetch Google Form data associated with Quiz Assignments, map core question types (including grids), extract correct answers, isolate image media assets, and serialize the content into explicit structured Markdown documents.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Constraints

### 1. File Provisioning & Placements
For any parsed `QUIZ_ASSIGNMENT`, retrieve the associated target form payload structure via the Forms API. Generate two distinct files positioned beside the assignment's `index.md`:
* `{form-title-slug}-questions.md`
* `{form-title-slug}-answers.md`

### 2. Heading Layout Structural Invariants
* **Questions File (`*-questions.md`):**
  * A single Level 1 heading `# {Form Title}` must be positioned at the top of the file.
  * Every question component must open with a Level 2 heading configured precisely as: `## {question_number}. {Question Type}` (e.g., `## 1. Multiple Choice`).
  * A required Level 3 heading `### Question` must immediately follow, housing the question's text body.
  * An optional Level 3 heading `### Choices` must follow only if options or grid matrices are present, utilizing the asterisk (`*`) marker syntax.
* **Answers File (`*-answers.md`):**
  * Must preserve identical 1:1 question numbering sequence matching the primary file using matching Level 2 headings: `## {question_number}. {Question Type}`.
  * Beneath the header, render the literal string text matching the designated correct answer option or key payload. If a question is subjective, open-ended, or lacks an absolute programmatic answer key, write the header but leave the spacing blank beneath it.

### 3. Supported System Type Mappings & Layout Rules
Translate incoming Google Form core element structural types into these exact human-readable header string designations:
* `MULTIPLE_CHOICE` → `Multiple Choice`
* `PARAGRAPH` → `Paragraph`
* `SHORT_ANSWER` → `Short Answer`
* `CHECKBOXES` → `Checkboxes`
* `DROPDOWN` → `Dropdown`
* `MULTIPLE_CHOICE_GRID` → `Multiple Choice Grid`

#### Grid Layout Formatting Variant
When processing a `MULTIPLE_CHOICE_GRID`:
* In `*-questions.md`, render two explicit Level 4 headings under `### Choices` containing standard asterisk bullet lists for the dimensions:
```markdown
  ### Choices

  #### Columns
  * Column Option A
  * Column Option B

  #### Rows
  * Row Prompt 1
  * Row Prompt 2

```

* In `*-answers.md`, serialize the answer keys using an asterisk list pairing rows to columns via a strict, space-padded colon separator (`:`) to ensure inline question characters remain intact:
```markdown
## 3. Multiple Choice Grid
* Row Prompt 1 : Column Option A
* Row Prompt 2 : Column Option B

```

### 4. Binary Media Asset Extraction

If a question contains a nested media or image element structure:

* Provision a localized directory named `form-files/` inside the current active coursework destination directory.
* Stream the raw file payload binary down, saving it as `form-files/{question-number}.{extension}` where the extension matches the true content layout type (e.g., `.png`, `.jpg`).
* Append a relative markdown image pointer declaration inline at the bottom of the `### Question` section formatted as: `![{question-number}](form-files/{question-number}.{extension})`.

### 5. Error Boundaries and Strict Validation

* **Unsupported Type Trapping:** During the processing loop of any Google Form component, evaluate the type identifier before executing serialization mapping.
* **Execution Halting:** If an unmapped or unhandled element type is encountered (e.g., `SCALE`, `GRID`, `FILE_UPLOAD`, `RATING`), the script must immediately raise a descriptive `RuntimeError` and terminate execution.
* **Error Message Contract:** The error message must clearly state the exact unhandled form item type discovered in the payload to allow immediate categorization and subsequent implementation triage. Example format:
`"Unsupported Google Form question type: [SCALE] found in form [form_id]. Archive execution halted to prevent structural data loss."`

## Acceptance Criteria

* Form data files generate predictably alongside `index.md` inside `assessments/` folders.
* Headers adhere strictly to standard casing formatting controls without breaking Markdown structures.
* Grid dimensions divide into clear sub-lists, and grid answers map cleanly with `:` text delimiters.
* `python3 -m pytest` passes completely.

