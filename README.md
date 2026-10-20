# Playwright + Python SDET Framework

[![Playwright](https://img.shields.io/badge/Playwright-1.63-2EAD33)](https://playwright.dev/python)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB)](https://www.python.org)
[![pytest](https://img.shields.io/badge/pytest-9.1-0A9EDC)](https://pytest.org)
[![Docker](https://img.shields.io/badge/Docker-reproducible-2496ED)](https://www.docker.com)
[![Jenkins](https://img.shields.io/badge/CI-Jenkins-D24939)](https://www.jenkins.io)

An end-to-end test automation framework built with **Playwright** and **pytest**,
covering UI, API, hybrid, and BDD testing — containerized with Docker and driven
by a declarative Jenkins pipeline.

**Applications under test:** [Sauce Demo](https://www.saucedemo.com) (Swag Labs) · [JSONPlaceholder](https://jsonplaceholder.typicode.com) (REST API) · [Playwright Python docs](https://playwright.dev/python)

---

## What this demonstrates

| Capability | Where it lives |
|---|---|
| Page Object Model + API client abstraction | `pages/` |
| Fixture-based dependency injection, scopes, composition | `tests/conftest.py` |
| Session-scoped authentication via `storage_state` | `auth/`, `tests/conftest.py` |
| Self-healing auth (expiry detection + regeneration) | `auth/save_auth.py` |
| API + UI hybrid testing | `tests/test_06_hybrid.py` |
| BDD / Gherkin scenarios | `features/`, `tests/step_defs/` |
| Cross-platform containerized execution | `Dockerfile` |
| CI pipeline with published test reports | `Jenkinsfile` |
| Role-based locator strategy | `tests/test_02_locators.py`, all page objects |
| Data-driven testing (`parametrize`) | `tests/test_05_api.py` |
| Marker-based suite selection (smoke / regression / api / bdd) | `pytest.ini`, markers across tests |

---

## Stack

| Layer | Tooling |
|---|---|
| Browser automation | Playwright 1.63 (Python, sync API) |
| Test runner | pytest 9.1 + pytest-playwright |
| BDD | pytest-bdd 9.0 (Gherkin) |
| Test data | Faker |
| Reporting | pytest-html, JUnit XML → Jenkins |
| Containerization | Docker, `mcr.microsoft.com/playwright/python:v1.63.0-noble` |
| CI | Jenkins (declarative pipeline) |

---

## Architecture

```
playwright-python-sdet/
├── Jenkinsfile                  # Declarative CI pipeline
├── Dockerfile                   # Playwright base image + pinned deps
├── .dockerignore                # Excludes .venv, secrets, reports
├── pytest.ini                   # Markers, --strict-markers, discovery
├── requirements.txt             # Pinned dependencies
├── conftest.py                  # Root: places project on sys.path
│
├── auth/
│   ├── save_auth.py             # Login + storage_state; freshness check
│   └── auth.json                # GITIGNORED — live session tokens
│
├── features/
│   └── login.feature            # Gherkin scenarios
│
├── pages/
│   ├── login_page.py            # Page Object
│   └── api_client.py            # REST client wrapper
│
└── tests/
    ├── conftest.py              # Shared fixtures
    ├── test_01.py               # Smoke: navigation
    ├── test_02_locators.py      # Locator strategy, strict mode
    ├── test_03_pom.py           # Page Object usage
    ├── test_04_auth.py          # Authenticated without logging in
    ├── test_05_api.py           # API-only tests
    ├── test_06_hybrid.py        # API arrange + UI assert
    └── step_defs/
        ├── __init__.py
        └── test_step_login.py   # Gherkin step definitions
```

---

## Getting started

### Local

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium
```

### Run the suite

```bash
pytest                                          # everything
pytest -m smoke                                 # fast critical-path subset
pytest -m "not slow"                            # exclude slow tests
pytest tests/test_03_pom.py -v                  # one file
pytest tests/test_03_pom.py::test_successful_login
pytest --headed                                 # watch the browser
pytest -k "login"                               # match by name
pytest --html=reports/report.html --self-contained-html
```

### Docker

```bash
docker build -t playwright-python-sdet .
docker run --rm playwright-python-sdet
```

The suite runs **unmodified on Linux** — no host Python, no local browser, no
pre-seeded auth state.

### CI

The `Jenkinsfile` pipeline:

1. **Build Image** — builds a versioned image tagged with the build number
2. **Test** — creates a container, runs the suite inside it, streams output,
   then copies JUnit reports out with `docker cp`
3. **Post** — publishes test results, archives reports, removes the image

---

## Design decisions

### Role-based locators over CSS/XPath

Locators query the **accessibility tree** rather than DOM structure:

```python
page.get_by_role("link", name="Get started", exact=True)
```

A CSS or XPath locator encodes *how the page is built*, so it breaks on a
markup refactor. A role locator encodes *what the element means to a user*, so
it only fails when the product genuinely changes — which is a failure worth
having. The side benefit: a suite built on role locators provides baseline
accessibility coverage for free. If `get_by_role("button", name="Submit")`
can't find an element, neither can a screen reader.

`exact=True` is used where substring matching would be ambiguous — for example
`"Get started"` also matches `"Getting started"`, and Playwright's strict mode
treats multiple matches as a hard error.

### `expect()` over `assert` for browser-facing assertions

```python
assert page.title() == "Shop"          # reads ONCE, fails if still loading
expect(page).to_have_title("Shop")     # retries until true or timeout (5s)
```

Web-first assertions eliminate entire categories of timing flakiness. A failure
report also includes expected vs actual, a call log showing how many polls
occurred, and an accessibility snapshot of the page.

`assert` is reserved for values that need no retrying — HTTP status codes,
response payload shape, computed Python values.

### One browser per session, one context per test

pytest-playwright launches the browser once and creates a fresh
`BrowserContext` per test — an incognito-like sandbox with isolated cookies,
`localStorage`, and cache.

This gives Selenium's `driver.quit()`-level isolation without paying
browser-launch cost per test. It prevents order-dependent failures where one
test's login or cart leaks into the next. It does **not** protect a shared
backend database — that requires application-level isolation, which is why
test data is generated per test with Faker.

### Self-healing authentication

Tests run authenticated without repeating the login flow. State is persisted
once and injected into every fresh context:

```python
@pytest.fixture(scope="session")
def auth_state(playwright):
    if is_state_fresh():
        return str(AUTH_FILE)
    # stale or missing -> log in via UI and save state
    ...
    return str(AUTH_FILE)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, auth_state):
    return {**browser_context_args,
            "storage_state": auth_state,
            "base_url": "https://www.saucedemo.com"}
```

`is_state_fresh()` reads the cookie expiry from `auth.json` without launching a
browser, with a 300-second safety buffer so state expiring mid-run doesn't
cause a late failure.

**Why this matters:** a committed `auth.json` is perishable state, and a suite
that depends on it silently acquires a ~24-hour shelf life. That is a
time-bomb flaky test — it passes today and fails on Monday with no code change.
Checking expiry and regenerating on demand removes the dependency entirely,
which is also what allows the Docker image to work with no pre-seeded state.

### API for arrange, UI for act and assert

Setup state is built through the API; the behaviour under test is exercised
through the UI.

An all-UI setup for "the cart shows the right total" means eight steps that can
each fail for reasons unrelated to the behaviour under test — a broken search
feature fails the cart test, and the test's name lies about the cause. API
setup also isolates test data the way a fresh context isolates cookies.

**The guardrail:** API setup is only valid when the API and UI produce the same
state. If the UI performs validation or a multi-stage flow that the API
bypasses, using the API tests a state a real user can never reach.

### Function-scoped API context

A fresh `APIRequestContext` per test costs milliseconds against browser
startup, and it buys isolated cookies and headers plus a contained blast
radius: a test that corrupts its context fails alone rather than cascading
through the run. Widening the scope would need a reset fixture clearing headers
and cookies between tests, so the wider scope should only follow a measured
bottleneck.

### Path resolution anchored to `__file__`

```python
FEATURE_FILE = Path(__file__).parent.parent.parent / "features" / "login.feature"
```

Relative traversal (`../../features/...`) resolved differently inside the Linux
container and failed collection entirely. Paths anchored to `__file__` are
independent of the working directory and behave identically everywhere.

### Reports copied out with `docker cp`

Bind-mounting a report directory into a nested container inside a
Windows/WSL2-backed Jenkins home did not propagate files. The pipeline instead
uses `docker create` → `docker start -a` → `docker cp` → `docker rm`, which
streams artifacts through the Docker API and behaves identically on Linux CI.

---

## Testing notes

**Markers.** `pytest.ini` sets `--strict-markers`, so a typo like
`@pytest.mark.smke` is a hard error rather than a test that silently never
runs.

```bash
pytest -m smoke        # critical path
pytest -m regression   # full regression
pytest -m api          # API-only, no browser
pytest -m bdd          # Gherkin scenarios
```

**Test reports.** JUnit XML is written inside the container and published by
Jenkins:

```
reports/junit.xml
```

---

## Security notes

- `auth/auth.json` contains **live session cookies** and is gitignored.
- `.dockerignore` excludes it from the image; the auth fixture regenerates
  state inside the container instead.
- The container runs as root because the Playwright base image expects it.
  Reports are copied out via `docker cp` rather than a writable bind mount. A
  hardened deployment would run as non-root with `PLAYWRIGHT_BROWSERS_PATH`
  configured and a dedicated CI agent.
- Jenkins-in-Docker with the Docker socket mounted has host-level Docker
  access. Acceptable for local learning; production should use a purpose-built
  agent rather than mounting the socket into a controller.

---

## Roadmap

- [x] pytest foundations — fixtures, scopes, parametrize, markers
- [x] Locator strategy — role-based, strict mode
- [x] Page Object Model
- [x] Storage-state authentication with self-healing regeneration
- [x] API + UI hybrid testing
- [x] BDD with pytest-bdd
- [x] Dockerized, reproducible execution
- [x] Jenkins pipeline with JUnit reporting
- [ ] Parallel execution with pytest-xdist
- [ ] Visual regression baselines
- [ ] Cross-browser matrix (Firefox, WebKit)

---

## About

Built by **Vilayat Ali Mirza** — Automation Test Engineer, 3+ years in manual and
automation testing (Java/Selenium/TestNG, TypeScript/Playwright, Python).

- GitHub: [@vilayatalimirza](https://github.com/vilayatalimirza)
- LinkedIn: [vilayat-ali-mirza](https://linkedin.com/in/vilayat-ali-mirza)