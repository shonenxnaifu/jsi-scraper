"""
Global state management for scraping process
This module provides a thread-safe mechanism to track the scraping status
across multiple gunicorn workers using optimized file-based locks.
"""
import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, Optional
from fastapi import HTTPException

# Import fcntl if available (Unix-like systems), otherwise use basic file operations
FCNTL_AVAILABLE = False
try:
    import fcntl  # For file locking (Unix-like systems: Linux, macOS)
    FCNTL_AVAILABLE = True
except ImportError:
    pass  # fcntl not available on this system

# Use separate files for different purposes to minimize lock contention
STATE_FILE_PATH = Path("/tmp/jsi_scraper_state.json")
LOCK_FILE_PATH = Path("/tmp/jsi_scraper_main.lock")  # Just for locking
STATE_FILE_PATH.parent.mkdir(exist_ok=True)
LOCK_FILE_PATH.parent.mkdir(exist_ok=True)

# Define the state file structure
DEFAULT_STATE = {
    "is_scraping": False,
    "start_time": None,
    "status": "IDLE",  # IDLE, ON PROGRESS, FINISHED
    "message": "System is idle",
    "progress": 0,
    "total_projects": 0
}

# Create state file if it doesn't exist
if not STATE_FILE_PATH.exists():
    with open(STATE_FILE_PATH, 'w') as f:
        json.dump(DEFAULT_STATE, f)

# Create lock file if it doesn't exist
LOCK_FILE_PATH.touch(exist_ok=True)


class GlobalStateManager:
    """
    Global state manager for tracking scraping process across gunicorn workers
    """
    _lock = threading.Lock()  # For thread safety within a single process

    @staticmethod
    def _read_state() -> Dict:
        """Read current state from state file (no exclusive locking needed for reading)"""
        try:
            with open(STATE_FILE_PATH, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    # Handle empty or corrupted file
                    return DEFAULT_STATE.copy()
        except FileNotFoundError:
            return DEFAULT_STATE.copy()

    @staticmethod
    def _write_state(state: Dict) -> None:
        """Write state to state file"""
        with open(STATE_FILE_PATH, 'w') as f:
            json.dump(state, f)
            f.flush()  # Ensure data is written

    @classmethod
    def get_status(cls) -> Dict:
        """Get current scraping status"""
        # Use both thread and file locking for maximum safety
        with cls._lock:
            state = cls._read_state()
            return {
                "status": state.get("status", "IDLE"),
                "message": state.get("message", "System is idle"),
                "progress": state.get("progress", 0),
                "total_projects": state.get("total_projects", 0),
                "is_scraping": state.get("is_scraping", False),
                "start_time": state.get("start_time")
            }

    @classmethod
    def is_scraping(cls) -> bool:
        """Check if scraping is currently in progress"""
        with cls._lock:
            state = cls._read_state()
            return state.get("is_scraping", False)

    @classmethod
    def start_scraping(cls) -> None:
        """Mark scraping as started - using exclusive file lock"""
        with cls._lock:
            if FCNTL_AVAILABLE:
                # Use exclusive lock file for atomic check-and-set operation
                with open(LOCK_FILE_PATH, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
                    # Read state while holding exclusive lock
                    try:
                        state = cls._read_state()
                    except json.JSONDecodeError:
                        # Handle empty or corrupted file
                        state = DEFAULT_STATE.copy()

                    if state.get("is_scraping", False):
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        raise RuntimeError("Scraping already in progress")

                    # Update the state file
                    state["is_scraping"] = True
                    state["status"] = "ON PROGRESS"
                    state["message"] = "Scraping in progress"
                    state["start_time"] = time.time()
                    state["progress"] = 0
                    state["total_projects"] = 0

                    cls._write_state(state)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            else:
                # Fallback for systems without fcntl - use thread lock only
                state = cls._read_state()
                if state.get("is_scraping", False):
                    raise RuntimeError("Scraping already in progress")

                state["is_scraping"] = True
                state["status"] = "ON PROGRESS"
                state["message"] = "Scraping in progress"
                state["start_time"] = time.time()
                state["progress"] = 0
                state["total_projects"] = 0
                cls._write_state(state)

    @classmethod
    def update_progress(cls, progress: float, total_projects: int = 0) -> None:
        """Update scraping progress"""
        with cls._lock:
            # No need for file locking here - just a fast update
            state = cls._read_state()
            if not state.get("is_scraping", False):
                return  # Only update if scraping is active

            state["progress"] = progress
            state["total_projects"] = total_projects
            cls._write_state(state)

    @classmethod
    def finish_scraping(cls, message: str = "Scraping completed") -> None:
        """Mark scraping as finished"""
        with cls._lock:
            if FCNTL_AVAILABLE:
                # Use exclusive lock file for atomic finish operation
                with open(LOCK_FILE_PATH, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
                    # Read state while holding exclusive lock
                    try:
                        state = cls._read_state()
                    except json.JSONDecodeError:
                        # Handle empty or corrupted file
                        state = DEFAULT_STATE.copy()

                    state["is_scraping"] = False
                    state["status"] = "FINISHED"
                    state["message"] = message
                    state["progress"] = 100

                    cls._write_state(state)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            else:
                # Fallback for systems without fcntl
                state = cls._read_state()
                state["is_scraping"] = False
                state["status"] = "FINISHED"
                state["message"] = message
                state["progress"] = 100
                cls._write_state(state)

    @classmethod
    def check_and_start_scraping(cls) -> bool:
        """Check if scraping is in progress and start if not - using exclusive lock"""
        with cls._lock:
            if FCNTL_AVAILABLE:
                # Use lock file for atomic check-and-set operation
                with open(LOCK_FILE_PATH, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
                    # Read state while holding exclusive lock
                    try:
                        state = cls._read_state()
                    except json.JSONDecodeError:
                        # Handle empty or corrupted file
                        state = DEFAULT_STATE.copy()

                    if state.get("is_scraping", False):
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        return False  # Scraping already in progress

                    # Update the state file
                    state["is_scraping"] = True
                    state["status"] = "ON PROGRESS"
                    state["message"] = "Scraping in progress"
                    state["start_time"] = time.time()
                    state["progress"] = 0
                    state["total_projects"] = 0

                    cls._write_state(state)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    return True
            else:
                # Fallback for systems without fcntl
                state = cls._read_state()
                if state.get("is_scraping", False):
                    return False  # Scraping already in progress

                state["is_scraping"] = True
                state["status"] = "ON PROGRESS"
                state["message"] = "Scraping in progress"
                state["start_time"] = time.time()
                state["progress"] = 0
                state["total_projects"] = 0
                cls._write_state(state)
                return True


# Create a global instance
state_manager = GlobalStateManager()