# Task
Implement Google Workspace document exports, sidecar image extraction, and local offline attachment linking in `bin/classroom-archiver.py`.

## Scope
* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. Google Workspace Export Mappings
When encountering Google Workspace Drive attachments (`application/vnd.google-apps.*`), export and save them to the assignment's `attachments/` folder according to the following mapping:

* **Google Docs** (`application/vnd.google-apps.document`):
  * Export as **`.md`** (Markdown) AND **`.docx`** (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`).
* **Google Sheets** (`application/vnd.google-apps.spreadsheet`):
  * Export as **`.csv`** (`text/csv`).
* **Google Slides** (`application/vnd.google-apps.presentation`):
  * Export as **`.pptx`** (`application/vnd.openxmlformats-officedocument.presentationml.presentation`) AND **`.pdf`** (`application/pdf`).

### 2. Embedded Media Extraction & Sidecar Folder for Google Docs
* When exporting a Google Doc to Markdown (`.md`), extract all embedded images and media objects.
* Save extracted assets into a dedicated sidecar folder inside `attachments/` named `<Doc Title>.md-files/`.
* Update image links within `<Doc Title>.md` to point relatively to these local sidecar files (e.g., `![Diagram](<Doc Title>.md-files/image1.png)`).

### 3. Binary & Standard Downloads
* For non-Workspace files (`.pdf`, `.png`, `.zip`, `text/html`, `text/css`, `text/plain`, etc.), download the original file directly via Drive API `files().get_media(fileId=...)` into `attachments/`.

### 4. Offline-Only Relative Links in `index.md`
* In the assignment's `index.md` under `## Materials` / `## Attachments`, **do not include any live Google URLs**.
* Point strictly to local relative paths inside `attachments/`:
  ```markdown
  ## Materials
  * [Syllabus](attachments/Syllabus.md) ([DOCX](attachments/Syllabus.docx))
  * [Grade Sheet](attachments/Grades.csv)
  * [Lecture Presentation](attachments/Lecture.pptx) ([PDF](attachments/Lecture.pdf))
  * [Starter Code](attachments/index.html)

