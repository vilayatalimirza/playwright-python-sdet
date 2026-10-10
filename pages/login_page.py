from playwright.sync_api import Page, expect


class LoginPage:
    """Page Object for the saucedemo login screen."""
    URL = "https://www.saucedemo.com"

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.get_by_placeholder("Username")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.error_message = page.locator("[data-test='error']")
    def open(self) -> "LoginPage":
        """Navigate to the login screen."""
        self.page.goto(self.URL)
        return self         
    def login(self, username: str, password: str) -> None:
        """Perform a login. Callers pass intent, not selectors."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
    def expect_error(self, text: str) -> None:
        """Assert an error banner is shown."""
        expect(self.error_message).to_contain_text(text)