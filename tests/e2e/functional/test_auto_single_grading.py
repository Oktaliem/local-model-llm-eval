"""
E2E tests for Auto Single Response Grading feature
"""
import pytest
from playwright.sync_api import Page
from tests.e2e.pages.auto_single_page import AutoSinglePage
from tests.e2e.pages.navigation import Navigation


class TestAutoSingleGrading:
    """Test cases for Auto Single Response Grading."""
    
    def test_navigate_to_auto_single_page(self, app_page: Page):
        """Test navigation to Auto Single Response Grading page."""
        nav = Navigation(app_page)
        nav.navigate_to_auto_single_grading()
        
        auto_single_page = AutoSinglePage(app_page)
        auto_single_page.wait_for_page_load()
        
        # Verify page loaded
        assert auto_single_page.is_visible("h2:has-text('Auto Single Response Grading')")
    
    @pytest.mark.skip(reason="Requires model availability and long execution time")
    def test_auto_single_workflow(self, app_page: Page):
        """Test complete auto single response grading workflow."""
        auto_single_page = AutoSinglePage(app_page)
        auto_single_page.navigate()
        
        # Enter question
        question = "Explain machine learning in simple terms."
        auto_single_page.enter_question(question)
        
        # Select model (assuming models are available)
        # This would need to be adjusted based on available models
        auto_single_page.select_model("llama3")
        
        # Optional: Add custom criteria
        auto_single_page.enter_criteria("Focus on clarity and simplicity.")
        
        # Toggle save to DB off
        auto_single_page.toggle_save_to_db(False)
        
        # Click generate and evaluate
        auto_single_page.click_generate_and_evaluate()
        
        # Wait for generation to complete
        auto_single_page.wait_for_generation_complete(timeout=120000)  # 2 minutes
        
        # Verify generated response is displayed
        assert auto_single_page.is_generated_response_displayed()
        
        # Wait for evaluation to complete (this can take several minutes)
        auto_single_page.wait_for_evaluation_complete(timeout=180000)  # 3 minutes
        
        # Verify evaluation is displayed
        assert auto_single_page.is_evaluation_displayed()
        
        # Get evaluation result
        result = auto_single_page.get_evaluation_result()
        assert "evaluation_text" in result
        
        # Get generated response
        generated_response = auto_single_page.get_generated_response()
        assert len(generated_response) > 0, "Generated response should not be empty"
    
    def test_auto_single_ui_elements(self, app_page: Page):
        """Test that all UI elements are present."""
        auto_single_page = AutoSinglePage(app_page)
        auto_single_page.navigate()
        
        # Verify key UI elements exist
        # Streamlit textareas don't have placeholder attributes, use label-based selectors
        assert auto_single_page.is_visible("label:has-text('Question'), label:has-text('Task')") or auto_single_page.is_visible("textarea")
        assert auto_single_page.is_visible("button:has-text('Generate')")
        # Verify model selector exists
        assert auto_single_page.is_visible("select, [role='combobox']") or auto_single_page.is_visible("div:has-text('Select Model')")

