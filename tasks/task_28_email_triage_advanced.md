---
id: task_28_email_triage_advanced
name: Smart Email Triage & Auto-Reply
category: automation
grading_type: hybrid
timeout_seconds: 180
workspace_files:
  - source: inbox.json
    dest: inbox.json
---

## Prompt

You have an inbox of 15 emails in `inbox.json`. Triage them by:

1. Categorizing each email: urgent, action_required, informational, spam
2. Drafting auto-reply templates for urgent and action_required emails
3. Creating a deletion list for spam emails
4. Saving results to:
   - `triage_report.json` — each email with category and reasoning
   - `auto_replies/` directory — one `.txt` file per reply draft (named by email ID)
   - `spam_list.txt` — list of spam email IDs to delete

## Expected Behavior

The agent should:

1. Read and parse the inbox JSON file
2. Analyze each email's sender, subject, and content to determine category
3. Apply prioritization logic (e.g., boss emails = urgent, newsletters = informational)
4. Draft contextually appropriate replies for actionable emails
5. Identify spam patterns (unknown senders, promotional content)
6. Output structured results in the specified format

## Grading Criteria

- [ ] triage_report.json created with all 15 emails categorized
- [ ] Each email has a category field (urgent/action_required/informational/spam)
- [ ] Each email has reasoning for categorization
- [ ] auto_replies/ directory created with reply drafts
- [ ] Reply drafts are contextually relevant
- [ ] spam_list.txt created
- [ ] Categories are logically applied

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import json

    scores = {}
    workspace = Path(workspace_path)

    # Check triage report
    report = workspace / "triage_report.json"
    if report.exists():
        scores["report_created"] = 1.0
        try:
            data = json.loads(report.read_text())
            scores["report_valid_json"] = 1.0

            # Check it's a list/dict with entries
            entries = data if isinstance(data, list) else list(data.values()) if isinstance(data, dict) else []
            scores["report_has_entries"] = 1.0 if len(entries) >= 10 else len(entries) / 10.0

            # Check categories
            valid_cats = {"urgent", "action_required", "informational", "spam"}
            if entries:
                cats_found = set()
                has_reasoning = 0
                for e in entries:
                    cat = e.get("category", "").lower().replace(" ", "_")
                    if cat in valid_cats:
                        cats_found.add(cat)
                    if e.get("reasoning") or e.get("reason"):
                        has_reasoning += 1
                scores["valid_categories"] = len(cats_found) / 4.0
                scores["has_reasoning"] = min(1.0, has_reasoning / max(len(entries), 1))
            else:
                scores["valid_categories"] = 0.0
                scores["has_reasoning"] = 0.0
        except (json.JSONDecodeError, Exception):
            scores["report_valid_json"] = 0.0
            scores["report_has_entries"] = 0.0
            scores["valid_categories"] = 0.0
            scores["has_reasoning"] = 0.0
    else:
        scores["report_created"] = 0.0
        scores["report_valid_json"] = 0.0
        scores["report_has_entries"] = 0.0
        scores["valid_categories"] = 0.0
        scores["has_reasoning"] = 0.0

    # Check auto_replies directory
    replies_dir = workspace / "auto_replies"
    if replies_dir.exists() and replies_dir.is_dir():
        reply_files = list(replies_dir.glob("*.txt"))
        scores["replies_created"] = 1.0 if len(reply_files) >= 1 else 0.0
        scores["replies_count"] = min(1.0, len(reply_files) / 3.0)
    else:
        scores["replies_created"] = 0.0
        scores["replies_count"] = 0.0

    # Check spam list
    spam = workspace / "spam_list.txt"
    if spam.exists():
        content = spam.read_text().strip()
        scores["spam_list_created"] = 1.0 if content else 0.5
    else:
        scores["spam_list_created"] = 0.0

    return scores
```

## LLM Judge Rubric

### Criterion 1: Categorization Accuracy (Weight: 40%)

**Score 1.0**: Categories are consistently logical. Urgent items are truly urgent, spam is correctly identified, reasoning is sound.
**Score 0.75**: Most categorizations are correct with 1-2 questionable decisions.
**Score 0.5**: Basic categorization works but several emails miscategorized.
**Score 0.25**: Random or inconsistent categorization.
**Score 0.0**: No categorization or completely wrong.

### Criterion 2: Reply Quality (Weight: 35%)

**Score 1.0**: Replies are professional, contextually appropriate, and address the email's specific content.
**Score 0.75**: Good replies with minor tone or context issues.
**Score 0.5**: Generic replies that don't reference specific email content.
**Score 0.25**: Inappropriate or irrelevant replies.
**Score 0.0**: No replies generated.

### Criterion 3: Output Organization (Weight: 25%)

**Score 1.0**: All output files properly structured, consistent naming, easy to process programmatically.
**Score 0.75**: Good organization with minor inconsistencies.
**Score 0.5**: Files exist but poorly organized.
**Score 0.25**: Missing major output files.
**Score 0.0**: No meaningful output.
