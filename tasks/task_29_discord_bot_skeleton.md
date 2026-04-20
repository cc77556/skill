---
id: task_29_discord_bot_skeleton
name: Discord Control Hub Skeleton
category: integration
grading_type: automated
timeout_seconds: 180
workspace_files: []
---

## Prompt

Create a Discord bot skeleton that serves as a digital control hub. Write the following files:

1. `bot.py` — Main bot file using discord.py with slash commands for: `/status` (system info), `/run` (execute a task by name), `/schedule` (list scheduled tasks), and `/ask` (forward a question to an AI endpoint).
2. `tasks.py` — Task registry with at least 3 example tasks (e.g., check_disk, backup_logs, generate_report). Each task should be a function that returns a result dict.
3. `config.json` — Bot configuration with token placeholder, prefix, enabled channels, and task schedule.
4. `requirements.txt` — Dependencies list.

Do NOT include real tokens. Use placeholders like `YOUR_TOKEN_HERE`.

## Expected Behavior

The agent should:

1. Create a functional discord.py bot structure with modern slash commands
2. Implement a task registry pattern for extensibility
3. Define configuration externally (not hardcoded)
4. Include proper error handling and permission checks
5. Use async/await patterns correctly for discord.py

## Grading Criteria

- [ ] bot.py created with discord.py bot setup
- [ ] At least 4 slash commands defined
- [ ] tasks.py created with task registry
- [ ] At least 3 tasks defined
- [ ] config.json created with proper structure
- [ ] requirements.txt created
- [ ] No real tokens or secrets in code
- [ ] Async patterns used correctly

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import ast
    import json
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check bot.py
    bot_file = workspace / "bot.py"
    if bot_file.exists():
        code = bot_file.read_text()
        scores["bot_created"] = 1.0
        try:
            ast.parse(code)
            scores["bot_valid"] = 1.0
        except SyntaxError:
            scores["bot_valid"] = 0.0

        # Check for slash commands
        slash_patterns = [r'@.*command', r'@.*slash_command', r'SlashCommand', r'app_commands', r'@tree\.command']
        cmd_count = sum(1 for p in slash_patterns if re.search(p, code))
        # Also count command-like function definitions
        cmd_funcs = len(re.findall(r'async def (status|run|schedule|ask|help)', code))
        total_cmds = max(cmd_count, cmd_funcs)
        scores["has_commands"] = 1.0 if total_cmds >= 3 else total_cmds / 3.0

        # Check async usage
        scores["uses_async"] = 1.0 if "async def" in code else 0.0

        # Check no real tokens
        scores["no_real_tokens"] = 0.0 if re.search(r'[A-Za-z0-9_-]{50,}', code) else 1.0
    else:
        scores["bot_created"] = 0.0
        scores["bot_valid"] = 0.0
        scores["has_commands"] = 0.0
        scores["uses_async"] = 0.0
        scores["no_real_tokens"] = 1.0

    # Check tasks.py
    tasks_file = workspace / "tasks.py"
    if tasks_file.exists():
        code = tasks_file.read_text()
        scores["tasks_created"] = 1.0
        task_funcs = len(re.findall(r'def \w+', code))
        scores["has_task_funcs"] = 1.0 if task_funcs >= 3 else task_funcs / 3.0
    else:
        scores["tasks_created"] = 0.0
        scores["has_task_funcs"] = 0.0

    # Check config.json
    config_file = workspace / "config.json"
    if config_file.exists():
        scores["config_created"] = 1.0
        try:
            config = json.loads(config_file.read_text())
            scores["config_valid"] = 1.0
        except json.JSONDecodeError:
            scores["config_valid"] = 0.0
    else:
        scores["config_created"] = 0.0
        scores["config_valid"] = 0.0

    # Check requirements.txt
    req_file = workspace / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text()
        scores["requirements_created"] = 1.0 if "discord" in content.lower() else 0.5
    else:
        scores["requirements_created"] = 0.0

    return scores
```
