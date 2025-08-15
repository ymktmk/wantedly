from playwright.sync_api import sync_playwright
import urllib.parse
import time
import random
import os

def _serpapi_search(query):
    """SerpAPI を使って Google 検索結果を取得（環境変数 SERPAPI_API_KEY が必要）"""
    api_key = os.getenv('SERPAPI_API_KEY')
    if not api_key:
        return []
    try:
        # requests はローカルimport（未インストール環境でも既存フォールバックを使えるように）
        import requests  # type: ignore
        params = {
            'engine': 'google',
            'q': query,
            'hl': 'ja',
            'gl': 'jp',
            'num': 10,
            'api_key': api_key,
        }
        resp = requests.get('https://serpapi.com/search.json', params=params, timeout=20)
        if resp.status_code != 200:
            print(f"⚠️ SerpAPI エラー: {resp.status_code} {resp.text[:200]}")
            return []
        data = resp.json()
        organic = data.get('organic_results') or []
        results = []
        for item in organic:
            title = item.get('title')
            url = item.get('link')
            desc = item.get('snippet') or ''
            if title and url:
                results.append({'title': title, 'url': url, 'description': desc})
        return results
    except Exception as e:
        print(f"⚠️ SerpAPI 呼び出し失敗: {e}")
        return []

def _google_cse_search(query):
    """Google Custom Search JSON API を使って検索結果を取得（環境変数 GOOGLE_CSE_API_KEY, GOOGLE_CSE_ENGINE_ID が必要）"""
    api_key = os.getenv('GOOGLE_CSE_API_KEY')
    engine_id = os.getenv('GOOGLE_CSE_ENGINE_ID')
    if not api_key or not engine_id:
        return []
    try:
        import requests  # type: ignore
        params = {
            'key': api_key,
            'cx': engine_id,
            'q': query,
            'hl': 'ja',
            'num': 10,
            'safe': 'off',
            'lr': 'lang_ja',
        }
        resp = requests.get('https://www.googleapis.com/customsearch/v1', params=params, timeout=20)
        if resp.status_code != 200:
            print(f"⚠️ Google CSE API エラー: {resp.status_code} {resp.text[:200]}")
            return []
        data = resp.json()
        items = data.get('items') or []
        results = []
        for item in items:
            title = item.get('title')
            url = item.get('link')
            desc = item.get('snippet') or ''
            if title and url:
                results.append({'title': title, 'url': url, 'description': desc})
        return results
    except Exception as e:
        print(f"⚠️ Google CSE API 呼び出し失敗: {e}")
        return []

def google_search(query):
    """Google検索を実行して結果を取得（優先順: CSE → SerpAPI → Playwright）"""
    # 1) CSE（最優先）
    cse_results = _google_cse_search(query)
    if cse_results:
        return cse_results

    # 2) SerpAPI
    serp_results = _serpapi_search(query)
    if serp_results:
        return serp_results

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1366, 'height': 768},
            locale='ja-JP'
        )
        
        # ブラウザの自動化検出を無効化
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        
        try:
            # URLエンコードしたクエリでGoogle検索
            encoded_query = urllib.parse.quote_plus(query)
            page.goto(f"https://www.google.com/search?q={encoded_query}&hl=ja", timeout=30000)
            
            # ランダムな待機時間（人間らしい動作）
            time.sleep(random.uniform(0.5, 1))
            
            # 複数のセレクターを試して検索結果要素の存在を確認
            search_result_selectors = [
                'h3',
                '.tF2Cxc',
                '.g', 
                'div[data-ved]',
                '.yuRUbf',  # 新しいGoogle結果セレクタ
                '.MjjYud'   # 新しいGoogle結果セレクタ
            ]
            
            element_found = False
            for selector in search_result_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    element_found = True
                    print(f"検索結果を '{selector}' セレクターで検出しました")
                    break
                except:
                    continue
            
            if not element_found:
                print("⚠️ 検索結果要素が見つかりませんでした。ページの構造が変更された可能性があります")
                # デバッグ用にページのタイトルとURLを確認
                print(f"現在のページタイトル: {page.title()}")
                print(f"現在のURL: {page.url}")
                browser.close()
                return []
                
        except Exception as e:
            print(f"⚠️ ページの読み込みに失敗しました: {e}")
            browser.close()
            return []
        
        # 上位10件の検索結果を取得
        results = []
        
        # 検索結果コンテナのセレクタ
        container_selectors = [
            '.tF2Cxc',
            '.g',
            'div[data-ved]'
        ]
        
        search_containers = None
        for selector in container_selectors:
            elements = page.locator(selector)
            if elements.count() > 0:
                search_containers = elements
                break
        
        if search_containers is None:
            browser.close()
            return []
        
        count = min(search_containers.count(), 10)
        
        for i in range(count):
            try:
                container = search_containers.nth(i)
                
                # タイトルを取得
                title_selectors = ['h3', '.LC20lb']
                title = None
                title_element = None
                for title_sel in title_selectors:
                    title_el = container.locator(title_sel).first
                    if title_el.count() > 0:
                        title = title_el.text_content()
                        title_element = title_el
                        break
                
                if not title:
                    continue
                
                # URLを取得
                parent_link = title_element.locator('xpath=ancestor::a[1]')
                href = parent_link.get_attribute('href')
                
                # スニペット（説明文）を取得
                snippet_selectors = ['.VwiC3b', '.s', '.aCOpRe', 'div[data-sncf="1"]', '.st']
                snippet = ""
                for snippet_sel in snippet_selectors:
                    snippet_els = container.locator(snippet_sel)
                    if snippet_els.count() > 0:
                        snippet_text = snippet_els.first.text_content()
                        # より緩い条件でスニペットを取得
                        if snippet_text and len(snippet_text.strip()) > 10:
                            snippet = snippet_text
                            break
                
                if title and href and not href.startswith('/search') and 'google.com' not in href:
                    results.append({
                        'title': title.strip(),
                        'url': href,
                        'description': snippet.strip() if snippet else ""
                    })
                    
            except Exception:
                continue
        
        browser.close()
        return results