import asyncio, edge_tts, json, os

plan = json.load(open("scripts/current_video_plan.json"))
tts_script = plan["tts_script"]

async def main():
    tts = edge_tts.Communicate(tts_script, "ja-JP-NanamiNeural")
    await tts.save("/tmp/narration.mp3")

asyncio.run(main())
print("✅ TTS生成完了")
