"""Tmux session management for OpenTown."""

import os
import subprocess
from pathlib import Path


def create_session(name: str, working_dir: str = None) -> bool:
    """Create a new tmux session."""
    cmd = ["tmux", "new-session", "-d", "-s", name]
    if working_dir:
        cmd.extend(["-c", working_dir])

    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def attach_session(name: str) -> None:
    """Attach to a tmux session."""
    os.system(f"tmux attach -t {name}")


def kill_session(name: str) -> bool:
    """Kill a tmux session."""
    result = subprocess.run(["tmux", "kill-session", "-t", name], capture_output=True)
    return result.returncode == 0


def list_sessions() -> list:
    """List all OpenTown tmux sessions."""
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return []

    sessions = result.stdout.strip().split("\n")
    return [s for s in sessions if s.startswith("ot-")]


def send_command(session: str, command: str) -> None:
    """Send a command to a tmux session."""
    os.system(f"tmux send-keys -t {session} '{command}' Enter")


def session_exists(name: str) -> bool:
    """Check if a tmux session exists."""
    result = subprocess.run(["tmux", "has-session", "-t", name], capture_output=True)
    return result.returncode == 0
