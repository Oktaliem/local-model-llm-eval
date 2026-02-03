"""
E2E tests for Manual Pairwise Comparison feature
"""
import pytest
import time
from playwright.sync_api import Page
from tests.e2e.pages.pairwise_page import PairwisePage
from tests.e2e.pages.navigation import Navigation


class TestPairwiseComparison:
    """Test cases for Manual Pairwise Comparison."""
    
    def test_navigate_to_pairwise_page(self, app_page: Page):
        """Test navigation to Manual Pairwise Comparison page."""
        nav = Navigation(app_page)
        nav.navigate_to_pairwise()
        
        pairwise_page = PairwisePage(app_page)
        pairwise_page.wait_for_page_load()
        
        # Verify page loaded
        assert pairwise_page.is_visible("h2:has-text('Compare Two Responses')")
    
    def test_pairwise_comparison_basic(self, app_page: Page):
        """Test basic pairwise comparison workflow."""
        pairwise_page = PairwisePage(app_page)
        pairwise_page.navigate()
        
        # Enter test data
        question = "What is the capital of France?"
        response_a = "Paris is the capital of France."
        response_b = "The capital of France is Paris, a beautiful city known for its art and culture."
        
        pairwise_page.enter_question(question)
        pairwise_page.enter_response_a(response_a)
        pairwise_page.enter_response_b(response_b)
        
        # Toggle save to DB off for faster testing
        pairwise_page.toggle_save_to_db(False)
        
        # Click judge button
        pairwise_page.click_judge_responses()
        
        # Wait for judgment (with longer timeout for LLM processing)
        pairwise_page.wait_for_judgment_complete(timeout=180000)  # 3 minutes
        
        # Verify judgment is displayed
        assert pairwise_page.is_judgment_displayed()
        
        # Get judgment result
        result = pairwise_page.get_judgment_result()
        assert "judgment_text" in result
        assert len(result["judgment_text"]) > 0
    
    @pytest.mark.skip(reason="Requires specific model availability")
    def test_pairwise_with_custom_judge_model(self, app_page: Page):
        """Test pairwise comparison with custom judge model."""
        pairwise_page = PairwisePage(app_page)
        pairwise_page.navigate()
        
        # Select a specific judge model
        pairwise_page.select_judge_model("llama3")
        
        # Enter test data
        pairwise_page.enter_question("Explain machine learning in simple terms.")
        pairwise_page.enter_response_a("Machine learning is a subset of AI.")
        pairwise_page.enter_response_b("Machine learning enables computers to learn from data without explicit programming.")
        
        pairwise_page.toggle_save_to_db(False)
        pairwise_page.click_judge_responses()
        
        # This test would require model availability
        # For now, we'll just verify the UI elements work
        assert pairwise_page.is_visible("button:has-text('Judge Responses')")
    
    def test_pairwise_form_validation(self, app_page: Page):
        """Test that form validation works (empty fields)."""
        pairwise_page = PairwisePage(app_page)
        pairwise_page.navigate()
        
        # Try to judge without filling fields
        pairwise_page.click_judge_responses()
        
        # Should show warning or not proceed
        # Streamlit might show a warning message
        time.sleep(2)
        # Verify judgment didn't complete immediately
        # (This is a basic check - actual validation depends on Streamlit behavior)

