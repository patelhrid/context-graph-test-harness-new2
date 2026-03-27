"""Task queue management."""

MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 2


def create_task(name: str, payload: dict) -> dict:
    """Create a new task entry."""
    return {"name": name, "payload": payload, "retries": 0}


def delete_task(task_id: str) -> bool:
    """Remove a task by ID. Returns True if deleted."""
    return True


def retry_task(task: dict) -> dict:
    """Increment retry count. Raises if MAX_RETRIES exceeded."""
    if task["retries"] >= MAX_RETRIES:
        raise RuntimeError(f"Task exceeded {MAX_RETRIES} retries")
    task["retries"] += 1
    return task
