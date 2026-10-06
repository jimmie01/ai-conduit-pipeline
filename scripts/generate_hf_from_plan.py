import json, os, sys

plan = json.load(open("scripts/current_video_plan.json"))
scenes = plan["scenes"]
palette = plan["color_palette"]
primary = palette["primary"]
accent = palette["accent"]
bg = "#0a0a0f"

def make_scene(scene):
    sid = scene["id"]
    text_main = scene["text_main"].replace('"', '&quot;').replace("'", "&#39;")
    text_sub = scene.get("text_sub","").replace('"', '&quot;').replace("'", "&#39;")
    seconds = scene["seconds"]
    effect = scene.get("effect","")
    effect_css = "box-shadow:inset 0 0 120px rgba(0,0,0,0.8);" if "ビネット" in effect else ""
    glow_css = f"filter:drop-shadow(0 0 30px {primary});" if "グロー" in effect else ""
    return f"""<template>
<div id="{sid}" data-composition-id="{sid}" data-start="0" data-duration="{seconds}"
     data-width="1080" data-height="1920"
     style="position:relative;width:1080px;height:1920px;overflow:hidden;background:{bg};">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=block');
.vignette{{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 40%,rgba(0,0,0,0.9) 100%);pointer-events:none;{effect_css}{glow_css}}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:80px 80px;}}
.content{{position:absolute;top:50%;left:0;right:0;padding:0 80px;transform:translateY(-50%);text-align:center;opacity:0;}}
.text-main{{font-size:80px;font-weight:900;line-height:1.2;margin-bottom:32px;background:linear-gradient(180deg,#fff 0%,{primary} 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.text-sub{{font-size:40px;color:rgba(255,255,255,0.65);line-height:1.6;}}
.bar{{height:4px;background:linear-gradient(to right,{primary},{accent});border-radius:2px;margin:0 auto 40px;width:0;}}
</style>
<div class="grid"></div><div class="vignette"></div>
<div class="content" id="{sid}-c">
  <div class="bar" id="{sid}-bar"></div>
  <div class="text-main">{text_main}</div>
  {'<div class="text-sub">'+text_sub+'</div>' if text_sub else ''}
</div>
<script>
(function(){{
  const tl=gsap.timeline({{defaults:{{ease:"power3.out"}}}});
  tl.to("#{sid}-bar",{{width:240,duration:0.5}},0.1)
    .to("#{sid}-c",{{opacity:1,y:0,duration:0.7}},0.3);
  if(window.__timelines) window.__timelines["{sid}"]=tl;
}})();
</script>
</div>
</template>"""

total = sum(s["seconds"] for s in scenes)
offset = 0
clips = []
for i,s in enumerate(scenes):
    clips.append(f'<div class="clip" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" data-start="{offset}" data-duration="{s["seconds"]}" data-track-index="{i+1}"></div>')
    offset += s["seconds"]

index_html = f"""<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box;}}html,body{{width:1080px;height:1920px;overflow:hidden;background:#000;}}#root{{position:relative;width:1080px;height:1920px;}}.clip{{position:absolute;inset:0;}}</style>
<script>window.__timelines={{}};</script>
</head><body>
<div id="root" data-composition-id="answer-html-hook" data-start="0" data-width="1080" data-height="1920" data-duration="{total}">
  {" ".join(clips)}
</div></body></html>"""

os.makedirs("/tmp/hf_launch/compositions", exist_ok=True)
open("/tmp/hf_launch/index.html","w").write(index_html)
for s in scenes:
    open(f"/tmp/hf_launch/compositions/{s[\'id\']+\'.html\'}","w").write(make_scene(s))
print(f"✅ HF HTML生成完了 ({total}秒・{len(scenes)}シーン)")
