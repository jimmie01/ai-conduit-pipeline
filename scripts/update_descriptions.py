#!/usr/bin/env python3
"""全動画の概要欄冒頭にギフトページURLを追加"""
import os, requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

GIFT_LINE = "🎁 プロンプト66本を無料プレゼント中 → https://jimmie01.github.io\n\n"

def get_youtube():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
        "client_id": os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
    }, timeout=10)
    token = r.json()["access_token"]
    creds = Credentials(token=token)
    return build("youtube", "v3", credentials=creds)

def update_all():
    yt = get_youtube()
    videos = []
    req = yt.search().list(part="id", forMine=True, type="video", maxResults=50)
    while req:
        res = req.execute()
        videos += [i["id"]["videoId"] for i in res.get("items", [])]
        req = yt.search().list_next(req, res)

    print(f"Found {len(videos)} videos")
    for vid in videos:
        detail = yt.videos().list(part="snippet", id=vid).execute()
        if not detail["items"]: continue
        snippet = detail["items"][0]["snippet"]
        desc = snippet.get("description", "")
        if "jimmie01.github.io" in desc:
            print(f"SKIP {vid}")
            continue
        snippet["description"] = GIFT_LINE + desc
        yt.videos().update(part="snippet", body={"id": vid, "snippet": snippet}).execute()
        print(f"UPDATED {vid}: {snippet['title'][:40]}")

update_all()
