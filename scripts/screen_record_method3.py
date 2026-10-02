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

        scenes = [
            (0, 0, 3),
            (0, 500, 3),
            (0, 1000, 3),
            (0, 0, 2),
        ]

        frame_idx = 0
        for scroll_x, scroll_y, duration_sec in scenes:
            await page.evaluate(f"window.scrollTo({scroll_x}, {scroll_y})")
            await page.wait_for_timeout(300)
            for f in range(duration_sec * 5):
                await page.screenshot(
                    path=f"/tmp/method3/frames/frame_{frame_idx:04d}.png",
                    full_page=False
                )
                frame_idx += 1
                await page.wait_for_timeout(200)

        await browser.close()
        print(f"✅ Method3: {frame_idx}フレーム取得完了")

asyncio.run(capture())
