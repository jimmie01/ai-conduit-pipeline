import asyncio
import os
import json
import subprocess
from playwright.async_api import async_playwright

SAMPLE_NAME = os.environ.get("SAMPLE_NAME", "recordly-launch")
OUTPUT_DIR = "/tmp/screen_scenes"
FINAL_OUTPUT = "/tmp/final_screen_recording.mp4"

# viewport=540x960（狭い）→ 文字が大きく見える → 1080x1920に拡大
VIEWPORT_W = 540
VIEWPORT_H = 960
OUTPUT_W = 1080
OUTPUT_H = 1920

async def record_scene(page, scene, output_path):
    print(f"  録画中: {scene['id']} - {scene['description']}")
    
    for attempt in range(3):
        try:
            await page.goto(scene["url"], wait_until="domcontentloaded", timeout=60000)
            break
        except Exception as e:
            if attempt == 2:
                print(f"    ⚠️ {scene['id']} スキップ: {e}")
                return None
            print(f"    リトライ {attempt+1}/3...")
            await asyncio.sleep(2)
    
    await page.wait_for_timeout(2000)
    
    scroll_from = scene["scroll_from"]
    scroll_to = scene["scroll_to"]
    duration_sec = scene["duration_sec"]
    fps = 30
    total_frames = duration_sec * fps
    
    os.makedirs(output_path, exist_ok=True)
    
    for frame_idx in range(total_frames):
        if scroll_to > scroll_from:
            progress = frame_idx / total_frames
            current_scroll = int(scroll_from + (scroll_to - scroll_from) * progress)
        else:
            current_scroll = scroll_from
        
        await page.evaluate(f"window.scrollTo(0, {current_scroll})")
        await page.screenshot(
            path=f"{output_path}/frame_{frame_idx:04d}.png",
            full_page=False
        )
        await page.wait_for_timeout(int(1000 / fps))
    
    scene_mp4 = f"{output_path}/scene.mp4"
    subprocess.run([
        "ffmpeg", "-r", str(fps),
        "-i", f"{output_path}/frame_%04d.png",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={OUTPUT_W}:{OUTPUT_H}:flags=lanczos",
        "-b:v", "4M",
        scene_mp4, "-y"
    ], capture_output=True)
    
    size_kb = os.path.getsize(scene_mp4) // 1024
    print(f"    ✅ {scene['id']} 完了: {size_kb}KB")
    return scene_mp4

async def main():
    with open("scripts/screen_record_scenes.json") as f:
        all_scenes = json.load(f)
    
    sample_scenes = all_scenes.get(SAMPLE_NAME)
    if not sample_scenes:
        print(f"❌ {SAMPLE_NAME} のシーン設定が見つかりません")
        return
    
    scenes = sample_scenes["scenes"]
    print(f"✅ {SAMPLE_NAME}: {len(scenes)}シーンを録画します（viewport={VIEWPORT_W}x{VIEWPORT_H}→{OUTPUT_W}x{OUTPUT_H}）")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    scene_videos = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        page = await browser.new_page(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        
        for i, scene in enumerate(scenes):
            scene_dir = f"{OUTPUT_DIR}/scene_{i:02d}_{scene['id']}"
            mp4_path = await record_scene(page, scene, scene_dir)
            if mp4_path:
                scene_videos.append(mp4_path)
        
        await browser.close()
    
    if not scene_videos:
        print("❌ 録画できたシーンがありません")
        return
    
    print(f"\n{len(scene_videos)}シーンを結合中...")
    concat_file = f"{OUTPUT_DIR}/concat.txt"
    with open(concat_file, "w") as f:
        for v in scene_videos:
            f.write(f"file '{v}'\n")
    
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-pix_fmt", "yuv420p", "-b:v", "4M",
        FINAL_OUTPUT, "-y"
    ], capture_output=True)
    
    if os.path.exists(FINAL_OUTPUT):
        size = os.path.getsize(FINAL_OUTPUT) / 1024 / 1024
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration,bit_rate",
             "-of", "csv=p=0", FINAL_OUTPUT],
            capture_output=True, text=True
        )
        info = result.stdout.strip().split(",")
        duration = float(info[0])
        bitrate = int(info[1]) // 1000 if len(info) > 1 else 0
        print(f"\n✅ 最終動画完成: {size:.1f}MB, {duration:.1f}秒, {bitrate}kbps")
    else:
        print("❌ 最終動画の生成に失敗")

asyncio.run(main())
