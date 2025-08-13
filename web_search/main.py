import os
from openai import OpenAI

def search_talent():
    """指定ジャンルに最適なタレントを検索する"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    if not os.getenv("OPENAI_API_KEY"):
        print("エラー: OPENAI_API_KEY 環境変数が設定されていません")
        return
    
    try:
        response = client.responses.create(
            model="gpt-4o",
            tools=[
                {
                    "type": "web_search",
                    "user_location": {
                        "type": "approximate",
                        "country": "JP",
                        "region": "Tokyo",
                    },
                    # "search_params": {
                    #     "num_results": 5,
                    #     "include_domains": ["https://manzaigekijyo.yoshimoto.co.jp/profile"]
                    # }
                },
            ],
            temperature=0,
            input=f"""渋谷109前広場でのJK向けイベント「Shibuya Girls Festival 2025」の出演者選定について相談です。

【イベント概要】
- 開催日時：2025年10月の土日、13:00-17:00
- 会場：渋谷109前 イベントスペース（屋外ステージ）
- 収容人数：立ち見含め800人程度
- 予算：1出演者あたり30-100万円
- 主催：ファッションブランド×ショッピングモール

【ターゲット層】
- メイン：現役JK（15-18歳）
- サブ：女子大生・20代前半女性
- 渋谷・原宿によく来る「今どき女子」
- TikTok、Instagram、YouTube視聴層

【イベントの特徴】
- 通りがかりの人も気軽に参加できるオープンな雰囲気
- インスタ映え・TikTok映えする演出
- 観客との距離が近い、親近感重視
- ショッピングとの連動性（グッズ販売、コラボ商品等）

【質問】
上記条件に最適な日本人タレント・インフルエンサー10組を、以下の情報とともに教えてください。
また、その理由も教えてください。

1. 名前・グループ名
2. SNSのURL
3. 推薦理由（なぜ渋谷JKイベントに最適か）
4. 想定出演料
5. メインプラットフォーム（TikTok/Instagram/YouTube等）
6. 代表的なバズコンテンツ・話題性
7. 提案企画内容（トークショー/ダンス/ファッションショー/撮影会等）
8. 集客力・話題性の見込み
9. 渋谷・原宿での知名度
10. コラボ・タイアップ実績
11. リスク要因があれば

【希望ジャンル】
TikToker、美容系YouTuber、ファッションモデル、アイドル、ダンサー、インフルエンサーなど、JKのトレンドを押さえた人選でお願いします。
検索結果で取得したファクトのみをOutputで出力してください（創作一切禁止）。加えて、実際の検索したURLも付与すること。
""",
        )
        
        print(response.output_text)
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    search_talent()
