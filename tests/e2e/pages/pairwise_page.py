"""
Page Object for Manual Pairwise Comparison feature
"""
from playwright.sync_api import Page
from .base_page import BasePage
import time


class PairwisePage(BasePage):
    """Page Object for Manual Pairwise Comparison."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.page_name = "🔀 Manual Pairwise Comparison"
    
    def navigate(self) -> None:
        """Navigate to Manual Pairwise Comparison page."""
        super().navigate()
        self.navigate_to_page(self.page_name)
        self.wait_for_page_load()
    
    def wait_for_page_load(self, timeout: int = 10000) -> None:
        """Wait for the pairwise page to load."""
        # Wait for the main header
        self.page.wait_for_selector("h2:has-text('Compare Two Responses')", timeout=timeout)
        time.sleep(1)
    
    def enter_question(self, question: str) -> None:
        """Enter question/task."""
        # Streamlit renders textareas with labels as text above them
        # The first textarea on the page is typically the question field
        # Find textarea near text containing "Question" or "Task"
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
    
    def enter_response_a(self, response: str) -> None:
        """Enter Response A."""
        # Response A textarea - look for textarea with key="response_a" or placeholder
        response_a_selector = "textarea[placeholder*='Response A'], textarea[key='response_a']"
        # If not found, try to find by position (first textarea in Response A column)
        if not self.is_visible(response_a_selector):
            # Try finding by column structure
            response_a_selector = "div:has-text('Response A') >> .. >> textarea"
        self.fill(response_a_selector, response)
    
    def enter_response_b(self, response: str) -> None:
        """Enter Response B."""
        # Response B textarea
        response_b_selector = "textarea[placeholder*='Response B'], textarea[key='response_b']"
        if not self.is_visible(response_b_selector):
            response_b_selector = "div:has-text('Response B') >> .. >> textarea"
        self.fill(response_b_selector, response)
    
    def select_judge_model(self, model: str) -> None:
        """Select judge model from sidebar."""
        # Judge model is in sidebar
        sidebar_selector = "section[data-testid='stSidebar']"
        selectbox_selector = f"{sidebar_selector} select, {sidebar_selector} [role='combobox']"
        if self.is_visible(selectbox_selector):
            self.select_option(selectbox_selector, model)
    
    def toggle_save_to_db(self, save: bool = True) -> None:
        """Toggle 'Save to DB' checkbox."""
        checkbox_selector = "input[type='checkbox'][key*='save'], label:has-text('Save to DB') >> input"
        checkbox = self.page.locator(checkbox_selector).first
        if checkbox.is_visible():
            if checkbox.is_checked() != save:
                checkbox.click()
    
    def click_judge_responses(self) -> None:
        """Click the 'Judge Responses' button."""
        button_selector = "button:has-text('Judge Responses'), button:has-text('⚖️ Judge')"
        self.click(button_selector)
        time.sleep(1)  # Wait for button click to register
    
    def wait_for_judgment_complete(self, timeout: int = 120000) -> None:
        """Wait for judgment to complete."""
        # Wait for judgment result to appear
        # Look for the success message first (most specific)
        # Then check for judgment content or metrics
        try:
            # Strategy 1: Look for the success message "✅ Judgment Complete!"
            success_selector = "div:has-text('Judgment Complete')"
            self.page.wait_for_selector(success_selector, timeout=timeout, state="visible")
        except Exception:
            # Strategy 2: Look for judgment header or content
            try:
                judgment_selector = "h3:has-text('Judgment'), div:has-text('🎯 Judgment')"
                self.page.wait_for_selector(judgment_selector, timeout=timeout, state="visible")
            except Exception:
                # Strategy 3: Look for metrics (Score A, Score B, Winner)
                metrics_selector = "div:has-text('Score A'), div:has-text('Score B'), div:has-text('Winner')"
                self.page.wait_for_selector(metrics_selector, timeout=timeout, state="visible")
        time.sleep(2)  # Give it time to fully render
    
    def get_judgment_result(self) -> dict:
        """Get the judgment result."""
        result = {}
        
        # Try to extract winner, scores, and reasoning
        judgment_text = self.page.locator("div:has-text('Judgment'), div:has-text('Winner')").first.inner_text()
        result["judgment_text"] = judgment_text
        
        # Try to extract winner
        winner_match = self.page.locator("text=/Winner:?\\s*([AB])/i")
        if winner_match.count() > 0:
            result["winner"] = winner_match.first.inner_text()
        
        # Try to extract scores
        score_matches = self.page.locator("text=/Score [AB]:?\\s*([0-9.]+)/i")
        if score_matches.count() > 0:
            scores = [score.inner_text() for score in score_matches.all()]
            result["scores"] = scores
        
        return result
    
    def is_judgment_displayed(self) -> bool:
        """Check if judgment result is displayed."""
        return self.is_visible("div:has-text('Judgment'), div:has-text('Winner'), div:has-text('Score')")
    
    def click_new_evaluation(self) -> None:
        """Click the 'New Evaluation' button."""
        button_selector = "button:has-text('New Evaluation'), button:has-text('🔄 New')"
        if self.is_visible(button_selector):
            self.click(button_selector)
            time.sleep(1)

