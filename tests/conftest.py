"""Fixtures shared by all tests. pytest auto-discovers this file."""

import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pathlib import Path

AUTH_FILE = Path(__file__).parent.parent / "auth" / "auth.json"

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.open()
    return lp

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "storage_state": str(AUTH_FILE),
        "base_url": "https://www.saucedemo.com",
    }