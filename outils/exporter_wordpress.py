"""Copie le site WordPress en ligne (joueretplanter.com) en site statique dans public/.

- Mêmes adresses que sur WordPress (/challenges/, /faq/, /2026/07/22/challenges-1er/...).
- Les médias gardent leur chemin /wp-content/uploads/... (les anciens emails continuent d'afficher leurs images).
- Scripts WordPress, Jetpack, statistiques et emojis retirés ; menu mobile et newsletter gérés par /assets/js/site.js.
- Le formulaire Jetpack « S'abonner » est remplacé par un formulaire Brevo (adresse dans outils/config.json).

À lancer tant que le site WordPress est encore en ligne :  python outils/exporter_wordpress.py
"""
import hashlib
import json
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

SITE = "https://joueretplanter.com"
RACINE = Path(__file__).resolve().parent.parent
OUT = RACINE / "public"
CONFIG = json.loads((RACINE / "outils" / "config.json").read_text(encoding="utf-8"))
UA = {"User-Agent": "Mozilla/5.0 (export statique Jouer et Planter)"}

PAGES_FIXES = ["/", "/challenges/", "/nos-actions/", "/about/", "/faire-un-dons/", "/faq/"]
CSS_IGNORES = ("likes", "related-posts", "gravatar", "fonts-api.wp.com")
STYLES_IGNORES = ("wp-emoji-styles-inline-css", "jetpack-stats-inline-css")
HEAD_RELS_IGNORES = {"dns-prefetch", "preconnect", "EditURI", "shortlink", "https://api.w.org/", "modulepreload", "alternate", "pingback"}

telecharges: dict[str, str] = {}


def lire(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def ecrire(chemin_site: str, data: bytes) -> None:
    f = OUT / chemin_site.lstrip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(data)


def original(url: str) -> str:
    """i0.wp.com/joueretplanter.com/x?fit=.. -> https://joueretplanter.com/x ; &amp; nettoyé."""
    url = url.replace("&amp;", "&").replace("&#038;", "&")
    url = re.sub(r"^(https?:)?//i[0-3]\.wp\.com/joueretplanter\.com", SITE, url)
    if url.startswith("//"):
        url = "https:" + url
    return url


def ressource(url: str) -> str:
    """Télécharge un fichier (image, police, svg) et renvoie son chemin local (racine du site)."""
    url = original(url)
    p = urllib.parse.urlparse(url)
    if p.netloc == "fonts.gstatic.com":
        local = "/assets/fonts/" + Path(p.path).name
    elif p.netloc == "joueretplanter.com":
        local = p.path
    else:
        return url
    if local not in telecharges.values():
        statut, data = lire(f"{p.scheme}://{p.netloc}{p.path}")
        if statut != 200:
            print(f"  ! {statut} {url}")
        else:
            ecrire(local, data)
        telecharges[url] = local
    return local


RE_URL_ASSET = re.compile(
    r"(?:https?:)?//(?:i[0-3]\.wp\.com/)?joueretplanter\.com/(?:wp-content|wp-includes)/[^\s\"'()<>,]+"
    r"|https://fonts\.gstatic\.com/[^\s\"'()<>,]+"
)
RE_URL_PAGE = re.compile(r"https://joueretplanter\.com(/[^\s\"'<>]*)?")


def localiser_texte(t: str) -> str:
    t = RE_URL_ASSET.sub(lambda m: ressource(m.group(0)), t)
    return RE_URL_PAGE.sub(lambda m: m.group(1) or "/", t)


def css_local(href: str) -> str:
    href = original(href)
    statut, data = lire(href)
    if statut != 200:
        sys.exit(f"CSS introuvable ({statut}) : {href}")
    css = data.decode("utf-8")

    def url_css(m):
        u = m.group(2)
        if u.startswith("data:") or u.startswith("#"):
            return m.group(0)
        absolue = urllib.parse.urljoin(href, u)
        return f"url({m.group(1)}{ressource(absolue) if RE_URL_ASSET.match(absolue) else absolue}{m.group(1)})"

    css = re.sub(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", url_css, css)
    nom = "/assets/css/" + hashlib.md5(href.encode()).hexdigest()[:12] + ".css"
    ecrire(nom, css.encode("utf-8"))
    return nom


def formulaire_brevo(soup: BeautifulSoup) -> None:
    for form in soup.select("form#subscribe-blog"):
        champ = form.select_one("input[type=email]")
        bouton = form.select_one("button[type=submit]")
        nouveau = BeautifulSoup(
            f"""<form id="subscribe-blog" class="jp-brevo" method="post" action="{CONFIG['brevo_form_action']}" accept-charset="utf-8">
<div class="wp-block-jetpack-subscriptions__form-elements">
<p id="subscribe-email"><label class="screen-reader-text" for="subscribe-field">Ton adresse email</label>
<input type="email" name="EMAIL" id="subscribe-field" class="{' '.join(champ.get('class', []))}" style="{champ.get('style', '')}" placeholder="Ton adresse email" autocomplete="email" required></p>
<p id="subscribe-submit"><input type="text" name="email_address_check" value="" class="jp-piege" tabindex="-1" autocomplete="off" aria-hidden="true"><input type="hidden" name="locale" value="fr"><input type="hidden" name="html_type" value="simple"><button type="submit" class="{' '.join(bouton.get('class', []))}" style="{bouton.get('style', '')}">{bouton.get_text(strip=True)}</button></p>
</div>
<p class="jp-brevo-message" role="status" aria-live="polite"></p>
</form>""",
            "html.parser",
        )
        form.replace_with(nouveau)


def nettoyer(html: str, chemin: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    head, body = soup.head, soup.body

    for s in soup.find_all("script"):
        texte = s.string or ""
        if s.get("type") == "application/ld+json" or "haWidgetLight" in texte:
            continue
        s.decompose()
    for m in head.find_all("meta", attrs={"name": "generator"}):
        m.decompose()
    for l in head.find_all("link"):
        rels = set(l.get("rel") or [])
        if rels & HEAD_RELS_IGNORES:
            l.decompose()
        elif "stylesheet" in rels:
            href = l.get("href", "")
            if any(x in href for x in CSS_IGNORES):
                l.decompose()
            else:
                l.attrs = {"rel": "stylesheet", "href": css_local(href)}
    for s in soup.find_all("style"):
        if s.get("id") in STYLES_IGNORES:
            s.decompose()
    for sel in (".wp-block-comments", ".wp-block-post-comments-form", "#wpadminbar", "#actionbar", "#jp-relatedposts", ".sharedaddy"):
        for el in soup.select(sel):
            el.decompose()

    # Balises de partage : adresses absolues, mais vers l'image d'origine
    for m in head.find_all("meta"):
        c = m.get("content", "")
        if "wp.com/joueretplanter.com" in c or "joueretplanter.com/wp-content" in c:
            ressource(c)
            m["content"] = SITE + urllib.parse.urlparse(original(c)).path
    for l in head.find_all("link", rel=["icon", "apple-touch-icon"]):
        l["href"] = ressource(l["href"])
    canon = head.find("link", rel="canonical")
    canon_url = canon["href"] if canon else None

    for img in soup.find_all(["img", "source"]):
        if "wp.com" in img.get("srcset", "") or "joueretplanter.com" in img.get("srcset", ""):
            del img["srcset"]
            img.attrs.pop("sizes", None)
        for a in list(img.attrs):
            if a.startswith(("data-orig", "data-medium", "data-large", "data-image", "data-comments", "data-permalink", "data-attachment")):
                del img[a]

    formulaire_brevo(soup)
    head.append(BeautifulSoup('<link rel="stylesheet" href="/assets/css/ajouts.css">', "html.parser"))
    body.append(BeautifulSoup('<script src="/assets/js/site.js" defer></script>', "html.parser"))

    sortie = localiser_texte(str(soup))
    # Précharger les polices des titres (font-display: fallback abandonne une police arrivée trop tard)
    polices = sorted(set(re.findall(r"url\('(/assets/fonts/[^']+\.woff2)'\)", sortie)))
    pre = "".join(f'<link rel="preload" href="{p}" as="font" type="font/woff2" crossorigin>' for p in polices)
    sortie = sortie.replace("</title>", "</title>" + pre, 1)
    # JSON-LD (adresses échappées \/) : images d'origine au lieu du proxy i0.wp.com
    sortie = re.sub(r'https:\\/\\/i[0-3]\.wp\.com\\/joueretplanter\.com(\\/[^"?]*)\?[^"]*', r"https:\\/\\/joueretplanter.com\1", sortie)
    # Les balises absolues voulues (canonical, og:, twitter:) ont été rendues relatives : on les remet.
    if canon_url:
        sortie = sortie.replace(f'<link href="{urllib.parse.urlparse(canon_url).path}" rel="canonical"/>', f'<link href="{canon_url}" rel="canonical"/>')
    sortie = re.sub(
        r'(<meta content=")(/[^"]*)(" (?:property="og:(?:url|image)"|name="twitter:image"))',
        lambda m: m.group(1) + SITE + m.group(2) + m.group(3),
        sortie,
    )
    return sortie


def chemins_a_exporter() -> list[str]:
    chemins = list(PAGES_FIXES)
    for type_, cle in (("posts", "link"), ("categories", "link"), ("tags", "link")):
        statut, data = lire(f"{SITE}/wp-json/wp/v2/{type_}?per_page=100")
        for item in json.loads(data):
            if type_ != "posts" and item["count"] == 0:
                continue
            chemins.append(urllib.parse.urlparse(item[cle]).path)
    return chemins


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for f in OUT.iterdir():  # vider sans supprimer le dossier (un serveur d'aperçu peut l'occuper)
        shutil.rmtree(f) if f.is_dir() else f.unlink()
    shutil.copytree(RACINE / "outils" / "statique", OUT, dirs_exist_ok=True)

    chemins = chemins_a_exporter()
    for chemin in chemins:  # la liste grandit avec les liens internes découverts (page auteur...)
        statut, data = lire(SITE + chemin)
        print(f"{statut} {chemin}")
        if statut != 200:
            sys.exit("Page introuvable, export arrêté.")
        page = nettoyer(data.decode("utf-8"), chemin)
        ecrire(chemin + "index.html", page.encode("utf-8"))
        for lien in re.findall(r'href="(/[^"#?]*/)"', page):
            if not lien.startswith(("/wp-", "/assets/")) and lien not in chemins:
                chemins.append(lien)

    statut, data = lire(SITE + "/cette-page-n-existe-pas-export/")
    print(f"{statut} (page 404)")
    ecrire("/404.html", nettoyer(data.decode("utf-8"), "/404").encode("utf-8"))

    # Médiathèque complète : les anciens emails pointent vers ces fichiers
    statut, data = lire(f"{SITE}/wp-json/wp/v2/media?per_page=100")
    for m in json.loads(data):
        ressource(m["source_url"])

    restes = sorted({u for f in OUT.rglob("*.html") for u in re.findall(r"(?:wp\.com|joueretplanter\.com)[^\s\"'<>]*", f.read_text(encoding="utf-8"))})
    print(f"\n{len(chemins) + 1} pages, {len(telecharges)} fichiers téléchargés.")
    print("Adresses absolues restantes (normalement : canonical, og, JSON-LD) :")
    for u in restes:
        print("  ", u)


if __name__ == "__main__":
    main()
