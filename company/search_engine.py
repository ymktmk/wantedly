from playwright.sync_api import sync_playwright
import urllib.parse
import time
import random

def google_search(query):
    """Google検索を実行して結果を取得"""
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