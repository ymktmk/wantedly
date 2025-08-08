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
    time.sleep(random.uniform(1, 2))  # リクエスト間隔を開ける
    contact_results = find_company_contact(company_name)
    time.sleep(random.uniform(1, 2))  # リクエスト間隔を開ける
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
        print("ℹ️  更新する情報が見つからなかったため、データベースは更新されませんでした")

if __name__ == "__main__":
    try:
        # SupabaseのPostgreSQLデータベースに接続
        db = create_postgresql_database_with_url()
        
        # homepage_urlが空の会社数を取得
        total_companies = db.get_companies_without_homepage_count()
        print(f"homepage_urlが空の会社が{total_companies}件見つかりました")
        
        if total_companies == 0:
            print("処理対象の会社がありません。終了します。")
            exit()
        
        # 取得開始位置の設定
        start_index = input(f"開始位置を入力してください（1-{total_companies}、最初から開始する場合はEnter）: ").strip()
        if start_index and start_index.isdigit():
            start_index = max(1, min(int(start_index), total_companies)) - 1  # 0ベースのインデックスに変換
            print(f"{start_index + 1}番目の会社から開始します")
        else:
            start_index = 0
            print("最初の会社から開始します")
        
        # 取得件数の設定
        remaining_companies = total_companies - start_index
        max_companies = input(f"処理する会社数を入力してください（1-{remaining_companies}、残り全て処理する場合はEnter）: ").strip()
        if max_companies and max_companies.isdigit():
            max_companies = min(int(max_companies), remaining_companies)
            print(f"{start_index + 1}番目から{max_companies}件の会社を処理します")
        else:
            max_companies = remaining_companies
            print(f"{start_index + 1}番目から残り全ての会社を処理します")
        
        print("homepage_urlが空の会社のみを対象に、データベースの特定フィールド（homepage_url、contact_url、description）を更新します")
        
        input("処理を開始します。Enterキーを押してください...")
        
        # homepage_urlが空の会社データを取得
        companies = db.get_companies_without_homepage(limit=max_companies, offset=start_index)
        
        # 各会社を順番に処理
        for i, company_data in enumerate(companies):
            try:
                process_company(company_data, i+1, len(companies), db)
                
                # 各会社の処理後に少し待機（API制限回避）
                if i < len(companies) - 1:  # 最後の会社でない場合
                    wait_time = random.uniform(2, 4)
                    print(f"\n⏰ {wait_time:.1f}秒待機中...")
                    time.sleep(wait_time)
                    
            except KeyboardInterrupt:
                print(f"\n\n⚠️  処理が中断されました。{i+1}件目まで処理済み。")
                break
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                print("次の会社の処理を続行します...")
                continue
        
        print(f"\n🎉 処理完了！データベースの更新が完了しました。")
        
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        print("接続パラメータを確認してください")
    finally:
        # データベース接続を切断
        if 'db' in locals():
            db.disconnect()
