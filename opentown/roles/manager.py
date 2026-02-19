"""Manager role - coordinates work distribution and monitoring."""

import time
from ..persistence import (
    load_tasks,
    save_tasks,
    load_state,
    save_state,
    get_next_task,
    set_task_status,
    TOWN_DIR,
)


MANAGER_PROMPT = """
You are the Manager of OpenTown.

Your responsibilities:
1. Read .town/tasks.json to find current task
2. Spawn engineers for each subtask (run: ot spawn <n>)
3. Assign subtasks to engineers
4. Monitor progress via .town/state.json
5. When all engineers are "done", update phase to "qa"

Current state is in .town/state.json
Task details are in .town/tasks.json

Commands you can use:
- ot spawn <n> : spawn n engineer instances
- ot status : check current progress
"""


def run_manager(task_id: str = None) -> None:
    """Run manager coordination loop."""
    print("Manager: Starting coordination...")

    state = load_state()
    tasks = load_tasks()

    if not tasks or not tasks.get("tasks"):
        print("Manager: No tasks found. Run 'ot ceo' first.")
        return

    if task_id:
        state["current_task"] = task_id
        state["phase"] = "planning"
        save_state(state)

    current_task = None
    for task in tasks["tasks"]:
        if task["id"] == state.get("current_task"):
            current_task = task
            break

    if not current_task:
        next_task = get_next_task()
        if next_task:
            current_task = next_task
            state["current_task"] = current_task["id"]
            set_task_status(current_task["id"], "in_progress")
            print(
                f"Manager: Picked up task {current_task['id']}: {current_task['title']}"
            )
        else:
            print("Manager: No pending tasks found.")
            return

    subtasks = current_task.get("subtasks", [])
    if not subtasks:
        print(f"Manager: Task {current_task['id']} has no subtasks. Skipping.")
        return

    engineer_count = len(subtasks)
    print(f"Manager: Task has {engineer_count} subtasks")
    print(f"Manager: Run 'ot spawn {engineer_count}' to create engineer instances")

    print("\n" + "=" * 60)
    print("MANAGER SESSION INSTRUCTIONS:")
    print("=" * 60)
    print(MANAGER_PROMPT)
    print(f"\nCurrent Task: {current_task['id']} - {current_task['title']}")
    print("\nSubtasks:")
    for st in subtasks:
        print(f"  - [{st['id']}] {st['desc']}")
    print("=" * 60)


def monitor_progress() -> bool:
    """Check if all engineers are done. Returns True if QA should run."""
    state = load_state()

    if state.get("phase") != "implementation":
        return False

    engineers = state.get("engineers", [])
    if not engineers:
        return False

    all_done = all(eng.get("status") == "done" for eng in engineers)

    if all_done:
        state["phase"] = "qa"
        state["qa_status"] = "ready"
        save_state(state)
        print("Manager: All engineers done! Transitioning to QA phase.")
        return True

    return False
