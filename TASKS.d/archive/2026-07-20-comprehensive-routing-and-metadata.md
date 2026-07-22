Codex is **technically correct** about the underlying API limitation, but there is a straightforward, elegant structural trick to resolve this.

In the Google Classroom API, a "Quiz Assignment" is not a distinct first-class `workType` enum value; the API treats it as a standard `ASSIGNMENT`. The only difference is that when a user clicks "Quiz assignment" in the UI, Google Classroom automatically provisions a blank **Google Form** and attaches it to the item's `materials` collection.

---

## The Solution

To separate standard assignments from assessments, your script can inspect the `materials` array attached to the `CourseWork` object payload. If the `workType` is `ASSIGNMENT` and one of its materials is a Google Form link, you can classify it as a **Quiz Assignment** and route it directly to the `assessments` folder directory.

### 1. Resolving Topics and Rubrics

Codex also pointed out a data synchronization gap. In the live API layout:

* `topicId` must be mapped to a human-readable topic name using a separate `courses.topics` lookup dictionary.
* `rubric` data requires fetching from the active coursework preview version or localized extensions depending on your setup.

To give Codex a bulletproof implementation blueprint that works seamlessly with the actual Google Classroom API structure, drop this refined task configuration block into your system workspace.

---

### Deliverable: `2026-06-29-comprehensive-routing-and-metadata.md`

```markdown
# Task
Implement dynamic coursework type routing subdirectories handling implicit quiz assignments, resolve human-readable topic metadata names, and export clean metadata blocks.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Constraints

### 1. Implicit Quiz Assignment Identification & Folder Taxonomy
Since the Google Classroom API represents Quiz Assignments as standard `ASSIGNMENT` items with attached forms, implement a detection rule inside `GoogleClassroomScraper._map_course_work()`:
* Inspect the item's `materials` array elements.
* If `workType == "ASSIGNMENT"` **AND** at least one material item contains a `link` object targeting a Google Forms URL (`forms.google.com` or matching a `form` payload object container), classify the target internal metadata model property `work_type` as exactly `"QUIZ_ASSIGNMENT"`.
* Map `work_type` values to these specific pluralized disk collection directories:
  * `"ASSIGNMENT"` $\rightarrow$ `assignments`
  * `"QUIZ_ASSIGNMENT"` $\rightarrow$ `assessments`
  * `"QUESTION"`, `"SHORT_ANSWER_QUESTION"`, `"MULTIPLE_CHOICE_QUESTION"` $\rightarrow$ `questions`
  * `"MATERIAL"` $\rightarrow$ `resources`

### 2. Path Generation Alignment
Construct your absolute target file output paths matching this exact configuration layout convention:
```text
corpus/courses/{course-slug}/{type-subdirectory}/{YYYY-MM-DD}-{assignment-slug}/index.md

```

*(Note: As per previous criteria, Topics are horizontal text metadata descriptors inside the index file—they are NOT path steps).*

### 3. Resolve Topics & Rubrics Gracefully

* **Topics:** Extract the `topicId` string attribute from the payload item. If a global look-up cache dictionary map is available linking `topicId` to raw text string topic names, use that value for the file block line. Otherwise, fall back gracefully to the raw `topicId` string instead of failing execution.
* **Rubrics:** If an explicit rubric field or attachment payload parameter is present, evaluate its structural status. If true, map out the relative grading file line pointer.

### 4. Unbolded Plain-Text Markdown Appendix

At the very end of your generated asset file prose content, append the metadata attributes block utilizing clean unbolded markers:

* Output labels must match: `Created:`, `Due:`, `Points:`, `Topic:`, and `Rubric:`.
* If a data parameter value evaluates to `None` or an empty string, completely omit that single line from compilation.
* If all lines evaluate to empty, strip the `## Assignment Details` parent block entirely.

```markdown
## Assignment Details
* Created: 2018-10-24
* Due: 2018-10-26 23:59
* Points: 100
* Topic: Classwork
* Rubric: ./rubric.csv

```

## Acceptance Criteria

* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --archive-classroom 19601548035-2018-g12-ict` executes cleanly.
* Items with attached forms correctly route directly into the `assessments/` directory tier on disk.
* Metadata keys append exactly without markdown bold wrappers (`**`).
* `python3 -m pytest` passes completely with all 20 tests green.

## Deliverables

1. Summary of form attachment verification mapping logic additions.
2. Suggested git commit message in the format: `<agent>: <commit message>`

```

---

For a quick structural look at how different components like assignments, questions, and material payloads behave inside the system hierarchy, you can review this [Google Classroom: Types of Assignments guide](https://www.youtube.com/watch?v=j_dNdjIDXxI). This breakdown highlights the core operational distinctions between actionable student submissions and flat, standalone reference items in the course stream.

```
