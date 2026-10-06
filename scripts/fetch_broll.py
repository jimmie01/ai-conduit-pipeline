import urllib.request, json, os

headers = {"Authorization": os.environ.get("PEXELS_API_KEY", "")}
plan = json.load(open("scripts/current_video_plan.json"))
queries = [s["visual"] for s in plan["scenes"]]

os.makedirs("/tmp/clips", exist_ok=True)

for i, q in enumerate(queries):
    try:
        req = urllib.request.Request(
            f"https://api.pexels.com/videos/search?query={q}&orientation=portrait&per_page=1",
            headers=headers)
        data = json.load(urllib.request.urlopen(req, timeout=30))
        if data.get("videos"):
            url = data["videos"][0]["video_files"][0]["link"]
            urllib.request.urlretrieve(url, f"/tmp/clips/broll_{i}.mp4")
            print(f"✅ Broll{i}: {q}")
        else:
            print(f"⚠️ Broll{i}結果なし: {q}")
    except Exception as e:
        print(f"⚠️ Broll{i}失敗: {e}")
