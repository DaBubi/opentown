"""Pipeline monitor - auto-transitions between phases."""

import time
import subprocess
from .persistence import (
    load_state,
    save_state,
    load_tasks,
    get_next_task,
    set_task_status,
    TOWN_DIR,
)
from .roles.manager import monitor_progress
from .roles.qa import run_qa


def run_pipeline(task_id: str = None) -> None:
    """Run the full pipeline with auto-transition."""
    print("OpenTown Pipeline: Starting...")

    state = load_state()
    tasks = load_tasks()

    if not tasks or not tasks.get("tasks"):
        print("No tasks found. Run 'ot ceo' first.")
        return

    if not task_id:
        next_task = get_next_task()
        if next_task:
            task_id = next_task["id"]
        else:
            print("No pending tasks.")
            return

    state["current_task"] = task_id
    state["phase"] = "planning"
    state["active_since"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    save_state(state)
    set_task_status(task_id, "in_progress")

    print(f"Pipeline: Working on task {task_id}")
    print("\nNext steps:")
    print("1. Manager should analyze task and spawn engineers")
    print("2. Run 'ot spawn <n>' where n = number of subtasks")
    print("3. Monitor with 'ot status'")
    print("4. When engineers finish, QA will auto-trigger")

    print("\nStarting monitor loop (Ctrl+C to stop)...")

    try:
        monitor_loop()
    except KeyboardInterrupt:
        print("\nPipeline monitoring stopped.")


def monitor_loop() -> None:
    """Background monitor that auto-transitions phases."""
    while True:
        state = load_state()

        phase = state.get("phase", "idle")

        if phase == "implementation":
            if monitor_progress():
                print("\nAll engineers done! QA phase starting...")
                run_qa()
                break

        elif phase == "qa":
            print("Waiting for QA to complete...")

        elif phase == "complete":
            print("Task complete! Run 'ot run' for next task.")
            break

        elif phase == "idle":
            print("No active task. Run 'ot ceo' to plan work.")
            break

        time.sleep(30)
