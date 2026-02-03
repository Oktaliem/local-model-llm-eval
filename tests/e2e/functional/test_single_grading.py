"""
E2E tests for Single Response Grading feature
"""
import pytest
from playwright.sync_api import Page
from tests.e2e.pages.single_grading_page import SingleGradingPage
from tests.e2e.pages.navigation import Navigation


class TestSingleGrading:
    """Test cases for Single Response Grading."""
    
    def test_navigate_to_single_grading_page(self, app_page: Page):
        """Test navigation to Single Response Grading page."""
        nav = Navigation(app_page)
        nav.navigate_to_single_grading()
        
        single_page = SingleGradingPage(app_page)
        single_page.wait_for_page_load()
        
        # Verify page loaded
        assert single_page.is_visible("h2:has-text('Grade Single Response')")
    
    @pytest.mark.skip(reason="Requires model availability and long execution time")
    def test_single_grading_workflow(self, app_page: Page):
        """Test complete single grading workflow."""
        single_page = SingleGradingPage(app_page)
        single_page.navigate()
        
        # Enter test data
        question = "Explain machine learning in simple terms."
        response = "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed."
        
        single_page.enter_question(question)
        single_page.enter_response(response)
        
        # Optional: Add custom criteria
        single_page.enter_criteria("Focus on clarity and simplicity.")
        
        # Toggle save to DB off
        single_page.toggle_save_to_db(False)
        
        # Click evaluate
        single_page.click_evaluate_response()
        
        # Wait for evaluation (with long timeout)
        single_page.wait_for_evaluation_complete(timeout=180000)  # 3 minutes
        
        # Verify evaluation is displayed
        assert single_page.is_evaluation_displayed()
        
        # Get evaluation result
        result = single_page.get_evaluation_result()
        assert "evaluation_text" in result
    
    def test_single_grading_ui_elements(self, app_page: Page):
        """Test that all UI elements are present."""
        single_page = SingleGradingPage(app_page)
        single_page.navigate()
        
        # Verify key UI elements exist
        # Streamlit textareas don't have placeholder attributes, use label-based selectors
        assert single_page.is_visible("label:has-text('Question'), label:has-text('Task')") or single_page.is_visible("textarea")
        assert single_page.is_visible("label:has-text('Response')") or single_page.is_visible("textarea")
        assert single_page.is_visible("button:has-text('Evaluate')")

