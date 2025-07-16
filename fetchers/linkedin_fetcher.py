"""
LinkedIn Fetcher - ULTRATHINK-AI-PRO LinkedIn Integration Framework
=================================================================

PURPOSE:
- Framework ready for LinkedIn company update tracking and pricing intelligence
- Monitors vendor company pages for pricing announcements and strategic updates
- Uses Playwright for reliable web automation and session management
- Provides structured data integration with existing ULTRATHINK-AI-PRO ecosystem

TECHNICAL APPROACH:
- Playwright browser automation with persistent user context
- Company page monitoring for major IT vendors (Microsoft, Dell, HP, etc.)
- Post content analysis for pricing signals and strategic announcements
- Session management with automatic login handling
- Quality filtering for relevant enterprise content

INTEGRATION:
- Part of ULTRATHINK-AI-PRO hybrid pricing intelligence system
- Feeds into GPT summarizer alongside Reddit and Google data
- Provides enterprise-grade vendor communication monitoring
- Outputs structured data for HTML report generation

ACTIVATION STATUS:
- Framework ready, activation pending
- Requires LinkedIn credentials in config for full functionality
- Can be enabled by adding companies to linkedin.companies in config
- Anonymous browsing available with limited functionality

AUTHENTICATION:
- LinkedIn credentials (username/password) for full access
- Persistent session management via Playwright
- Falls back to anonymous browsing if credentials not provided

Author: Dollar (dollarvora@icloud.com)
System: ULTRATHINK-AI-PRO v3.1.0 Hybrid
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, Error as PlaywrightError
from fetchers.base_fetcher import BaseFetcher


class LinkedInFetcher(BaseFetcher):
    """Fetches content from LinkedIn company pages"""

    def get_source_name(self) -> str:
        return 'linkedin'

    async def fetch_raw(self) -> List[Dict[str, Any]]:
        """Fetch posts from LinkedIn company pages"""
        all_posts = []

        async with async_playwright() as p:
            browser = await self._launch_browser(p)

            try:
                page = await browser.new_page()

                if await self._needs_login(page):
                    await self._login(page)

                for company in self.source_config['companies']:
                    try:
                        self.logger.info(f"Fetching LinkedIn posts from {company}")
                        posts = await self._fetch_company_posts(page, company)
                        all_posts.extend(posts)
                    except Exception as e:
                        self.logger.error(f"Error fetching from {company}: {e}")
                        continue

            except PlaywrightError as e:
                self.logger.error(f"LinkedIn Playwright error: {e}")
                return []

            finally:
                try:
                    await browser.close()
                except Exception as e:
                    self.logger.warning(f"Failed to close browser cleanly: {e}")

        return all_posts

    async def _launch_browser(self, playwright) -> Browser:
        user_data_dir = Path('cache/playwright')
        user_data_dir.mkdir(parents=True, exist_ok=True)

        browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        return browser

    async def _needs_login(self, page: Page) -> bool:
        try:
            await page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
            return 'linkedin.com/login' in page.url or 'Sign in' in await page.title()
        except PlaywrightError:
            return True

    async def _login(self, page: Page) -> None:
        creds = self.config.get('credentials', {}).get('linkedin', {})

        if not creds.get('username') or not creds.get('password'):
            self.logger.warning("LinkedIn credentials not provided, using anonymous browsing")
            return

        try:
            self.logger.info("Logging in to LinkedIn...")
            await page.goto('https://www.linkedin.com/login')
            await page.fill('input[name="session_key"]', creds['username'])
            await page.fill('input[name="session_password"]', creds['password'])
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')

            storage = await page.context.storage_state()
            session_file = Path('cache/linkedin_session.json')
            with open(session_file, 'w') as f:
                json.dump(storage, f)

            self.logger.info("LinkedIn login successful")

        except Exception as e:
            self.logger.error(f"LinkedIn login failed: {e}")
            raise

    async def _fetch_company_posts(self, page: Page, company_name: str) -> List[Dict[str, Any]]:
        posts = []
        company_url = await self._find_company_url(page, company_name)
        if not company_url:
            self.logger.warning(f"Could not find LinkedIn page for {company_name}")
            return posts

        posts_url = f"{company_url}/posts/"
        await page.goto(posts_url, wait_until='networkidle')
        await self._scroll_page(page, 3)
        post_elements = await page.query_selector_all('div[data-urn*="activity"]')

        for element in post_elements[:self.source_config['post_limit']]:
            try:
                post_data = await self._extract_post_data(element, company_name)
                if post_data:
                    posts.append(post_data)
            except Exception as e:
                self.logger.debug(f"Error extracting post: {e}")
                continue

        return posts

    async def _find_company_url(self, page: Page, company_name: str) -> Optional[str]:
        normalized_name = company_name.lower().replace(' ', '-').replace('.', '')
        direct_url = f"https://www.linkedin.com/company/{normalized_name}"

        await page.goto(direct_url)
        if await page.query_selector('h1'):
            return direct_url

        search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name}"
        await page.goto(search_url, wait_until='networkidle')
        first_result = await page.query_selector('a[href*="/company/"]')
        if first_result:
            href = await first_result.get_attribute('href')
            return href.split('?')[0]

        return None

    async def _scroll_page(self, page: Page, times: int) -> None:
        for _ in range(times):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)

    async def _extract_post_data(self, element, company_name: str) -> Optional[Dict[str, Any]]:
        try:
            text_element = await element.query_selector('.feed-shared-text')
            text = await text_element.inner_text() if text_element else ''
            link_element = await element.query_selector('a[href*="/feed/update/"]')
            post_url = await link_element.get_attribute('href') if link_element else ''

            time_element = await element.query_selector('time')
            if time_element:
                datetime_str = await time_element.get_attribute('datetime')
                created_at = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                created_at = datetime.now()

            reactions_element = await element.query_selector('[data-test-social-counts-reactions]')
            reactions = 0
            if reactions_element:
                reactions_text = await reactions_element.inner_text()
                reactions = self._parse_count(reactions_text)

            comments_element = await element.query_selector('[data-test-social-counts-comments]')
            comments = 0
            if comments_element:
                comments_text = await comments_element.inner_text()
                comments = self._parse_count(comments_text)

            post_id = re.search(r'urn:li:activity:(\d+)', post_url)
            post_id = post_id.group(1) if post_id else None

            return {
                'id': post_id or f"{company_name}_{created_at.timestamp()}",
                'text': text,
                'url': post_url,
                'company': company_name,
                'created_at': created_at,
                'reactions': reactions,
                'comments': comments,
                'has_image': bool(await element.query_selector('img[src*="media"]')),
                'has_video': bool(await element.query_selector('video')),
                'has_document': bool(await element.query_selector('[data-test-document-entity]'))
            }

        except Exception as e:
            self.logger.debug(f"Error extracting LinkedIn post: {e}")
            return None

    def _parse_count(self, text: str) -> int:
        if not text:
            return 0

        text = text.strip().upper()
        multipliers = {'K': 1000, 'M': 1000000}

        for suffix, multiplier in multipliers.items():
            if suffix in text:
                number = float(text.replace(suffix, '').replace(',', ''))
                return int(number * multiplier)

        return int(text.replace(',', ''))
