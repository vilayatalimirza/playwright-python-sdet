import json
import time
from pathlib import Path

AUTH_FILE = Path(__file__).parent / "auth.json"
LOGIN_URL = "https://www.saucedemo.com"


def is_state_fresh(path: Path = AUTH_FILE, buffer_seconds: int = 300) -> bool:
    """True if auth.json exists and no cookie expires within the buffer.

    No browser needed - just reads the JSON. The buffer prevents the race
    where state is valid now but expires mid-run.
    """
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False            # corrupt file -> treat as stale

    cookies = data.get("cookies", [])
    if not cookies:
        return False

    now = time.time()
    for cookie in cookies:
        expires = cookie.get("expires", -1)
        if expires and expires > 0 and expires <= now + buffer_seconds:
            return False        # this cookie is expired or about to be
    return True


def save_state_from_context(context, path: Path = AUTH_FILE) -> None:
    """Persist cookies + localStorage. Callable from a fixture."""
    context.storage_state(path=str(path))


def login_and_save(path: Path = AUTH_FILE) -> None:
    """Standalone CLI path: launch a browser, log in, save state."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_placeholder("Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        page.wait_for_url("**/inventory.html")
        save_state_from_context(context, path)
        browser.close()


if __name__ == "__main__":
    login_and_save()
    print(f"Saved auth state to {AUTH_FILE}")