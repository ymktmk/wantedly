import csv
import os

class CompanyDatabase:
    """会社データベースクラス - CSVファイルからの読み込みと検索機能を提供"""
    
    def __init__(self, csv_file_path=None):
        """
        初期化
        
        Args:
            csv_file_path (str): CSVファイルのパス。Noneの場合はデフォルトファイルを使用
        """
        self.companies = {}
        self.csv_file_path = csv_file_path or self._get_default_csv_path()
        
    def _get_default_csv_path(self):
        """デフォルトのCSVファイルパスを取得"""
        return os.path.join(os.path.dirname(__file__), 'prefecture_split/東京都_00_zenkoku_all_20250630_filtered.csv')
    
    def load_data(self):
        """CSVファイルから会社データを読み込む"""
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    company_name = row['company']
                    self.companies[company_name] = {
                        'id': row['id'],
                        'code': row['code'],
                        'prefecture': row['prefecture'],
                        'date': row['date']
                    }
            print(f"✅ CSVファイルから{len(self.companies)}件の会社データを読み込みました")
            return True
        except FileNotFoundError:
            print(f"❌ CSVファイルが見つかりません: {self.csv_file_path}")
            return False
        except Exception as e:
            print(f"❌ CSVファイルの読み込み中にエラーが発生しました: {e}")
            return False
    
    def search_company(self, company_name):
        """
        会社を検索
        
        Args:
            company_name (str): 検索する会社名
            
        Returns:
            dict or list: 完全一致の場合は辞書、部分一致の場合はリスト、見つからない場合は空リスト
        """
        # 完全一致
        if company_name in self.companies:
            return self.companies[company_name]
        
        # 部分一致検索
        matches = []
        for name, data in self.companies.items():
            if company_name in name:
                matches.append((name, data))
        
        return matches
    
    def display_search_result(self, company_name, search_result):
        """
        検索結果を表示
        
        Args:
            company_name (str): 検索した会社名
            search_result: search_company()の結果
        """
        print("📊 CSV データベースからの情報:")
        if isinstance(search_result, dict):
            # 完全一致の場合
            print(f"   会社名: {company_name}")
            print(f"   ID: {search_result['id']}")
            print(f"   コード: {search_result['code']}")
            print(f"   都道府県: {search_result['prefecture']}")
            print(f"   登録日: {search_result['date']}")
        elif isinstance(search_result, list) and search_result:
            # 部分一致の場合
            print(f"   部分一致で{len(search_result)}件見つかりました:")
            for i, (name, data) in enumerate(search_result[:5], 1):  # 最大5件表示
                print(f"   {i}. {name} (ID: {data['id']}, {data['prefecture']})")
            if len(search_result) > 5:
                print(f"   ...他{len(search_result) - 5}件")
        else:
            print("   CSVデータベースに該当する会社が見つかりませんでした。")
    
    def get_company_count(self):
        """読み込まれた会社数を取得"""
        return len(self.companies)

# 便利関数
def create_company_database(csv_file_path=None):
    """
    会社データベースを作成し、データを読み込む
    
    Args:
        csv_file_path (str): CSVファイルのパス
        
    Returns:
        CompanyDatabase: 初期化されたデータベースインスタンス
    """
    db = CompanyDatabase(csv_file_path)
    db.load_data()
    return db 