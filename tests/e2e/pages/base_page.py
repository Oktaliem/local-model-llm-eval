"""
Base Page Object Model class
"""
from playwright.sync_api import Page, Locator
from typing import Optional
import time
import os


class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = os.getenv("TEST_BASE_URL", "http://localhost:8501")
    
    def navigate(self, url: str = None) -> None:
        """Navigate to the page."""
        if url:
            self.page.goto(url)
        else:
            self.page.goto(self.base_url)
        self.wait_for_load()
    
    def wait_for_load(self, timeout: int = 10000) -> None:
        """Wait for the page to load."""
        # Wait for main content
        self.page.wait_for_selector("h1", timeout=timeout)
        time.sleep(1)  # Give Streamlit time to finish rendering
    
    def click(self, selector: str, timeout: int = 5000) -> None:
        """Click an element."""
        self.page.click(selector, timeout=timeout)
    
    def fill(self, selector: str, text: str, timeout: int = 5000) -> None:
        """Fill an input field."""
        self.page.fill(selector, text, timeout=timeout)
    
    def select_option(self, selector: str, value: str, timeout: int = 5000) -> None:
        """Select an option from a selectbox."""
        self.page.select_option(selector, value, timeout=timeout)
    
    def get_text(self, selector: str, timeout: int = 5000) -> str:
        """Get text content of an element."""
        return self.page.locator(selector).inner_text(timeout=timeout)
    
    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element is visible."""
        try:
            locator = self.page.locator(selector).first
            if locator.is_visible(timeout=timeout):
                return True
            return False
        except:
            return False
    
    def wait_for_text(self, selector: str, text: str, timeout: int = 10000) -> None:
        """Wait for element to contain specific text."""
        self.page.wait_for_selector(
            f"{selector}:has-text('{text}')",
            timeout=timeout
        )
    
    def get_title(self) -> str:
        """Get page title."""
        return self.page.title()
    
    def take_screenshot(self, filename: str) -> None:
        """Take a screenshot."""
        self.page.screenshot(path=f"tests/e2e/screenshots/{filename}.png")
    
    def navigate_to_page(self, page_name: str) -> None:
        """Navigate to a specific page using sidebar navigation."""
        import time
        time.sleep(1)  # Wait for sidebar to render
        
        # Find and click the navigation button
        # Try multiple selector strategies
        button = None
        
        # Strategy 1: Exact text match
        button_selector = f"button:has-text('{page_name}')"
        if self.is_visible(button_selector, timeout=2000):
            button = self.page.locator(button_selector).first
        else:
            # Strategy 2: Partial text match (without emoji)
            # Extract text without emoji
            text_without_emoji = ''.join(c for c in page_name if ord(c) < 128).strip()
            if text_without_emoji:
                button_selector = f"button:has-text('{text_without_emoji}')"
                if self.is_visible(button_selector, timeout=2000):
                    button = self.page.locator(button_selector).first
        
        # Strategy 3: Find by emoji or key part
        if not button:
            # Try to find button containing key words
            key_words = page_name.split()
            for word in key_words:
                if len(word) > 3:  # Skip short words and emojis
                    button_selector = f"button:has-text('{word}')"
                    buttons = self.page.locator(button_selector)
                    if buttons.count() > 0:
                        button = buttons.first
                        break
        
        if button and button.is_visible():
            button.click()
            time.sleep(1)  # Wait for navigation
            self.wait_for_load()
            return
        
        # Last resort: try to find any button or clickable element in sidebar with similar text
        sidebar = self.page.locator("section[data-testid='stSidebar']")
        
        # Normalize page name for comparison (remove emoji, lowercase)
        page_name_normalized = ''.join(c for c in page_name if ord(c) < 128).lower().strip()
        key_words = [w for w in page_name_normalized.split() if len(w) > 2]
        
        # Try buttons first
        all_buttons = sidebar.locator("button")
        button_count = all_buttons.count()
        
        for i in range(min(button_count, 20)):  # Check first 20 buttons
            btn = all_buttons.nth(i)
            if btn.is_visible():
                try:
                    btn_text = btn.inner_text().lower()
                    btn_text_normalized = ''.join(c for c in btn_text if ord(c) < 128).lower().strip()
                    
                    # Check if key words match
                    if any(word in btn_text_normalized for word in key_words) or \
                       any(word in page_name_normalized for word in btn_text_normalized.split()):
                        btn.click()
                        time.sleep(1)
                        self.wait_for_load()
                        return
                except:
                    continue
        
        # Also check for clickable divs (selected page might be rendered as a div)
        clickable_divs = sidebar.locator("div[style*='background-color'], div[style*='border']")
        div_count = clickable_divs.count()
        for i in range(min(div_count, 20)):
            div = clickable_divs.nth(i)
            if div.is_visible():
                try:
                    div_text = div.inner_text().lower()
                    div_text_normalized = ''.join(c for c in div_text if ord(c) < 128).lower().strip()
                    if any(word in div_text_normalized for word in key_words):
                        div.click()
                        time.sleep(1)
                        self.wait_for_load()
                        return
                except:
                    continue
        
        # Debug: print what buttons we found
        button_texts = []
        for i in range(min(button_count, 20)):
            btn = all_buttons.nth(i)
            if btn.is_visible():
                try:
                    button_texts.append(btn.inner_text())
                except:
                    button_texts.append("(could not read)")
        
        raise ValueError(
            f"Navigation button for '{page_name}' not found. "
            f"Found {button_count} buttons. Button texts: {button_texts[:5]}"
        )

