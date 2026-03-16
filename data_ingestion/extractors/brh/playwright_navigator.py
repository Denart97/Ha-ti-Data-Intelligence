from playwright.sync_api import sync_playwright, Page
from typing import List, Optional, Dict
import logging

logger = logging.getLogger("brh_playwright")


class PlaywrightNavigator:
    """Navigator using Playwright to reproduce user interactions on BRH site.

    Methods:
    - open_home()
    - navigate_menu(main_label, sub_label)
    - collect_links_from_current_page()
    - fetch_html(url)
    """

    def __init__(self, base_url: str = "https://www.brh.ht", headless: bool = True, timeout: int = 30000):
        self.base_url = base_url.rstrip('/')
        self.headless = headless
        self.timeout = timeout
        self._pw = None
        self._browser = None
        self._page: Optional[Page] = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()
        self._page.set_default_timeout(self.timeout)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._browser:
                self._browser.close()
        finally:
            if self._pw:
                self._pw.stop()

    def open_home(self) -> str:
        assert self._page is not None
        logger.info(f"Opening home {self.base_url}")
        self._page.goto(self.base_url)
        return self._page.content()

    def click_selector_if_present(self, selector: str) -> bool:
        try:
            if self._page.query_selector(selector):
                self._page.click(selector)
                return True
        except Exception as e:
            logger.debug(f"click_selector_if_present failed for {selector}: {e}")
        return False

    def navigate_menu(self, main_label: str, sub_label: Optional[str] = None) -> str:
        """Attempt to open top menu item with visible text `main_label`, then optionally a sub_label.

        This method is heuristic-driven because site markup can vary.
        Returns HTML content of the landing intermediate page.
        """
        assert self._page is not None

        # Try to find a top-level nav link by text
        # Try several heuristics: anchor text, nav item with role menu, elements with aria-label
        found = False
        try:
            anchors = self._page.query_selector_all('a')
            for a in anchors:
                try:
                    text = a.inner_text().strip().lower()
                except Exception:
                    text = ''
                if main_label.lower() in text:
                    a.click()
                    found = True
                    break
        except Exception as e:
            logger.debug(f"menu anchor scan failed: {e}")

        if not found:
            # fallback: click elements in header nav
            self.click_selector_if_present('nav')

        # If sub_label provided, attempt to expand and click
        if sub_label:
            # look for element containing the sub_label
            try:
                anchors = self._page.query_selector_all('a')
                for a in anchors:
                    try:
                        text = a.inner_text().strip().lower()
                    except Exception:
                        text = ''
                    if sub_label.lower() in text:
                        a.click()
                        break
            except Exception as e:
                logger.debug(f"sub anchor scan failed: {e}")

        # Wait for navigation network idle
        try:
            self._page.wait_for_load_state('networkidle', timeout=self.timeout)
        except Exception:
            pass

        return self._page.content()

    def collect_links_from_current_page(self) -> List[Dict[str, str]]:
        assert self._page is not None
        anchors = self._page.query_selector_all('a')
        results = []
        for a in anchors:
            try:
                href = a.get_attribute('href') or ''
                text = a.inner_text().strip()
                results.append({'href': href, 'text': text})
            except Exception:
                continue
        return results

    def fetch_html(self, url: str) -> str:
        assert self._page is not None
        logger.info(f"Fetching HTML via Playwright: {url}")
        self._page.goto(url)
        try:
            self._page.wait_for_load_state('networkidle', timeout=self.timeout)
        except Exception:
            pass
        return self._page.content()
