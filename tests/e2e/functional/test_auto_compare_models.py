"""
E2E tests for Auto Pairwise Comparison feature
"""
import pytest
from playwright.sync_api import Page
from tests.e2e.pages.auto_compare_page import AutoComparePage
from tests.e2e.pages.navigation import Navigation


class TestAutoCompareModels:
    """Test cases for Auto Pairwise Comparison."""
    
    def test_navigate_to_auto_compare_page(self, app_page: Page):
        """Test navigation to Auto Pairwise Comparison page."""
        nav = Navigation(app_page)
        nav.navigate_to_auto_compare()
        
        auto_compare_page = AutoComparePage(app_page)
        auto_compare_page.wait_for_page_load()
        
        # Verify page loaded
        assert auto_compare_page.is_visible("h2:has-text('Auto Compare Two Models')")
    
    @pytest.mark.skip(reason="Requires model availability and long execution time")
    def test_auto_compare_workflow(self, app_page: Page):
        """Test complete auto compare workflow."""
        auto_compare_page = AutoComparePage(app_page)
        auto_compare_page.navigate()
        
        # Enter question
        question = "What is the capital of Indonesia?"
        auto_compare_page.enter_question(question)
        
        # Select models (assuming models are available)
        # This would need to be adjusted based on available models
        auto_compare_page.select_model_a("llama3")
        auto_compare_page.select_model_b("mistral")
        
        # Toggle save to DB off
        auto_compare_page.toggle_save_to_db(False)
        
        # Click generate and judge
        auto_compare_page.click_generate_and_judge()
        
        # Wait for completion (this can take several minutes)
        auto_compare_page.wait_for_generation_complete(timeout=300000)  # 5 minutes
        
        # Verify results
        assert auto_compare_page.is_judgment_displayed()
        
        responses = auto_compare_page.get_generated_responses()
        # Responses might be empty if models aren't available, but structure should be there
        assert isinstance(responses, dict)
    
    def test_auto_compare_ui_elements(self, app_page: Page):
        """Test that all UI elements are present."""
        auto_compare_page = AutoComparePage(app_page)
        auto_compare_page.navigate()
        
        # Verify key UI elements exist
        # Streamlit textareas don't have placeholder attributes, use label-based selectors
        assert auto_compare_page.is_visible("label:has-text('Question'), label:has-text('Task')") or auto_compare_page.is_visible("textarea")
        assert auto_compare_page.is_visible("button:has-text('Generate')")

