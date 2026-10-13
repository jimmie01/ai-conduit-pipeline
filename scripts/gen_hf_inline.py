#!/usr/bin/env python3
"""
Generate HyperFrames HTML templates locally (no GitHub API push needed).
Called from workflow: python3 scripts/gen_hf_inline.py <slug>
"""
import json, os, sys

slug = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SLUG", "")
if not slug:
    print("ERROR: slug required", file=sys.stderr)
    sys.exit(1)

data = json.load(open('scripts/grok_usecases.json'))
uc = next((u for u in data if u['id'] == slug), {})

name = uc.get('name', slug)
cat = uc.get('category', 'General')
desc = uc.get('desc', '')

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
    "General": "汎用", "Sales": "営業", "Marketing": "マーケティング",
    "Customer Success": "カスタマーサクセス", "Recruiting": "採用",
    "Finance": "財務", "Engineering": "エンジニアリング",
    "Product": "プロダクト", "Life": "ライフスタイル",
}

colors = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["General"])
bg, text_c, accent = colors["bg"], colors["text"], colors["accent"]
cat_ja = CATEGORY_JA.get(cat, cat)

scenes = {
    "hook":     {"main": f"Grok Bot<br>{name}", "sub": f"#{cat_ja} #GrokBot #AI活用", "badge": "新機能"},
    "problem":  {"main": f"{cat_ja}の<br>課題を解決", "sub": (desc[:40] + "...") if len(desc) > 40 else desc, "badge": "PROBLEM"},
    "solution": {"main": "Grok Botで<br>全自動化", "sub": f"{name}が365日稼働", "badge": "SOLUTION"},
    "demo":     {"main": "導入は<br>簡単3ステップ", "sub": "x.ai/botで今すぐ無料体験", "badge": "DEMO"},
    "cta":      {"main": "今すぐ試す", "sub": "x.ai/bot", "badge": "FREE"},
}

def make_html(s):
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: 1080px; height: 1920px;
  background: {bg};
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  font-family: 'Noto Sans JP', sans-serif; overflow: hidden;
  position: relative;
}}
.badge {{
  position: absolute; top: 120px;
  background: {accent}; color: #000;
  font-size: 36px; font-weight: 900;
  padding: 12px 40px; border-radius: 50px;
}}
.cat {{ position: absolute; top: 220px; font-size: 32px; color: {accent}; opacity: 0.8; }}
.main {{ font-size: 96px; font-weight: 900; color: {text_c}; text-align: center;
  line-height: 1.2; padding: 0 60px; text-shadow: 0 0 40px {accent}80; }}
.line {{ width: 200px; height: 6px; background: {accent}; margin: 40px auto; border-radius: 3px; }}
.sub {{ font-size: 48px; font-weight: 400; color: {accent}; text-align: center;
  margin-top: 20px; padding: 0 80px; }}
.footer {{ position: absolute; bottom: 180px; font-size: 34px; color: {text_c}; opacity: 0.5; }}
</style></head>
<body>
<div class="badge">{s["badge"]}</div>
<div class="cat">#{cat_ja.upper()}</div>
<div class="main">{s["main"]}</div>
<div class="line"></div>
<div class="sub">{s["sub"]}</div>
<div class="footer">Powered by Grok Bot x xAI</div>
</body></html>"""

os.makedirs(f"hf_original/{slug}/compositions", exist_ok=True)
os.makedirs(f"hf_original/{slug}/assets", exist_ok=True)

for scene_name, s_data in scenes.items():
    path = f"hf_original/{slug}/compositions/{scene_name}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(make_html(s_data))
    print(f"✅ {scene_name}.html")

index_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{slug}</title></head>
<body style="margin:0">
<script>
const scenes = ["hook","problem","solution","demo","cta"];
const durations = [3000,3000,3000,3000,3000];
let i = 0;
function next() {{
  if(i >= scenes.length) return;
  document.body.innerHTML = '<iframe src="compositions/' + scenes[i] + '.html" style="width:1080px;height:1920px;border:none"></iframe>';
  const d = durations[i]; i++;
  setTimeout(next, d);
}}
next();
</script></body></html>"""

with open(f"hf_original/{slug}/index.html", "w") as f:
    f.write(index_html)

print(f"✅ All templates generated for {slug}")
