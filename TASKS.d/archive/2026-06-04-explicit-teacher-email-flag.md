# Task
Implement an explicit `--teacher-email` command-line flag to restrict discovered classrooms strictly to those taught by a specific user profile email address.

## Scope
* Modified files: `bin/classroom-archiver.py`

## Constraints

### 1. Argument Parser Updates
Add the optional long-form argument to the `argparse` configuration block inside `build_parser()`:
* **Flag:** `--teacher-email`
* **Type:** `str`
* **Default:** `None`
* **Help:** "Filter discovered courses strictly to those taught by this teacher email address."

### 2. Upstream API Parameter Mapping
Modify the live Google API service call inside the concrete `fetch_courses()` method:
* Accept the `teacher_email` string parameter passed down through the scraper interface routing.
* If `teacher_email` is provided, map it directly as the argument for the API's native query parameter: `.list(teacherId=teacher_email)`.
* If `teacher_email` is `None`, execute `.list()` without the `teacherId` filter restriction to keep default unfiltered behavior intact.

### 3. Loop and Pagination Invariants
Ensure `fetch_courses()` continues to leverage `nextPageToken` evaluation loops to reliably aggregate all matching courses across multi-page payloads from the server response.

## Acceptance Criteria
* Running `python3 bin/classroom-archiver.py --help` shows `--teacher-email` in the options block.
* Running `python3 bin/classroom-archiver.py --creds .secrets/credentials.json --list-classrooms --teacher-email your-profile@school.edu` accurately pipes the string into the Google API backend and cleanly filters down the 1,107 course list to only your matching courses.

## Deliverables
1. Summary of `--teacher-email` parameter integration into the `build_parser` and scraper loop logic
2. Suggested git commit message in the format: `<agent>: <commit message>`

