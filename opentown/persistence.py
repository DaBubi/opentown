"""Persistence layer - git-backed JSON state management."""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

TOWN_DIR = Path.cwd() / ".town"
DESCRIBE_TEMPLATE = """# Project: {project_name}

## Context
Brief description of your project, tech stack, conventions.

## Done
<!-- Move completed items here -->

## Next
- [ ] Add your first task here
- [ ] Another task to work on

## Notes
- Add any guidelines for engineers
- Testing framework: pytest
- Code style: follow existing patterns
"""


def init_town(project_name: str = "") -> None:
    """Initialize .town directory structure."""
    TOWN_DIR.mkdir(exist_ok=True)
    (TOWN_DIR / "worktrees").mkdir(exist_ok=True)

    describe_path = TOWN_DIR / "describe.md"
    if not describe_path.exists():
        describe_path.write_text(
            DESCRIBE_TEMPLATE.format(project_name=project_name or "My Project")
        )

    tasks_path = TOWN_DIR / "tasks.json"
    if not tasks_path.exists():
        save_tasks({"current_task": None, "tasks": []})

    state_path = TOWN_DIR / "state.json"
    if not state_path.exists():
        save_state(
            {
                "phase": "idle",
                "active_since": None,
                "current_task": None,
                "engineers": [],
                "qa_status": "waiting",
            }
        )


def load_json(path: Path) -> Optional[dict]:
    """Load JSON file."""
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_json(path: Path, data: dict) -> None:
    """Save JSON file."""
    path.write_text(json.dumps(data, indent=2))


def load_tasks() -> Optional[dict]:
    """Load tasks.json."""
    return load_json(TOWN_DIR / "tasks.json")


def save_tasks(tasks: dict) -> None:
    """Save tasks.json."""
    save_json(TOWN_DIR / "tasks.json", tasks)


def load_state() -> Optional[dict]:
    """Load state.json."""
    return load_json(TOWN_DIR / "state.json")


def save_state(state: dict) -> None:
    """Save state.json."""
    save_json(TOWN_DIR / "state.json", state)


def load_describe() -> str:
    """Load describe.md content."""
    describe_path = TOWN_DIR / "describe.md"
    if not describe_path.exists():
        return ""
    return describe_path.read_text()


def save_describe(content: str) -> None:
    """Save describe.md content."""
    (TOWN_DIR / "describe.md").write_text(content)


def get_worktree_path(engineer_id: str) -> Path:
    """Get worktree path for an engineer."""
    return TOWN_DIR / "worktrees" / engineer_id


def create_worktree(engineer_id: str, branch_name: str) -> Path:
    """Create a git worktree for an engineer."""
    worktree_path = get_worktree_path(engineer_id)
    worktree_path.mkdir(parents=True, exist_ok=True)

    os.system(
        f"git worktree add {worktree_path} -b {branch_name} 2>/dev/null || git worktree add {worktree_path} {branch_name}"
    )

    return worktree_path


def remove_worktree(engineer_id: str) -> None:
    """Remove a git worktree."""
    worktree_path = get_worktree_path(engineer_id)
    if worktree_path.exists():
        os.system(f"git worktree remove {worktree_path} --force 2>/dev/null")


def update_engineer_status(engineer_id: str, status: str, branch: str = None) -> None:
    """Update an engineer's status in state.json."""
    state = load_state() or {}
    engineers = state.get("engineers", [])

    for eng in engineers:
        if eng["id"] == engineer_id:
            eng["status"] = status
            if branch:
                eng["branch"] = branch
            break
    else:
        engineers.append(
            {
                "id": engineer_id,
                "status": status,
                "branch": branch,
                "tmux_session": f"ot-{engineer_id}",
            }
        )

    state["engineers"] = engineers
    save_state(state)


def get_next_task() -> Optional[dict]:
    """Get the next pending task."""
    tasks = load_tasks()
    if not tasks:
        return None

    for task in tasks.get("tasks", []):
        if task["status"] == "pending":
            return task
    return None


def set_task_status(task_id: str, status: str) -> None:
    """Update task status."""
    tasks = load_tasks()
    if not tasks:
        return

    for task in tasks.get("tasks", []):
        if task["id"] == task_id:
            task["status"] = status
            break

    save_tasks(tasks)
