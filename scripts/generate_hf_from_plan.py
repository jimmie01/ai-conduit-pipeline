#!/usr/bin/env python3
import json, os, sys

PLAN_PATH = os.environ.get("PLAN_PATH", "scripts/current_video_plan.json")
OUT_DIR = "/tmp/hf_launch/compositions"
os.makedirs(OUT_DIR, exist_ok=True)

def make_scene(scene):
    sid = scene.get("id", "scene")
    text_main = scene.get("text_main", "")
    text_sub = scene.get("text_sub", "")
    color = scene.get("color_palette", {})
    if isinstance(color, dict):
        bg = color.get("bg", "#0a0a0a")
        tc = color.get("text", "#ffffff")
        ac = color.get("accent", "#00d4ff")
    else:
        bg, tc, ac = "#0a0a0a", "#ffffff", "#00d4ff"
    sub_block = ""
    if text_sub:
        sub_block = "<div class=\"sub\">" + text_sub + "</div>"
    return (
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><style>"
        "* { margin:0; padding:0; box-sizing:border-box; }"
        "body { width:1080px; height:1920px; background:" + bg + ";"
        " display:flex; flex-direction:column; align-items:center;"
        " justify-content:center; font-family:'Noto Sans JP',sans-serif; }"
        ".main { font-size:88px; font-weight:900; color:" + tc + ";"
        " text-align:center; padding:0 60px; line-height:1.2;"
        " text-shadow:0 0 40px " + ac + "80; }"
        ".line { width:200px; height:6px; background:" + ac + ";"
        " margin:40px auto; border-radius:3px; }"
        ".sub { font-size:48px; color:" + ac + ";"
        " text-align:center; padding:0 80px; }"
        "</style></head><body>"
        "<div class=\"main\">" + text_main + "</div>"
        "<div class=\"line\"></div>"
        + sub_block +
        "</body></html>"
    )

def main():
    if not os.path.exists(PLAN_PATH):
        print("ERROR: " + PLAN_PATH + " not found", file=sys.stderr)
        sys.exit(1)
    with open(PLAN_PATH, encoding="utf-8") as f:
        plan = json.load(f)
    scenes = plan.get("scenes", [])
    if not scenes:
        print("ERROR: no scenes", file=sys.stderr); sys.exit(1)
    for i, scene in enumerate(scenes):
        sid = scene.get("id", "scene_" + str(i))
        out = os.path.join(OUT_DIR, sid + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(make_scene(scene))
        print("Generated: " + out)
    print("Total: " + str(len(scenes)))
    with open("/tmp/hf_launch/scene_ids.txt", "w") as f:
        f.write("\n".join(s.get("id","") for s in scenes) + "\n")
    print("Done")

if __name__ == "__main__":
    main()
