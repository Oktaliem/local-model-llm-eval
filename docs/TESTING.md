# Testing Framework for LLM & AI Agent Evaluation

This directory contains comprehensive testing framework for the LLM Evaluation Framework, including unit tests, E2E tests, and testing utilities.

## Project Overview

`llm-evaluation-simple-app` is an open-source framework for evaluating LLMs and AI agents using the **"LLM as a Judge"** approach. It provides comprehensive evaluation capabilities including pairwise comparison, single-response grading, batch evaluation, and specialized metrics for AI agents.

For full project documentation, see the main [README.md](../README.md).

---

## Table of Contents
1. [Unit Testing](#unit-testing)
2. [Mutation Testing](#mutation-testing)
3. [E2E Testing Overview](#e2e-testing-overview)
4. [Setup](#setup)
5. [Running Tests](#running-tests)
6. [Test Structure](#test-structure)
7. [Visual Regression Testing](#visual-regression-testing)
8. [Docker Testing](#docker-testing)
9. [Configuration](#configuration)
10. [Reports](#reports)

---

## Unit Testing

The project includes comprehensive unit tests with **100% code coverage** for all backend and core modules.

### Unit Test Coverage

- ✅ **Backend API Layer**: 100% coverage (routes, middleware, models)
- ✅ **Backend Services**: 100% coverage (all service modules)
- ✅ **Core Domain Layer**: 100% coverage (strategies, models, factory)
- ✅ **Core Infrastructure**: 100% coverage (DB, LLM clients)
- ✅ **Core Services**: 100% coverage (evaluation, batch, judgment services)
- ✅ **Core Common**: 100% coverage (utilities, settings, sanitization)

### Running Unit Tests

**Run all unit tests:**
```bash
pytest tests/unit/ -v
```

**Run with coverage report:**
```bash
pytest tests/unit/ --cov=core --cov=backend --cov-report=term-missing -v
```

**Run with HTML coverage report:**
```bash
pytest tests/unit/ --cov=core --cov=backend --cov-report=html -v
# Then open: htmlcov/index.html
```

**Run specific test file:**
```bash
pytest tests/unit/test_ollama_client.py -v
```

**Run tests matching a pattern:**
```bash
pytest tests/unit/ -k ollama -v
```

For detailed unit testing documentation, see [documentation/test_guide/TESTING_GUIDE.md](../documentation/test_guide/TESTING_GUIDE.md).

---

## Mutation Testing

The project uses `mutmut` for mutation testing to evaluate test quality beyond code coverage.

### Running Mutation Tests

```bash
# Install mutmut
pip install mutmut

# Run mutation testing
mutmut run

# View results
mutmut results

# Show specific mutant
mutmut show <mutant_id>
```

For detailed mutation testing documentation, see [documentation/MUTATION_TESTING_README.md](../documentation/MUTATION_TESTING_README.md).

---

## E2E Testing Overview

The E2E testing framework provides:
- **Browser Automation**: Using Playwright for reliable cross-browser testing
- **Page Object Model**: Organized, maintainable test code
- **Visual Regression Testing**: Automated screenshot comparison
- **Docker Support**: Run tests in isolated containers
- **Comprehensive Coverage**: Tests for all 15 application pages

---

## Setup

### Option 1: Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   python -m playwright install chromium
   ```

3. **Start the application:**
   ```bash
   docker-compose up -d llm-judge-app
   ```

### Option 2: Docker Setup (Recommended)

All tests can be run in Docker containers for consistent, isolated testing.

---

## Running Tests

### Local Execution

**Run all E2E tests:**
```bash
pytest tests/e2e/ -v
```

**Run visual regression tests:**
```bash
HEADLESS=false pytest tests/e2e/test_visual_navigation.py -v
```

**Run specific test:**
```bash
pytest tests/e2e/test_pairwise_comparison.py::TestPairwiseComparison::test_basic_pairwise_evaluation -v
```

**Run with HTML report:**
```bash
pytest tests/e2e/ -v --html=reports/report.html --self-contained-html
```

> **Note:** For unit tests, see the [Unit Testing](#unit-testing) section above.

### Docker Execution

**Prerequisites:** Ensure the application containers are running:
```bash
docker-compose up -d
```

**Test Execution Flow:**
1. ✅ Bring up Docker container for Playwright E2E testing
2. ✅ Run Playwright tests in that Docker container
3. ✅ Container is automatically removed after completion (using `--rm` flag)

**Run all E2E tests in Docker:**
```bash
docker-compose -f docker-compose.test.yml run --rm llm-judge-tests pytest tests/e2e/ -v
```

**Or use the helper script:**
```bash
./run-tests-docker.sh tests/e2e/ -v
```

> **Note:** Unit tests can also be run in Docker using the same container. See [Unit Testing](#unit-testing) section for details.

**Run specific test suite (container auto-removed after completion):**
```bash
docker-compose -f docker-compose.test.yml run --rm llm-judge-tests pytest tests/e2e/test_visual_navigation.py -v
```

**Run with custom pytest arguments (container auto-removed after completion):**
```bash
docker-compose -f docker-compose.test.yml run --rm llm-judge-tests pytest tests/e2e/ -v --tb=short -k "pairwise"
```

**Run tests and keep container for debugging (remove --rm to keep container):**
```bash
docker-compose -f docker-compose.test.yml run llm-judge-tests bash
# Then inside container: pytest tests/e2e/ -v
# Container will remain after exit for inspection
```

---

## Test Structure

```
tests/
├── e2e/                        # E2E (End-to-End) tests
│   ├── conftest.py            # Pytest fixtures and configuration
│   ├── pages/                 # Page Object Model classes
│   ├── utils/                 # E2E test utilities
│   ├── screenshots/           # Test screenshots (gitignored)
│   ├── visual_baselines/      # Baseline images for visual tests
│   └── test_*.py              # E2E test files
├── unit/                       # Unit tests
│   └── test_*.py              # Unit test files
└── README.md                   # This file
```

---

## Visual Regression Testing

Visual regression tests compare screenshots to detect unintended UI changes.

### Running Visual Tests

**Run all visual tests locally:**
```bash
pytest tests/e2e/test_visual_navigation.py -v
```

**Run all visual tests in Docker (same viewport, same results):**
```bash
docker-compose -f docker-compose.test.yml run --rm llm-judge-tests pytest tests/e2e/test_visual_navigation.py -v
```

**Run visual tests with browser visible (local only):**
```bash
HEADLESS=false pytest tests/e2e/test_visual_navigation.py -v
```

**Update baselines (when intentional UI changes are made):**
```bash
# Local (using environment variable)
UPDATE_BASELINES=true pytest tests/e2e/test_visual_navigation.py -v

# Local (using pytest option)
pytest tests/e2e/test_visual_navigation.py -v --update-baseline

# Docker (using environment variable)
UPDATE_BASELINES=true docker-compose -f docker-compose.test.yml run --rm llm-judge-tests pytest tests/e2e/test_visual_navigation.py -v

# Docker (using pytest option - recommended)
docker-compose -f docker-compose.test.yml run --rm llm-judge-tests pytest tests/e2e/test_visual_navigation.py -v --update-baseline
```

**Note:** When updating baselines, tests will run and verify the baseline was saved correctly (should pass with 0% difference). Tests no longer skip when updating baselines.

**Run specific visual test:**
```bash
# Local
pytest tests/e2e/test_visual_navigation.py::TestVisualNavigation::test_page_visual_layout -k "pairwise" -v

# Docker
docker-compose -f docker-compose.test.yml run --rm llm-judge-tests pytest tests/e2e/test_visual_navigation.py::TestVisualNavigation::test_page_visual_layout -k "pairwise" -v
```

### Visual Test Configuration

- **Threshold**: 0% difference (pixel perfect) - configurable in `tests/e2e/utils/visual_testing.py`
- **Diff Images**: Only created when tests fail (for debugging)
- **Baselines**: Stored in `tests/e2e/visual_baselines/`
- **Screenshots**: Stored in `tests/e2e/screenshots/`

---

## Docker Testing

### Docker Compose Files

- **`docker-compose.yml`**: Application services (app, API)
- **`docker-compose.test.yml`**: E2E test service (separate)

### Test Container Features

- **Isolated Environment**: Tests run in separate container
- **Network Access**: Connects to app via Docker network
- **Volume Mounts**: Test results accessible on host
- **Headless Mode**: Runs in headless browser by default
- **Health Checks**: Waits for app to be healthy before running

### Docker Test Workflow

1. **Start application:**
   ```bash
   docker-compose up -d
   ```

2. **Run tests:**
   ```bash
   docker-compose -f docker-compose.test.yml up --build
   ```

3. **View results:**
   - HTML report: `reports/report.html`
   - Screenshots: `tests/e2e/screenshots/`
   - Diff images: `tests/e2e/screenshots/diff_*.png` (only on failures)

---

## Configuration

### Environment Variables

- `TEST_BASE_URL`: Base URL for the Streamlit app (default: http://localhost:8501)
- `TEST_API_BASE_URL`: Base URL for the API server (default: http://localhost:8000)
- `HEADLESS`: Run browser in headless mode (default: true)
- `SLOW_MO`: Slow down operations by milliseconds (default: 0)
- `TEST_TIMEOUT`: Test timeout in milliseconds (default: 30000)
- `UPDATE_BASELINES`: Update baseline screenshots (default: false)
- `VIEWPORT_WIDTH`: Browser viewport width (default: 1920) - **Must match between local and Docker**
- `VIEWPORT_HEIGHT`: Browser viewport height (default: 1080) - **Must match between local and Docker**
- `DEVICE_SCALE_FACTOR`: Device pixel ratio (default: 1.0) - **Ensures consistent rendering**

### Docker Environment

In Docker, these are automatically set:
- `TEST_BASE_URL=http://llm-judge-app:8501`
- `TEST_API_BASE_URL=http://llm-judge-api:8000`
- `HEADLESS=true`
- `VIEWPORT_WIDTH=1920` (matches local default)
- `VIEWPORT_HEIGHT=1080` (matches local default)
- `DEVICE_SCALE_FACTOR=1.0` (ensures consistent rendering)

**Important:** The viewport configuration ensures that screenshots taken in Docker match those taken locally (1920x1080, scale factor 1.0), preventing false positives in visual regression tests.

---

## Reports

### HTML Reports

Test reports are generated in `reports/report.html` with:
- Test results summary
- Pass/fail status
- Execution times
- Error details

### Screenshots

- **Current screenshots**: `tests/e2e/screenshots/`
- **Baseline images**: `tests/e2e/visual_baselines/`
- **Diff images**: `tests/e2e/screenshots/diff_*.png` (only created on failures)

---

## Best Practices

1. **Run tests before committing**: Ensure all tests pass
2. **Update baselines intentionally**: Only when UI changes are expected
3. **Use Page Object Model**: Keep test code maintainable
4. **Run in Docker**: For consistent, reproducible results
5. **Check reports**: Review HTML reports for detailed results

---

## Troubleshooting

### Tests fail in Docker but pass locally

- Check network connectivity: `docker-compose -f docker-compose.test.yml run llm-judge-tests curl http://llm-judge-app:8501/_stcore/health`
- Verify app is healthy: `docker-compose ps`
- Check logs: `docker-compose logs llm-judge-app`

### Visual tests fail with small differences

- Review diff images in `tests/e2e/screenshots/diff_*.png`
- If change is intentional, update baseline: `pytest ... --update-baseline` (tests will run and verify, no skipping)
- Adjust threshold in `tests/e2e/utils/visual_testing.py` if needed

### Browser not found in Docker

- Ensure Playwright browsers are installed: `playwright install chromium`
- Check Dockerfile.test includes browser installation

---

## Examples

### Run all navigation tests:
```bash
pytest tests/e2e/test_all_navigation.py -v
```

### Debug test in Docker:
```bash
docker-compose -f docker-compose.test.yml run --rm llm-judge-tests bash
# Inside container:
pytest tests/e2e/test_pairwise_comparison.py -v -s
```

---

**TL;DR:** Comprehensive testing framework with 100% unit test coverage, E2E tests, visual regression testing, and mutation testing to ensure quality and reliability.
