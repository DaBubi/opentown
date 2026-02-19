# OpenTown

Multi-opencode agent orchestrator - run multiple opencode instances in parallel with persistent work tracking.

## Quick Start

```bash
# Install
pip install opentown

# Initialize in your project
cd your-project
ot init

# Describe your work
ot describe

# Run CEO to break down tasks
ot ceo

# Run the pipeline
ot run
```

## The 4 Roles

| Role | Purpose |
|------|---------|
| **CEO** | Reads describe.md, breaks ideas into atomic tasks |
| **Manager** | Spawns engineers, monitors progress, coordinates work |
| **Engineer** | Implements assigned subtasks in parallel branches |
| **QA** | Tests, merges all branches into main |

## Commands

| Command | Description |
|---------|-------------|
| `ot init` | Initialize .town/ in current project |
| `ot describe` | Open describe.md in editor |
| `ot ceo` | Start CEO session to process describe.md |
| `ot run` | Run the full pipeline (auto-loop) |
| `ot status` | Show current task, phase, active agents |
| `ot spawn <n>` | Manually spawn N engineers |
| `ot qa` | Manually trigger QA merge |

## Architecture

```
.town/
├── describe.md    # Human's project notes & next work
├── tasks.json     # Structured task queue
├── state.json     # Current phase, active agents
└── worktrees/     # Git worktrees for parallel work
```

## License

MIT
