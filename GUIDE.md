# PinchBench 操作指南

> Fork 自 [pinchbench/skill](https://github.com/pinchbench/skill)，由 CC 維護
> 最後更新：2026-03-25

---

## 目錄

1. [環境準備](#環境準備)
2. [跑測試](#跑測試)
3. [查看結果](#查看結果)
4. [人工評分](#人工評分)
5. [新增題目](#新增題目)
6. [修改題目](#修改題目)
7. [維護與同步](#維護與同步)

---

## 環境準備

### 必要工具

| 工具 | 安裝指令 |
|------|---------|
| Python 3.10+ | `brew install python@3.12` |
| uv 套件管理器 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| OpenClaw | 需要已在運行的 OpenClaw gateway |
| Git | `brew install git` |

### API Key 設定

OpenRouter API key 需要設定在兩個地方：

**1. 環境變數（benchmark 程式用）：**
```bash
export OPENROUTER_API_KEY="sk-or-v1-你的key"
# 或加到 ~/.zshrc 永久生效
```

**2. OpenClaw provider（agent 用）：**

在 `~/.openclaw/openclaw.json` 的 `models.providers` 裡加入：
```json
"openrouter": {
  "baseUrl": "https://openrouter.ai/api/v1",
  "apiKey": "sk-or-v1-你的key",
  "api": "openai-completions",
  "models": [{
    "id": "模型ID",
    "name": "模型名稱",
    "contextWindow": 128000,
    "maxTokens": 16384
  }]
}
```

### 確認免費模型可用

```bash
# 測試模型是否通（應回傳 JSON 結果，不是 error）
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "你的模型ID", "messages": [{"role": "user", "content": "hi"}]}'
```

---

## 跑測試

### 基本指令

```bash
cd /Users/cc/skill/scripts
source $HOME/.local/bin/env  # 載入 uv

# 跑單題（推薦先跑 sanity check）
uv run benchmark.py --model "openrouter/nvidia/nemotron-3-super-120b-a12b:free" \
  --suite task_00_sanity --no-upload

# 跑多題
uv run benchmark.py --model "openrouter/nvidia/nemotron-3-super-120b-a12b:free" \
  --suite task_01_calendar,task_02_stock,task_04_weather --no-upload

# 跑全部
uv run benchmark.py --model "openrouter/nvidia/nemotron-3-super-120b-a12b:free" \
  --no-upload

# 跑多輪取平均
uv run benchmark.py --model "openrouter/nvidia/nemotron-3-super-120b-a12b:free" \
  --runs 3 --no-upload

# 慢模型加 timeout
uv run benchmark.py --model "openrouter/nvidia/nemotron-3-super-120b-a12b:free" \
  --timeout-multiplier 2 --no-upload
```

### 常用參數

| 參數 | 說明 | 預設 |
|------|------|------|
| `--model` | 模型 ID（必填） | — |
| `--suite` | `all` / 逗號分隔的 task ID | all |
| `--runs N` | 每題跑幾輪 | 1 |
| `--timeout-multiplier` | timeout 倍數 | 1.0 |
| `--no-upload` | 不上傳排行榜 | 關 |
| `--output-dir` | 結果存放目錄 | results/ |

### 目前可用的免費模型

| 模型 ID | 大小 |
|---------|------|
| `nvidia/nemotron-3-super-120b-a12b:free` | 120B |
| `google/gemma-3-4b-it:free` | 4B |

> 注意：部分免費模型受 OpenRouter privacy policy 限制，需在 openrouter.ai/settings/privacy 調整

---

## 查看結果

### 結果檔案位置

```bash
ls scripts/results/
# 格式: {run_id}_{model_slug}.json
# 例: 0007_openrouter-nvidia-nemotron-3-super-120b-a12b:free.json
```

### 快速查看分數

```bash
# 用 python 看整體分數
python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
for t in d['tasks']:
    bd = t['grading']['runs'][0]['breakdown']
    print(f'{t[\"task_id\"]}: {t[\"grading\"][\"mean\"]*100:.0f}%')
    for k,v in bd.items():
        icon = '✅' if v >= 1.0 else '⚠️' if v > 0 else '❌'
        print(f'  {icon} {k}: {v}')
" results/你的結果.json
```

### 結果 JSON 結構

```
{
  "model": "模型ID",
  "run_id": "0007",
  "tasks": [
    {
      "task_id": "task_01_calendar",
      "status": "success",
      "execution_time": 27.8,          ← 耗時（秒）
      "usage": {
        "input_tokens": 68959,          ← 輸入 tokens
        "output_tokens": 1650,          ← 輸出 tokens
        "cost_usd": 0.0,               ← 費用
        "request_count": 3              ← API 呼叫次數
      },
      "grading": {
        "mean": 1.0,                    ← 平均分數
        "runs": [{
          "breakdown": {                ← 各項細節
            "file_created": 1.0,
            "date_correct": 1.0,
            ...
          }
        }]
      }
    }
  ],
  "efficiency": {                       ← 整體效率
    "total_tokens": {...},
    "total_api_requests": 20,
    "avg_tokens_per_task": 121684
  }
}
```

---

## 人工評分

自動評分只看「有沒有做到」，人工評分看「做得好不好」。

### 步驟 1：產生評分表

```bash
cd scripts/
python3 human_review.py generate results/你的結果.json
```

會產生 `results/你的結果_human_review.json`。

### 步驟 2：填寫評分

用編輯器打開 `_human_review.json`，每題填：

```json
{
  "human_score": 0.8,              // 整體分數 0.0~1.0
  "human_notes": "你的觀察備註",
  "human_breakdown": {
    "correctness": 1.0,            // 結果正確嗎
    "efficiency": 0.7,             // 過程有效率嗎（API call 次數、步驟多寡）
    "robustness": 0.6,             // 換個情境還行嗎
    "readability": 0.9             // 輸出好讀嗎
  }
}
```

### 步驟 3：查看對比

```bash
python3 human_review.py compare results/你的結果.json
```

輸出範例：
```
題目                     自動   人工   差異   備註
task_01_calendar        100%    90%   -10%  缺少時區設定
task_02_stock           100%    75%   -25%  摘要太短
```

### 怎麼判讀

| 差異 | 意思 | 行動 |
|------|------|------|
| 自動 100% 人工 < 80% | 自動評分有盲點 | 考慮加更嚴格的 automated check |
| 自動 < 50% 人工 > 80% | 自動評分太嚴 | 檢查 grading function 是否有 bug |
| 兩者都低 | 模型真的不行 | 換模型或 fine-tune |
| 兩者都高 | 沒問題 | 可以跳過不看 |

---

## 新增題目

### 步驟 1：建立 task 檔案

在 `tasks/` 目錄下新增 `.md` 檔案，命名格式：`task_XX_描述.md`

```markdown
---
id: task_31_my_new_task
name: My New Task
category: developer
grading_type: automated    # automated | llm_judge | hybrid
timeout_seconds: 180
workspace_files: []        # 如果需要輸入檔案，在這裡指定
---

## Prompt

（給 agent 的指令，要具體明確）

## Expected Behavior

（預期 agent 應該怎麼做）

## Grading Criteria

- [ ] 檢查項目 1
- [ ] 檢查項目 2

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    from pathlib import Path
    scores = {}
    workspace = Path(workspace_path)

    # 你的評分邏輯
    if (workspace / "output.txt").exists():
        scores["file_created"] = 1.0
    else:
        scores["file_created"] = 0.0

    return scores
```
```

### 步驟 2：如果需要輸入檔案

把 fixture 放在 `assets/` 目錄，在 frontmatter 指定：

```yaml
workspace_files:
  - source: assets/my_input.json
    dest: input.json
```

### 步驟 3：測試新題目

```bash
uv run benchmark.py --model "你的模型" --suite task_31_my_new_task --no-upload
```

### 評分方式選擇

| 方式 | 適合 | 優缺點 |
|------|------|--------|
| `automated` | 有明確對錯的任務（建檔案、寫程式） | 快、免費、客觀，但只看「有沒有」 |
| `llm_judge` | 需要判斷品質的任務（寫文章、設計） | 能看品質，但要花 judge 模型費用 |
| `hybrid` | 兩者都需要 | 最全面，成本也最高 |

---

## 修改題目

### 改題目內容

直接編輯 `tasks/task_XX_xxx.md`，修改 Prompt 或 Expected Behavior。

### 改評分標準

修改 `Automated Checks` 裡的 `grade()` 函式。常用模式：

```python
# 檢查檔案是否存在
scores["file_exists"] = 1.0 if (workspace / "output.txt").exists() else 0.0

# 檢查 JSON 是否合法
try:
    data = json.loads((workspace / "data.json").read_text())
    scores["valid_json"] = 1.0
except:
    scores["valid_json"] = 0.0

# 檢查內容包含關鍵字
content = (workspace / "report.md").read_text()
scores["has_keyword"] = 1.0 if "summary" in content.lower() else 0.0

# 部分給分
scores["completeness"] = min(1.0, len(items) / expected_count)
```

### 改 timeout

在 frontmatter 修改 `timeout_seconds`。慢模型可搭配 `--timeout-multiplier 2`。

---

## 維護與同步

### 同步上游更新

```bash
cd /Users/cc/skill
git fetch upstream
git merge upstream/main
# 如果有衝突，手動解決後 commit
```

### 推送到你的 GitHub

```bash
git add tasks/task_XX_new.md assets/new_fixture.json
git commit -m "新增 task_XX 測試題"
git push origin main
```

### 推送到公司 GitLab（如果有）

```bash
git remote add gitlab https://gitlab.公司.com/group/pinchbench.git
git push gitlab main
```

### 建議的維護習慣

1. **每次測試結果都 commit** — 在 `results/` 裡留紀錄
2. **人工評分也 commit** — `_human_review.json` 一起存
3. **題目有改就跑一次** — 確認 grading function 沒壞
4. **定期同步上游** — 拿到新的官方題目和 bug fix

---

## 快速參考

```bash
# 完整流程
cd /Users/cc/skill/scripts
source $HOME/.local/bin/env
export OPENROUTER_API_KEY="你的key"

# 1. 跑測試
uv run benchmark.py --model "openrouter/nvidia/nemotron-3-super-120b-a12b:free" \
  --suite task_00_sanity --no-upload

# 2. 產生人工評分表
python3 human_review.py generate results/最新結果.json

# 3. 填寫人工評分（用編輯器）
code results/最新結果_human_review.json

# 4. 查看對比
python3 human_review.py compare results/最新結果.json
```
