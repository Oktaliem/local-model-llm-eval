"""
Page Object for Auto Single Response Grading feature
"""
from playwright.sync_api import Page
from .base_page import BasePage
import time


class AutoSinglePage(BasePage):
    """Page Object for Auto Single Response Grading."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.page_name = "🤖 Auto Single Response Grading"
    
    def navigate(self) -> None:
        """Navigate to Auto Single Response Grading page."""
        super().navigate()
        self.navigate_to_page(self.page_name)
        self.wait_for_page_load()
    
    def wait_for_page_load(self, timeout: int = 10000) -> None:
        """Wait for the auto single page to load."""
        self.page.wait_for_selector("h2:has-text('Auto Single Response Grading')", timeout=timeout)
        time.sleep(1)
    
    def enter_question(self, question: str) -> None:
        """Enter question/task."""
        # Streamlit renders textareas with labels as text above them
        # The first textarea on the page is typically the question field
        try:
            # Strategy 1: Find text containing "Question/Task:" and get the following textarea
            question_text = self.page.locator("text=/Question.*Task|Task.*Question/i").first
            if question_text.is_visible(timeout=2000):
                # Get the textarea that comes after this text
                textarea = question_text.locator(".. >> textarea").first
                if not textarea.is_visible(timeout=1000):
                    # Alternative: find first textarea in the same section
                    textarea = self.page.locator("textarea").first
                textarea.fill(question)
                return
        except Exception:
            pass
        
        # Strategy 2: Use first textarea (most reliable - first textarea is usually question)
        self.page.locator("textarea").first.fill(question)
    
    def select_model(self, model: str) -> None:
        """Select model for response generation."""
        # Model selectbox
        model_selector = "div:has-text('Select Model'), div:has-text('Response Generator Model') >> .. >> select, div:has-text('Select Model') >> .. >> [role='combobox']"
        if not self.is_visible(model_selector):
            # Try alternative selector
            model_selector = "select, [role='combobox']"
        self.select_option(model_selector, model)
    
    def enter_criteria(self, criteria: str) -> None:
        """Enter custom evaluation criteria (optional)."""
        criteria_selector = "textarea[placeholder*='Criteria'], textarea[placeholder*='criteria']"
        if self.is_visible(criteria_selector):
            self.fill(criteria_selector, criteria)
    
    def toggle_save_to_db(self, save: bool = True) -> None:
        """Toggle 'Save to DB' checkbox."""
        checkbox_selector = "input[type='checkbox'][key*='save'], label:has-text('Save to DB') >> input"
        checkbox = self.page.locator(checkbox_selector).first
        if checkbox.is_visible():
            if checkbox.is_checked() != save:
                checkbox.click()
    
    def click_generate_and_evaluate(self) -> None:
        """Click the 'Generate & Evaluate' button."""
        button_selector = "button:has-text('Generate & Evaluate'), button:has-text('📊 Generate')"
        self.click(button_selector)
        time.sleep(1)
    
    def wait_for_generation_complete(self, timeout: int = 120000) -> None:
        """Wait for response generation to complete."""
        # Wait for generated response to appear
        result_selector = "div:has-text('Response Generated'), div:has-text('Generated Response'), textarea[disabled]"
        self.page.wait_for_selector(result_selector, timeout=timeout)
        time.sleep(2)
    
    def wait_for_evaluation_complete(self, timeout: int = 180000) -> None:
        """Wait for evaluation to complete."""
        result_selector = "div:has-text('Evaluation Results'), div:has-text('Evaluation Complete'), div:has-text('Score')"
        self.page.wait_for_selector(result_selector, timeout=timeout)
        time.sleep(2)
    
    def get_generated_response(self) -> str:
        """Get generated response."""
        # Try to get the generated response from disabled textarea
        response_selector = "textarea[disabled], div:has-text('Generated Response') >> .. >> textarea"
        if self.is_visible(response_selector):
            return self.get_text(response_selector)
        return ""
    
    def get_evaluation_result(self) -> dict:
        """Get the evaluation result."""
        result = {}
        
        # Try to extract score
        score_match = self.page.locator("text=/Score:?\\s*([0-9.]+)/i")
        if score_match.count() > 0:
            result["score"] = score_match.first.inner_text()
        
        # Get full evaluation text
        evaluation_text = self.page.locator("div:has-text('Evaluation Results'), div:has-text('Score')").first.inner_text()
        result["evaluation_text"] = evaluation_text
        
        return result
    
    def is_evaluation_displayed(self) -> bool:
        """Check if evaluation result is displayed."""
        return self.is_visible("div:has-text('Evaluation Results'), div:has-text('Score')")
    
    def is_generated_response_displayed(self) -> bool:
        """Check if generated response is displayed."""
        return self.is_visible("div:has-text('Response Generated'), div:has-text('Generated Response'), textarea[disabled]")

