#!/usr/bin/env python3
"""Issueフォームの本文を読み取り、data/groups.json に追加・更新する。
使い方: python scripts/apply_issue.py  （環境変数 ISSUE_BODY に本文を入れる）
"""
import json, os, re, sys, datetime

path = os.path.join(os.path.dirname(__file__), "..", "data", "groups.json")
body = os.environ.get("ISSUE_BODY", "")

LABELS = {
    "部門": "type",
    "グループ名 / ソロの活動名": "name",
    "グループ名": "name",
    "Xアカウント（@は不要）": "x",
    "YouTubeチャンネルURL（あれば）": "youtube",
    "主な活動エリア": "area",
    "メンバー数（人）※グループのみ": "members",
    "メンバー数（人）": "members",
    "結成年・活動開始年（西暦）": "formedYear",
    "結成年（西暦）": "formedYear",
    "Xフォロワー数（確認した数字）": "xFollowers",
    "YouTube登録者数（確認した数字）": "ytSubscribers",
}

fields = {}
for block in re.split(r"^### ", body, flags=re.M)[1:]:
    head, _, val = block.partition("\n")
    key = LABELS.get(head.strip())
    val = val.strip()
    if key and val and val != "_No response_":
        fields[key] = val

def to_int(v):
    v = re.sub(r"[^\d]", "", v or "")
    return int(v) if v else None

name = fields.get("name")
x = (fields.get("x") or "").lstrip("@").strip()
if not name or not re.fullmatch(r"[A-Za-z0-9_]{1,15}", x):
    print("グループ名またはXアカウントが不正です", file=sys.stderr)
    sys.exit(1)

yt = fields.get("youtube")
if yt and not re.match(r"^https://(www\.)?youtube\.com/", yt):
    yt = None

kind = "solo" if fields.get("type") == "ソロ" else "group"

entry = {
    "type": kind,
    "name": name,
    "x": x,
    "youtube": yt,
    "area": fields.get("area"),
    "members": None if kind == "solo" else to_int(fields.get("members")),
    "formedYear": to_int(fields.get("formedYear")),
    "xFollowers": to_int(fields.get("xFollowers")),
    "ytSubscribers": to_int(fields.get("ytSubscribers")),
}

with open(path, encoding="utf-8") as f:
    data = json.load(f)

groups = data.setdefault("groups", [])
for g in groups:
    if g["x"].lower() == x.lower():
        for k, v in entry.items():
            if v is not None:
                g[k] = v
        break
else:
    groups.append(entry)

data["updatedAt"] = datetime.date.today().isoformat()
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"反映しました: {name} (@{x})")
