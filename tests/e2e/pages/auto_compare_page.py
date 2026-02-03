"""
Page Object for Auto Pairwise Comparison feature
"""
from playwright.sync_api import Page
from .base_page import BasePage
import time


class AutoComparePage(BasePage):
    """Page Object for Auto Pairwise Comparison."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.page_name = "🤖 Auto Pairwise Comparison"
    
    def navigate(self) -> None:
        """Navigate to Auto Pairwise Comparison page."""
        super().navigate()
        self.navigate_to_page(self.page_name)
        self.wait_for_page_load()
    
    def wait_for_page_load(self, timeout: int = 10000) -> None:
        """Wait for the auto compare page to load."""
        self.page.wait_for_selector("h2:has-text('Auto Compare Two Models')", timeout=timeout)
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
    
    def select_model_a(self, model: str) -> None:
        """Select Model A."""
        # Model A selectbox
        model_a_selector = "div:has-text('Model A') >> .. >> select, div:has-text('Model A') >> .. >> [role='combobox']"
        if not self.is_visible(model_a_selector):
            # Try alternative selector
            model_a_selector = "select:has-text('Model A'), [role='combobox']:has-text('Model A')"
        self.select_option(model_a_selector, model)
    
    def select_model_b(self, model: str) -> None:
        """Select Model B."""
        # Model B selectbox
        model_b_selector = "div:has-text('Model B') >> .. >> select, div:has-text('Model B') >> .. >> [role='combobox']"
        if not self.is_visible(model_b_selector):
            model_b_selector = "select:has-text('Model B'), [role='combobox']:has-text('Model B')"
        self.select_option(model_b_selector, model)
    
    def toggle_save_to_db(self, save: bool = True) -> None:
        """Toggle 'Save to DB' checkbox."""
        checkbox_selector = "input[type='checkbox'][key*='save'], label:has-text('Save to DB') >> input"
        checkbox = self.page.locator(checkbox_selector).first
        if checkbox.is_visible():
            if checkbox.is_checked() != save:
                checkbox.click()
    
    def click_generate_and_judge(self) -> None:
        """Click the 'Generate & Judge' button."""
        button_selector = "button:has-text('Generate & Judge'), button:has-text('🚀 Generate')"
        self.click(button_selector)
        time.sleep(1)
    
    def wait_for_generation_complete(self, timeout: int = 120000) -> None:
        """Wait for response generation and judgment to complete."""
        # Wait for judgment result
        result_selector = "div:has-text('Judgment'), div:has-text('Winner'), div:has-text('Response A generated'), div:has-text('Response B generated')"
        self.page.wait_for_selector(result_selector, timeout=timeout)
        time.sleep(2)
    
    def get_generated_responses(self) -> dict:
        """Get generated responses."""
        responses = {}
        
        # Try to get Response A
        response_a_selector = "div:has-text('Response A'), textarea[disabled]:has-text('')"
        if self.is_visible(response_a_selector):
            responses["response_a"] = self.get_text(response_a_selector)
        
        # Try to get Response B
        response_b_selector = "div:has-text('Response B'), textarea[disabled]:has-text('')"
        if self.is_visible(response_b_selector):
            responses["response_b"] = self.get_text(response_b_selector)
        
        return responses
    
    def get_judgment_result(self) -> dict:
        """Get the judgment result."""
        result = {}
        judgment_text = self.page.locator("div:has-text('Judgment'), div:has-text('Winner')").first.inner_text()
        result["judgment_text"] = judgment_text
        return result
    
    def is_judgment_displayed(self) -> bool:
        """Check if judgment result is displayed."""
        return self.is_visible("div:has-text('Judgment'), div:has-text('Winner')")

