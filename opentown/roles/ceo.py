"""CEO role - processes describe.md into structured tasks."""

import re
from pathlib import Path
from ..persistence import (
    load_describe,
    save_tasks,
    save_state,
    TOWN_DIR,
)


CEO_PROMPT = """
You are the CEO of OpenTown.

Your job is to read .town/describe.md and break down the work items in the "Next" section into atomic, parallelizable subtasks.

Rules:
1. Each subtask should be completable by ONE engineer in ONE session
2. Subtasks should be independent (parallelizable)
3. Include clear acceptance criteria
4. Write structured output to .town/tasks.json

Format for tasks.json:
{
  "current_task": null,
  "tasks": [
    {
      "id": "task-001",
      "title": "Task title from describe.md",
      "status": "pending",
      "phase": "planning",
      "subtasks": [
        {"id": "001-a", "desc": "Specific subtask", "assignee": null, "status": "pending", "branch": null},
        {"id": "001-b", "desc": "Another subtask", "assignee": null, "status": "pending", "branch": null}
      ]
    }
  ]
}

Now read .town/describe.md and create the tasks.json file.
"""


def parse_describe_tasks(content: str) -> list:
    """Parse tasks from describe.md Next section."""
    tasks = []

    lines = content.split("\n")
    in_next_section = False

    for line in lines:
        if "## Next" in line:
            in_next_section = True
            continue
        if line.startswith("## ") and in_next_section:
            in_next_section = False
            continue

        if in_next_section:
            match = re.match(r"-\s*\[\s*\]\s*(.+)", line)
            if match:
                task_title = match.group(1).strip()
                tasks.append(task_title)

    return tasks


def generate_task_id(existing_tasks: list) -> str:
    """Generate a unique task ID."""
    max_id = 0
    for task in existing_tasks:
        if task.get("id", "").startswith("task-"):
            try:
                num = int(task["id"].split("-")[1])
                max_id = max(max_id, num)
            except (IndexError, ValueError):
                pass
    return f"task-{max_id + 1:03d}"


def run_ceo() -> None:
    """Run CEO to process describe.md into tasks.json."""
    print("CEO: Reading describe.md...")

    content = load_describe()
    if not content:
        print("CEO: No describe.md found. Run 'ot init' first.")
        return

    task_titles = parse_describe_tasks(content)
    if not task_titles:
        print("CEO: No tasks found in describe.md 'Next' section.")
        return

    print(f"CEO: Found {len(task_titles)} tasks to break down.")
    print("CEO: Launching opencode session for task breakdown...")

    print("\n" + "=" * 60)
    print("INSTRUCTIONS FOR CEO SESSION:")
    print("=" * 60)
    print(CEO_PROMPT)
    print("=" * 60)
    print(f"\nTasks found in describe.md:")
    for i, title in enumerate(task_titles, 1):
        print(f"  {i}. {title}")
    print("\nStart opencode and paste the instructions above.")
    print("The CEO will read describe.md and create tasks.json")
