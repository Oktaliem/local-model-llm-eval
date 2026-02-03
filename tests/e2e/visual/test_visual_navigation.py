"""
Visual regression tests for navigation and page layouts
"""
import pytest
import time
from playwright.sync_api import Page
from tests.e2e.pages.navigation import Navigation
from tests.e2e.utils.visual_testing import VisualTesting


class TestVisualNavigation:
    """Visual regression tests for navigation."""
    
    @pytest.fixture(scope="class")
    def visual_tester(self):
        """Create visual testing instance."""
        return VisualTesting()
    
    NAVIGATION_PAGES = [
        ("pairwise", "🔀 Manual Pairwise Comparison", "Compare Two Responses"),
        ("auto_compare", "🤖 Auto Pairwise Comparison", "Auto Compare Two Models"),
        ("single_grading", "📊 Single Response Grading", "Grade Single Response"),
        ("comprehensive", "🎯 Comprehensive Evaluation", "Comprehensive Evaluation"),
        ("code_eval", "💻 Code-Based Evaluation", "Code-Based Evaluation"),
        ("batch_eval", "📦 Batch Evaluation", "Batch Evaluation"),
        ("human_eval", "👤 Human Evaluation", "Human Evaluation"),
        ("router_eval", "🔀 Router Evaluation", "Router Evaluation"),
        ("skills_eval", "🎓 Skills Evaluation", "Skills Evaluation"),
        ("trajectory_eval", "🛤️ Trajectory Evaluation", "Trajectory Evaluation"),
        ("analytics", "📈 Advanced Analytics", "Advanced Analytics"),
        ("saved_judgments", "💾 Saved Judgments & Dashboard", "Saved Judgments"),
        ("ab_testing", "🧪 A/B Testing", "A/B Testing"),
        ("templates", "📋 Evaluation Templates", "Evaluation Templates"),
        ("custom_metrics", "🎯 Custom Metrics", "Custom Metrics"),
    ]
    
    @pytest.mark.parametrize("page_id,page_name,expected_content", NAVIGATION_PAGES)
    def test_page_visual_layout(self, app_page: Page, visual_tester: VisualTesting, 
                                page_id: str, page_name: str, expected_content: str,
                                update_baseline):
        """
        Visual test for each page layout.
        
        Set update_baseline=True to update baseline screenshots.
        """
        nav = Navigation(app_page)
        
        # Navigate to the page
        nav.navigate_to_page(page_name)
        
        # Wait for page to fully load and stabilize
        time.sleep(5)
        # Wait for any dynamic content to finish loading
        app_page.wait_for_load_state("networkidle", timeout=10000)
        
        # Take full page screenshot and compare
        result = visual_tester.visual_test(
            app_page,
            name=f"page_{page_id}_full",
            update_baseline=update_baseline,
            full_page=True,
            threshold=0.0  # 0% difference threshold (pixel perfect)
        )
        
        if result["status"] == "compared":
            comparison = result["comparison"]
            
            # Handle error cases (e.g., dimension mismatch)
            if "error" in comparison:
                pytest.fail(
                    f"Visual test error for {page_name}: {comparison['error']}. "
                    f"Baseline shape: {comparison.get('baseline_shape', 'unknown')}, "
                    f"Current shape: {comparison.get('current_shape', 'unknown')}"
                )
            
            assert comparison["match"], (
                f"Visual regression detected for {page_name}. "
                f"Difference: {comparison.get('difference', 0):.2%} "
                f"(threshold: {comparison.get('threshold', 0):.2%}). "
                f"Diff image: {comparison.get('diff_path', 'N/A')}"
            )
        elif result["status"] == "baseline_created":
            # After creating baseline, verify it matches (should be 0% difference)
            # Re-run comparison to ensure baseline was saved correctly
            comparison = visual_tester.compare_screenshots(
                result["current_path"], result["baseline_path"], threshold=0.0
            )
            
            # Handle error cases
            if "error" in comparison:
                pytest.fail(
                    f"Baseline creation error for {page_name}: {comparison['error']}"
                )
            
            assert comparison["match"], (
                f"Baseline created for {page_name} but verification failed. "
                f"Difference: {comparison['difference']:.2%}"
            )
    
    def test_sidebar_visual(self, app_page: Page, visual_tester: VisualTesting,
                           update_baseline):
        """Visual test for sidebar navigation."""
        # Wait for sidebar to render
        time.sleep(2)
        
        # Take screenshot of sidebar only
        sidebar_selector = "section[data-testid='stSidebar']"
        sidebar = app_page.locator(sidebar_selector)
        
        if sidebar.is_visible():
            # Take element screenshot
            screenshot_path = visual_tester.take_element_screenshot(
                app_page, sidebar_selector, "sidebar_navigation"
            )
            
            baseline_path = visual_tester.get_baseline_path("sidebar_navigation")
            
            if update_baseline or not baseline_path.exists():
                # Save baseline
                sidebar.screenshot(path=str(baseline_path))
                # After updating baseline, compare to ensure it matches (should be 0% difference)
                comparison = visual_tester.compare_screenshots(
                    screenshot_path, str(baseline_path), threshold=0.0
                )
                assert comparison["match"], (
                    f"Baseline updated but comparison failed. "
                    f"Difference: {comparison['difference']:.2%}"
                )
            else:
                # Compare
                comparison = visual_tester.compare_screenshots(
                    screenshot_path, str(baseline_path), threshold=0.0
                )
                assert comparison["match"], (
                    f"Sidebar visual regression detected. "
                    f"Difference: {comparison['difference']:.2%}"
                )
    
    def test_main_layout_visual(self, app_page: Page, visual_tester: VisualTesting,
                               update_baseline):
        """Visual test for main application layout."""
        # Wait for page to load
        time.sleep(2)
        
        result = visual_tester.visual_test(
            app_page,
            name="main_layout",
            update_baseline=update_baseline,
            full_page=True,
            threshold=0.0
        )
        
        if result["status"] == "compared":
            comparison = result["comparison"]
            assert comparison["match"], (
                f"Main layout visual regression detected. "
                f"Difference: {comparison['difference']:.2%}"
            )
        elif result["status"] == "baseline_created":
            # After creating baseline, verify it matches (should be 0% difference)
            comparison = visual_tester.compare_screenshots(
                result["current_path"], result["baseline_path"], threshold=0.0
            )
            assert comparison["match"], (
                f"Baseline created for main layout but verification failed. "
                f"Difference: {comparison['difference']:.2%}"
            )
    

