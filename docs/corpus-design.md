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

Large educational collections are therefore composed from the same simple building blocks as individual lessons or assignments.

---

## Simplicity

The corpus intentionally defines as few rules as possible.

Whenever possible:

* prefer universal rules over special cases
* prefer conventions over configuration
* prefer topology over metadata

Additional semantics may always be introduced through TAGL without increasing filesystem complexity.

---

# Definitions

## Corpus

A corpus is a filesystem containing educational content and associated resources.

It is the authoritative source from which semantic knowledge is generated.

---

## File Asset

A **file asset** is any file or directory contained within the corpus.

Every file asset has a canonical path relative to the corpus root.

---

## `eduk8r:asset`

An **`eduk8r:asset`** is a semantic entity represented as the subject of one or more TAGL statements.

An `eduk8r:asset` is generated from one or more related file assets within the corpus.

Examples include:

* course
* lesson
* tutorial
* assignment
* resource
* document
* image
* source code
* video

---

## Asset Identity

The identity of an asset is determined by its containment hierarchy within the corpus.

A generated tag identifier should therefore preserve the asset's canonical location.

For example:

```
eduk8r:courses:python:tutorials:introduction
```

represents the educational entity located within the corresponding corpus hierarchy.

---

## `index.md`

`index.md` is the canonical human-readable representation of an educational asset.

Every asset directory shall contain an `index.md`.

The minimum valid form is:

```markdown
# Title
```

The first non-blank line shall be exactly one level-one heading.

Additional Markdown content is optional.

---

## `meta.tagl`

`meta.tagl` is optional.

It provides semantic enrichment, customization, or overrides which cannot be inferred from the corpus topology alone.

`meta.tagl` never establishes the existence of an asset.

Only `index.md` establishes asset identity.

---

## Generator

A generator traverses the corpus and produces TAGL describing the educational assets discovered within it.

The generated tagspace is a semantic projection of the corpus.

---

# Corpus Axioms

The following statements are always true.

1. The corpus is the authoritative representation of educational content.

2. Every file or directory within the corpus is a file asset.

3. A directory containing `index.md` is an educational asset.

4. Assets may recursively contain subordinate assets.

5. Asset identity is determined by containment within the corpus hierarchy.

6. `index.md` provides the canonical human-readable representation of an asset.

7. `meta.tagl` is optional semantic enrichment.

8. The generated tagspace preserves the containment hierarchy of the corpus.

---

# Canonical Organization

A minimal corpus may be organized as follows.

```text
corpus/
├── courses/
│   ├── index.md
│   └── python/
│       ├── index.md
│       ├── tutorials/
│       │   ├── index.md
│       │   └── introduction/
│       │       ├── index.md
│       │       ├── meta.tagl
│       │       └── files/
│       │           ├── hello.py
│       │           └── slides.pdf
│       └── assignments/
│           ├── index.md
│           └── personal-data/
│               ├── index.md
│               └── files/
└── resources/
    ├── index.md
    └── python/
        ├── index.md
        └── tutorials/
            ├── index.md
            └── files/
```

The names of directories are significant because they contribute to the identity of the generated semantic entities.

---

# Generated Identity

The generator derives semantic identity from the corpus hierarchy.

Conceptually:

```
corpus/
    courses/
        python/
            tutorials/
                introduction/
```

becomes:

```tagl
>> eduk8r:courses:python:tutorials:introduction
    type_of eduk8r:tutorial;
```

Additional semantic relationships may be generated from the containment hierarchy.

For example:

```tagl
>> eduk8r:courses:python:tutorials
    _sub eduk8r:courses:python;

>> eduk8r:courses:python:tutorials:introduction
    _sub eduk8r:courses:python:tutorials;
```

The resulting tagspace preserves the topology of the corpus.

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

The simplicity of the corpus is its greatest strength.

