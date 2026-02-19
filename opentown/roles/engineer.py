"""Engineer role - implements assigned subtasks."""

import os
import subprocess
from pathlib import Path
from ..persistence import (
    load_state,
    save_state,
    load_tasks,
    save_tasks,
    create_worktree,
    update_engineer_status,
    TOWN_DIR,
)


ENGINEER_PROMPT = """
You are Engineer {engineer_id}.

Your assignment:
- Subtask ID: {subtask_id}
- Description: {subtask_desc}
- Branch: {branch_name}

Process:
1. Read .town/describe.md for project context
2. Work in your assigned worktree: {worktree_path}
3. Implement the assigned subtask
4. Commit your changes to your branch
5. When complete, update .town/state.json:
   - Find your engineer entry
   - Set status to "done"

Guidelines:
- Follow existing code patterns
- Write tests if applicable
- Keep changes focused on your subtask
"""


def spawn_engineers(count: int) -> None:
    """Spawn N engineer instances in tmux."""
    state = load_state()
    tasks = load_tasks()

    if not state or not tasks:
        print("No state or tasks. Run 'ot ceo' first.")
        return

    current_task_id = state.get("current_task")
    if not current_task_id:
        print("No current task. Run 'ot run' first.")
        return

    current_task = None
    for task in tasks["tasks"]:
        if task["id"] == current_task_id:
            current_task = task
            break

    if not current_task:
        print(f"Task {current_task_id} not found.")
        return

    subtasks = current_task.get("subtasks", [])

    print(f"Spawning {count} engineers for task {current_task_id}...")

    engineers = []
    for i in range(count):
        engineer_id = f"eng-{i + 1}"
        subtask = subtasks[i] if i < len(subtasks) else None
        branch_name = f"{current_task_id}-eng-{i + 1}"

        worktree_path = create_worktree(engineer_id, branch_name)

        engineer = {
            "id": engineer_id,
            "status": "working",
            "branch": branch_name,
            "tmux_session": f"ot-{engineer_id}",
            "subtask_id": subtask["id"] if subtask else None,
        }
        engineers.append(engineer)

        if subtask:
            subtask["assignee"] = engineer_id
            subtask["branch"] = branch_name

        print(f"  Created: {engineer_id} on branch {branch_name}")
        print(f"    Worktree: {worktree_path}")

    state["engineers"] = engineers
    state["phase"] = "implementation"
    save_state(state)
    save_tasks(tasks)

    print(f"\nSpawned {count} engineers. They will work on their assigned subtasks.")
    print("Monitor progress with 'ot status'")


def create_engineer_session(
    engineer_id: str, subtask_id: str, subtask_desc: str, branch: str
) -> None:
    """Create a tmux session for an engineer."""
    worktree_path = TOWN_DIR / "worktrees" / engineer_id

    session_name = f"ot-{engineer_id}"

    prompt = ENGINEER_PROMPT.format(
        engineer_id=engineer_id,
        subtask_id=subtask_id,
        subtask_desc=subtask_desc,
        branch_name=branch,
        worktree_path=worktree_path,
    )

    tmux_cmd = f"tmux new-session -d -s {session_name} -c {worktree_path}"
    os.system(tmux_cmd)

    print(f"Created tmux session: {session_name}")
    print(f"Attach with: tmux attach -t {session_name}")
    print(f"\nPrompt for engineer:\n{prompt}")


def run_engineer(engineer_id: str) -> None:
    """Run an engineer session."""
    state = load_state()
    tasks = load_tasks()

    engineer = None
    for eng in state.get("engineers", []):
        if eng["id"] == engineer_id:
            engineer = eng
            break

    if not engineer:
        print(f"Engineer {engineer_id} not found.")
        return

    print(f"\n{'=' * 60}")
    print(f"ENGINEER {engineer_id} SESSION")
    print(f"{'=' * 60}")
    print(f"Branch: {engineer.get('branch')}")
    print(f"Status: {engineer.get('status')}")
    print(f"Subtask: {engineer.get('subtask_id')}")

    if engineer.get("status") == "done":
        print("\nThis engineer has already completed their work.")
        return

    print("\nTo start working, run:")
    print(f"  cd {TOWN_DIR}/worktrees/{engineer_id}")
    print("  opencode")
    print("\nThen paste your assignment instructions.")
