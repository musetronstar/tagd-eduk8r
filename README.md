# tagd-eduk8r

`tagd-eduk8r` turns teacher-visible Google Classroom content into a local,
filesystem-based educational corpus. The corpus remains useful as ordinary
Markdown and files, while also serving as the authoritative source for future
[TAGL](https://github.com/musetronstar/tagd) generation and semantic tooling.

The repository keeps application behavior and educational material separate:

```text
app/       Web application code
corpus/    Educational corpus content
bin/       Import and maintenance utilities
docs/      Design and status documentation
tagl/      TAGL bootstrap definitions
tests/     Automated tests
```

The current working utility is
[`bin/classroom-archiver.py`](bin/classroom-archiver.py), a read-only Google
Classroom and Drive archiver.

## What the Classroom archiver does

The archiver:

- discovers active and archived courses visible to a teacher;
- imports assignments, questions, materials, and quiz-assignment references;
- resolves Classroom topic IDs to topic titles;
- writes course and coursework metadata as Markdown;
- downloads ordinary Drive files directly, including source code, documents,
  archives, images, and video;
- exports Google Docs as Markdown and DOCX;
- exports Google Sheets as CSV;
- exports Google Slides as PPTX and PDF;
- extracts embedded Google Doc images and rewrites their Markdown paths;
- keeps external links and YouTube resources in a dedicated `## Links` section;
- stages each course in a temporary directory before publishing it to the
  corpus; and
- fails quickly on unsupported Classroom entities or Google Workspace file
  types instead of silently producing an incomplete representation.

Student submissions, grades, and student personally identifiable information
are not archived.

## Requirements

- Python 3.10 or newer
- a Google Cloud OAuth 2.0 Desktop client credentials file
- access to the Google Classroom and Drive APIs

Install the runtime and test dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install \
  google-auth-oauthlib \
  google-api-python-client \
  markdownify \
  pytest
```

The repository does not currently provide a packaged dependency manifest, so
the dependencies are installed directly.

## Google OAuth setup

Create a Desktop application OAuth client in Google Cloud and download its
client-secrets JSON file. Store it outside version control, for example:

```text
.secrets/credentials.json
```

On the first run, the archiver opens the browser-based consent flow and listens
for the callback on `localhost:8080`. It writes the resulting cached credentials
to `token.json` beside the client-secrets file. Later runs reuse or refresh that
token.

The archiver requests read-only Classroom and Drive access. The authenticated
account must be able to view the courses and coursework being archived.

## Usage

Display all options:

```bash
python3 bin/classroom-archiver.py --help
```

### List available classrooms

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --list-classrooms
```

Each line is a canonical archive token containing the Classroom ID and a
human-readable slug:

```text
19601548035-2018-g12-ict
41161136862-2019-2020-g12-ict
```

Optionally restrict discovery to one teacher:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --teacher-email teacher@example.edu \
  --list-classrooms
```

### Archive one classroom

Archive one listed token into the repository-local `corpus/` directory:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --archive-classroom 19601548035-2018-g12-ict
```

Archive one course by ID or slug into an existing external corpus:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --corpus-dir ../eduk8r-corpus/corpus \
  --course 19601548035
```

`--corpus-dir` must name an existing directory. The default local `./corpus`
directory is created automatically when needed.

### Archive a resumable classroom list

Create a UTF-8 text file containing one archive token per line. Blank lines and
lines beginning with `#` are ignored:

```text
# Historical ICT courses
19601548035-2018-g12-ict
41161136862-2019-2020-g12-ict
41164573488-2019-2020-g11-ict
```

Run the batch:

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --archive-classrooms-file ../eduk8r-corpus/docs/classrooms-list.txt \
  --corpus-dir ../eduk8r-corpus/corpus
```

Batch mode skips course directories that already exist, archives the remaining
tokens in file order, and prints the number of courses added. This makes the
token-file workflow the preferred way to resume a large historical archive.

### Archive all discovered courses

```bash
python3 bin/classroom-archiver.py \
  --creds .secrets/credentials.json \
  --corpus-dir ../eduk8r-corpus/corpus \
  --course all
```

Unlike token-file batch mode, the general `--course` path does not skip an
existing selected course directory. Existing archives are never overwritten.

## Corpus output

A representative archive looks like:

```text
corpus/
└── courses/
    └── ict-grade-12/
        ├── index.md
        ├── assignments/
        │   └── 2022-08-15-history-of-the-pc-essay/
        │       ├── index.md
        │       └── attachments/
        │           ├── Reading.md
        │           ├── Reading.md-files/
        │           │   └── image1.png
        │           ├── Reading.docx
        │           └── starter.py
        ├── assessments/
        ├── questions/
        └── resources/
```

Coursework is routed by Classroom work type:

| Classroom type | Corpus directory |
| --- | --- |
| `ASSIGNMENT` | `assignments/` |
| `QUIZ_ASSIGNMENT` | `assessments/` |
| `QUESTION` | `questions/` |
| `SHORT_ANSWER_QUESTION` | `questions/` |
| `MULTIPLE_CHOICE_QUESTION` | `questions/` |
| `MATERIAL` | `resources/` |

When a valid creation date is available, coursework directories use
`YYYY-MM-DD-{slug}`. The complete directory component is limited to 120
characters for compatibility with restrictive filesystems while preserving the
date prefix.

Assignment Markdown may contain:

- the title and description;
- external links and YouTube resources under `## Links`;
- downloaded or exported Drive files under `## Materials`; and
- creation date, due time, points, and resolved topic under
  `## Assignment Details`.

See [`docs/corpus-design.md`](docs/corpus-design.md) for the corpus model and
filesystem identity rules.

## Attachment behavior

Google Workspace files use explicit export formats:

| Drive type | Local output |
| --- | --- |
| Google Docs | `.md`, `.docx`, and extracted image sidecars |
| Google Sheets | `.csv` |
| Google Slides | `.pptx` and `.pdf` |

Ordinary uploaded Drive files use the Drive media download stream and retain
their sanitized titles. Path-traversal and OS-unsafe filename characters are
replaced with hyphens.

Some attachment failures are recoverable:

- missing or inaccessible files produce a warning and an offline Markdown stub;
- Workspace files exceeding Drive export limits produce a warning and an
  offline Markdown stub.

Unsupported Google Workspace application types, such as Forms, Sites, and
Drawings when encountered as Drive attachments, remain fatal. Form links are
preserved, but Google Forms question and answer serialization is a separate
future feature.

## Safety and failure model

Each course is built under the system temporary directory before being
transferred into `{corpus-root}/courses/{course-slug}`. Existing course
directories are not overwritten.

The archiver deliberately stops on structures it cannot represent safely,
including:

- unsupported Classroom work or material types;
- unsupported or missing Drive MIME metadata;
- non-downloadable Google Workspace application types;
- Drive permission failures; and
- malformed attachment filenames.

Transient Google API 500, 502, 503, and 504 responses are retried with bounded
backoff before the archive fails.

For a large archive, complete courses written before a later failure remain
available. Fix or explicitly support the reported feature gap, then rerun the
token-file batch to skip completed courses.

## Development

Run the complete test suite:

```bash
python3 -m pytest
```

Check that the script compiles:

```bash
python3 -m py_compile bin/classroom-archiver.py
```

Tests use temporary directories and must never write fixtures into the
production corpus.

Repository guidance for contributors and coding agents is in
[`AGENTS.md`](AGENTS.md). Historical implementation tasks live under
[`TASKS.d/`](TASKS.d/).

## Current limitations

- Google Forms payloads and answer keys are not serialized.
- Classroom rubrics are not fetched or written as CSV.
- Student submissions and grades are intentionally excluded.
- TAGL generation from archived corpus content is not yet implemented.

## License

This project is dedicated to the public domain under
[CC0 1.0 Universal](LICENSE).
