"""Génère GUIDE-QUITTER-WORDPRESS.pdf à partir de outils/guide/guide.html (Chromium de Playwright)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent
SORTIE = ICI.parent.parent / "GUIDE-QUITTER-WORDPRESS.pdf"
exe = sorted(Path.home().glob("AppData/Local/ms-playwright/chromium-*/chrome-win/chrome.exe"))
with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=str(exe[-1]) if exe else None)
    page = nav.new_page()
    page.goto((ICI / "guide.html").as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.pdf(path=str(SORTIE), format="A4", print_background=True, prefer_css_page_size=True)
    for i in range(6):
        page.set_viewport_size({"width": 794, "height": 1123})
    nav.close()
print(SORTIE)
