import re
from playwright.sync_api import Page, expect


def test_click_get_started(page: Page):
    """🥇 Best practice: role-based locator, exact name match."""
    page.goto("https://playwright.dev/python/")
    page.get_by_role("link", name="Get started", exact=True).click()
    expect(page).to_have_url(re.compile(r"/docs/intro$"))


def test_hero_heading(page: Page):
    """Assert the level-1 heading using its role, not its CSS class."""
    page.goto("https://playwright.dev/python/")
    heading = page.get_by_role("heading", level=1)
    expect(heading).to_contain_text("Playwright enables reliable web automation")
    print(f"\nHeading found: {heading.inner_text()!r}")


def test_bad_locator_is_not_visible(page: Page):
    """The negative assertion form: expect(...).not_to_be_visible()"""
    page.goto("https://playwright.dev/python/")
    ghost = page.locator(".this-does-not-exist")
    expect(ghost).not_to_be_visible()
    print(f"\nElements matched: {ghost.count()}")