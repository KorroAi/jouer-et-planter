"""Retouches du 09/11/2026 : challenge 2 (bains d'eau froide) mis en avant, nouvel article, engagements de l'accueil.

Modifie directement public/ (source du site). Relançable : chaque étape vérifie si elle est déjà faite.
    python outils/retouches/2026-11-09-challenge-2.py
"""
import re
from pathlib import Path

PUB = Path(__file__).resolve().parents[2] / "public"
AFF = "/images/affiche-challenge-2-bain-ubaye.jpg"
ALT = "Affiche du Challenge 2 associatif : samedi 2 janvier à minuit, bain d’eau froide à moins 5 degrés, à la rivière de l’Ubaye"
ART = "/2026/11/09/challenge-2-bains-deau-froide/"
ART_TITRE = "Challenge 2 : bains d’eau froide dans l’Ubaye"
ART_EXTRAIT = "Samedi 2 janvier 2027 à minuit, nous plongeons dans la rivière de l’Ubaye, à Barcelonnette, par moins 5 degrés et déguisés en lapin."


def lire(p):
    return p.read_text(encoding="utf-8")


def ecrire(p, t):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, encoding="utf-8")


def bloc_div(t, debut):
    """Renvoie (début, fin) du <div> qui commence à l'index debut."""
    prof = 0
    for m in re.finditer(r"<div\b|</div>", t[debut:]):
        prof += 1 if m.group(0) == "<div" else -1
        if prof == 0:
            return debut, debut + m.end()
    raise ValueError("div non fermé")


def li_article(avec_image=True):
    img = (f'<div class="wp-block-latest-posts__featured-image"><a href="{ART}"><img alt="{ALT}" class="attachment-large size-large wp-post-image" '
           f'decoding="async" src="{AFF}" width="900" height="1350" style="max-height:340px;width:auto"/></a></div>') if avec_image else ""
    return (f'<li class="jp2-article-nouveau">{img}<a class="wp-block-latest-posts__post-title" href="{ART}">{ART_TITRE}</a>'
            f'<time class="wp-block-latest-posts__post-date" datetime="2026-11-09T18:00:00+01:00">9 novembre 2026</time>'
            f'<div class="wp-block-latest-posts__post-excerpt">{ART_EXTRAIT} <a class="wp-block-latest-posts__read-more" href="{ART}">Lire la suite</a></div></li>')


def listes_blog(t):
    """Ajoute l'article en tête des listes « derniers articles » et remplace l'affiche du challenge 1 à côté."""
    if "jp2-article-nouveau" not in t:
        t = t.replace('<ul class="wp-block-latest-posts__list', '<ul class="wp-block-latest-posts__list', 1)
        t = re.sub(r'(<ul class="wp-block-latest-posts__list[^"]*">)', lambda m: m.group(1) + li_article(False), t, count=1)
    # affiche de la colonne de droite du blog : challenge 1 -> challenge 2, lien vers l'article
    t = re.sub(
        r'<a href="/challenges/"><img alt="Affiche du Challenge 1 associatif[^"]*"([^>]*?)src="/wp-content/uploads/2026/10/affiche-challenge-velo-v3.jpg"/></a>',
        lambda m: f'<a href="{ART}"><img alt="{ALT}"{m.group(1)}src="{AFF}"/></a>', t)
    return t


# ---------- Accueil ----------
p = PUB / "index.html"
t = lire(p)
i = t.find('<div class="wp-block-group jp-grappe jp-grappe--espacee')
if i != -1:
    a, b = bloc_div(t, i)
    textes = re.findall(r'<p class="has-text-align-center wp-block-paragraph">(.*?)</p>', t[a:b])
    assert len(textes) == 4, textes
    cartes = "".join(f'<article class="jp2-engagement"><span class="jp2-num">{k}</span><p>{x}</p></article>' for k, x in enumerate(textes, 1))
    t = t[:a] + f'<div class="jp2-grille jp2-grille--4 jp2-engagements">{cartes}</div>' + t[b:]
k = t.index(">Blog associatif</h2>")
t = t[:k] + listes_blog(t[k:])
ecrire(p, t)

# ---------- Challenges ----------
p = PUB / "challenges" / "index.html"
t = lire(p)
# l'encart ajouté plus tôt en haut de page fait doublon avec la nouvelle section : on le retire
t = re.sub(r'<section id="prochain-challenge" class="jp2-section jp2-section--bleu alignfull">.*?</section>', "", t, flags=re.S)
if 'id="becane-infernale"' in t:
    k = t.index('id="becane-infernale"')
    debut = t.rindex(">1er challenge</p>", 0, k)
    fin = t.index(">Suivre nos challenges sur le blog<", k)
    zone = t[debut:fin]
    for a_, b_ in (
        (">1er challenge</p>", ">2e challenge</p>"),
        ('id="becane-infernale">L’Épopée de la « Bécane Infernale »</h2>', 'id="prochain-challenge">Le Challenge 2 : bains d’eau froide</h2>'),
        (">Barcelonnette ➔ Valpréveyre</p>", ">Barcelonnette ➔ rivière de l’Ubaye</p>"),
        (">Lundi 12 octobre</p>", ">Samedi 2 janvier 2027</p>"),
        (">6 heures d’ascension…</p>", ">À minuit…</p>"),
        (">… sur un vélo pourri !</p>", ">… par moins 5 degrés !</p>"),
        (">Soutenir le défi</a>", ">Soutenir le challenge</a>"),
        ('href="/2026/07/22/challenges-1er/" style="color:#1d2410">Lire l’article</a>', f'href="{ART}" style="color:#1d2410">Lire l’article</a>'),
    ):
        assert a_ in zone, a_
        zone = zone.replace(a_, b_, 1)
    # texte de la colonne : du « Pourquoi ce défi fou ? » jusqu'à la fin de la liste « objectif »
    d = zone.index('<h3 class="wp-block-heading">Pourquoi ce défi fou ?</h3>')
    f = zone.index("</ul>", zone.index("Quel est l’objectif ?")) + len("</ul>")
    nouveau = (
        '<h3 class="wp-block-heading">Pourquoi ce défi fou ?</h3>'
        '<p class="wp-block-paragraph">Chez Jouer et Planter, nous croyons que la joie naît de l’effort et de l’absurde. '
        'Après la « Bécane Infernale » du 12 octobre, nous plongeons cette fois dans l’eau glacée de l’Ubaye, à minuit, déguisés en lapin.</p>'
        '<p class="wp-block-paragraph">Nos challenges sont des épreuves pour dépasser ses propres limites physiques et psychiques, dans un but de bien être humain.</p>'
        '<h3 class="wp-block-heading">Le rendez vous</h3>'
        '<ul class="wp-block-list">'
        '<li><strong>Quand :</strong> samedi 2 janvier 2027, à minuit.</li>'
        '<li><strong>Où :</strong> à la rivière de l’Ubaye, à Barcelonnette.</li>'
        '<li><strong>Pour qui :</strong> tous ceux qui veulent relever le défi. Un mineur peut participer uniquement avec une autorisation écrite de ses parents ou de la personne qui en a la responsabilité.</li>'
        '</ul>'
        '<h3 class="wp-block-heading">Quel est l’objectif ?</h3>'
        '<ul class="wp-block-list">'
        '<li><strong>Récolter des fonds :</strong> chaque don sert à financer nos projets de plantations et des fêtes dans les villages français.</li>'
        '<li><strong>Se dépasser :</strong> montrer que la volonté peut transformer n’importe quelle situation, même un bain glacé en pleine nuit.</li>'
        '</ul>'
    )
    zone = zone[:d] + nouveau + zone[f:]
    # images de la colonne : affiche du challenge 2 à la place du challenge 1, plus de carte du parcours vélo
    zone = re.sub(r'<img alt="Affiche du Challenge 1 associatif[^"]*"([^>]*?)src="/wp-content/uploads/2026/10/affiche-challenge-velo-v3.jpg"/>',
                  lambda m: f'<img alt="{ALT}"{m.group(1)}src="{AFF}"/>', zone, count=1)
    zone = re.sub(r'<figure class="wp-block-image size-large jp-photo jp-carte-parcours">.*?</figure>', "", zone, flags=re.S)
    t = t[:debut] + zone + t[fin:]
k = t.index(">Suivre nos challenges sur le blog<")
t = t[:k] + listes_blog(t[k:])
ecrire(p, t)

# ---------- Nouvel article ----------
src = lire(PUB / "2026" / "10" / "08" / "1er-challenges" / "index.html")
corps = f"""
<p class="wp-block-paragraph">Bonjour à toutes et à tous !</p>
<p class="wp-block-paragraph">Après la « Bécane Infernale », voici le deuxième challenge de Jouer et Planter : <strong>un bain d’eau froide dans la rivière de l’Ubaye</strong>, à Barcelonnette.</p>
<p class="wp-block-paragraph">Rendez vous le <strong>samedi 2 janvier 2027 à minuit</strong>, au bord de l’Ubaye. Au programme : de l’eau glacée, <strong>moins 5 degrés</strong> et, comme toujours, des costumes de lapin !</p>
<figure class="wp-block-image size-large"><img alt="{ALT}" decoding="async" height="1350" src="{AFF}" width="900"/></figure>
<h2 class="wp-block-heading">Le premier challenge en chiffres</h2>
<p class="wp-block-paragraph">Le lundi 12 octobre 2026, la « Bécane Infernale » a relié Barcelonnette à Valpréveyre : <strong>87 km</strong>, <strong>8 h 35 de vélo non stop</strong> et seulement <strong>5 pauses de 5 minutes</strong>.</p>
<h2 class="wp-block-heading">Pourquoi se baigner dans l’eau glacée ?</h2>
<p class="wp-block-paragraph">Nos challenges sont des épreuves pour dépasser ses propres limites physiques et psychiques, dans un but de bien être humain. Et chaque don récolté finance nos plantations et nos fêtes dans les villages.</p>
<h2 class="wp-block-heading">Comment participer</h2>
<p class="wp-block-paragraph">Tu veux relever le défi avec nous ? Écris à l’association. Un mineur peut participer uniquement avec une autorisation écrite de ses parents ou de la personne qui en a la responsabilité.</p>
<div class="wp-block-buttons is-layout-flex wp-block-buttons-is-layout-flex">
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" href="mailto:joueretplanter@proton.me?subject=Je%20participe%20au%20bain%20d%27eau%20froide" style="color:#ffffff;background-color:#2b2f9e">Je veux participer</a></div>
</div>
<h2 class="wp-block-heading">Comment nous aider</h2>
<p class="wp-block-paragraph">Transformer chaque don en graine de bonheur.</p>
<div class="wp-block-buttons is-layout-flex wp-block-buttons-is-layout-flex">
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" href="/faire-un-dons/" style="color:#1d2410;background-color:#fd9a08">Faire un don</a></div>
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" href="https://whatsapp.com/channel/0029VbEFFdm3LdQMiE0TdR1c" style="color:#ffffff;background-color:#2f6b17">Suis notre chaîne WhatsApp</a></div>
</div>
<p class="wp-block-paragraph">À très vite,<br/>L’équipe Jouer et Planter</p>
<figure class="wp-block-image size-full is-resized"><a href="/"><img alt="Jouer et Planter" decoding="async" height="262" src="/wp-content/uploads/2026/09/logo-jouer-et-planter-email.png" style="width:90px;height:auto" width="378"/></a></figure>
"""
a = src.index('<p class="wp-block-paragraph">Bonjour à toutes et à tous !</p>')
a = src.rindex(">", 0, a) + 1
b = src.index('<figure class="wp-block-image size-full is-resized"><a href="/">', a)
b = src.index("</figure>", b) + len("</figure>")
t = src[:a] + corps + src[b:]
t = t.replace('<h1 class="wp-block-post-title">1er Challenges !!</h1>', f'<h1 class="wp-block-post-title">{ART_TITRE}</h1>')
t = re.sub(r'<div class="wp-block-post-author-name">.*?</div>', '<div class="wp-block-post-author-name">L’équipe Jouer et Planter</div>', t, count=1, flags=re.S)
t = t.replace('<a href="/category/uncategorized/" rel="tag">Uncategorized</a>', '<a href="/category/challenges-jp/" rel="tag">Challenges</a>', 1)
t = re.sub(r'<div class="post-navigation-link-previous wp-block-post-navigation-link">.*?</div>',
           '<div class="post-navigation-link-previous wp-block-post-navigation-link"><span aria-hidden="true" class="wp-block-post-navigation-link__arrow-previous is-arrow-arrow">←</span><a href="/2026/10/08/1er-challenges/" rel="prev">1er Challenges !!</a></div>',
           t, count=1, flags=re.S)
t = re.sub(r'<div class="post-navigation-link-next wp-block-post-navigation-link">.*?</div>', '<div class="post-navigation-link-next wp-block-post-navigation-link"></div>', t, count=1, flags=re.S)
t = re.sub(r'<script type="application/ld\+json">.*?</script>', "", t, flags=re.S)
t = re.sub(r'<meta content="[^"]*" property="article:(?:published|modified)_time"/>', "", t)
t = t.replace(f'content="https://joueretplanter.com/wp-content/uploads/2026/10/affiche-challenge-velo-v3.jpg" property="og:image"',
              f'content="https://joueretplanter.com{AFF}" property="og:image"')
plus = (f'<li class="wp-block-post jp2-article-nouveau"><div class="wp-block-group"><h3 class="wp-block-post-title has-large-font-size"><a href="{ART}" target="_self">{ART_TITRE}</a></h3>'
        f'<div class="has-text-align-right wp-block-post-date"><a href="{ART}"><time datetime="2026-11-09T18:00:00+01:00">9 novembre 2026</time></a></div></div></li>')


def plus_de_publications(x):
    if "jp2-article-nouveau" in x[x.find(">Plus de publications</h2>"):]:
        return x
    k = x.find(">Plus de publications</h2>")
    if k == -1:
        return x
    u = x.index("<ul", k)
    u = x.index(">", u) + 1
    return x[:u] + plus + x[u:]


ecrire(PUB / ART.strip("/") / "index.html", plus_de_publications(t))

# lien « suivant » et liste « Plus de publications » sur les autres articles
for chemin in ("2026/10/08/1er-challenges", "2026/07/22/challenges-1er"):
    p = PUB / chemin / "index.html"
    x = lire(p)
    if chemin == "2026/10/08/1er-challenges":
        x = re.sub(r'<div class="post-navigation-link-next wp-block-post-navigation-link"></div>',
                   f'<div class="post-navigation-link-next wp-block-post-navigation-link"><a href="{ART}" rel="next">{ART_TITRE}</a><span aria-hidden="true" class="wp-block-post-navigation-link__arrow-next is-arrow-arrow">→</span></div>', x, count=1)
    ecrire(p, plus_de_publications(x))
print("retouches appliquées")
