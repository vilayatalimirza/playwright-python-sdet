"""Fixtures shared by all tests. pytest auto-discovers this file."""

import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pathlib import Path
from collections.abc import Generator
from playwright.sync_api import APIRequestContext, Playwright
from auth.save_auth import AUTH_FILE, is_state_fresh, login_and_save

AUTH_FILE = Path(__file__).parent.parent / "auth" / "auth.json"



@pytest.fixture
def api(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    ctx = playwright.request.new_context()
    yield ctx
    ctx.dispose()

@pytest.fixture(scope="session")
def auth_state(playwright: Playwright) -> str:
    """Ensure auth.json is fresh. Regenerate ONLY when stale."""
    if is_state_fresh():
        print("\n[auth] reusing fresh auth state")
        return str(AUTH_FILE)

    print("\n[auth] state stale or missing - regenerating")
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.saucedemo.com")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/inventory.html")
    context.storage_state(path=str(AUTH_FILE))
    context.close()
    browser.close()
    return str(AUTH_FILE)

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.open()
    return lp

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args,auth_state):
    return {
        **browser_context_args,
        "storage_state": auth_state,
        "base_url": "https://www.saucedemo.com",
    }