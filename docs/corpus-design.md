# tagd-eduk8r corpus design

The tagd-eduk8r app and tagspace won't be very useful without
a corpus of educational content. This is a design document for that corpus.

## Terms

+ **assignment**: an assigned work item as part of a progression through a course
+ **assignment_type**: a single (one-and-only-one) category that an assignment falls under. Google Classroom calls these topics, but a a tagd-eduk8r topic will be different (an assignment will have 0 or many topics associated)
+ **topic**: a relation from an assignment to a specific topic tag - one assignment can have zero or many topics (`relators` horizontal relations, not `super_relators` which have one and only one subordinate relation)
+ **courses**: and educational course name
+ 

## Corpus Organization
We want a well organized local corpus of:

* Courses (course directories contain assignment subdirectories):
* Assignments (each assigment should have its own directory of):
  + directory path either in the form (let's use Socratic reasoning to decide):
    1. `<slugified-classroom-course>/<slugified-classroom-topic>/<slugified-assignment-title>/`
      or
    2. `<slugified-classroom-course>/<slugified-assignment-title>/`
  + `<slugified-assignment-title>-assignment.md`
  + file attachments (original file name)
  + rubrics as `<slugified-assignment-title>-rubric.csv`
  + rubrics as `<slugified-assignment-title>-meta.tagl`
    containing
```tagl

```

## Current Corpus Directory Structure

```bash
$ tree tagd-eduk8r/corpus/

tagd-eduk8r/corpus/
├── courses
│   └── full-stack-webdev
│       ├── assignments
│       │   └── 02-About-Me-JavaScript
│       │       └── index.md
│       └── index.md
└── resources
    ├── html
    │   ├── html5-skeleton.html
    │   ├── index.md
    │   └── pure-html5-css3-responsive-table-solution.html
    ├── index.md
    ├── javascript
    │   ├── index.md
    │   └── tutorials
    │       ├── arrays.md
    │       ├── class-selectors.md
    │       ├── data-attributes.md
    │       ├── meta-example
    │       │   ├── favicon32.png
    │       │   ├── meta-example.html
    │       │   ├── script.js
    │       │   └── style.css
    │       ├── query-selectors-events.md
    │       └── script-loading-sequence
    │           ├── async-defer.js
    │           └── index.html
    ├── LAMP
    │   ├── index.md
    │   └── twitter-clone-tutorial.md
    ├── linux
    │   ├── freetype2-howto.md
    │   ├── index.md
    │   └── setup-www-userdir.md
    ├── python
    │   ├── assignments
    │   │   ├── 01-personal-data
    │   │   │   ├── instructions.md
    │   │   │   └── personal-data.py
    │   │   ├── 02-personal-data-error-handling
    │   │   │   ├── hints.html
    │   │   │   ├── hints.md
    │   │   │   ├── instructions.md
    │   │   │   └── personal-data.py
    │   │   ├── 03-personal-data-loop
    │   │   │   └── instructions.md
    │   │   └── index.md
    │   ├── index.md
    │   └── tutorials
    │       ├── 01-strings-and-printing.md
    │       ├── 02-string-variables.md
    │       ├── 03-integers-and-floats.md
    │       ├── 04-conditionals.md
    │       ├── 05-loops.md
    │       ├── 06-functions-and-scope.md
    │       ├── factorial.py
    │       └── index.md
    └── text
        └── brown.txt

20 directories, 40 files
```

