# Agentic Development Rules and Constraints

Guidance for coding agents working in the `tagd-eduk8r` repository.

## Project Purpose & Architecture

`tagd-eduk8r` separates application behavior from educational source material:

```
tagd-eduk8r/
  app/     # httagd web application code
  corpus/  # Human-authored educational corpus files (Markdown, code, etc.)
```

Markdown is the default prose format for educational content. TAGL is used exclusively to define the semantic tagspace and data model.

## Core Rule: Ask, Don't Guess

Do not guess, infer, or fill in missing structural, schema, or conversion details.
**If a design decision is not explicitly defined in the repository or the active task prompt, stop and ask for clarification.**

This single rule applies strictly to:

* **Corpus & Migration:** Modifying folder structures, renaming/converting files, or finalizing Google Doc/Classroom conversion rules.
* **TAGL & Schema:** Creating `*.tagl` manifests, defining relations/ontologies, or deciding metadata placement.
* **App Architecture:** Assuming frameworks, build systems, or routing models inside `app/`.

*Exception: You are fully authorized to implement low-level mechanical logic (like string slugification or path resolution) if the exact algorithms and constraints are explicitly provided in your active task prompt.*

## Constraints

### File Handling & Isolation

* Keep `app/` and `corpus/` strictly separated.
* Do not alter human-authored educational prose or code examples unless explicitly tasked.
* Ensure all test suites use isolated test fixtures. Never allow tests to write temporary files or dummy directories directly into the production `corpus/` path.

### Comments

* **self-documenting code preferred**, but REQUIRED: add concise **intent comments** (**why** not "what")
* Comment the invariant or reason the code is shaped this way; do not restate mechanics or narrate the current task

### Workflow & Deliverables

1. **Acknowledge:** Restate the requested change in concrete terms before editing.
2. **Implement:** Make the smallest, most reviewable change that satisfies the task criteria.
3. **Report:** Conclude your turn with:
  * A concise summary of changes and test results.
  * A suggested git commit message in the format: `<agent>: <commit message>`.
  * Any open consistency concerns (e.g., naming or contract drift).

