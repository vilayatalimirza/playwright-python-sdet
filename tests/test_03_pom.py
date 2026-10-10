import re
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage

def test_successful_login(login_page: LoginPage, page: Page):
    login_page.login("standard_user", "secret_sauce")
    expect(page).to_have_url(re.compile(r"inventory\.html"))

def test_locked_out_user_sees_error(login_page: LoginPage):
    login_page.login("locked_out_user", "secret_sauce")
    login_page.expect_error("Sorry, this user has been locked out")