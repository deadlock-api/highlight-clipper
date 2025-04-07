"""
Core functionality for the Deadlock Highlight Clipper.

This package provides the core functionality of the application.
"""

from deadlock_highlight_clipper.core.app import run
from deadlock_highlight_clipper.core.match_processor import process_match, process_video

__all__ = [
    "run",
    "process_match",
    "process_video",
]
