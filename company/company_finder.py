from search_engine import google_search

def find_company_website(company_name):
    """会社名から公式ホームページを特定（シンプル版）"""
    
    print(f"「{company_name}」の公式ホームページを検索中...")
    
    # シンプルに「公式ホームページ」で検索
    search_query = f"{company_name} 公式ホームページ"
    print(f"検索クエリ: {search_query}")
    
    results = google_search(search_query)
    if not results:
        return []
    
    # 1番目の結果をそのまま返す
    return results[:1]

def find_company_contact(company_name):
    """会社名からお問い合わせページを特定（シンプル版）"""
    
    print(f"「{company_name}」のお問い合わせページを検索中...")
    
    # シンプルに「お問い合わせ」で検索
    search_query = f"{company_name} お問い合わせ"
    print(f"検索クエリ: {search_query}")
    
    results = google_search(search_query)
    if not results:
        return []
    
    # 1番目の結果をそのまま返す
    return results[:1]

def find_company_industry(company_name):
    """会社名から業界・事業内容を特定（シンプル版）"""
    
    print(f"「{company_name}」の業界・事業内容を検索中...")
    
    # シンプルに「業界 事業内容」で検索
    search_query = f"{company_name} 業界 事業内容"
    print(f"検索クエリ: {search_query}")
    
    results = google_search(search_query)    
    if not results:
        return []
    
    # 1番目の結果をそのまま返す
    return results[:1]
