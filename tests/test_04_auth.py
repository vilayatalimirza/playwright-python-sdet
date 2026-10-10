import re
from playwright.sync_api import Page, expect

def test_inventory_loads_without_logging_in(page: Page):
    page.goto("/inventory.html")
    expect(page).to_have_url(re.compile(r"inventory\.html"))
    expect(page.get_by_text("Products")).to_be_visible()