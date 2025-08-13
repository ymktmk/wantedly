import sys
import time
import random
import csv
from datetime import datetime
from company_finder import find_company_website, find_company_contact, find_company_industry
from postgresql_database import create_postgresql_database_with_url

def process_company(company_data, index, total, db):
    """個別の会社を処理してデータベースを更新する"""
    company_id = company_data['id']
    company_name = company_data['company']
    
    print(f"\n[{index}/{total}] 「{company_name}」(ID: {company_id})の情報:")
    print("=" * 50)
    
    # 更新用の辞書
    update_data = {}
    
    # 公式ホームページ、お問い合わせページ、業界情報を取得
    homepage_results = find_company_website(company_name)
    time.sleep(0.5)  # リクエスト間隔を開ける
    contact_results = find_company_contact(company_name)
    time.sleep(0.5)  # リクエスト間隔を開ける
    industry_results = find_company_industry(company_name)
    
    # 公式ホームページの表示・保存
    print("📱 公式ホームページ:")
    if not homepage_results:
        print("   見つかりませんでした。")
    else:
        result = homepage_results[0]
        print(f"   {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   説明: {result['description']}")
        update_data['homepage_url'] = result['url']
    
    # お問い合わせページの表示・保存
    print("✉️  お問い合わせページ:")
    if not contact_results:
        print("   見つかりませんでした。")
    else:
        result = contact_results[0]
        print(f"   {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   説明: {result['description']}")
        update_data['contact_url'] = result['url']
    
    # 業界・事業内容の表示・保存
    print("🏢 業界・事業内容:")
    if not industry_results:
        print("   見つかりませんでした。")
    else:
        result = industry_results[0]
        print(f"   {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   説明: {result['description']}")
        update_data['description'] = result['description']
    
    # データベースを更新
    if update_data:
        success = db.update_company_info(
            company_id=company_id,
            homepage_url=update_data.get('homepage_url'),
            contact_url=update_data.get('contact_url'),
            description=update_data.get('description')
        )
        if success:
            print("💾 データベースを更新しました")
        else:
            print("❌ データベースの更新に失敗しました")
    else:
        # 次回以降に同じレコードが再度選ばれ続けるのを防ぐため、空文字でマーク
        marked = db.update_company_info(company_id=company_id, homepage_url="")
        if marked:
            print("ℹ️  情報が見つからなかったため、homepage_urlを空文字でマークしました")
        else:
            print("ℹ️  情報が見つからず、マーク更新にも失敗しました")

if __name__ == "__main__":
    try:
        # SupabaseのPostgreSQLデータベースに接続
        db = create_postgresql_database_with_url()

        # print("homepage_urlが空の会社を、1件ずつ取得して処理します。")
        # input("処理を開始します。Enterキーを押してください...")

        processed_count = 0

        while True:
            # 1件だけ取得（毎回クエリ）
            companies = db.get_companies_without_homepage(limit=1, offset=0)

            if not companies:
                if processed_count == 0:
                    print("処理対象の会社がありません。終了します。")
                else:
                    print("\n🎉 処理完了！データベースの更新が完了しました。")
                break

            company_data = companies[0]

            try:
                # 合計件数は不定のためハイフン表示
                process_company(company_data, processed_count + 1, '-', db)
                processed_count += 1

                # 各会社の処理後に少し待機（API制限回避）
                wait_time = 0.1
                print(f"\n⏰ {wait_time:.1f}秒待機中...")
                time.sleep(wait_time)

            except KeyboardInterrupt:
                print(f"\n\n⚠️  処理が中断されました。{processed_count}件目まで処理済み。")
                break
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                print("次の会社の処理を続行します...")
                continue

    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        print("接続パラメータを確認してください")
    finally:
        # データベース接続を切断
        if 'db' in locals():
            db.disconnect()
