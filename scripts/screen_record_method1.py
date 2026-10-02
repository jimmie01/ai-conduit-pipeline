import asyncio
from playwright.async_api import async_playwright
import subprocess, os, sys

TARGET_URL = os.environ.get("TARGET_URL", "https://github.com/webadderallorg/Recordly")

async def record():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            record_video_dir="/tmp/method1/",
            record_video_size={"width": 1080, "height": 1920},
            viewport={"width": 1080, "height": 1920}
        )
        page = await context.new_page()
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.evaluate("window.scrollTo(0, 500)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 1000)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(2000)
        await context.close()
        await browser.close()
        print("✅ Method1: Playwright録画完了")

asyncio.run(record())
