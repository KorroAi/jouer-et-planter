"""Branche le formulaire newsletter de toutes les pages sur Brevo.

    python outils/brevo.py "https://xxxx.sibforms.com/serve/MUIF..."

L'adresse se trouve dans Brevo : Contacts > Formulaires > ton formulaire > Partager > « Code HTML »,
attribut action="..." de la balise <form>. Elle est aussi enregistrée dans outils/config.json
pour les prochains exports.
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

if len(sys.argv) != 2 or not sys.argv[1].startswith("https://"):
    sys.exit(__doc__)
action = sys.argv[1].strip()

config = RACINE / "outils" / "config.json"
data = json.loads(config.read_text(encoding="utf-8"))
data["brevo_form_action"] = action
config.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

n = 0
for f in (RACINE / "public").rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    t2 = re.sub(
        r'<form [^>]*class="jp-brevo"[^>]*>',
        lambda m: re.sub(r'action="[^"]*"', f'action="{action}"', m.group(0)),
        t,
    )
    if t2 != t:
        f.write_text(t2, encoding="utf-8")
        n += 1
print(f"Formulaire Brevo branché sur {n} pages.")
