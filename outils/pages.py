"""Assemble le site statique à partir de public/ (copie WordPress figée) et de outils/contenu/.

    python outils/pages.py

Sans risque à relancer : chaque ajout est entouré de marqueurs <!--jp2:...--> et remplacé à chaque passage.
- crée les pages de outils/contenu/<slug>.html (en-tête et pied repris de /nos-actions/) ;
- met à jour le menu (en-tête et pied) sur toutes les pages ;
- ajoute les compteurs et le prochain rendez-vous sur l'accueil, les documents sur /about/ ;
- réécrit titres et descriptions (référencement), génère sitemap.xml et robots.txt.
Les chiffres des compteurs et le prochain rendez-vous se changent dans outils/contenu/site.json.
"""
import html
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PUB = RACINE / "public"
CONTENU = RACINE / "outils" / "contenu"
SITE = "https://joueretplanter.com"
DONNEES = json.loads((CONTENU / "site.json").read_text(encoding="utf-8"))

MENU = [
    ("/jouer/", "Jouer"),
    ("/planter/", "Planter"),
    ("/challenges/", "Challenges"),
    ("/nos-actions/", "Nos actions"),
    ("/artistes/", "Artistes"),
    ("/benevoles/", "Bénévoles"),
    ("/carte/", "Carte"),
    ("/about/", "Nos valeurs"),
    ("/faq/", "FAQ"),
]


def lire(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def ecrire(p: Path, t: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, encoding="utf-8")


def bloc(nom: str, contenu: str) -> str:
    return f"<!--jp2:{nom}-->{contenu}<!--/jp2:{nom}-->"


def retirer_bloc(t: str, nom: str) -> str:
    return re.sub(rf"<!--jp2:{nom}-->.*?<!--/jp2:{nom}-->", "", t, flags=re.S)


def meta(t: str, chemin: str, titre: str, description: str) -> str:
    """Titre, description, Open Graph et canonical d'une page."""
    d = html.escape(description, quote=True)
    t = re.sub(r"<title>.*?</title>", f"<title>{html.escape(titre)}</title>", t, count=1, flags=re.S)
    for motif, rempl in (
        (r'<meta content="[^"]*" name="description"/>', f'<meta content="{d}" name="description"/>'),
        (r'<meta content="[^"]*" property="og:description"/>', f'<meta content="{d}" property="og:description"/>'),
        (r'<meta content="[^"]*" property="og:title"/>', f'<meta content="{html.escape(titre, quote=True)}" property="og:title"/>'),
        (r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{SITE}{chemin}" property="og:url"/>'),
        (r'<link href="[^"]*" rel="canonical"/>', f'<link href="{SITE}{chemin}" rel="canonical"/>'),
    ):
        if re.search(motif, t):
            t = re.sub(motif, lambda m: rempl, t, count=1)
        else:
            t = t.replace("</title>", "</title>" + rempl, 1)
    return t


def menu(t: str, chemin: str) -> str:
    items = "".join(
        f'<li class="wp-block-navigation-item wp-block-navigation-link{" current-menu-item" if h == chemin else ""}">'
        f'<a class="wp-block-navigation-item__content" href="{h}"{" aria-current=\"page\"" if h == chemin else ""}>'
        f'<span class="wp-block-navigation-item__label">{n}</span></a></li>'
        for h, n in MENU
    )
    t = re.sub(
        r'(<ul class="wp-block-navigation__container[^"]*">).*?(</ul>)',
        lambda m: m.group(1) + items + m.group(2), t, count=1, flags=re.S,
    )
    pied = "".join(f'\n<li><a href="{h}">{n}</a></li>' for h, n in MENU) + '\n<li><a href="/ma-commune/">Ma commune veut une fête</a></li>\n<li><a href="/faire-un-dons/">Faire un don</a></li>\n'
    t = re.sub(r'(<ul class="wp-block-list jp-liens">).*?(</ul>)', lambda m: m.group(1) + pied + m.group(2), t, count=1, flags=re.S)
    # restes WordPress inutiles
    t = re.sub(r'<meta content="" data-customproperties=.*?/>', "", t, flags=re.S)
    t = re.sub(r"<!--\s*generated in .*?-->", "", t, flags=re.S)
    return t


def hero(image: str, titre: str, accroche: str) -> str:
    """Bandeau photo identique à ceux du site WordPress."""
    return (
        '<div class="wp-block-cover alignfull has-custom-content-position is-position-bottom-left jp-visuel jp-visuel--haut" '
        'style="margin-top:0;margin-bottom:0;padding-top:var(--wp--preset--spacing--80);padding-right:var(--wp--preset--spacing--50);'
        'padding-bottom:var(--wp--preset--spacing--80);padding-left:var(--wp--preset--spacing--50);min-height:62vh;aspect-ratio:unset;">'
        f'<img alt="" class="wp-block-cover__image-background" decoding="async" src="https://images.unsplash.com/photo-{image}?w=2000&amp;q=78&amp;auto=format&amp;fit=crop" style="object-position:50% 50%"/>'
        '<span aria-hidden="true" class="wp-block-cover__background has-background-dim-100 has-background-dim wp-block-cover__gradient-background has-background-gradient" '
        'style="background:linear-gradient(180deg,rgba(18,24,10,0.15) 0%,rgba(18,24,10,0.30) 40%,rgba(18,24,10,0.82) 100%)"></span>'
        '<div class="wp-block-cover__inner-container has-global-padding is-layout-constrained wp-container-core-cover-is-layout-ed0592ac wp-block-cover-is-layout-constrained">'
        '<div class="wp-block-group jp-visuel__texte has-global-padding is-content-justification-left is-layout-constrained wp-container-core-group-is-layout-a5486a26 wp-block-group-is-layout-constrained">'
        f'<h1 class="wp-block-heading jp-titre-visuel">{titre}</h1><p class="jp-accroche wp-block-paragraph">{accroche}</p>'
        "</div></div></div>"
    )


LEAFLET = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">'
           '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" defer></script>')


def carte_bloc(titre: bool = True) -> str:
    """Carte des actions (Leaflet) avec légende ; données dans site.json > carte."""
    c = DONNEES["carte"]
    utilisees = {k for l in c["lieux"] for k in l["cat"]}
    legende = "".join(
        f'<li><span class="jp2-point" style="background:{v["couleur"]}"></span>{v["texte"]}</li>'
        for k, v in c["categories"].items() if k in utilisees
    )
    entete = ('<h2 class="jp2-titre">La carte de nos actions</h2>'
              '<p class="jp2-intro">Partout où Jouer et Planter est déjà passé.</p>') if titre else ""
    return (
        '<section class="jp2-section alignfull jp2-section--carte"><div class="jp2-contenu">' + entete +
        f'<ul class="jp2-legende">{legende}</ul>'
        '<div class="jp2-carte-map" role="region" aria-label="Carte des actions de Jouer et Planter"></div>'
        '<ul class="jp2-villes"></ul>'
        f'<p class="jp2-note">Mise à jour le {c["maj"]}.</p>'
        '<script type="application/json" class="jp2-carte-data">' + json.dumps(c, ensure_ascii=False) + "</script>"
        "</div></section>"
    )


def communes_bloc() -> str:
    """Liste des communes candidates (site.json > communes : [{"nom", "departement", "texte"}])."""
    communes = DONNEES.get("communes", [])
    if not communes:
        return ('<div class="jp2-encadre jp2-vide"><p><b>Aucune commune n’est encore en lice.</b> '
                'Sois la première : <a href="#candidater">propose ta commune</a> !</p></div>')
    cartes = []
    for c in communes:
        ancre = re.sub(r"[^a-z0-9]+", "-", c["nom"].lower()).strip("-")
        cartes.append(
            f'<article class="jp2-commune" id="{ancre}"><h3>{html.escape(c["nom"])}</h3>'
            f'<p class="jp2-etiquette">{html.escape(c["departement"])}</p><p>{html.escape(c.get("texte", ""))}</p>'
            f'<div class="jp2-boutons" style="justify-content:flex-start">'
            f'<a class="wp-block-button__link wp-element-button jp2-btn jp2-btn--orange" href="/faire-un-dons/">Soutenir par un don</a>'
            f'<button type="button" class="wp-block-button__link wp-element-button jp2-btn jp2-btn--blanc jp2-partager" '
            f'data-titre="Une fête Jouer et Planter à {html.escape(c["nom"], quote=True)} ?" data-ancre="{ancre}">Partager</button></div></article>'
        )
    return '<div class="jp2-grille">' + "".join(cartes) + "</div>"


def avec_leaflet(t: str) -> str:
    return t if "leaflet.min.js" not in LEAFLET or "leaflet.min.js" in t else t.replace("</title>", "</title>" + LEAFLET, 1)


def valeurs_page(t: str) -> str:
    """Page /about/ : bandeau d'origine + nouvelle mise en page (outils/contenu/valeurs.html) + documents."""
    debut = t.index('<div class="entry-content')
    debut = t.index(">", debut) + 1
    fin = t.rindex("</div>", 0, t.index("</main>"))
    contenu = t[debut:fin]
    i = contenu.index('<div class="wp-block-cover alignfull')
    profondeur, j = 0, i
    for m in re.finditer(r"<div\b|</div>", contenu[i:]):
        profondeur += 1 if m.group(0) == "<div" else -1
        if profondeur == 0:
            j = i + m.end()
            break
    bandeau = contenu[i:j]
    return t[:debut] + chr(10) + bandeau + bloc("valeurs", lire(CONTENU / "valeurs.html")) + chr(10) + t[fin:]


def nouvelles_pages() -> None:
    coquille = lire(PUB / "nos-actions" / "index.html")
    debut = coquille.index('<div class="entry-content')
    debut = coquille.index(">", debut) + 1
    fin = coquille.index("</main>")
    fin = coquille.rindex("</div>", 0, fin)
    for p in DONNEES["pages"]:
        corps = hero(p["image"], p["h1"], p["accroche"]) + lire(CONTENU / f"{p['slug']}.html").replace("<!--CARTE-->", carte_bloc(titre=False)).replace("<!--COMMUNES-->", communes_bloc())
        t = coquille[:debut] + "\n" + corps + "\n" + coquille[fin:]
        t = t.replace("page-id-155", f"page-jp2-{p['slug']}")
        t = re.sub(r'<meta content="[^"]*" property="article:(?:published|modified)_time"/>', "", t)
        t = re.sub(r'<script type="application/ld\+json">.*?</script>', "", t, flags=re.S)
        ecrire(PUB / p["slug"] / "index.html", t)


def accueil(t: str) -> str:
    t = retirer_bloc(t, "accueil")
    c = DONNEES["compteurs"]
    e = DONNEES["evenement"]
    chiffres = "".join(
        f'<div class="jp2-compteur"><span class="jp2-compteur__nombre">{x.get("prefixe", "")}<b data-cible="{x["nombre"]}">{x["nombre"]}</b></span>'
        f'<span class="jp2-compteur__texte">{x["texte"]}</span></div>'
        for x in c
    )
    section = (
        '<section class="jp2-section jp2-section--bleu alignfull jp2-dons"><div class="jp2-contenu">'
        f'<h2 class="jp2-grand">Grâce à vos dons</h2><div class="jp2-compteurs">{chiffres}</div>'
        '<div class="jp2-rdv">'
        + (f'<a class="jp2-rdv__affiche" href="{e["affiche"]}" target="_blank" rel="noopener"><img src="{e["affiche"]}" alt="Affiche : {html.escape(e["titre"], quote=True)}, {e["date"]}" loading="lazy" width="900" height="1350"></a>' if e.get("affiche") else "")
        + f'<div class="jp2-rdv__texte"><span class="jp2-rdv__label">Prochain rendez vous</span>'
        f'<span class="jp2-rdv__titre">{e["titre"]}</span><span class="jp2-rdv__date">{e["date"]}</span>'
        + (f'<span class="jp2-rdv__lieu">{e["lieu"]}</span>' if e.get("lieu") else "")
        + f'<a class="wp-block-button__link wp-element-button jp2-btn jp2-btn--orange" href="{e["lien"]}">{e["bouton"]}</a></div></div>'
        "</div></section>"
    )
    # juste après le premier bandeau photo de l'accueil
    i = t.index('<div class="wp-block-cover alignfull')
    profondeur, j = 0, i
    for m in re.finditer(r"<div\b|</div>", t[i:]):
        profondeur += 1 if m.group(0) == "<div" else -1
        if profondeur == 0:
            j = i + m.end()
            break
    return t[:j] + bloc("accueil", section) + t[j:]


def valeurs(t: str) -> str:
    t = retirer_bloc(t, "documents")
    docs = "".join(
        f'<li><a href="/documents/{d["fichier"]}" target="_blank" rel="noopener"><span class="jp2-doc-ico" aria-hidden="true">PDF</span>'
        f'<span><b>{d["titre"]}</b><small>{d["sous"]}</small></span></a></li>'
        for d in DONNEES["documents"]
    )
    section = (
        '<section class="jp2-section jp2-section--creme alignfull"><div class="jp2-contenu">'
        '<h2 class="jp2-titre">Nos documents officiels</h2>'
        '<p class="jp2-intro">Tout ce qui fait fonctionner l’association, en accès libre.</p>'
        f'<ul class="jp2-docs jp2-docs--ligne">{docs}</ul></div></section>'
    )
    fin = t.index("</main>")
    fin = t.rindex("</div>", 0, fin)
    return t[:fin] + bloc("documents", section) + t[fin:]


def main() -> None:
    nouvelles_pages()
    urls = []
    for f in sorted(PUB.rglob("index.html")):
        rel = f.parent.relative_to(PUB).as_posix()
        chemin = "/" if rel == "." else f"/{rel}/"
        t = lire(f)
        t = menu(t, chemin)
        if chemin == "/":
            t = accueil(t)
        if chemin == "/":
            t = retirer_bloc(t, "carte")
            k = t.index('<h2 class="wp-block-heading jp-titre-bandeau">Deviens bénévole')
            k = t.rindex('<div class="wp-block-cover alignfull', 0, k)
            t = t[:k] + bloc("carte", carte_bloc()) + t[k:]
        if chemin in ("/", "/faire-un-dons/"):
            # Animation « chaque don devient une graine » juste au-dessus de la phrase, dans « À quoi sert votre don ? »
            t = retirer_bloc(t, "graine")
            phrase = t.index("Transformer chaque don en graine de bonheur.", t.index(">À quoi sert votre don ?</h2>"))
            k = t.rindex("<p ", 0, phrase)
            t = t[:k] + bloc("graine", lire(CONTENU / "graine.html")) + t[k:]
        if chemin == "/faire-un-dons/":
            t = retirer_bloc(t, "carte")
            fin = t.rindex("</div>", 0, t.index("</main>"))
            t = t[:fin] + bloc("carte", carte_bloc()) + t[fin:]
        if chemin == "/about/":
            t = valeurs(valeurs_page(t))
        if chemin in ("/", "/faire-un-dons/", "/carte/"):
            t = avec_leaflet(t)
        info = DONNEES["seo"].get(chemin) or next((p for p in DONNEES["pages"] if f"/{p['slug']}/" == chemin), None)
        if info:
            t = meta(t, chemin, info["titre"], info["description"])
        ecrire(f, t)
        if not chemin.startswith(("/tag/", "/category/uncategorized/", "/author/")):
            urls.append(chemin)
    t = menu(lire(PUB / "404.html"), "")
    ecrire(PUB / "404.html", t)
    plan = "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls)
    ecrire(PUB / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{plan}</urlset>\n')
    ecrire(PUB / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(f"{len(urls)} pages dans le plan du site.")


if __name__ == "__main__":
    main()
