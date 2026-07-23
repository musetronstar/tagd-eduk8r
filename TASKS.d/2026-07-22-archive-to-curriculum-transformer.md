# Task: Archive-to-Curriculum Transformer

## Objective

Design and implement a standalone transformer that converts an immutable eduk8r archive into a curated educational curriculum.

Unlike the Google Classroom archiver, this tool performs **editorial transformation**, not preservation. The input archive remains unchanged.

---

## Motivation

The Google Classroom archiver has a single responsibility:

> Preserve classroom content faithfully.

The resulting archive retains institution-specific metadata such as assignment dates, due dates, Google identifiers, and original publication order.

A teacher-maintained curriculum has different goals:

* reusable by other educators
* independent of a particular school year
* collaboratively maintained
* semantically organized
* pedagogically sequenced

This transformer creates that second representation.

---

## Pipeline

```text
Google Classroom
        │
        ▼
 Immutable Archive
        │
        ▼
 Archive-to-Curriculum Transformer
        │
        ▼
 Curated Curriculum
        │
        ▼
 TAGL / Tagspace
```

Each stage has a single responsibility.

---

## Design Principles

The transformer shall:

* never modify the source archive
* produce deterministic output
* preserve educational content
* remove institution-specific metadata where appropriate
* support repeated execution

The archive is the historical record.

The curriculum is the maintained educational product.

---

## Inputs

A valid eduk8r archive.

Example:

```text
courses/
└── apcsa-2025-2026/
    ├── index.md
    ├── assignments/
    ├── assessments/
    ├── questions/
    └── resources/
```

---

## Outputs

A curated curriculum corpus.

Example:

```text
courses/
└── ap-computer-science-a/
    ├── index.md
    ├── assignments/
    │   ├── 001-primitive-types/
    │   ├── 002-variables/
    │   └── 003-expressions/
    ├── assessments/
    └── resources/
```

The output directory may be entirely separate from the archive.

---

## Planned Transformations

### Sequence Numbering

Replace archive chronology with pedagogical ordering.

Example:

```text
2026-07-20-unit-1-primitive-types
```

becomes

```text
001-unit-1-primitive-types
```

The numbering shall be contiguous.

---

### Duration

Replace institution-specific due dates with instructional duration.

Archive:

```text
Assigned: 2026-07-20
Due: 2026-07-24
```

becomes

```text
Duration: 4 days
```

Teachers may later edit these values manually.

---

### Metadata Cleanup

Remove metadata that only makes sense within Google Classroom.

Possible examples include:

* Assigned date
* Due date
* Google Classroom IDs
* Google URLs that are no longer needed
* institution-specific references

The educational content should remain intact.

---

### Content Cleanup

Future transformations may include:

* rewriting assignment wording
* normalizing formatting
* removing duplicate instructions
* merging equivalent lessons
* splitting overly large assignments

These changes are editorial rather than archival.

---

### Course Renaming

Allow curriculum-oriented course names.

Example:

```text
apcsa-2025-2026
```

may become

```text
ap-computer-science-a
```

---

### Reorganization

Support moving lessons between:

* assignments
* resources
* assessments

without affecting the original archive.

---

### Content Conversion

When archived attachments have been exported to open formats, replace proprietary Google references with local content.

Examples:

* Markdown
* PDF
* CSV
* local images

---

## Non-goals

This tool does not:

* communicate with Google APIs
* download content
* regenerate archives
* preserve provenance

Its only responsibility is transforming one corpus into another.

---

## Future Enhancements

Potential capabilities include:

* interactive renumbering
* lesson reordering
* curriculum validation
* duplicate lesson detection
* merge and split operations
* metadata normalization
* automatic duration estimation
* curriculum templates
* subject-specific transformation plugins

---

## Relationship to TAGD

The archive represents the historical territory.

The curriculum is a curated representation optimized for teaching.

TAGL and the semantic tagspace are then generated from the curriculum rather than directly from the archive.

This separation keeps archival concerns independent from curriculum authoring and semantic enrichment.

---

## Acceptance Criteria

A transformer shall:

1. Read an existing eduk8r archive.
2. Produce a separate curated curriculum.
3. Leave the archive unchanged.
4. Replace chronological ordering with pedagogical sequencing.
5. Replace due dates with instructional duration where appropriate.
6. Remove institution-specific metadata while preserving educational content.
7. Produce deterministic output suitable for collaborative maintenance.

The resulting curriculum should become the canonical source for future educational development, while the archive remains an immutable historical record.

