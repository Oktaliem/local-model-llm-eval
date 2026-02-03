"""
Navigation helper for the application
"""
from playwright.sync_api import Page
from .base_page import BasePage
import time


class Navigation(BasePage):
    """Navigation helper for moving between pages."""
    
    NAVIGATION_OPTIONS = [
        "🔀 Manual Pairwise Comparison",
        "🤖 Auto Pairwise Comparison",
        "📊 Single Response Grading",
        "🤖 Auto Single Response Grading",
        "🎯 Comprehensive Evaluation",
        "💻 Code-Based Evaluation",
        "📦 Batch Evaluation",
        "👤 Human Evaluation",
        "🔀 Router Evaluation",
        "🎓 Skills Evaluation",
        "🛤️ Trajectory Evaluation",
        "📈 Advanced Analytics",
        "💾 Saved Judgments & Dashboard",
        "🧪 A/B Testing",
        "📋 Evaluation Templates",
        "🎯 Custom Metrics"
    ]
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def navigate_to_pairwise(self) -> None:
        """Navigate to Manual Pairwise Comparison."""
        self.navigate_to_page("🔀 Manual Pairwise Comparison")
    
    def navigate_to_auto_compare(self) -> None:
        """Navigate to Auto Pairwise Comparison."""
        self.navigate_to_page("🤖 Auto Pairwise Comparison")
    
    def navigate_to_single_grading(self) -> None:
        """Navigate to Single Response Grading."""
        self.navigate_to_page("📊 Single Response Grading")
    
    def navigate_to_auto_single_grading(self) -> None:
        """Navigate to Auto Single Response Grading."""
        self.navigate_to_page("🤖 Auto Single Response Grading")
    
    def navigate_to_comprehensive(self) -> None:
        """Navigate to Comprehensive Evaluation."""
        self.navigate_to_page("🎯 Comprehensive Evaluation")
    
    def navigate_to_code_eval(self) -> None:
        """Navigate to Code-Based Evaluation."""
        self.navigate_to_page("💻 Code-Based Evaluation")
    
    def navigate_to_batch_eval(self) -> None:
        """Navigate to Batch Evaluation."""
        self.navigate_to_page("📦 Batch Evaluation")
    
    def navigate_to_human_eval(self) -> None:
        """Navigate to Human Evaluation."""
        self.navigate_to_page("👤 Human Evaluation")
    
    def navigate_to_router_eval(self) -> None:
        """Navigate to Router Evaluation."""
        self.navigate_to_page("🔀 Router Evaluation")
    
    def navigate_to_skills_eval(self) -> None:
        """Navigate to Skills Evaluation."""
        self.navigate_to_page("🎓 Skills Evaluation")
    
    def navigate_to_trajectory_eval(self) -> None:
        """Navigate to Trajectory Evaluation."""
        self.navigate_to_page("🛤️ Trajectory Evaluation")
    
    def navigate_to_analytics(self) -> None:
        """Navigate to Advanced Analytics."""
        self.navigate_to_page("📈 Advanced Analytics")
    
    def navigate_to_saved_judgments(self) -> None:
        """Navigate to Saved Judgments & Dashboard."""
        self.navigate_to_page("💾 Saved Judgments & Dashboard")
    
    def navigate_to_ab_testing(self) -> None:
        """Navigate to A/B Testing."""
        self.navigate_to_page("🧪 A/B Testing")
    
    def navigate_to_templates(self) -> None:
        """Navigate to Evaluation Templates."""
        self.navigate_to_page("📋 Evaluation Templates")
    
    def navigate_to_custom_metrics(self) -> None:
        """Navigate to Custom Metrics."""
        self.navigate_to_page("🎯 Custom Metrics")
    
    def verify_page_loaded(self, expected_title: str) -> bool:
        """Verify that a page has loaded by checking for expected content."""
        # Wait a bit for page to load
        time.sleep(2)
        # Check if expected title or content is visible
        return self.is_visible(f"h1, h2, h3:has-text('{expected_title}')")

