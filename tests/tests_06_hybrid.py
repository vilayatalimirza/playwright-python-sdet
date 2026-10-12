"""Hybrid: build state via API, verify via UI.

Note: saucedemo has no API, so this file demonstrates the PATTERN using
two independent targets - in a real app both halves hit the same system.
"""

import re
import pytest
from faker import Faker
from playwright.sync_api import APIRequestContext, Page, expect

from pages.api_client import PostsClient
from pages.login_page import LoginPage


@pytest.fixture
def fake() -> Faker:
    return Faker()


def test_api_created_data_is_visible_in_ui(
    page: Page, request: APIRequestContext, fake: Faker
):
    # ---- Arrange: create data over the API (fast, reliable) ----
    posts = PostsClient(request)
    title = fake.sentence()
    assert posts.create_post(title=title, body="x").status == 201

    # ---- Act + Assert: verify through the UI ----
    LoginPage(page).open()
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(re.compile(r"inventory\.html"))
    expect(page.get_by_text("Products")).to_be_visible()