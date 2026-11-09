"""Remplace les points-virgules du TEXTE VISIBLE par des points (règle de l'association, 10/11/2026).

Ne touche pas : balises et attributs, <script>, <style>, commentaires, entités HTML (&amp; &nbsp;…).
« résistant à la sécheresse ; » devient « résistant à la sécheresse. »
    python outils/retouches/points-virgules.py
"""
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parents[2]
JETONS = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<[^>]+>)", re.S | re.I)
PV = re.compile(r"(&[#A-Za-z0-9]+;)|[   ]*;")


def texte(t):
    return PV.sub(lambda m: m.group(1) if m.group(1) else ".", t)


def html(s):
    morceaux = JETONS.split(s)
    n = 0
    for i in range(0, len(morceaux), 2):  # indices pairs = texte hors balises
        neuf = texte(morceaux[i])
        if neuf != morceaux[i]:
            n += morceaux[i].count(";") - neuf.count(";")
            morceaux[i] = neuf
    return "".join(morceaux), n


total = 0
fichiers = list((R / "public").rglob("*.html")) + list((R / "outils/contenu").glob("*.html"))
for f in fichiers:
    s = f.read_text(encoding="utf-8")
    neuf, n = html(s)
    if n:
        f.write_text(neuf, encoding="utf-8")
        total += n
        print(f"  {f.relative_to(R)} : {n}")

# Textes de site.json (titres, descriptions, accroches) : ils finissent dans les pages et les résultats Google
j = R / "outils/contenu/site.json"
d = json.loads(j.read_text(encoding="utf-8"))


def parcourir(x):
    global total
    if isinstance(x, dict):
        return {k: parcourir(v) for k, v in x.items()}
    if isinstance(x, list):
        return [parcourir(v) for v in x]
    if isinstance(x, str) and ";" in x and not x.startswith("#"):
        total += x.count(";")
        return texte(x)
    return x


j.write_text(json.dumps(parcourir(d), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("points-virgules remplacés :", total)
