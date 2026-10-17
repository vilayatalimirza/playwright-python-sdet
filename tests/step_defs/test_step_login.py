import re
from pytest_bdd import given, parsers, scenarios, then, when
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage

# Binds every scenario in features/login.feature to this module.
scenarios("../../features/login.feature")

@given("I am on the login page")
def on_login_page(login_page: LoginPage) -> LoginPage:
    """The login_page fixture already navigated us here. Nothing to do."""
    return login_page

@when(parsers.parse('I log in as "{username}" with password "{password}"'))
def log_in(login_page: LoginPage, username: str, password: str) -> None:
    login_page.login(username, password)

@then("I should land on the inventory page")
def land_on_inventory(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"inventory\.html"))

@then(parsers.parse('I should see the error "{message}"'))
def see_error(login_page: LoginPage, message: str) -> None:
    login_page.expect_error(message)