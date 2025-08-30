from playwright.sync_api import sync_playwright
import urllib.parse
import time
import random

def google_search(query):
    """Google検索を実行して結果を取得"""

    # プロキシリスト
    proxy_list = [
        "45.87.51.66:6626",
        "64.137.58.171:6417",
        "82.29.214.96:6947",
        "206.41.169.40:5620",
        "82.24.249.182:6019",
        "148.135.148.242:6235",
        "23.109.232.239:6159",
        "154.203.48.121:5917",
        "172.102.223.180:5691",
        "38.154.227.176:5877",
        "45.38.84.86:7022",
        "23.27.210.2:6372",
        "45.43.87.51:7800",
        "45.251.61.178:6896",
        "82.29.235.90:7942",
        "104.239.39.194:6123",
        "31.58.151.64:6055",
        "92.112.170.61:6030",
        "92.112.238.171:7050",
        "82.22.245.232:6056",
        "94.46.206.161:6934",
        "148.135.179.114:6173",
        "185.135.10.34:5548",
        "198.46.246.19:6643",
        "46.203.96.48:6172",
        "45.92.77.61:6083",
        "45.117.55.252:6898",
        "173.211.8.84:6196",
        "179.61.166.214:6637",
        "69.58.9.27:7097",
        "104.253.55.169:5599",
        "92.112.236.47:6479",
        "92.113.231.63:7148",
        "50.114.15.143:6128",
        "91.123.10.196:6738",
        "107.181.141.93:6490",
        "64.137.89.210:6283",
        "89.249.194.251:6650",
        "185.171.254.211:6243",
        "82.23.228.197:6519",
        "91.223.126.177:6789",
        "92.112.228.193:6274",
        "173.211.8.241:6353",
        "50.114.99.186:6927",
        "142.111.113.182:6543",
        "82.22.230.54:7392",
        "82.24.242.186:8005",
        "145.223.41.95:6366",
        "104.168.118.119:6075",
        "104.253.50.109:6546",
        "194.38.26.206:7267",
        "23.94.138.162:6436",
        "82.29.237.184:7993",
        "92.112.137.67:6010",
        "92.112.171.113:6081",
        "184.174.56.112:5124",
        "92.112.172.22:6294",
        "38.153.148.42:5313",
        "216.173.104.199:6336",
        "82.25.242.239:7558",
        "154.13.221.19:6005",
        "198.37.116.49:6008",
        "23.236.216.235:6265",
        "45.39.15.169:6599",
        "154.30.242.98:9492",
        "179.61.166.9:6432",
        "45.41.169.150:6811",
        "23.236.247.169:8201",
        "86.38.236.109:6393",
        "104.253.77.12:5434",
        "216.173.104.3:6140",
        "82.29.233.166:8023",
        "23.27.75.203:6283",
        "82.22.215.54:7385",
        "185.101.253.244:5804",
        "46.202.67.134:6130",
        "145.223.57.117:6150",
        "92.112.85.74:5809",
        "46.202.227.95:6089",
        "107.181.148.212:6072",
        "145.223.54.122:6087",
        "23.27.209.254:6273",
        "50.114.84.93:7332",
        "140.99.203.167:6044",
        "104.143.244.32:5980",
        "107.181.132.139:6117",
        "23.27.184.10:5611",
        "45.43.191.37:5998",
        "148.135.144.138:5634",
        "154.203.49.77:5373",
        "45.38.101.119:6052",
        "82.24.225.223:8064",
        "104.239.88.19:5639",
        "45.38.111.17:5932",
        "85.198.47.231:6499",
        "82.24.221.7:5858",
        "104.168.118.78:6034",
        "45.43.95.67:6816",
        "91.198.95.56:5578",
        "193.239.176.241:5647"
    ]

    with sync_playwright() as p:
        # ランダムにプロキシを選択
        selected_proxy = random.choice(proxy_list)
        proxy_url = f"http://{selected_proxy}"
        print(f"使用するプロキシ: {proxy_url}")
        
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                f'--proxy-server={proxy_url}'
            ],
            proxy={
                'server': proxy_url,
                'username': 'vmqzsrah',
                'password': 'urzk08fa06pc'
            }
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