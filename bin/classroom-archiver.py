#!/usr/bin/env python3
"""
classroom-archiver.py
Archiving utility to pull courses, assignments, and resources from the Google 
Classroom HTTPS API and write them into a localized static directory structure.

Usage:
    python3 bin/classroom-archiver.py --creds secrets/credentials.json
    python3 bin/classroom-archiver.py --creds secrets/credentials.json --list-classrooms
    python3 bin/classroom-archiver.py --creds secrets/credentials.json --course full-stack-webdev
"""

import os
import re
import sys
import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- Configuration & Paths ---
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CORPUS_ROOT = REPO_ROOT / "corpus"


# --- Data Models ---
@dataclass
class ClassroomResource:
    """Represents a standalone educational material, attachment, or asset."""
    title: str
    source_type: str  # e.g., 'driveFile', 'link', 'youtube'
    source_url: str
    mime_type: Optional[str] = None
    local_filename: Optional[str] = None


@dataclass
class Assignment:
    """Represents a Google Classroom courseWork item (Assignment/Question)."""
    title: str
    description: Optional[str] = None
    materials: List[ClassroomResource] = field(default_factory=list)
    slug: str = ""

    def __post_init__(self):
        if not self.slug:
            self.slug = re.sub(r'[^a-zA-Z0-9_-]', '-', self.title.lower().replace(" ", "-"))


@dataclass
class Course:
    """Represents a Google Classroom Course."""
    id: str
    name: str
    description: Optional[str] = None
    assignments: List[Assignment] = field(default_factory=list)
    slug: str = ""

    def __post_init__(self):
        if not self.slug:
            self.slug = re.sub(r'[^a-zA-Z0-9_-]', '-', self.name.lower().replace(" ", "-"))


# --- Core Interfaces (Pluggable Abstractions) ---

class ClassroomScraper(ABC):
    """Responsible for live authentication and HTTPS API data fetching."""
    
    @abstractmethod
    def authenticate(self, creds_path: Path) -> None:
        """Handles OAuth2 token discovery using the provided credentials path."""
        pass

    @abstractmethod
    def fetch_courses(self) -> List[Course]:
        """Queries the live HTTPS API for active/archived courses."""
        pass

    @abstractmethod
    def fetch_assignments(self, course_id: str) -> List[Assignment]:
        """Queries the live HTTPS API for coursework tied to a specific course ID."""
        pass


class ContentConverter(ABC):
    """Pluggable translator for rendering external types into target file formats."""

    @abstractmethod
    def document_to_markdown(self, raw_content: Any) -> str:
        """Converts raw rich text/HTML elements into clean Markdown prose."""
        pass

    @abstractmethod
    def sheet_to_csv(self, raw_content: Any) -> str:
        """Converts Google Sheet structures into clean tabular CSV content."""
        pass


class CorpusWriter:
    """Handles the physical file system orchestration inside the corpus/ layout."""

    def __init__(self, target_root: Path = DEFAULT_CORPUS_ROOT):
        self.target_root = target_root

    def write_course_structure(self, course: Course) -> None:
        """Creates parent course directory and writes its primary index.md file."""
        pass

    def write_assignment_structure(self, course: Course, assignment: Assignment) -> None:
        """Creates target layout matching: corpus/courses/{course}/assignments/{assignment}/index.md"""
        pass


# --- Main Orchestration Execution ---

def main():
    parser = argparse.ArgumentParser(
        description="Archive Google Classroom courses into a local static file hierarchy."
    )
    
    parser.add_argument(
        "--creds",
        type=str,
        required=True,
        help="Path to the Google Cloud Console OAuth2 client credentials JSON file."
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_CORPUS_ROOT),
        help=f"Target output root directory (default: {DEFAULT_CORPUS_ROOT})"
    )
    
    parser.add_argument(
        "--course",
        type=str,
        default="all",
        help="Filter archive routine to a single specific course name slug or ID (default: all)"
    )
    
    parser.add_argument(
        "--list-classrooms",
        action="store_true",
        help="Query API to display available courses and their slug tokens, then exit cleanly."
    )

    args = parser.parse_args()
    creds_path = Path(args.creds)

    # 1. Short-circuit routing for Discovery Flag
    if args.list_classrooms:
        print(f"Connecting to Classroom API via profile: {creds_path}...")
        print("\nAvailable Classrooms:")
        print("-" * 60)
        # Mock example output template for the coding agent to bind onto
        print(f"Full Stack Web Development  [--course full-stack-webdev]")
        print(f"Python Programming 101       [--course python-programming-101]")
        sys.exit(0)

    # 2. Standard Archive Pipeline Routine
    print(f"Initializing Classroom Archiver Pipeline...")
    print(f"Using Credentials: {creds_path}")
    print(f"Target Output Directory: {args.output}")
    print(f"Processing Filter: {args.course}")
    
    # Ready for the coding agent to stitch concrete behaviors to these pathways.

if __name__ == "__main__":
    main()