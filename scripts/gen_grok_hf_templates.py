#!/usr/bin/env python3
"""
56ユースケース用HyperFrames HTMLテンプレートを生成してGitHub APIでpushするスクリプト
"""
import json
import os
import base64
import time
import urllib.request
import urllib.error

PAT = os.environ["GITHUB_TOKEN"]
REPO = "jimmie01/ai-conduit-pipeline"
BASE_URL = f"https://api.github.com/repos/{REPO}/contents"

CATEGORY_COLORS = {
    "General":          {"bg": "#0a0a0a", "text": "#ffffff", "accent": "#00d4ff"},
    "Sales":            {"bg": "#0a0f1a", "text": "#ffffff", "accent": "#ff6b35"},
    "Marketing":        {"bg": "#0f0a1a", "text": "#ffffff", "accent": "#b44fff"},
    "Customer Success": {"bg": "#0a1a10", "text": "#ffffff", "accent": "#00ff88"},
    "Recruiting":       {"bg": "#1a0a0a", "text": "#ffffff", "accent": "#ff4488"},
    "Finance":          {"bg": "#0a1a15", "text": "#ffffff", "accent": "#00ffcc"},
    "Engineering":      {"bg": "#0a0f15", "text": "#ffffff", "accent": "#4488ff"},
    "Product":          {"bg": "#150a1a", "text": "#ffffff", "accent": "#ff88ff"},
    "Life":             {"bg": "#1a1a0a", "text": "#ffffff", "accent": "#ffdd00"},
}

CATEGORY_JA = {
    "General": "汎用",
    "Sales": "営業",
    "Marketing": "マーケティング",
    "Customer Success": "カスタマーサクセス",
    "Recruiting": "採用",
    "Finance": "財務",
    "Engineering": "エンジニアリング",
    "Product": "プロダクト",
    "Life": "ライフスタイル",
}

def make_composition_html(uc, scene_type):
    """各シーンのHTMLを生成"""
    name = uc['name']
    cat = uc['category']
    cat_ja = CATEGORY_JA.get(cat, cat)
    colors = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["General"])
    bg = colors["bg"]
    text = colors["text"]
    accent = colors["accent"]
    desc = uc.get('desc', '')

    if scene_type == "hook":
        main_text = f"Grok Bot<br>{name}"
        sub_text = f"#{cat_ja} #GrokBot #AI活用"
        badge = "新機能"
    elif scene_type == "problem":
        main_text = f"{cat_ja}の<br>課題を解決"
        sub_text = desc[:40] + "..." if len(desc) > 40 else desc
        badge = "PROBLEM"
    elif scene_type == "solution":
        main_text = f"Grok Botで<br>全自動化"
        sub_text = f"{name}が365日稼働"
        badge = "SOLUTION"
    elif scene_type == "demo":
        main_text = f"導入は<br>簡単3ステップ"
        sub_text = "x.ai/botで今すぐ無料体験"
        badge = "DEMO"
    else:  # cta
        main_text = "今すぐ試す"
        sub_text = "x.ai/bot"
        badge = "FREE"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: 1080px;
  height: 1920px;
  background: {bg};
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif;
  overflow: hidden;
  position: relative;
}}
.badge {{
  position: absolute;
  top: 120px;
  background: {accent};
  color: #000;
  font-size: 36px;
  font-weight: 900;
  padding: 12px 40px;
  border-radius: 50px;
  letter-spacing: 0.1em;
}}
.category {{
  position: absolute;
  top: 220px;
  font-size: 32px;
  color: {accent};
  opacity: 0.8;
  letter-spacing: 0.15em;
}}
.main-text {{
  font-size: 96px;
  font-weight: 900;
  color: {text};
  text-align: center;
  line-height: 1.2;
  padding: 0 60px;
  text-shadow: 0 0 40px {accent}80;
  animation: fadeIn 0.8s ease forwards;
}}
.accent-line {{
  width: 200px;
  height: 6px;
  background: {accent};
  margin: 40px auto;
  border-radius: 3px;
}}
.sub-text {{
  font-size: 48px;
  font-weight: 400;
  color: {accent};
  text-align: center;
  margin-top: 20px;
  padding: 0 80px;
  opacity: 0.9;
  animation: slideUp 1s ease 0.3s both;
}}
.grok-tag {{
  position: absolute;
  bottom: 180px;
  font-size: 34px;
  color: {text};
  opacity: 0.5;
  letter-spacing: 0.1em;
}}
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(30px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slideUp {{
  from {{ opacity: 0; transform: translateY(80px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
</style>
</head>
<body>
<div class="badge">{badge}</div>
<div class="category">#{cat_ja.upper()}</div>
<div class="main-text">{main_text}</div>
<div class="accent-line"></div>
<div class="sub-text">{sub_text}</div>
<div class="grok-tag">Powered by Grok Bot × xAI</div>
</body>
</html>"""


def make_index_html(uc):
    """index.htmlを生成"""
    slug = uc['id']
    name = uc['name']
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{slug}</title>
</head>
<body>
<script>
const compositions = ["hook","problem","solution","demo","cta"];
const durations = [3, 3, 3, 3, 3];
let idx = 0;
function loadNext() {{
  if(idx >= compositions.length) return;
  const iframe = document.createElement('iframe');
  iframe.src = "compositions/" + compositions[idx] + ".html";
  iframe.style.cssText = "width:1080px;height:1920px;border:none;position:fixed;top:0;left:0;";
  document.body.innerHTML = '';
  document.body.appendChild(iframe);
  setTimeout(() => {{ idx++; loadNext(); }}, durations[idx] * 1000);
}}
loadNext();
</script>
</body>
</html>"""


def get_file_sha(path):
    """ファイルの現在SHAを取得（存在しない場合はNone）"""
    url = f"{BASE_URL}/{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {PAT}",
        "Accept": "application/vnd.github.v3+json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get('sha')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def push_file(path, content, message):
    """ファイルをGitHub APIでpush"""
    sha = get_file_sha(path)
    url = f"{BASE_URL}/{path}"

    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode()
    }
    if sha:
        payload["sha"] = sha

    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"token {PAT}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result.get('commit', {}).get('sha', 'ok')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR {e.code}: {body[:200]}")
        return None


def main():
    usecases = json.load(open(os.environ.get('GROK_JSON','/tmp/grok_usecases.json')))
    scenes = ["hook", "problem", "solution", "demo", "cta"]

    total = 0
    errors = 0

    for i, uc in enumerate(usecases):
        slug = uc['id']
        print(f"[{i+1}/56] {slug}")

        # index.html
        path = f"hf_original/{slug}/index.html"
        result = push_file(path, make_index_html(uc), f"feat: add HF template for {slug}")
        if result:
            total += 1
            print(f"  ✅ index.html")
        else:
            errors += 1
        time.sleep(0.5)

        # compositions/
        for scene in scenes:
            path = f"hf_original/{slug}/compositions/{scene}.html"
            html = make_composition_html(uc, scene)
            result = push_file(path, html, f"feat: add {scene} scene for {slug}")
            if result:
                total += 1
            else:
                errors += 1
                print(f"  ❌ {scene}.html failed")
            time.sleep(0.3)

        print(f"  ✅ all scenes done ({total} files total)")

    print(f"\n=== DONE: {total} files pushed, {errors} errors ===")


if __name__ == "__main__":
    main()
