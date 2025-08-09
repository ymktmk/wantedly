import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Dict, List, Optional, Union

class PostgreSQLCompanyDatabase:
    """PostgreSQLベースの会社データベースクラス"""
    
    def __init__(self, connection_info: Union[str, Dict[str, str]] = None):
        """
        初期化
        
        Args:
            connection_info: PostgreSQL接続情報（URLまたは接続パラメータ辞書）
        """
        self.connection_info = connection_info or self._get_default_connection_info()
        self.connection = None
        
    def _get_default_connection_info(self):
        """デフォルトの接続情報を取得（環境変数から）"""
        # まずDATABASE_URLを確認
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return database_url
        
        # 個別のパラメータを確認
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'company_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
    
    def connect(self):
        """データベースに接続"""
        try:
            if isinstance(self.connection_info, str):
                # URL形式で接続
                self.connection = psycopg2.connect(self.connection_info)
            else:
                # 辞書形式で接続
                self.connection = psycopg2.connect(**self.connection_info)
            
            print("✅ PostgreSQLデータベースに接続しました")
            return True
        except psycopg2.Error as e:
            print(f"❌ データベース接続エラー: {e}")
            return False
    
    def disconnect(self):
        """データベース接続を切断"""
        if self.connection:
            self.connection.close()
            print("🔌 データベース接続を切断しました")
    
    def get_companies_without_homepage(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """
        homepage_urlが空の会社データを取得
        
        Args:
            limit: 取得件数制限
            offset: 開始位置
            
        Returns:
            会社データのリスト
        """
        if not self.connection:
            raise Exception("データベースに接続されていません")
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # homepage_urlが空（NULL または空文字列）の会社を取得
                query = """
                    SELECT id, company, code, prefecture, date, homepage_url, contact_url, description
                    FROM companies
                    WHERE homepage_url IS NULL AND contact_url IS NULL AND description IS NULL
                    ORDER BY RANDOM()
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                if offset:
                    query += f" OFFSET {offset}"
                
                cursor.execute(query)
                companies = cursor.fetchall()
                
                print(f"✅ homepage_urlが空の会社{len(companies)}件をデータベースから取得しました")
                return [dict(company) for company in companies]
                
        except psycopg2.Error as e:
            print(f"❌ データベース取得エラー: {e}")
            return []
    
    def update_company_info(self, company_id: int, homepage_url: str = None, 
                           contact_url: str = None, description: str = None) -> bool:
        """
        会社の情報を更新（homepage_url、contact_url、descriptionのみ）
        
        Args:
            company_id: 会社ID
            homepage_url: ホームページURL
            contact_url: お問い合わせURL
            description: 事業内容説明
            
        Returns:
            更新成功かどうか
        """
        if not self.connection:
            raise Exception("データベースに接続されていません")
        
        try:
            with self.connection.cursor() as cursor:
                # 更新するフィールドと値を動的に構築
                update_fields = []
                values = []
                
                if homepage_url is not None:
                    update_fields.append("homepage_url = %s")
                    values.append(homepage_url)
                
                if contact_url is not None:
                    update_fields.append("contact_url = %s")
                    values.append(contact_url)
                
                if description is not None:
                    update_fields.append("description = %s")
                    values.append(description)
                
                if not update_fields:
                    return False  # 更新する項目がない
                
                # WHERE句用のIDを追加
                values.append(company_id)
                
                query = f"""
                    UPDATE companies 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """
                
                cursor.execute(query, values)
                self.connection.commit()
                
                if cursor.rowcount > 0:
                    print(f"✅ ID {company_id} の会社情報を更新しました")
                    return True
                else:
                    print(f"⚠️  ID {company_id} の会社が見つかりませんでした")
                    return False
                    
        except psycopg2.Error as e:
            print(f"❌ データベース更新エラー: {e}")
            self.connection.rollback()
            return False
    
    def get_company_count(self) -> int:
        """全会社数を取得"""
        if not self.connection:
            raise Exception("データベースに接続されていません")
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM companies")
                count = cursor.fetchone()[0]
                return count
        except psycopg2.Error as e:
            print(f"❌ カウント取得エラー: {e}")
            return 0

# 便利関数
def create_postgresql_database(connection_info: Union[str, Dict[str, str]] = None):
    """
    PostgreSQL会社データベースを作成し、接続する
    
    Args:
        connection_info: 接続情報（URLまたは接続パラメータ辞書）
        
    Returns:
        PostgreSQLCompanyDatabase: 初期化されたデータベースインスタンス
    """
    db = PostgreSQLCompanyDatabase(connection_info)
    if db.connect():
        return db
    else:
        raise Exception("データベースに接続できませんでした")

# デフォルトでSupabaseのURLを使用
def create_postgresql_database_with_url():
    """
    SupabaseのURLを使用してデータベースに接続
    """
    database_url = "postgresql://postgres.maveomskewmzyqjfgbwq:XRaFQiIg5BJdXtZv@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
    return create_postgresql_database(database_url)
