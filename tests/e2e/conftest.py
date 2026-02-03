"""
Pytest configuration and fixtures for e2e tests
"""
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
import os
import time
from typing import Generator


# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8501")
API_BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8000")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # Slow down operations by milliseconds
TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30000"))  # 30 seconds default

# Viewport configuration - ensure consistent size across environments
VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1920"))
VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
DEVICE_SCALE_FACTOR = float(os.getenv("DEVICE_SCALE_FACTOR", "1.0"))  # Ensure consistent pixel density


@pytest.fixture(scope="session")
def playwright():
    """Initialize Playwright."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright) -> Generator[Browser, None, None]:
    """Create a browser instance with consistent rendering settings."""
    browser = playwright.chromium.launch(
        headless=HEADLESS,
        slow_mo=SLOW_MO,
        args=[
            # Disable hardware acceleration for consistent rendering
            "--disable-gpu",
            "--disable-software-rasterizer",
            # Force consistent font rendering
            "--disable-font-subpixel-positioning",
            "--disable-lcd-text",
            # Disable features that can cause rendering differences
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ] if HEADLESS else [],
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a browser context for each test with consistent viewport."""
    context = browser.new_context(
        viewport={
            "width": VIEWPORT_WIDTH,
            "height": VIEWPORT_HEIGHT
        },
        device_scale_factor=DEVICE_SCALE_FACTOR,
        ignore_https_errors=True,
        # Ensure consistent rendering
        color_scheme="light",
        reduced_motion="no-preference",
        # Force consistent font rendering
        locale="en-US",
        timezone_id="UTC",
        # Disable hardware acceleration for consistent rendering
        java_script_enabled=True,
    )
    # Set additional browser flags for consistent rendering
    # Note: These are set at browser launch, not context level
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = context.new_page()
    page.set_default_timeout(TIMEOUT)
    yield page
    page.close()


@pytest.fixture(scope="function")
def app_page(page: Page) -> Page:
    """Navigate to the app and return the page."""
    page.goto(BASE_URL)
    # Wait for Streamlit to load
    page.wait_for_selector("h1", timeout=10000)
    return page


@pytest.fixture(scope="function")
def api_client():
    """Create an API client for API testing."""
    import httpx
    return httpx.Client(base_url=API_BASE_URL, timeout=30.0)


# Helper fixtures
@pytest.fixture
def wait_for_streamlit():
    """Wait for Streamlit to finish loading."""
    def _wait(page: Page, timeout: int = 10000):
        # Wait for main content to be visible
        page.wait_for_selector("h1", timeout=timeout)
        # Wait a bit more for any async operations
        time.sleep(1)
    return _wait


@pytest.fixture
def take_screenshot():
    """Take a screenshot helper."""
    def _screenshot(page: Page, name: str):
        screenshot_dir = "tests/e2e/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        page.screenshot(path=f"{screenshot_dir}/{name}.png")
    return _screenshot


@pytest.fixture
def update_baseline(request):
    """Fixture to check if baseline should be updated.
    
    Can be set via:
    1. Environment variable: UPDATE_BASELINES=true
    2. Pytest option: --update-baseline
    """
    import os
    # Check environment variable first
    env_update = os.getenv("UPDATE_BASELINES", "").lower() == "true"
    # Check pytest option
    pytest_option = request.config.getoption("--update-baseline", default=False)
    return env_update or pytest_option


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--update-baseline",
        action="store_true",
        default=False,
        help="Update visual test baselines instead of comparing"
    )

