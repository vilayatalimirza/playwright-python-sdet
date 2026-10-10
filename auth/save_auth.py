from pathlib import Path
from playwright.sync_api import sync_playwright

AUTH_FILE = Path(__file__).parent / "auth.json"
LOGIN_URL = "https://www.saucedemo.com"

def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        page.wait_for_url("**/inventory.html")
        context.storage_state(path=str(AUTH_FILE))

        browser.close()

    print(f"Saved auth state to {AUTH_FILE}")


if __name__ == "__main__":
    main()