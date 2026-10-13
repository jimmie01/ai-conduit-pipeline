#!/usr/bin/env python3
"""Direct YouTube upload - no exec(), no external scripts"""
import requests, os, sys

slug = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SLUG", "")
if not slug:
    print("ERROR: slug required", file=sys.stderr)
    sys.exit(1)

title_file = "/tmp/video_title.txt"
desc_file = "/tmp/video_description.txt"

title = open(title_file).read().strip() if os.path.exists(title_file) else f"Grok Bot {slug} 解説 #GrokBot #AI活用 #Shorts"
description = open(desc_file).read().strip() if os.path.exists(desc_file) else f"Grok Botの{slug}機能を解説。\n\n#GrokBot #xAI #AI活用 #自動化"
description += "\n\n✅ x.ai/botで無料体験"

print(f"Title: {title[:80]}")

# OAuth2 access token
r = requests.post("https://oauth2.googleapis.com/token", data={
    "grant_type": "refresh_token",
    "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
    "client_id": os.environ["YOUTUBE_CLIENT_ID"],
    "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
})
token_data = r.json()
token = token_data.get("access_token", "")
if not token:
    print(f"ERROR: token failed: {token_data}")
    sys.exit(1)
print("✅ token ok")

# Video metadata
metadata = {
    "snippet": {
        "title": title[:100],
        "description": description[:5000],
        "tags": ["GrokBot", "xAI", "AI活用", "自動化", "AIエージェント", "生産性向上", "Shorts"],
        "categoryId": "28",
        "defaultLanguage": "ja"
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False
    }
}

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Get resumable upload URL
r2 = requests.post(
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    headers=headers, json=metadata
)
upload_url = r2.headers.get("Location", "")
if not upload_url:
    print(f"ERROR: upload URL failed: {r2.status_code} {r2.text[:300]}")
    sys.exit(1)
print("✅ upload URL ok")

# Upload video
with open("output.mp4", "rb") as f:
    video_data = f.read()
print(f"Video size: {len(video_data)//1024//1024}MB")

r3 = requests.put(upload_url, data=video_data, headers={"Content-Type": "video/mp4"})
result = r3.json()
video_id = result.get("id", "")
if video_id:
    print(f"✅ YouTube投稿成功: https://youtube.com/shorts/{video_id}")
    print(f"Title: {title}")
else:
    print(f"ERROR: upload failed: {r3.status_code} {r3.text[:400]}")
    sys.exit(1)
