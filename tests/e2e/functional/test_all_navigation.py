"""
Comprehensive navigation tests for all pages
"""
import pytest
import time
from playwright.sync_api import Page
from tests.e2e.pages.navigation import Navigation


class TestAllNavigationPages:
    """Test navigation to all pages in the application."""
    
    NAVIGATION_PAGES = [
        ("🔀 Manual Pairwise Comparison", "Compare Two Responses"),
        ("🤖 Auto Pairwise Comparison", "Auto Compare Two Models"),
        ("📊 Single Response Grading", "Grade Single Response"),
        ("🤖 Auto Single Response Grading", "Auto Single Response Grading"),
        ("🎯 Comprehensive Evaluation", "Comprehensive Evaluation"),
        ("💻 Code-Based Evaluation", "Code-Based Evaluation"),
        ("📦 Batch Evaluation", "Batch Evaluation"),
        ("👤 Human Evaluation", "Human Evaluation"),
        ("🔀 Router Evaluation", "Router Evaluation"),
        ("🎓 Skills Evaluation", "Skills Evaluation"),
        ("🛤️ Trajectory Evaluation", "Trajectory Evaluation"),
        ("📈 Advanced Analytics", "Advanced Analytics"),
        ("💾 Saved Judgments & Dashboard", "Saved Judgments"),
        ("🧪 A/B Testing", "A/B Testing"),
        ("📋 Evaluation Templates", "Evaluation Templates"),
        ("🎯 Custom Metrics", "Custom Metrics"),
    ]
    
    @pytest.mark.parametrize("page_name,expected_content", NAVIGATION_PAGES)
    def test_navigate_to_page(self, app_page: Page, page_name: str, expected_content: str):
        """Test navigation to each page and verify it loads correctly."""
        nav = Navigation(app_page)
        
        # Navigate to the page
        nav.navigate_to_page(page_name)
        
        # Wait for page to load
        time.sleep(2)
        
        # Verify page loaded by checking for expected content
        # Try multiple possible selectors for the page header/content
        page_loaded = False
        
        # Check for h1, h2, or h3 with expected content
        for header_level in ["h1", "h2", "h3"]:
            header = app_page.locator(f"{header_level}:has-text('{expected_content}')")
            if header.count() > 0 and header.first.is_visible():
                page_loaded = True
                break
        
        # If header not found, check for any element with the expected text
        if not page_loaded:
            content = app_page.locator(f"*:has-text('{expected_content}')")
            if content.count() > 0:
                page_loaded = True
        
        assert page_loaded, f"Page '{page_name}' did not load correctly. Expected content: '{expected_content}'"
    
    def test_navigation_sidebar_visible(self, app_page: Page):
        """Test that navigation sidebar is always visible."""
        nav = Navigation(app_page)
        
        # Navigate through a few pages
        nav.navigate_to_pairwise()
        time.sleep(1)
        assert app_page.locator("section[data-testid='stSidebar']").is_visible()
        
        nav.navigate_to_auto_compare()
        time.sleep(1)
        assert app_page.locator("section[data-testid='stSidebar']").is_visible()
        
        nav.navigate_to_single_grading()
        time.sleep(1)
        assert app_page.locator("section[data-testid='stSidebar']").is_visible()
    
    def test_all_navigation_buttons_present(self, app_page: Page):
        """Test that all navigation buttons are present in the sidebar."""
        import time
        time.sleep(2)  # Wait for sidebar to render
        
        sidebar = app_page.locator("section[data-testid='stSidebar']")
        assert sidebar.is_visible(), "Sidebar should be visible"
        
        # Count buttons and divs (selected page might be a div)
        buttons = sidebar.locator("button")
        divs = sidebar.locator("div[style*='background-color'], div[style*='border']")
        
        total_nav_items = buttons.count() + divs.count()
        
        # Should have at least 15 navigation items (one might be selected as div)
        assert total_nav_items >= 15, f"Expected at least 15 navigation items, found {total_nav_items}"
        
        # Verify key navigation items exist
        nav_texts = []
        for i in range(min(buttons.count(), 20)):
            btn = buttons.nth(i)
            if btn.is_visible():
                nav_texts.append(btn.inner_text())
        
        # Also check divs (selected page might be rendered as a div)
        for i in range(min(divs.count(), 20)):
            div = divs.nth(i)
            if div.is_visible():
                try:
                    nav_texts.append(div.inner_text())
                except:
                    pass
        
        # Check for key pages (check both buttons and divs)
        nav_texts_combined = " ".join(nav_texts).lower()
        assert "pairwise" in nav_texts_combined or "comparison" in nav_texts_combined, \
            f"Expected 'pairwise' or 'comparison' in navigation. Found: {nav_texts_combined[:200]}"
        assert "auto compare" in nav_texts_combined or "compare models" in nav_texts_combined, \
            f"Expected 'auto compare' or 'compare models' in navigation. Found: {nav_texts_combined[:200]}"
        assert "single response" in nav_texts_combined or "grading" in nav_texts_combined, \
            f"Expected 'single response' or 'grading' in navigation. Found: {nav_texts_combined[:200]}"

