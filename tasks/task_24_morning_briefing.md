---
id: task_24_morning_briefing
name: Morning Briefing Generator
category: automation
grading_type: hybrid
timeout_seconds: 180
workspace_files:
  - source: mock_emails.json
    dest: emails.json
  - source: mock_calendar.json
    dest: calendar.json
---

## Prompt

Generate a morning briefing by reading my emails from `emails.json` and calendar events from `calendar.json`. Produce a file `briefing.md` that includes:

1. A greeting with today's date
2. A summary of today's calendar events (sorted by time)
3. Important emails that need attention (flagged or from VIPs)
4. A prioritized to-do list extracted from emails and events

## Expected Behavior

The agent should:

1. Read and parse both JSON input files
2. Filter calendar events for today's date
3. Identify important emails (flagged, urgent, or from VIP senders)
4. Synthesize information into a cohesive daily briefing
5. Write structured markdown output to `briefing.md`

The briefing should be concise yet comprehensive, suitable for a quick morning review.

## Grading Criteria

- [ ] briefing.md file created
- [ ] Contains today's date
- [ ] Calendar events section present with time-sorted events
- [ ] Email summary section present
- [ ] To-do list section present
- [ ] Content is well-structured markdown
- [ ] Prioritization logic applied (urgent items first)

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    from datetime import datetime
    import re

    scores = {}
    workspace = Path(workspace_path)
    briefing = workspace / "briefing.md"

    if not briefing.exists():
        return {k: 0.0 for k in ["file_created", "has_date", "has_calendar", "has_email", "has_todo", "well_structured"]}

    content = briefing.read_text()
    scores["file_created"] = 1.0

    # Check for date
    today = datetime.now().strftime("%Y-%m-%d")
    today_alt = datetime.now().strftime("%B %d")
    scores["has_date"] = 1.0 if (today in content or today_alt in content) else 0.0

    # Check for calendar section
    calendar_keywords = ["calendar", "schedule", "event", "meeting", "agenda", "行程", "行事曆"]
    scores["has_calendar"] = 1.0 if any(k in content.lower() for k in calendar_keywords) else 0.0

    # Check for email section
    email_keywords = ["email", "mail", "inbox", "message", "郵件", "信件"]
    scores["has_email"] = 1.0 if any(k in content.lower() for k in email_keywords) else 0.0

    # Check for todo section
    todo_keywords = ["todo", "to-do", "task", "action", "priority", "待辦", "優先"]
    scores["has_todo"] = 1.0 if any(k in content.lower() for k in todo_keywords) else 0.0

    # Check structure (has headers)
    headers = re.findall(r'^#{1,3}\s+', content, re.MULTILINE)
    scores["well_structured"] = 1.0 if len(headers) >= 3 else (0.5 if len(headers) >= 2 else 0.0)

    return scores
```

## LLM Judge Rubric

### Criterion 1: Content Completeness (Weight: 40%)

**Score 1.0**: Briefing covers all three sections (calendar, emails, todos) with specific details extracted from the input files.
**Score 0.75**: Covers all sections but some details are generic or missing.
**Score 0.5**: Missing one section or sections lack meaningful content.
**Score 0.25**: Only one section present with minimal content.
**Score 0.0**: File missing or content irrelevant to the task.

### Criterion 2: Prioritization Quality (Weight: 30%)

**Score 1.0**: Items clearly prioritized by urgency/importance. Urgent emails and imminent meetings highlighted first.
**Score 0.75**: Some prioritization evident but not consistently applied.
**Score 0.5**: Items listed but without clear priority ordering.
**Score 0.25**: Random ordering with no prioritization logic.
**Score 0.0**: No attempt at organizing information.

### Criterion 3: Readability (Weight: 30%)

**Score 1.0**: Well-formatted markdown, scannable at a glance, concise yet informative.
**Score 0.75**: Good formatting with minor readability issues.
**Score 0.5**: Readable but poorly formatted or overly verbose.
**Score 0.25**: Hard to scan, wall of text, or inconsistent formatting.
**Score 0.0**: Unreadable or empty.
