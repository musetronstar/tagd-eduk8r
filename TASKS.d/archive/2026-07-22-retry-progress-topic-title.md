# Task
Fix topic title resolution, add real-time stdout progress reporting, and add transient HTTP 500 retry logic in `bin/classroom-archiver.py`.

## Scope
* Modified files: `bin/classroom-archiver.py`
* Modified tests: `tests/test_classroom_archiver.py`

## Requirements & Constraints

### 1. Topic Title Resolution
* Ensure `GoogleClassroomScraper` resolves raw `topicId` strings into human-readable Topic names using the course topic cache (`self._resolve_topic(payload.get("topicId"), topic_cache)`).
* If `topicId` is missing or not found in the topic cache, map the topic field cleanly (e.g., `None` or omit from frontmatter/metadata rather than printing raw IDs like `19958784179`).

### 2. Real-Time Progress Logging
* Print informational progress messages to `stdout` during batch execution:
  * When starting a course: `Archiving course '{course.slug}' ({course.id})...`
  * When skipping an existing course: `Skipping course '{course.slug}' (directory already exists).`
  * When completed: `Successfully archived '{course.slug}'.`

### 3. Transient HTTP 500 Retry Logic
* In `_paginate()`, wrap `list_method.execute()` in a retry loop (up to 3 attempts with exponential backoff: 1s, 2s) for server-side status codes (`500`, `502`, `503`, `504`).
* If all attempts fail, raise a contextual `RuntimeError`:
  `RuntimeError: "Google API transient error ({status_code}) on course '{course_id}'. Halting execution."`

## Acceptance Criteria
* `index.md` files display human-readable topic names instead of raw numeric `topicId` strings.
* `classroom-archiver.py` prints clear status updates to `stdout` for each course being archived.
* Transient 500 API errors automatically retry up to 3 times before failing.
* `python3 -m pytest` passes completely with updated unit tests.

