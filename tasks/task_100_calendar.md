---
id: task_100_calendar
name: Calendar Event Search
category: calendar
grading_type: automated
timeout_seconds: 300
workspace_files:
  - source: calendar_export.ics
    dest: calendar.ics
---

## Prompt

workspace 裡有一個 calendar.ics 檔案，裡面包含多筆行事曆活動。請找出 2026 年 4 月的團隊聚餐相關約會，並將這個約會的所有細節列出。

找到後請：
1. 列出細節包括: 日期、時間、地點、費用、人數等
2. 將這些資訊整理成一封邀請信，寫入 invitation_email.md
3. 收件人: jaff_kuo@asus.com
4. 信件主旨: 聚餐邀請
5. 將該聚餐活動單獨轉為標準 ICS 格式，存為 event.ics
6. 使用你自己的信箱，將邀請信寄送給 jaff_kuo@asus.com

## Expected Behavior

The agent should:

1. 讀取 workspace 裡的 calendar.ics（180 筆活動）
2. 從中找到聚餐相關的約會（NAGOMI 共好活動）
3. 列出: 日期、時間、地點、費用、人數
4. 寫一封邀請信到 invitation_email.md，包含所有活動細節
5. 將聚餐活動單獨存成 event.ics（標準 ICS 格式）
6. 實際寄信給 jaff_kuo@asus.com

## Grading Criteria

- [ ] 聚餐 Event found from iCalendar (180 筆中找到正確的一筆)
- [ ] invitation_email.md 建立且包含活動細節（日期、時間、地點）
- [ ] 收件人 jaff_kuo@asus.com 出現在信件內容中
- [ ] 信件主旨包含「聚餐邀請」或「聚餐」
- [ ] event.ics 建立且為合法 ICS 格式
- [ ] (Bonus) 實際寄信給 jaff_kuo@asus.com

## Automated Checks

```python
def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the calendar search + email drafting task.

    Checks workspace files directly — no dependency on specific tool names.
    Works with any OpenClaw environment (native or Composio).
    """
    import re
    from pathlib import Path

    scores = {
        "event_found": 0.0,
        "email_created": 0.0,
        "recipient_correct": 0.0,
        "subject_correct": 0.0,
        "ics_created": 0.0,
        "email_sent_bonus": 0.0,
    }

    workspace = Path(workspace_path)

    # ── helpers ──
    def _flatten_text(obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            return " ".join(_flatten_text(i) for i in obj)
        if isinstance(obj, dict):
            return " ".join(_flatten_text(v) for v in obj.values())
        return str(obj)

    all_text = _flatten_text(transcript)

    # ── 1. event_found: agent found the NAGOMI dinner event ──
    event_keywords = ["聚餐", "共好", "NAGOMI", "nagomi"]
    event_detail_keywords = ["南京西路", "中山", "11:30", "15:00",
                             "4/17", "04/17", "4月17", "2026-04-17",
                             "1,380", "1380", "13人", "13 人"]

    has_event = any(kw in all_text for kw in event_keywords)
    detail_hits = sum(1 for kw in event_detail_keywords if kw in all_text)

    if has_event and detail_hits >= 3:
        scores["event_found"] = 1.0
    elif has_event and detail_hits >= 1:
        scores["event_found"] = 0.5
    elif has_event:
        scores["event_found"] = 0.25

    # ── 2. email_created: invitation_email.md exists with event details ──
    email_path = workspace / "invitation_email.md"
    if not email_path.exists():
        # Also check common alternatives
        for alt in ["invitation.md", "email.md", "invite.md",
                     "invitation_email.txt", "email.txt"]:
            alt_path = workspace / alt
            if alt_path.exists():
                email_path = alt_path
                break

    if email_path.exists():
        email_content = email_path.read_text(encoding="utf-8", errors="replace")
        email_lower = email_content.lower()

        # Check for event details in email
        email_detail_keywords = ["nagomi", "南京西路", "中山", "11:30", "15:00",
                                  "4/17", "04/17", "4月17", "2026-04-17",
                                  "日期", "時間", "地點",
                                  "date", "time", "location"]
        email_hits = sum(1 for kw in email_detail_keywords
                        if kw.lower() in email_lower)

        if email_hits >= 4:
            scores["email_created"] = 1.0
        elif email_hits >= 2:
            scores["email_created"] = 0.75
        elif email_hits >= 1:
            scores["email_created"] = 0.5
        else:
            scores["email_created"] = 0.25  # file exists but minimal content
    else:
        scores["email_created"] = 0.0

    # ── 3. recipient_correct: jaff_kuo@asus.com in email ──
    if email_path.exists():
        email_content = email_path.read_text(encoding="utf-8", errors="replace")
        if "jaff_kuo@asus.com" in email_content.lower():
            scores["recipient_correct"] = 1.0
        elif "jaff_kuo" in email_content.lower() or "asus.com" in email_content.lower():
            scores["recipient_correct"] = 0.5
    elif "jaff_kuo@asus.com" in all_text:
        scores["recipient_correct"] = 0.5

    # ── 4. subject_correct: 聚餐邀請 in email ──
    if email_path.exists():
        email_content = email_path.read_text(encoding="utf-8", errors="replace")
        if "聚餐邀請" in email_content:
            scores["subject_correct"] = 1.0
        elif "聚餐" in email_content and "邀請" in email_content:
            scores["subject_correct"] = 1.0
        elif "聚餐" in email_content:
            scores["subject_correct"] = 0.5
        elif "邀請" in email_content:
            scores["subject_correct"] = 0.5
    elif "聚餐邀請" in all_text:
        scores["subject_correct"] = 0.5

    # ── 5. ics_created: event.ics exists and is valid ICS format ──
    ics_path = workspace / "event.ics"
    if not ics_path.exists():
        # Check alternatives
        for alt in workspace.glob("*.ics"):
            if alt.name != "calendar.ics":  # skip the input file
                ics_path = alt
                break

    if ics_path.exists() and ics_path.name != "calendar.ics":
        ics_content = ics_path.read_text(encoding="utf-8", errors="replace")
        ics_upper = ics_content.upper()

        has_vcalendar = "BEGIN:VCALENDAR" in ics_upper and "END:VCALENDAR" in ics_upper
        has_vevent = "BEGIN:VEVENT" in ics_upper and "END:VEVENT" in ics_upper
        has_nagomi = any(kw.lower() in ics_content.lower()
                        for kw in ["nagomi", "共好", "聚餐"])

        if has_vcalendar and has_vevent and has_nagomi:
            scores["ics_created"] = 1.0
        elif has_vcalendar and has_vevent:
            scores["ics_created"] = 0.75
        elif has_vevent:
            scores["ics_created"] = 0.5
        elif "VCALENDAR" in ics_upper or "VEVENT" in ics_upper:
            scores["ics_created"] = 0.25
    else:
        scores["ics_created"] = 0.0

    # ── 6. email_sent_bonus: agent actually sent the email ──
    # Three-layer verification:
    #   1. Transcript: did agent attempt to send email with correct recipient?
    #   2. Tool result: did the send command succeed (no errors)?
    #   3. System check: is mailq empty (not stuck) and no bounce messages?
    import subprocess

    send_tool_keywords = [
        "mail ", "mail\t", "sendmail", "smtp",
        "gmail", "send_email", "GMAIL_SEND",
        "send-email", "send_mail",
    ]

    email_attempted = False
    send_result_ok = True  # assume ok unless we find errors

    for event in transcript:
        if not isinstance(event, dict):
            continue
        msg = event.get("message", event)
        role = msg.get("role", "")
        contents = msg.get("content", [])
        if not isinstance(contents, list):
            contents = [contents]

        for item in contents:
            if not isinstance(item, dict):
                continue

            # Check tool calls for send attempt
            if item.get("type") == "toolCall":
                name = (item.get("name", "") or "").lower()
                raw_args = item.get("arguments", {})
                if isinstance(raw_args, str):
                    args_text = raw_args
                elif isinstance(raw_args, dict):
                    args_text = _flatten_text(raw_args)
                else:
                    args_text = str(raw_args)
                combined = name + " " + args_text

                has_send_tool = any(kw in combined.lower() for kw in send_tool_keywords)
                has_recipient = "jaff_kuo@asus.com" in combined.lower()

                if has_send_tool and has_recipient:
                    email_attempted = True

                # Composio wrapper: check nested tools
                if name in ("composio_multi_execute_tool", "composio_remote_workbench"):
                    if isinstance(raw_args, dict):
                        tools_list = raw_args.get("tools", [])
                        for t in (tools_list if isinstance(tools_list, list) else []):
                            if isinstance(t, dict):
                                slug = (t.get("tool_slug", "") or "").upper()
                                if "GMAIL" in slug and "SEND" in slug:
                                    sub_text = _flatten_text(t.get("arguments", {}))
                                    if "jaff_kuo@asus.com" in sub_text.lower():
                                        email_attempted = True

            # Check tool results for errors
            if email_attempted and (role == "toolResult" or item.get("type") == "toolResult"):
                result_text = _flatten_text(
                    item.get("output", item.get("text", ""))
                ).lower()
                error_keywords = [
                    "error", "failed", "denied", "refused",
                    "authentication failed", "connection timed out",
                    "no route to host", "command not found",
                    "permission denied", "cannot send",
                ]
                if any(kw in result_text for kw in error_keywords):
                    send_result_ok = False

    # System-level checks: mailq and bounce messages
    mailq_ok = True
    no_bounce = True

    if email_attempted:
        # Check if mail queue has stuck messages for our recipient
        try:
            mq = subprocess.run(["mailq"], capture_output=True, text=True, timeout=5)
            if "jaff_kuo@asus.com" in mq.stdout:
                mailq_ok = False  # mail stuck in queue
        except Exception:
            pass  # can't check, assume ok

        # Check for bounce messages
        import os
        user = os.environ.get("USER", "")
        mailbox = Path(f"/var/mail/{user}")
        if mailbox.exists():
            try:
                bounce_content = mailbox.read_text(encoding="utf-8", errors="replace")
                # Look for recent bounce to our recipient
                if "jaff_kuo@asus.com" in bounce_content and "Action: failed" in bounce_content:
                    no_bounce = False
            except Exception:
                pass

    # Score based on all three layers
    if email_attempted and send_result_ok and mailq_ok and no_bounce:
        scores["email_sent_bonus"] = 1.0
    elif email_attempted and send_result_ok:
        scores["email_sent_bonus"] = 0.5  # sent but queue stuck or bounced
    elif email_attempted:
        scores["email_sent_bonus"] = 0.25  # attempted but command errored
    else:
        scores["email_sent_bonus"] = 0.0  # no attempt

    return scores
```
