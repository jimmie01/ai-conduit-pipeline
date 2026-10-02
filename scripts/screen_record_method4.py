import asyncio
from playwright.async_api import async_playwright
import os

TARGET_URL = os.environ.get("TARGET_URL", "https://github.com/webadderallorg/Recordly")

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1000)

        frame_idx = 0
        fps = 15

        for _ in range(fps):
            await page.screenshot(path=f"/tmp/method4/frames/frame_{frame_idx:04d}.png")
            frame_idx += 1
            await page.wait_for_timeout(66)

        total_scroll = 1500
        steps = fps * 4
        for step in range(steps):
            scroll_y = int(total_scroll * step / steps)
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await page.screenshot(path=f"/tmp/method4/frames/frame_{frame_idx:04d}.png")
            frame_idx += 1
            await page.wait_for_timeout(66)

        for _ in range(fps):
            await page.screenshot(path=f"/tmp/method4/frames/frame_{frame_idx:04d}.png")
            frame_idx += 1
            await page.wait_for_timeout(66)

        await browser.close()
        print(f"✅ Method4: {frame_idx}フレーム取得完了")

asyncio.run(capture())
