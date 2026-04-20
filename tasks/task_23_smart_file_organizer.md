---
id: task_23_smart_file_organizer
name: Smart File Organizer
category: productivity
grading_type: automated
timeout_seconds: 120
workspace_files:
  - source: messy_files/report_2024Q1.pdf
    dest: downloads/report_2024Q1.pdf
  - source: messy_files/vacation_photo.jpg
    dest: downloads/vacation_photo.jpg
  - source: messy_files/budget_2024.xlsx
    dest: downloads/budget_2024.xlsx
  - source: messy_files/meeting_notes.txt
    dest: downloads/meeting_notes.txt
  - source: messy_files/logo_draft_v2.png
    dest: downloads/logo_draft_v2.png
  - source: messy_files/invoice_march.pdf
    dest: downloads/invoice_march.pdf
  - source: messy_files/song_demo.mp3
    dest: downloads/song_demo.mp3
  - source: messy_files/presentation.pptx
    dest: downloads/presentation.pptx
---

## Prompt

I have a messy `downloads/` folder with 8 files of different types (PDFs, images, spreadsheets, text files, audio, presentations). Organize them into categorized subdirectories based on file type. Create a manifest file `organized_manifest.json` that maps each original filename to its new path.

## Expected Behavior

The agent should:

1. Scan the `downloads/` directory and identify all files
2. Create logical subdirectories (e.g., `documents/`, `images/`, `spreadsheets/`, `media/`, `presentations/`)
3. Move or copy each file into the appropriate subdirectory
4. Generate `organized_manifest.json` mapping original filenames to new locations
5. Handle edge cases (e.g., PDFs could be documents or invoices)

Acceptable directory structures vary, but files should be grouped by type logically.

## Grading Criteria

- [ ] Subdirectories created (at least 3 categories)
- [ ] All 8 files moved to categorized directories
- [ ] No files left in root downloads/ directory
- [ ] manifest.json created with correct mappings
- [ ] manifest.json is valid JSON
- [ ] File categorization is logical (e.g., images together, documents together)

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import json

    scores = {}
    workspace = Path(workspace_path)
    downloads = workspace / "downloads"

    # Check subdirectories created
    subdirs = [d for d in downloads.rglob("*") if d.is_dir()]
    scores["subdirs_created"] = 1.0 if len(subdirs) >= 3 else (0.5 if len(subdirs) >= 2 else 0.0)

    # Check all files moved (not in root downloads/)
    root_files = [f for f in downloads.iterdir() if f.is_file() and f.name != "organized_manifest.json"]
    scores["no_root_files"] = 1.0 if len(root_files) == 0 else 0.0

    # Check all 8 files exist somewhere under downloads/
    all_files = list(downloads.rglob("*"))
    all_filenames = {f.name for f in all_files if f.is_file() and f.name != "organized_manifest.json"}
    expected = {"report_2024Q1.pdf", "vacation_photo.jpg", "budget_2024.xlsx",
                "meeting_notes.txt", "logo_draft_v2.png", "invoice_march.pdf",
                "song_demo.mp3", "presentation.pptx"}
    found = expected & all_filenames
    scores["all_files_present"] = len(found) / len(expected)

    # Check manifest
    manifest_path = workspace / "organized_manifest.json"
    if not manifest_path.exists():
        manifest_path = downloads / "organized_manifest.json"

    if manifest_path.exists():
        scores["manifest_created"] = 1.0
        try:
            manifest = json.loads(manifest_path.read_text())
            scores["manifest_valid_json"] = 1.0
            scores["manifest_mappings"] = min(1.0, len(manifest) / 8.0)
        except (json.JSONDecodeError, Exception):
            scores["manifest_valid_json"] = 0.0
            scores["manifest_mappings"] = 0.0
    else:
        scores["manifest_created"] = 0.0
        scores["manifest_valid_json"] = 0.0
        scores["manifest_mappings"] = 0.0

    return scores
```
