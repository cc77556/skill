---
id: task_30_meal_planner
name: Weekly Meal Planner
category: personal
grading_type: hybrid
timeout_seconds: 180
workspace_files:
  - source: dietary_preferences.json
    dest: preferences.json
---

## Prompt

Create a weekly meal plan based on my dietary preferences in `preferences.json`. Generate:

1. `meal_plan.md` — A 7-day meal plan (breakfast, lunch, dinner) with recipe names and brief descriptions
2. `shopping_list.md` — A consolidated shopping list grouped by category (produce, protein, dairy, pantry)
3. `nutrition_estimate.json` — Rough daily calorie and macro estimates for each day

Consider the preferences file for allergies, cuisine preferences, and calorie targets.

## Expected Behavior

The agent should:

1. Read dietary preferences (allergies, cuisine type, calorie target, etc.)
2. Generate varied meals across 7 days (avoid repetition)
3. Include balanced nutrition (protein, carbs, fats)
4. Consolidate ingredients into a deduplicated shopping list
5. Group shopping items by store section
6. Provide rough nutrition estimates

## Grading Criteria

- [ ] meal_plan.md created with 7 days of meals
- [ ] Each day has breakfast, lunch, and dinner
- [ ] Meals respect dietary preferences/allergies
- [ ] shopping_list.md created with categorized items
- [ ] Shopping list items are deduplicated
- [ ] nutrition_estimate.json created with daily estimates
- [ ] Meal variety (not repetitive)

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    import json
    import re

    scores = {}
    workspace = Path(workspace_path)

    # Check meal plan
    plan = workspace / "meal_plan.md"
    if plan.exists():
        content = plan.read_text().lower()
        scores["plan_created"] = 1.0

        # Check for 7 days
        day_patterns = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                       "day 1", "day 2", "day 3", "day 4", "day 5", "day 6", "day 7",
                       "週一", "週二", "週三", "週四", "週五", "週六", "週日"]
        days_found = sum(1 for d in day_patterns if d in content)
        scores["has_7_days"] = 1.0 if days_found >= 7 else days_found / 7.0

        # Check for meal types
        meal_types = ["breakfast", "lunch", "dinner", "早餐", "午餐", "晚餐"]
        meals_found = sum(1 for m in meal_types if m in content)
        scores["has_meal_types"] = 1.0 if meals_found >= 3 else meals_found / 3.0
    else:
        scores["plan_created"] = 0.0
        scores["has_7_days"] = 0.0
        scores["has_meal_types"] = 0.0

    # Check shopping list
    shopping = workspace / "shopping_list.md"
    if shopping.exists():
        content = shopping.read_text().lower()
        scores["shopping_created"] = 1.0
        # Check for categories
        categories = ["produce", "protein", "dairy", "pantry", "蔬果", "肉類", "乳製品"]
        cats_found = sum(1 for c in categories if c in content)
        scores["shopping_categorized"] = 1.0 if cats_found >= 3 else cats_found / 3.0
    else:
        scores["shopping_created"] = 0.0
        scores["shopping_categorized"] = 0.0

    # Check nutrition estimates
    nutrition = workspace / "nutrition_estimate.json"
    if nutrition.exists():
        scores["nutrition_created"] = 1.0
        try:
            data = json.loads(nutrition.read_text())
            scores["nutrition_valid"] = 1.0
            # Check has daily entries
            entries = data if isinstance(data, list) else list(data.values()) if isinstance(data, dict) else []
            scores["nutrition_complete"] = 1.0 if len(entries) >= 7 else len(entries) / 7.0
        except (json.JSONDecodeError, Exception):
            scores["nutrition_valid"] = 0.0
            scores["nutrition_complete"] = 0.0
    else:
        scores["nutrition_created"] = 0.0
        scores["nutrition_valid"] = 0.0
        scores["nutrition_complete"] = 0.0

    return scores
```

## LLM Judge Rubric

### Criterion 1: Meal Quality & Variety (Weight: 40%)

**Score 1.0**: Diverse, realistic meals with no repetition. Nutritionally balanced across days. Respects all dietary constraints.
**Score 0.75**: Good variety with minor repetition or slight nutritional imbalance.
**Score 0.5**: Some variety but noticeable repetition or generic meal names.
**Score 0.25**: Highly repetitive or unrealistic meal suggestions.
**Score 0.0**: No meaningful meal plan.

### Criterion 2: Shopping List Practicality (Weight: 30%)

**Score 1.0**: Well-categorized, deduplicated, quantities included, organized for efficient shopping.
**Score 0.75**: Good list with minor organizational issues.
**Score 0.5**: List exists but poorly organized or has duplicates.
**Score 0.25**: Incomplete or impractical list.
**Score 0.0**: No shopping list.

### Criterion 3: Dietary Compliance (Weight: 30%)

**Score 1.0**: All meals comply with stated dietary preferences and allergies. Calorie targets respected.
**Score 0.75**: Mostly compliant with 1-2 minor deviations.
**Score 0.5**: Some meals violate dietary constraints.
**Score 0.25**: Dietary preferences largely ignored.
**Score 0.0**: Completely ignores preferences or includes allergens.
