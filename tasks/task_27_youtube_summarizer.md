---
id: task_27_youtube_summarizer
name: YouTube Video Summarizer
category: automation
grading_type: hybrid
timeout_seconds: 300
workspace_files: []
---

## Prompt

Build a YouTube video summarizer. Write a Python script `yt_summarizer.py` that:

1. Accepts a YouTube URL as a command-line argument
2. Extracts the video title, channel, duration, and description using yt-dlp
3. Fetches the transcript/subtitles (if available)
4. Generates a structured summary and saves it to `summary.md`

For testing, use this video: https://www.youtube.com/watch?v=dQw4w9WgXcQ

The summary should include: video metadata, key topics, and a bullet-point summary.

## Expected Behavior

The agent should:

1. Create a Python script that uses yt-dlp (or youtube-transcript-api) to fetch video metadata
2. Extract available subtitles/transcript
3. Generate a structured markdown summary
4. Handle the case where subtitles are not available (fall back to description-based summary)
5. Save output to `summary.md`

The script should be executable from command line: `python3 yt_summarizer.py "URL"`

## Grading Criteria

- [ ] yt_summarizer.py created
- [ ] Script is valid Python
- [ ] Script accepts URL as command-line argument
- [ ] Script uses yt-dlp or equivalent for metadata
- [ ] summary.md generated with video metadata
- [ ] Summary contains structured sections (metadata, topics, bullet points)
- [ ] Error handling for missing subtitles

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import ast
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check script exists and is valid
    script = workspace / "yt_summarizer.py"
    if script.exists():
        scores["script_created"] = 1.0
        code = script.read_text()
        try:
            ast.parse(code)
            scores["valid_python"] = 1.0
        except SyntaxError:
            scores["valid_python"] = 0.0

        # Check for CLI argument handling
        scores["has_cli_args"] = 1.0 if ("argv" in code or "argparse" in code or "sys.argv" in code) else 0.0

        # Check for yt-dlp usage
        scores["uses_ytdlp"] = 1.0 if ("yt_dlp" in code or "yt-dlp" in code or "ytdl" in code or "youtube_transcript" in code) else 0.0

        # Check for error handling
        scores["has_error_handling"] = 1.0 if ("try" in code and "except" in code) else 0.0
    else:
        scores["script_created"] = 0.0
        scores["valid_python"] = 0.0
        scores["has_cli_args"] = 0.0
        scores["uses_ytdlp"] = 0.0
        scores["has_error_handling"] = 0.0

    # Check summary output
    summary = workspace / "summary.md"
    if summary.exists():
        content = summary.read_text()
        scores["summary_created"] = 1.0
        headers = re.findall(r'^#{1,3}\s+', content, re.MULTILINE)
        scores["summary_structured"] = 1.0 if len(headers) >= 2 else 0.5 if len(headers) >= 1 else 0.0
    else:
        scores["summary_created"] = 0.0
        scores["summary_structured"] = 0.0

    return scores
```

## LLM Judge Rubric

### Criterion 1: Functionality (Weight: 50%)

**Score 1.0**: Script runs end-to-end, fetches metadata, extracts transcript, produces well-formatted summary.
**Score 0.75**: Core functionality works with minor issues (e.g., partial metadata).
**Score 0.5**: Script runs but output is incomplete or poorly formatted.
**Score 0.25**: Script has significant issues but shows correct approach.
**Score 0.0**: Script doesn't work or is fundamentally wrong.

### Criterion 2: Robustness (Weight: 25%)

**Score 1.0**: Handles missing subtitles, invalid URLs, network errors gracefully.
**Score 0.75**: Handles most edge cases.
**Score 0.5**: Basic error handling present.
**Score 0.25**: Crashes on common edge cases.
**Score 0.0**: No error handling.

### Criterion 3: Output Quality (Weight: 25%)

**Score 1.0**: Summary is well-organized, concise, includes all metadata and key points.
**Score 0.75**: Good summary with minor formatting issues.
**Score 0.5**: Summary present but lacks structure or key information.
**Score 0.25**: Minimal or poorly formatted output.
**Score 0.0**: No meaningful output.
