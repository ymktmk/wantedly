import sys
import time
import random
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from company_finder import find_company_website, find_company_contact, find_company_industry
from postgresql_database import create_postgresql_database_with_url

# スレッドセーフなカウンターとロック
processed_counter = 0
print_lock = Lock()

def process_company(company_data, index, total, db):
    """個別の会社を処理してデータベースを更新する"""
    global processed_counter
    
    company_id = company_data['id']
    company_name = company_data['company_name']
    
    with print_lock:
        print(f"\n[{index}/{total}] 「{company_name}」(ID: {company_id})の情報:")
        print("=" * 50)
    
    # 更新用の辞書
    update_data = {}
    
    # 公式ホームページ、お問い合わせページ、業界情報を取得
    # homepage_results = find_company_website(company_name)
    # time.sleep(random.uniform(0.5, 1))  # リクエスト間隔を開ける
    # contact_results = find_company_contact(company_name)
    # time.sleep(random.uniform(0.5, 1))  # リクエスト間隔を開ける
    industry_results = find_company_industry(company_name)
    
    # 公式ホームページの表示・保存
    # print("📱 公式ホームページ:")
    # if not homepage_results:
    #     print("   見つかりませんでした。")
    # else:
    #     result = homepage_results[0]
    #     print(f"   {result['title']}")
    #     print(f"   URL: {result['url']}")
    #     print(f"   説明: {result['description']}")
    #     update_data['homepage_url'] = result['url']
    
    # # お問い合わせページの表示・保存
    # print("✉️  お問い合わせページ:")
    # if not contact_results:
    #     print("   見つかりませんでした。")
    # else:
    #     result = contact_results[0]
    #     print(f"   {result['title']}")
    #     print(f"   URL: {result['url']}")
    #     print(f"   説明: {result['description']}")
    #     update_data['contact_url'] = result['url']
    
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
        with print_lock:
            if success:
                print("💾 データベースを更新しました")
            else:
                print("❌ データベースの更新に失敗しました")
    else:
        # 次回以降に同じレコードが再度選ばれ続けるのを防ぐため、空文字でマーク
        marked = db.update_company_info(company_id=company_id, homepage_url="")
        with print_lock:
            if marked:
                print("ℹ️  情報が見つからなかったため、homepage_urlを空文字でマークしました")
            else:
                print("ℹ️  情報が見つからず、マーク更新にも失敗しました")
    
    global processed_counter
    with print_lock:
        processed_counter += 1
    
    return company_id

if __name__ == "__main__":
    try:
        # SupabaseのPostgreSQLデータベースに接続
        db = create_postgresql_database_with_url()

        # print("homepage_urlが空の会社を、1件ずつ取得して処理します。")
        # input("処理を開始します。Enterキーを押してください...")

        # 並列処理の設定
        max_workers = 3  # 同時実行スレッド数（API制限を考慮）
        batch_size = 10  # バッチサイズ

        print(f"並列処理開始（最大{max_workers}スレッド、バッチサイズ{batch_size}）")

        while True:
            # バッチで取得
            companies = db.get_companies_without_description(limit=batch_size, offset=0)
            if not companies:
                if processed_counter == 0:
                    print("処理対象の会社がありません。終了します。")
                else:
                    print(f"\n🎉 処理完了！{processed_counter}件のデータベース更新が完了しました。")
                break

            print(f"\n📦 {len(companies)}件のバッチを並列処理中...")
            
            try:
                # ThreadPoolExecutorで並列処理
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # 各会社の処理を並列実行
                    future_to_company = {
                        executor.submit(process_company, company, i+1, len(companies), db): company 
                        for i, company in enumerate(companies)
                    }
                    
                    # 完了を待機
                    completed_in_batch = 0
                    for future in as_completed(future_to_company):
                        company = future_to_company[future]
                        try:
                            company_id = future.result()
                            completed_in_batch += 1
                        except Exception as e:
                            with print_lock:
                                print(f"\n❌ 会社ID {company['id']} でエラー: {e}")
                
                with print_lock:
                    print(f"\n✅ バッチ完了: {completed_in_batch}/{len(companies)}件処理")
                    print(f"📊 総処理件数: {processed_counter}件")

                # バッチ間の待機（API制限回避）
                wait_time = 1.0
                print(f"\n⏰ 次のバッチまで{wait_time:.1f}秒待機...")
                time.sleep(wait_time)

            except KeyboardInterrupt:
                print(f"\n\n⚠️  処理が中断されました。{processed_counter}件処理済み。")
                break
            except Exception as e:
                print(f"\n❌ バッチ処理でエラー: {e}")
                print("次のバッチを続行します...")
                continue

    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        print("接続パラメータを確認してください")
    finally:
        # データベース接続を切断
        if 'db' in locals():
            db.disconnect()
