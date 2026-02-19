"""CLI entry point for OpenTown."""

import click
import os
import subprocess
from pathlib import Path
from .persistence import (
    init_town,
    load_tasks,
    save_tasks,
    load_state,
    save_state,
    load_describe,
    TOWN_DIR,
)


@click.group()
def main():
    """OpenTown - Multi-opencode agent orchestrator."""
    pass


@main.command()
@click.option("--project-name", default="", help="Project name for describe.md")
def init(project_name: str):
    """Initialize .town/ directory in current project."""
    if TOWN_DIR.exists():
        click.echo("OpenTown already initialized in this project.")
        return

    init_town(project_name)
    click.echo(f"Initialized OpenTown in {TOWN_DIR}/")
    click.echo("Run 'ot describe' to start planning your work.")


@main.command()
def describe():
    """Open describe.md in editor."""
    describe_path = TOWN_DIR / "describe.md"
    if not describe_path.exists():
        click.echo("Run 'ot init' first.")
        return

    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, str(describe_path)])


@main.command()
def ceo():
    """Start CEO session to process describe.md into tasks."""
    from .roles.ceo import run_ceo

    run_ceo()


@main.command()
@click.option("--task", default=None, help="Specific task ID to work on")
def run(task: str):
    """Run the full pipeline: Manager -> Engineers -> QA."""
    from .monitor import run_pipeline

    run_pipeline(task_id=task)


@main.command()
def status():
    """Show current task, phase, and active agents."""
    state = load_state()
    tasks = load_tasks()

    if not state:
        click.echo("No active state. Run 'ot ceo' first.")
        return

    click.echo(f"Phase: {state.get('phase', 'idle')}")
    click.echo(f"Current Task: {state.get('current_task', 'none')}")

    if state.get("engineers"):
        click.echo("\nEngineers:")
        for eng in state["engineers"]:
            click.echo(
                f"  - {eng['id']}: {eng['status']} ({eng.get('branch', 'no branch')})"
            )

    if tasks and tasks.get("tasks"):
        pending = sum(1 for t in tasks["tasks"] if t["status"] == "pending")
        in_progress = sum(1 for t in tasks["tasks"] if t["status"] == "in_progress")
        done = sum(1 for t in tasks["tasks"] if t["status"] == "done")
        click.echo(
            f"\nTasks: {in_progress} in progress, {pending} pending, {done} done"
        )


@main.command()
@click.argument("count", type=int, default=1)
def spawn(count: int):
    """Spawn N engineer instances."""
    from .roles.engineer import spawn_engineers

    spawn_engineers(count)


@main.command()
def qa():
    """Manually trigger QA merge process."""
    from .roles.qa import run_qa

    run_qa()


if __name__ == "__main__":
    main()
