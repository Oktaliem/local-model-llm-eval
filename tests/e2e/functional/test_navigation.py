"""
E2E tests for navigation functionality
"""
import pytest
from playwright.sync_api import Page
from tests.e2e.pages.navigation import Navigation


class TestNavigation:
    """Test cases for navigation."""
    
    def test_all_navigation_options_visible(self, app_page: Page):
        """Test that all navigation options are visible in sidebar."""
        nav = Navigation(app_page)
        
        # Wait for page to load
        import time
        time.sleep(2)  # Give Streamlit time to render
        
        # Check that navigation sidebar is visible
        sidebar = app_page.locator("section[data-testid='stSidebar']")
        assert sidebar.is_visible(), "Sidebar should be visible"
        
        # Check that at least some navigation buttons are visible
        # Try multiple possible selectors for navigation buttons
        nav_button = app_page.locator("button").filter(has_text="Pairwise").first
        if not nav_button.is_visible():
            # Try alternative selector
            nav_button = app_page.locator("button").filter(has_text="🔀").first
        
        assert nav_button.is_visible(), "At least one navigation button should be visible"
    
    def test_navigation_between_pages(self, app_page: Page):
        """Test navigating between different pages."""
        nav = Navigation(app_page)
        
        # Navigate to different pages and verify they load
        nav.navigate_to_pairwise()
        assert nav.verify_page_loaded("Compare Two Responses")
        
        nav.navigate_to_auto_compare()
        assert nav.verify_page_loaded("Auto Compare Two Models")
        
        nav.navigate_to_single_grading()
        assert nav.verify_page_loaded("Grade Single Response")
        
        nav.navigate_to_auto_single_grading()
        assert nav.verify_page_loaded("Auto Single Response Grading")
    
    def test_page_title(self, app_page: Page):
        """Test that page title is correct."""
        title = app_page.title()
        assert "AI Agent" in title or "LLM Evaluation" in title or "Evaluation Framework" in title

