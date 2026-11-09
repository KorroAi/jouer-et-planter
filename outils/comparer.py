"""Compare chaque page du site statique (local) avec le site WordPress en ligne : captures pleine page,
ordinateur et téléphone, et pourcentage de pixels différents.

    python -m http.server 8765 --directory public   (dans un autre terminal)
    python outils/comparer.py
Captures dans outils/.comparaison/ (ignoré par git).
"""
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
OUT = RACINE / "outils" / ".comparaison"
import sys
LOCAL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8765"  # ou l adresse Vercel
EN_LIGNE = "https://joueretplanter.com"
FORMATS = {"pc": {"width": 1440, "height": 900}, "tel": {"width": 412, "height": 915}}

# Masque ce qui change d'un chargement à l'autre ou qui diffère volontairement (formulaire newsletter, iframe HelloAsso)
CSS_STABLE = """*,*::before,*::after{animation:none!important;transition:none!important}
iframe{visibility:hidden!important} #actionbar,#wpadminbar{display:none!important}"""


def chemins():
    out = []
    for f in sorted((RACINE / "public").rglob("index.html")):
        rel = f.parent.relative_to(RACINE / "public").as_posix()
        out.append("/" if rel == "." else f"/{rel}/")
    return out


def capture(page, url, fichier):
    page.goto(url, wait_until="networkidle", timeout=90000)
    page.add_style_tag(content=CSS_STABLE)
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(800)
    page.screenshot(path=fichier, full_page=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        # Chromium déjà téléchargé par Playwright (la version attendue peut manquer)
        exe = sorted(Path.home().glob("AppData/Local/ms-playwright/chromium-*/chrome-win/chrome.exe"))
        nav = p.chromium.launch(executable_path=str(exe[-1]) if exe else None)
        for nom, vp in FORMATS.items():
            ctx = nav.new_context(viewport=vp, device_scale_factor=1, locale="fr-FR")
            page = ctx.new_page()
            for c in chemins():
                base = OUT / f"{nom}{c.strip('/').replace('/', '_') or '_accueil'}"
                a, b = f"{base}-local.png", f"{base}-enligne.png"
                capture(page, LOCAL + c, a)
                capture(page, EN_LIGNE + c, b)
                ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
                if ia.size != ib.size:
                    print(f"{nom:4} {c:45} TAILLES DIFFÉRENTES local {ia.size} / en ligne {ib.size}")
                    continue
                diff = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v > 24 else 0)
                pct = 100 * sum(diff.histogram()[255:]) / (ia.size[0] * ia.size[1])
                if pct > 0:
                    diff.save(f"{base}-diff.png")
                print(f"{nom:4} {c:45} {pct:6.2f} % de pixels différents  {ia.size}")
            ctx.close()
        nav.close()


if __name__ == "__main__":
    main()
