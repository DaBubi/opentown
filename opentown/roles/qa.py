"""QA role - tests and merges engineer branches."""

import os
import subprocess
from ..persistence import (
    load_state,
    save_state,
    load_tasks,
    save_tasks,
    load_describe,
    save_describe,
    remove_worktree,
    TOWN_DIR,
)


QA_PROMPT = """
You are QA for OpenTown.

All engineers have completed their work. Your job is to:
1. For each engineer branch (in order):
   - Checkout main
   - Merge the branch
   - Resolve any conflicts
   - Run tests
2. After all merges:
   - Run full test suite
   - Update tasks.json: mark task as done
   - Update describe.md: move from Next to Done
   - Update state.json: phase = "complete"

Current branches to merge:
{branches}

Test command: {test_cmd}

Start by checking out main: git checkout main
Then merge each branch one by one.
"""


def run_qa() -> None:
    """Run QA merge process."""
    state = load_state()
    tasks = load_tasks()

    if not state or not tasks:
        print("No state or tasks found.")
        return

    if state.get("phase") != "qa" and state.get("qa_status") != "ready":
        print("QA not ready. Engineers may still be working.")
        print("Check status with 'ot status'")
        return

    engineers = state.get("engineers", [])
    branches = [eng["branch"] for eng in engineers if eng.get("branch")]

    if not branches:
        print("No branches to merge.")
        return

    current_task_id = state.get("current_task")

    print(f"QA: Starting merge process for task {current_task_id}")
    print(f"QA: Branches to merge: {', '.join(branches)}")

    print("\n" + "=" * 60)
    print("QA SESSION INSTRUCTIONS:")
    print("=" * 60)
    print(
        QA_PROMPT.format(
            branches="\n".join(f"  - {b}" for b in branches),
            test_cmd="pytest",  # Could be configurable
        )
    )
    print("=" * 60)

    print("\nManual merge steps:")
    print("1. git checkout main")
    for branch in branches:
        print(f"2. git merge {branch}")
        print("3. Resolve conflicts if any")
        print("4. pytest  # run tests")
    print("5. git push origin main")

    print("\nAfter successful merge, run:")
    print("  ot complete")


def complete_task() -> None:
    """Mark current task as complete and update describe.md."""
    state = load_state()
    tasks = load_tasks()

    current_task_id = state.get("current_task")

    for task in tasks["tasks"]:
        if task["id"] == current_task_id:
            task["status"] = "done"
            task_title = task["title"]
            break

    save_tasks(tasks)

    describe = load_describe()
    lines = describe.split("\n")

    new_lines = []
    in_next = False
    task_moved = False

    for line in lines:
        if "## Done" in line:
            in_next = False
            new_lines.append(line)
            if not task_moved:
                new_lines.append(f"- [x] {task_title}")
                task_moved = True
        elif "## Next" in line:
            in_next = True
            new_lines.append(line)
        elif in_next and not task_moved and task_title.lower() in line.lower():
            continue
        else:
            new_lines.append(line)

    save_describe("\n".join(new_lines))

    for eng in state.get("engineers", []):
        remove_worktree(eng["id"])

    state["phase"] = "idle"
    state["current_task"] = None
    state["engineers"] = []
    state["qa_status"] = "waiting"
    save_state(state)

    print(f"Task {current_task_id} marked as complete!")
    print("Run 'ot run' to process the next task.")
