---
id: task_26_multi_agent_workflow
name: Multi-Agent Task Dispatcher
category: developer
grading_type: hybrid
timeout_seconds: 180
workspace_files: []
---

## Prompt

Design a multi-agent task dispatching system. Create a Python module with the following files:

1. `dispatcher.py` — A task dispatcher that accepts task descriptions, classifies them by type (code, research, writing, data), and routes to the appropriate handler function.
2. `handlers.py` — Handler stubs for each task type, each returning a structured result dict.
3. `config.yaml` — Configuration file defining task types, priorities, and routing rules.
4. `test_dispatcher.py` — Unit tests that verify routing logic works correctly.

The dispatcher should support: task queuing, priority ordering, and type-based routing.

## Expected Behavior

The agent should:

1. Create a well-structured Python module with clear separation of concerns
2. Implement a dispatcher class that classifies and routes tasks
3. Define handler functions/classes for each task type
4. Write a YAML config for routing rules
5. Include unit tests with at least 3 test cases
6. Code should be runnable (no external dependencies beyond stdlib + pyyaml)

## Grading Criteria

- [ ] dispatcher.py created with dispatcher class/function
- [ ] handlers.py created with handler stubs
- [ ] config.yaml created with valid YAML
- [ ] test_dispatcher.py created with test cases
- [ ] Dispatcher implements task classification logic
- [ ] At least 3 task types defined
- [ ] Unit tests cover routing logic

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import ast
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check files exist
    for fname in ["dispatcher.py", "handlers.py", "test_dispatcher.py"]:
        fpath = workspace / fname
        if fpath.exists():
            scores[f"{fname}_exists"] = 1.0
            try:
                ast.parse(fpath.read_text())
                scores[f"{fname}_valid"] = 1.0
            except SyntaxError:
                scores[f"{fname}_valid"] = 0.0
        else:
            scores[f"{fname}_exists"] = 0.0
            scores[f"{fname}_valid"] = 0.0

    # Check config.yaml
    config = workspace / "config.yaml"
    if config.exists():
        scores["config_exists"] = 1.0
        content = config.read_text()
        # Basic YAML validation (has key-value structure)
        scores["config_valid"] = 1.0 if ":" in content else 0.0
    else:
        scores["config_exists"] = 0.0
        scores["config_valid"] = 0.0

    # Check dispatcher has classification logic
    if (workspace / "dispatcher.py").exists():
        code = (workspace / "dispatcher.py").read_text()
        has_class = "class " in code or "def dispatch" in code or "def route" in code
        has_types = sum(1 for t in ["code", "research", "writing", "data"] if t in code.lower())
        scores["has_dispatch_logic"] = 1.0 if has_class else 0.0
        scores["has_task_types"] = min(1.0, has_types / 3.0)

    # Check test file has test cases
    if (workspace / "test_dispatcher.py").exists():
        test_code = (workspace / "test_dispatcher.py").read_text()
        test_count = len(re.findall(r'def test_', test_code))
        scores["test_count"] = 1.0 if test_count >= 3 else test_count / 3.0

    return scores
```

## LLM Judge Rubric

### Criterion 1: Architecture Quality (Weight: 40%)

**Score 1.0**: Clean separation of concerns, well-defined interfaces between dispatcher and handlers, extensible design.
**Score 0.75**: Good structure with minor coupling issues.
**Score 0.5**: Functional but tightly coupled or poorly organized.
**Score 0.25**: Code works but is monolithic or hard to extend.
**Score 0.0**: No meaningful architecture.

### Criterion 2: Completeness (Weight: 35%)

**Score 1.0**: All files present, dispatcher routes correctly, handlers return structured results, config is used, tests pass.
**Score 0.75**: Most components work, minor gaps.
**Score 0.5**: Core dispatching works but missing tests or config integration.
**Score 0.25**: Partial implementation, major gaps.
**Score 0.0**: Incomplete or non-functional.

### Criterion 3: Code Quality (Weight: 25%)

**Score 1.0**: Clean, idiomatic Python, good naming, docstrings, type hints.
**Score 0.75**: Good code with minor style issues.
**Score 0.5**: Functional but messy or inconsistent style.
**Score 0.25**: Hard to read, poor naming, no documentation.
**Score 0.0**: Unreadable or broken.
