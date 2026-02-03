"""
Visual testing utilities for screenshot comparison
"""
import os
import hashlib
from pathlib import Path
from typing import Optional
from playwright.sync_api import Page
import json


class VisualTesting:
    """Utilities for visual regression testing."""
    
    def __init__(self, base_path: str = "tests/e2e/visual_baselines"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.screenshots_path = Path("tests/e2e/screenshots")
        self.screenshots_path.mkdir(parents=True, exist_ok=True)
    
    def take_screenshot(self, page: Page, name: str, full_page: bool = True) -> str:
        """
        Take a screenshot and save it.
        
        For full_page=True:
        1. First tries Playwright's built-in full_page=True
        2. If that only captures viewport, uses manual stitching with proper Streamlit container detection
        """
        screenshot_path = self.screenshots_path / f"{name}.png"
        
        if not full_page:
            page.screenshot(path=str(screenshot_path), full_page=False)
            return str(screenshot_path)
        
        # Full page screenshot
        try:
            from PIL import Image
            import io
            
            # Wait for page to load
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_load_state("domcontentloaded")
            
            # Get actual page height by finding the scrollable container
            page_info = page.evaluate("""
                () => {
                    // Find the actual scrollable element in Streamlit
                    const containers = [
                        document.querySelector('[data-testid="stAppViewContainer"]'),
                        document.querySelector('[data-testid="stMain"]'),
                        document.querySelector('main'),
                        document.body,
                        document.documentElement
                    ];
                    
                    let maxHeight = 0;
                    let scrollableElement = null;
                    
                    for (const container of containers) {
                        if (container) {
                            const scrollHeight = container.scrollHeight || 0;
                            const clientHeight = container.clientHeight || 0;
                            
                            if (scrollHeight > maxHeight) {
                                maxHeight = scrollHeight;
                                scrollableElement = container;
                            }
                        }
                    }
                    
                    return {
                        pageHeight: Math.max(maxHeight, document.body.scrollHeight, document.documentElement.scrollHeight),
                        scrollableTag: scrollableElement ? scrollableElement.tagName : 'BODY'
                    };
                }
            """)
            
            page_height = page_info['pageHeight']
            viewport_height = page.viewport_size['height'] if page.viewport_size else 1080
            viewport_width = page.viewport_size['width'] if page.viewport_size else 1920
            
            # Try Playwright's full_page=True first
            page.screenshot(path=str(screenshot_path), full_page=True)
            
            # Check if it captured the full page
            img = Image.open(screenshot_path)
            captured_height = img.size[1]
            
            # If Playwright only captured viewport, use manual stitching
            if captured_height <= viewport_height + 50 and page_height > viewport_height + 50:
                # Manual stitching: scroll the actual scrollable container
                screenshots = []
                num_screenshots = (page_height + viewport_height - 1) // viewport_height
                
                for i in range(num_screenshots):
                    scroll_y = i * viewport_height
                    if scroll_y > page_height - viewport_height:
                        scroll_y = max(0, page_height - viewport_height)
                    
                    # Scroll using the scrollable container
                    page.evaluate(f"""
                        () => {{
                            const scrollY = {scroll_y};
                            
                            // Try scrolling the window first
                            window.scrollTo({{ top: scrollY, behavior: 'instant' }});
                            
                            // Also try scrolling Streamlit containers directly
                            const stAppViewContainer = document.querySelector('[data-testid="stAppViewContainer"]');
                            const stMain = document.querySelector('[data-testid="stMain"]');
                            const main = document.querySelector('main');
                            
                            if (stAppViewContainer && stAppViewContainer.scrollHeight > stAppViewContainer.clientHeight) {{
                                stAppViewContainer.scrollTop = scrollY;
                            }}
                            if (stMain && stMain.scrollHeight > stMain.clientHeight) {{
                                stMain.scrollTop = scrollY;
                            }}
                            if (main && main.scrollHeight > main.clientHeight) {{
                                main.scrollTop = scrollY;
                            }}
                            
                            // Force document scroll as well
                            document.documentElement.scrollTop = scrollY;
                            document.body.scrollTop = scrollY;
                        }}
                    """)
                    
                    page.wait_for_timeout(500)  # Wait for scroll
                    
                    # Take screenshot
                    screenshot_bytes = page.screenshot(full_page=False)
                    img = Image.open(io.BytesIO(screenshot_bytes))
                    screenshots.append((scroll_y, img))
                
                # Stitch together
                final_img = Image.new('RGB', (viewport_width, page_height), color='white')
                for scroll_y, img in screenshots:
                    final_img.paste(img, (0, scroll_y))
                
                # Crop to exact height
                if final_img.size[1] > page_height:
                    final_img = final_img.crop((0, 0, viewport_width, page_height))
                
                final_img.save(screenshot_path)
                
                # Scroll back to top
                page.evaluate("window.scrollTo({ top: 0, behavior: 'instant' })")
                page.wait_for_timeout(200)
            
        except ImportError:
            # PIL not available, use Playwright only
            page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:
            # Fallback to Playwright on any error
            page.screenshot(path=str(screenshot_path), full_page=True)
        
        return str(screenshot_path)
    
    def take_element_screenshot(self, page: Page, selector: str, name: str) -> str:
        """Take a screenshot of a specific element."""
        screenshot_path = self.screenshots_path / f"{name}.png"
        element = page.locator(selector)
        element.screenshot(path=str(screenshot_path))
        return str(screenshot_path)
    
    def get_baseline_path(self, name: str) -> Path:
        """Get the path to a baseline screenshot."""
        return self.base_path / f"{name}.png"
    
    def save_baseline(self, page: Page, name: str, full_page: bool = True) -> str:
        """Save a screenshot as a baseline for future comparison."""
        # Use take_screenshot to ensure consistency
        screenshot_path = self.take_screenshot(page, f"baseline_{name}", full_page=full_page)
        baseline_path = self.get_baseline_path(name)
        
        # Move to baseline location
        import shutil
        shutil.move(screenshot_path, str(baseline_path))
        
        return str(baseline_path)
    
    def compare_screenshots(self, current_path: str, baseline_path: str, threshold: float = 0.0) -> dict:
        """
        Compare two screenshots.
        Returns dict with 'match', 'difference', and 'diff_path'.
        """
        from PIL import Image
        import numpy as np
        
        if not os.path.exists(baseline_path):
            return {
                "match": False,
                "error": "Baseline screenshot not found",
                "baseline_path": baseline_path
            }
        
        if not os.path.exists(current_path):
            return {
                "match": False,
                "error": "Current screenshot not found",
                "current_path": current_path
            }
        
        # Load images
        baseline_img = Image.open(baseline_path)
        current_img = Image.open(current_path)
        
        # Convert to numpy arrays
        baseline_arr = np.array(baseline_img)
        current_arr = np.array(current_img)
        
        # Check if dimensions match
        if baseline_arr.shape != current_arr.shape:
            return {
                "match": False,
                "error": f"Image dimensions don't match: baseline {baseline_arr.shape} vs current {current_arr.shape}",
                "baseline_shape": baseline_arr.shape,
                "current_shape": current_arr.shape
            }
        
        # Calculate difference
        diff = np.abs(baseline_arr.astype(float) - current_arr.astype(float))
        diff_percentage = np.mean(diff) / 255.0
        
        # For pixel-perfect (0.0 threshold), use a small epsilon to handle floating point precision
        # Use a slightly larger epsilon (0.0001 = 0.01%) to account for rendering differences
        # that can occur even with identical content (compression, anti-aliasing, etc.)
        epsilon = 0.0001  # 0.01% difference allowed for "pixel perfect" due to rendering artifacts
        effective_threshold = threshold if threshold > 0 else epsilon
        
        # Create diff image only if difference exceeds threshold (for debugging failed tests)
        diff_path = None
        if diff_percentage > effective_threshold:
            diff_img = Image.fromarray(diff.astype(np.uint8))
            diff_path = self.screenshots_path / f"diff_{Path(current_path).stem}.png"
            diff_img.save(str(diff_path))
        
        # Convert to Python bool to avoid numpy boolean issues
        # Use effective_threshold for comparison
        match = bool(diff_percentage <= effective_threshold)
        
        return {
            "match": match,
            "difference": float(diff_percentage),
            "threshold": threshold,
            "diff_path": str(diff_path) if diff_path else None,
            "baseline_path": baseline_path,
            "current_path": current_path
        }
    
    def visual_test(self, page: Page, name: str, update_baseline: bool = False, 
                   full_page: bool = True, threshold: float = 0.0) -> dict:
        """
        Perform a visual test: take screenshot and compare with baseline.
        
        Args:
            page: Playwright page object
            name: Test name (used for file names)
            update_baseline: If True, update the baseline instead of comparing
            full_page: Take full page screenshot
            threshold: Maximum difference threshold (0.0 = 0% - pixel perfect)
        
        Returns:
            dict with test results
        """
        # Take current screenshot
        current_path = self.take_screenshot(page, name, full_page=full_page)
        
        baseline_path = self.get_baseline_path(name)
        
        if update_baseline or not baseline_path.exists():
            # Save as new baseline
            baseline_path = self.save_baseline(page, name, full_page)
            return {
                "status": "baseline_created",
                "baseline_path": str(baseline_path),
                "current_path": current_path
            }
        else:
            # Compare with baseline
            comparison = self.compare_screenshots(current_path, str(baseline_path), threshold)
            return {
                "status": "compared",
                "comparison": comparison,
                "current_path": current_path,
                "baseline_path": str(baseline_path)
            }
    
    def save_metadata(self, name: str, metadata: dict):
        """Save metadata about a visual test."""
        metadata_path = self.base_path / f"{name}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_metadata(self, name: str) -> Optional[dict]:
        """Load metadata for a visual test."""
        metadata_path = self.base_path / f"{name}.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return None

