#!/usr/bin/env python3
"""Setup usecase info - called from GitHub Actions"""
import json, os, sys

slug = os.environ.get("SLUG", "")
if not slug:
    print("ERROR: SLUG env var not set", file=sys.stderr)
    sys.exit(1)

data = json.load(open('scripts/grok_usecases.json'))
uc = next((u for u in data if u['id'] == slug), None)

if not uc:
    print(f"ERROR: {slug} not found in grok_usecases.json", file=sys.stderr)
    sys.exit(1)

name = uc['name']
cat = uc['category']
desc = uc.get('desc', '')

CATEGORY_JA = {
    "General": "汎用", "Sales": "営業", "Marketing": "マーケティング",
    "Customer Success": "カスタマーサクセス", "Recruiting": "採用",
    "Finance": "財務", "Engineering": "エンジニアリング",
    "Product": "プロダクト", "Life": "ライフスタイル",
}
cat_ja = CATEGORY_JA.get(cat, cat)

github_output = os.environ.get('GITHUB_OUTPUT', '')
if github_output:
    with open(github_output, 'a') as f:
        f.write(f"name={name}\n")
        f.write(f"category={cat}\n")
        f.write(f"cat_ja={cat_ja}\n")

input_title = os.environ.get('INPUT_TITLE', '').strip()
title = input_title if input_title else f"Grok Bot「{name}」の使い方 #GrokBot #AI活用 #自動化"

with open('/tmp/video_title.txt', 'w') as f:
    f.write(title)

description = f"""Grok Botの「{name}」機能を解説します。

{desc}

✅ x.ai/botで無料体験できます

#GrokBot #xAI #AI活用 #{cat_ja} #自動化 #生産性向上 #AIアシスタント"""

with open('/tmp/video_description.txt', 'w') as f:
    f.write(description)

print(f"✅ {name} ({cat_ja}) ready")
print(f"Title: {title}")
