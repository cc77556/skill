---
id: task_25_web_scraper
name: Large-Scale Data Scraping
category: developer
grading_type: automated
timeout_seconds: 300
workspace_files: []
---

## Prompt

Write a Python script called `scraper.py` that scrapes the top 30 stories from Hacker News (https://news.ycombinator.com/) and saves them to `hn_stories.json`. Each story should include: rank, title, URL, points, author, and number of comments. Also create a brief `summary.txt` with the top 5 stories by points.

## Expected Behavior

The agent should:

1. Write a Python script that fetches the Hacker News front page
2. Parse the HTML to extract story details (rank, title, URL, points, author, comments)
3. Save structured data to `hn_stories.json` as a JSON array
4. Create `summary.txt` with the top 5 stories sorted by points
5. The script should handle edge cases (stories without URLs, missing fields)

The agent may use requests + BeautifulSoup, or the HN API (https://hacker-news.firebaseio.com/). Both approaches are acceptable.

## Grading Criteria

- [ ] scraper.py file created
- [ ] scraper.py is valid Python (no syntax errors)
- [ ] hn_stories.json created with story data
- [ ] JSON contains at least 20 stories
- [ ] Each story has required fields (title, points, author)
- [ ] summary.txt created with top 5 stories
- [ ] Stories in summary are sorted by points descending

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import json
    import ast

    scores = {}
    workspace = Path(workspace_path)

    # Check scraper.py exists
    scraper = workspace / "scraper.py"
    if scraper.exists():
        scores["script_created"] = 1.0
        # Validate Python syntax
        try:
            ast.parse(scraper.read_text())
            scores["valid_python"] = 1.0
        except SyntaxError:
            scores["valid_python"] = 0.0
    else:
        scores["script_created"] = 0.0
        scores["valid_python"] = 0.0

    # Check hn_stories.json
    stories_file = workspace / "hn_stories.json"
    if stories_file.exists():
        scores["json_created"] = 1.0
        try:
            stories = json.loads(stories_file.read_text())
            scores["json_valid"] = 1.0
            scores["enough_stories"] = 1.0 if len(stories) >= 20 else len(stories) / 20.0

            # Check fields
            required_fields = {"title"}
            optional_fields = {"points", "author", "url", "comments", "rank"}
            if stories:
                first = stories[0]
                has_required = all(f in first for f in required_fields)
                has_optional = sum(1 for f in optional_fields if f in first)
                scores["has_fields"] = 1.0 if has_required and has_optional >= 2 else 0.5 if has_required else 0.0
            else:
                scores["has_fields"] = 0.0
        except (json.JSONDecodeError, Exception):
            scores["json_valid"] = 0.0
            scores["enough_stories"] = 0.0
            scores["has_fields"] = 0.0
    else:
        scores["json_created"] = 0.0
        scores["json_valid"] = 0.0
        scores["enough_stories"] = 0.0
        scores["has_fields"] = 0.0

    # Check summary.txt
    summary = workspace / "summary.txt"
    if summary.exists():
        content = summary.read_text()
        scores["summary_created"] = 1.0
        # Check it has multiple entries
        lines = [l for l in content.strip().split("\n") if l.strip()]
        scores["summary_has_content"] = 1.0 if len(lines) >= 5 else len(lines) / 5.0
    else:
        scores["summary_created"] = 0.0
        scores["summary_has_content"] = 0.0

    return scores
```
