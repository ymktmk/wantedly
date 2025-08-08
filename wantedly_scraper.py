#!/usr/bin/env python3
"""
Wantedly スクレイピングツール (Playwright版)
求人情報やミートアップ情報を取得するためのツール
"""

import asyncio
import time
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class WantedlyScraperPlaywright:
    def __init__(self, email: str, password: str, headless: bool = True):
        """
        Wantedlyスクレイパーの初期化
        
        Args:
            email: ログイン用メールアドレス
            password: ログイン用パスワード
            headless: ヘッドレスモードで実行するかどうか
        """
        self.email = email
        self.password = password
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.base_url = "https://www.wantedly.com"
    
    # ブラウザをセットアップ
    async def setup_browser(self):
        """Playwrightブラウザのセットアップ"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # コンテキストを作成（ユーザーエージェントなどを設定）
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # ページを作成
        self.page = await self.context.new_page()
        
        # webdriverプロパティを隠す
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
    
    # ログイン
    async def login(self) -> bool:
        """
        Wantedlyにログイン
        
        Returns:
            bool: ログイン成功の場合True
        """
        try:
            print("ログイン中...")
            await self.page.goto(f"{self.base_url}/signin_or_signup")
            
            # メールアドレス入力
            email_input = await self.page.wait_for_selector("input[placeholder*='email']", timeout=10000)
            await email_input.click()
            await email_input.fill("")  # フィールドをクリア
            await email_input.fill(self.email)
            
            # 次へボタンをクリック
            next_button = await self.page.wait_for_selector("button[type='submit']", timeout=5000)
            await next_button.click()
            
            # パスワード入力フィールドが表示されるまで待機
            password_input = await self.page.wait_for_selector("input[placeholder*='パスワード']", timeout=10000)
            await password_input.click()
            await password_input.fill("")  # フィールドをクリア
            await password_input.fill(self.password)
            
            # ログインボタンをクリック
            login_button = await self.page.wait_for_selector("button[type='submit']", timeout=5000)
            await login_button.click()
            
            # ログイン成功を確認（URLの変化を待つ）
            await self.page.wait_for_function(
                "() => !window.location.href.includes('signin')",
                timeout=10000
            )
            print("ログイン成功")
            return True
            
        except Exception as e:
            print(f"ログインエラー: {e}")
            return False
    
    # 求人データを取得
    async def get_job_posts(self, max_pages: int = 5) -> List[Dict]:
        """
        求人情報を取得
        
        Args:
            max_pages: 取得する最大ページ数
            filters: フィルター条件（キーワード、職種など）
            
        Returns:
            List[Dict]: 求人情報のリスト
        """
        job_posts = []
        
        try:
            for page_num in range(1, max_pages + 1):
                print(f"ページ {page_num} を処理中...")
                
                # 各ページに直接アクセス
                # url = f"{self.base_url}/projects?new=true&page={page_num}&occupationTypes=jp__engineering&hiringTypes=side_job&order=mixed"
                url = f"{self.base_url}/projects?new=true&page={page_num}&occupationTypes=jp__engineering&hiringTypes=internship&hiringTypes=side_job&hiringTypes=freelance&order=mixed"
                await self.page.goto(url)
                await asyncio.sleep(3)
                
                # ページの求人情報を取得
                page_jobs = await self._extract_jobs_from_page()
                if not page_jobs:
                    print(f"ページ {page_num} に求人情報が見つかりません。処理を終了します。")
                    break
                    
                job_posts.extend(page_jobs)
                await asyncio.sleep(2)  # レート制限対策
                
        except Exception as e:
            print(f"求人情報取得エラー: {e}")
            
        return job_posts
    
    # 求人データ抽出
    async def _extract_jobs_from_page(self) -> List[Dict]:
        """現在のページから求人情報を抽出"""
        jobs = []
        
        try:
            # ページが完全に読み込まれるまで待機
            await asyncio.sleep(3)
            
            # 指定されたクラス名でスクレイピング対象を特定
            job_section_selectors = [
                "section.ProjectListJobPostItem__Base-sc-bjcnhh-0.blCPPw.projects-index-single",
                "section.ProjectListJobPostItem__Base-sc-bjcnhh-0",
                ".ProjectListJobPostItem__Base-sc-bjcnhh-0",
                ".projects-index-single",
                "section[class*='ProjectListJobPostItem__Base']",
            ]
            
            job_sections = []
            for selector in job_section_selectors:
                try:
                    sections = await self.page.query_selector_all(selector)
                    if sections:
                        job_sections = sections
                        print(f"セレクター '{selector}' で {len(job_sections)} 件の求人セクションを発見")
                        break
                except Exception as selector_error:
                    print(f"セレクター '{selector}' でエラー: {selector_error}")
                    continue
            
            print(f"見つかった求人セクション数: {len(job_sections)}")
            
            for i, section in enumerate(job_sections):
                try:
                    print(f"求人 {i+1}/{len(job_sections)} を処理中...")
                    job_data = await self._extract_job_data_from_section(section)
                    if job_data:
                        jobs.append(job_data)
                        print(f"  - タイトル: {job_data.get('title', 'N/A')}")
                        print(f"  - 会社名: {job_data.get('company', 'N/A')}")
                except Exception as e:
                    print(f"求人データ抽出エラー (セクション {i+1}): {e}")
                    continue
                    
        except Exception as e:
            print(f"ページ解析エラー: {e}")
            
        return jobs
    
    # 求人セクションからデータ抽出
    async def _extract_job_data_from_section(self, section_element) -> Optional[Dict]:
        """求人セクションから詳細データを抽出"""
        try:
            job_data = {
                'title': '',
                'company': '',
                'location': '',
                'description': '',
                'url': '',
                'tags': [],
                'entry_count': '',
                'scraped_at': datetime.now().isoformat()
            }
            
            # プロジェクトリンクとURLを取得
            project_link = await section_element.query_selector("a.ProjectListJobPostItem__ProjectLink-sc-bjcnhh-1, a[href*='/projects/']")
            if project_link:
                href = await project_link.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        job_data['url'] = f"{self.base_url}{href}"
                    else:
                        job_data['url'] = href
            
            # タイトルを抽出
            title_element = await section_element.query_selector("h2.ProjectListJobPostItem__TitleText-sc-bjcnhh-5, h2[class*='TitleText'], h2")
            if title_element:
                job_data['title'] = await title_element.text_content()
                job_data['title'] = job_data['title'].strip() if job_data['title'] else ''
            
            # 説明を抽出
            description_element = await section_element.query_selector("p.ProjectListJobPostItem__DescriptionText-sc-bjcnhh-7, p[class*='DescriptionText']")
            if description_element:
                job_data['description'] = await description_element.text_content()
                job_data['description'] = job_data['description'].strip() if job_data['description'] else ''
            
            # 会社名を抽出
            company_element = await section_element.query_selector("p.JobPostCompanyWithWorkingConnectedUser__CompanyNameText-sc-1nded7v-5, p[class*='CompanyNameText'], #company-name")
            if company_element:
                job_data['company'] = await company_element.text_content()
                job_data['company'] = job_data['company'].strip() if job_data['company'] else ''
            
            # エントリー数を抽出
            entry_count_element = await section_element.query_selector("p.ProjectListJobPostItem__EntryCountText-sc-bjcnhh-8, p[class*='EntryCountText']")
            if entry_count_element:
                entry_text = await entry_count_element.text_content()
                if entry_text:
                    job_data['entry_count'] = entry_text.strip()
            
            # タグを抽出
            tag_elements = await section_element.query_selector_all("span.FeatureTagList__TagLabelNormal-sc-lktsv0-7, span[class*='TagLabel']")
            if tag_elements:
                tags = []
                for tag_element in tag_elements:
                    tag_text = await tag_element.text_content()
                    if tag_text and tag_text.strip():
                        tags.append(tag_text.strip())
                job_data['tags'] = tags
            
            return job_data if job_data['title'] or job_data['url'] else None
            
        except Exception as e:
            print(f"求人セクションデータ抽出エラー: {e}")
            return None
    
    # データをJSONファイルに保存
    def save_to_json(self, data: List[Dict], filename: str):
        """データをJSONファイルに保存"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"データを {filename} に保存しました")
    
    # データをCSVファイルに保存
    def save_to_csv(self, data: List[Dict], filename: str):
        """データをCSVファイルに保存"""
        if not data:
            print("保存するデータがありません")
            return
            
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"データを {filename} に保存しました")
    
    # ブラウザを閉じる
    async def close(self):
        """ブラウザを閉じる"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

async def main():
    """メイン実行関数"""
    # ログイン情報
    EMAIL = "ketsutataki03@gmail.com"
    PASSWORD = "ZHF8ipHw"
    
    # スクレイパーを初期化
    scraper = WantedlyScraperPlaywright(EMAIL, PASSWORD, headless=True)
    
    try:
        # ブラウザをセットアップ
        await scraper.setup_browser()
        
        # ログイン
        if not await scraper.login():
            print("ログインに失敗しました")
            return
        
        # エンジニアリング求人を取得
        print("エンジニアリング求人情報を取得中...")
        job_posts = await scraper.get_job_posts(max_pages=596)
        
        print(f"取得した求人数: {len(job_posts)}")
        
        # データを保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if job_posts:
            scraper.save_to_json(job_posts, f"wantedly/wantedly_jobs_playwright_{timestamp}.json")
            scraper.save_to_csv(job_posts, f"wantedly/wantedly_jobs_playwright_{timestamp}.csv")
        
        print("スクレイピング完了")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
