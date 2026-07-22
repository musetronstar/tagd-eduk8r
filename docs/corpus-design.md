# Corpus Design

## Objective

The purpose of the eduk8r corpus is to provide a canonical, filesystem-based representation of educational knowledge from which a semantic tagspace may be generated.

The corpus is the **territory**. The generated TAGL and resulting tagspace are the **map**.

The design intentionally minimizes required structure, relying instead on a small set of recursively applied constraints. Rich semantic relationships emerge from the topology of the corpus rather than from extensive metadata.

---

# Design Philosophy

The corpus is designed according to the following principles.

## Territory Before Map

The filesystem is the authoritative representation of the corpus.

The generated TAGL is a semantic representation of the corpus and must always be derivable from it.

The corpus must remain useful and understandable even if no tagspace is ever generated.

---

## Identity by Containment

An entity derives its identity from its position within the corpus hierarchy.

Containment is therefore not merely organization—it defines identity.

The generated tagspace preserves this containment hierarchy.

---

## Recursive (Fractal) Organization

The corpus is recursively self-similar.

Every educational asset follows the same structural rules regardless of depth within the corpus.

Large educational collections are therefore composed from the same simple building blocks whether they be courses, lessons, assignments, rubrics, etc.

---

## Simplicity

The corpus intentionally defines as few rules as possible.

Whenever possible:

* prefer universal rules over special cases
* prefer conventions over configuration
* prefer tagspace topology over metadata

Additional semantics can be introduced through `meta.tagl` files without increasing filesystem complexity.

---

# Definitions

## Corpus

A corpus is a filesystem containing educational content and associated resources.

It is the authoritative source from which semantic knowledge is generated.

---

## Corpus Asset

A **corpus asset** is any filesystem object (file or directory) contained within the corpus.

Every file asset has a canonical path relative to the corpus root.

---

## Assets and `eduk8r:` prefix

Every educational asset is represented in the generated tagspace
by a tag whose identifier begins with the `eduk8r:` namespace.

---

## Asset Identity

A directory containing `index.md` represents an educational asset.

The generator recursively traverses the corpus searching for `index.md` files.

For each `index.md` encountered, the generator constructs a canonical asset identifier from:

1. the directory path relative to the corpus root; and
2. the first level-one heading in `index.md`.

For example:

```text
corpus/
└── courses/
    └── intro-to-python/
        └── assignments/
            └── 2026-07-20-personal-data/
                └── index.md
```

```markdown
# Personal Data
```

may generate:

```tagl
>> eduk8r:courses:Introduction_to_Python:Personal_Data;
```

The directory hierarchy provides structural identity.

The level-one heading provides the human-readable component of that identity.

All remaining Markdown content is unrestricted.

A directory may optionally contain `meta.tagl`, whose semantic extensions or overrides are applied after the asset identity has been established.

---

# Generator

A generator traverses the corpus and produces TAGL UTF-8 text describing the educational assets discovered within it.

The generated tagspace is the TAGL **map** of the corpus **territory**.

---

# Corpus Constraints

The following statements are always true.

1. The corpus is the authoritative representation of educational content.
2. Every file or directory within the corpus is a file asset.
3. A directory containing `index.md` is an educational asset.
4. Assets may recursively contain subordinate assets.
5. Asset identity is determined by containment within the corpus hierarchy.
6. `index.md` provides the canonical human-readable representation of an asset.
7. `meta.tagl` provide optional semantic extensions or overrides.
8. The generated tagspace preserves the containment hierarchy of the corpus.

---

# Complete Assignment Asset Structure

Teacher-authored coursework assets imported from Google Classroom are serialized into deterministic local asset folders. Student submissions, student grades, and student PII are explicitly excluded.

```text
corpus/courses/{course-slug}/assignments/{YYYY-MM-DD}-{assignment-slug}/
├── index.md                      # Title, description, points, due date, topics
├── rubric.csv                    # Tabular rubric criteria/levels (if present)
├── attachments/                  # Downloaded assignment materials and resources
│   ├── {Sanitized-Title}.pdf     # Binary attachments or exported Google Slides
│   ├── {Sanitized-Title}.csv     # Exported Google Sheets
│   ├── {Sanitized-Title}.docx    # Exported Google Doc binary format
│   ├── {Sanitized-Title}.md      # Exported Google Doc Markdown representation
│   └── {Sanitized-Title}_files/  # Media assets extracted from exported Google Docs
├── {form-slug}-questions.md     # Serialized quiz questions (for QUIZ_ASSIGNMENT)
├── {form-slug}-answers.md       # Serialized quiz answer keys
└── form-files/                   # Embedded media extracted from Google Forms
```

### Attachment Filename Sanitization Rules

When writing files into `attachments/`:

1. Use exact human-readable asset/file titles.
2. Replace OS-unsafe and path-traversal characters (`/`, `\`, `:`, `?`, `*`, `<`, `>`, `|`, `"`) with hyphens (`-`).
3. Strip leading and trailing whitespace and leading hyphens/spaces so files never begin with unsafe characters.

---

# Extensibility

The corpus intentionally specifies only the minimum required structure.

Future generators may derive additional semantic information from:

* directory conventions
* file types
* Markdown content
* `meta.tagl`
* external repositories
* imported learning management systems

without requiring changes to the corpus model itself.

The strength of the corpus is its small set of simple and composable constraints.

