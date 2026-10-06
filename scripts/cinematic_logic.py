#!/usr/bin/env python3
"""
Cinematic Logic Layer + Viral Structure Database
Layer2: 台本 → 映像監督レベルの指示に変換
Layer3: バイラル構造を台本に自動適用
"""
import os, json, urllib.request

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# =============================================
# LAYER 3: バイラル構造データベース
# =============================================
VIRAL_STRUCTURES = {
    "problem_solution": {
        "name": "問題→解決型",
        "description": "視聴者の痛みを突いて解決策を見せる",
        "best_for": ["ツール紹介", "AI", "開発"],
        "structure": [
            {"id": "hook",    "seconds": 3,  "role": "問いかけ or 驚きの事実", "example": "「○○に3時間かかってた？」"},
            {"id": "agitate", "seconds": 4,  "role": "問題を深堀り・共感", "example": "「エンジニアなら誰でも経験する...」"},
            {"id": "present", "seconds": 6,  "role": "解決策を見せる", "example": "「これを使えば30秒で終わる」"},
            {"id": "demo",    "seconds": 5,  "role": "実際の動作を見せる", "example": "画面録画・デモ"},
            {"id": "cta",     "seconds": 2,  "role": "行動を促す", "example": "「コメントにパスワードで...」"},
        ]
    },
    "reveal": {
        "name": "衝撃リビール型",
        "description": "最初に結果を見せて興味を引く",
        "best_for": ["新機能", "リリース", "比較"],
        "structure": [
            {"id": "hook",    "seconds": 2,  "role": "結果を先に見せる", "example": "「見てこれ、○○が...」"},
            {"id": "build",   "seconds": 5,  "role": "どうやったか説明", "example": "「実はこのツールを使った」"},
            {"id": "present", "seconds": 6,  "role": "詳細を見せる", "example": "機能説明・デモ"},
            {"id": "social",  "seconds": 3,  "role": "社会的証明", "example": "「スター数・ユーザー数」"},
            {"id": "cta",     "seconds": 4,  "role": "次のアクション", "example": "「試したい人はコメントに...」"},
        ]
    },
    "listicle": {
        "name": "リスト型",
        "description": "○選・○つの理由でテンポよく見せる",
        "best_for": ["まとめ", "比較", "Tips"],
        "structure": [
            {"id": "hook",    "seconds": 2,  "role": "数字でフック", "example": "「知らないと損する3つのこと」"},
            {"id": "item1",   "seconds": 4,  "role": "1つ目", "example": "最も驚くものを最初に"},
            {"id": "item2",   "seconds": 4,  "role": "2つ目", "example": "実用的なもの"},
            {"id": "item3",   "seconds": 4,  "role": "3つ目", "example": "締めとなるもの"},
            {"id": "cta",     "seconds": 2,  "role": "CTA", "example": "「保存して後で使って」"},
        ]
    }
}

# =============================================
# LAYER 2: Cinematic Logic Layer
# =============================================
CINEMATIC_PROMPT = """あなたはSNS動画の映像監督です。
以下のトピックと構造を受け取り、各シーンの映像指示を日本語で出力してください。

出力はJSON形式で：
{
  "title": "動画タイトル",
  "color_palette": {
    "primary": "#hex",
    "accent": "#hex", 
    "bg": "#hex"
  },
  "overall_mood": "映像の雰囲気（例：ダークテック・ミニマル・エネルギッシュ）",
  "scenes": [
    {
      "id": "scene_id",
      "seconds": 秒数,
      "camera": "カメラワーク（例：ドリーイン・クローズアップ・オーバーザショルダー）",
      "text_main": "メインテキスト（短く・インパクト重視）",
      "text_sub": "サブテキスト（補足説明）",
      "visual": "映像内容（Pexels検索キーワード英語）",
      "animation": "テキストアニメーション（例：フェードイン・スライドアップ・ズームイン）",
      "effect": "エフェクト（例：グリッチ・ビネット・グロー・なし）"
    }
  ],
  "tts_script": "ナレーション全文（自然な話し言葉・20秒分）"
}"""

def select_viral_structure(topic: str, topic_type: str = "ツール紹介") -> dict:
    """トピックに最適なバイラル構造を選択"""
    for key, structure in VIRAL_STRUCTURES.items():
        if topic_type in structure["best_for"]:
            return structure
    return VIRAL_STRUCTURES["reveal"]  # デフォルト

def apply_cinematic_logic(topic: str, structure: dict) -> dict:
    """Groq APIでCinematic Logic Layerを実行"""
    
    structure_text = json.dumps(structure["structure"], ensure_ascii=False)
    
    user_prompt = f"""
トピック: {topic}
構造タイプ: {structure["name"]} - {structure["description"]}
各シーン構造: {structure_text}

このトピックと構造に基づいて映像指示を生成してください。
SNS縦型動画（1080x1920）、合計15〜20秒、日本語コンテンツです。
"""

    payload = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": CINEMATIC_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }).encode()

    import subprocess
    result_raw = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://api.groq.com/openai/v1/chat/completions",
        "-H", f"Authorization: Bearer {GROQ_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload.decode()
    ], capture_output=True, text=True, timeout=30)
    result = json.loads(result_raw.stdout)
    
    content = result["choices"][0]["message"]["content"]
    
    # JSONを抽出
    import re
    json_match = re.search(r'\{[\s\S]*\}', content)
    if json_match:
        return json.loads(json_match.group())
    return {}

def generate_video_plan(topic: str, topic_type: str = "ツール紹介") -> dict:
    """メイン関数：トピック → 完全な動画プラン"""
    print(f"🎬 トピック: {topic}")
    
    # Layer3: バイラル構造選択
    structure = select_viral_structure(topic, topic_type)
    print(f"📐 構造: {structure['name']}")
    
    # Layer2: Cinematic Logic
    print("🎥 映像指示を生成中...")
    plan = apply_cinematic_logic(topic, structure)
    
    if plan:
        print(f"✅ 映像プラン生成完了")
        print(f"  タイトル: {plan.get('title')}")
        print(f"  ムード: {plan.get('overall_mood')}")
        print(f"  カラー: {plan.get('color_palette')}")
        print(f"  シーン数: {len(plan.get('scenes', []))}")
        return plan
    else:
        print("❌ 生成失敗")
        return {}

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "xAI Grok Bot - AIチャットボット"
    topic_type = sys.argv[2] if len(sys.argv) > 2 else "ツール紹介"
    
    plan = generate_video_plan(topic, topic_type)
    print("\n=== 生成された動画プラン ===")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
