from playwright.sync_api import Page, expect

def test_open_playwright_site(page: Page):
    page.goto("https://playwright.dev/python/")
    expect(page).to_have_title("Fast and reliable end-to-end testing for modern web apps | Playwright Python")