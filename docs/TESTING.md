## Testing

The project includes end-to-end (E2E) tests using **Playwright** and the **Page Object Model (POM)** pattern.

---

## Test Framework Features

- Page Object Model for maintainable selectors and interactions  
- Visual regression testing with screenshot comparison  
- Navigation tests for all 16 navigation pages (6 categories)  
- Playwright-based browser automation

---

## Setup

### 1. Install testing dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
python -m playwright install chromium
```

---

## Running Tests

### Functional Tests

```bash
# Run all functional tests
pytest tests/e2e/functional/ -v

# Run specific functional test
pytest tests/e2e/functional/test_all_navigation.py -v

# Headed mode (see browser)
HEADLESS=false pytest tests/e2e/functional/test_all_navigation.py -v
```

### Visual Regression Tests

```bash
# Create/update baselines (first time or after UI changes)
pytest tests/e2e/visual/test_visual_navigation.py --update-baseline -v

# Compare with baselines
pytest tests/e2e/visual/test_visual_navigation.py -v
```

### All E2E Tests

```bash
pytest tests/e2e/ -v
```

---

## Test Coverage

- Navigation tests across all 16 pages and 6 categories  
- Visual regression tests for page layouts and navigation  
- Reusable page object models for core flows  

---

## Test Structure

```text
tests/
├── e2e/                    # E2E test cases
│   ├── functional/         # Functional E2E tests
│   │   ├── test_all_navigation.py
│   │   ├── test_pairwise_comparison.py
│   │   ├── test_auto_compare_models.py
│   │   └── test_single_grading.py
│   ├── visual/             # Visual regression tests
│   │   ├── test_visual_navigation.py
│   │   ├── screenshots/    # Test screenshots
│   │   └── visual_baselines/  # Baseline images
│   ├── pages/              # Page Object Models
│   │   ├── base_page.py
│   │   ├── pairwise_page.py
│   │   ├── auto_compare_page.py
│   │   └── navigation.py
│   └── utils/              # Shared test utilities
│       ├── test_data.py
│       └── visual_testing.py
```

---

## Configuration

Environment variables for tests:

- `TEST_BASE_URL` – Base URL for Streamlit app (default: `http://localhost:8501`)  
- `TEST_API_BASE_URL` – Base URL for API server (default: `http://localhost:8000`)  
- `HEADLESS` – Whether to run browser headless (default: `true`)  
- `SLOW_MO` – Delay in ms between operations (default: `0`)  
- `TEST_TIMEOUT` – Default timeout in ms (default: `30000`)  

---

## Test Reports

- HTML reports generated in `reports/report.html`  
- Screenshots stored in `tests/e2e/visual/screenshots/`  
- Visual baselines in `tests/e2e/visual/visual_baselines/`  

For more details on tests, also see `tests/README.md`.

