"""Jingle de 4 s pour l'animation « chaque don devient une graine » (page dons). Composé pour Onde.

    python outils/musique/jingle_graine.py   -> outils/musique/jingle_graine.json
    ~/tools/onde/onde.exe rendu outils/musique/jingle_graine.json -o outils/musique/jingle_graine.wav

120 BPM : 1 temps = 0,5 s. Calage sur l'animation : chute 0 à 0,7 s (temps 0 à 1,4), impact 0,7 s (1,4),
germination 1,4 à 2,4 s (2,8 à 4,8), feuilles 2,0 s (4), pétales 2,5 s (5), « pop » 3,3 s (6,6), fin 4 s (8).
Instruments réels CC0 (VSCO 2) : glockenspiel, violons pizzicato, violoncelles pizzicato, marimba.
"""
import json
from pathlib import Path

BANQUE = Path.home() / "AppData/Roaming/Onde/banques/vsco2/VSCO-2-CE-SFZ"
ICI = Path(__file__).resolve().parent


def n(at, key, vel=0.8, ln="1/8"):
    return {"at": round(at, 3), "len": ln, "key": key, "vel": vel}


glock = []
# chute : glissando descendant, de plus en plus fort
for i, k in enumerate(["G6", "E6", "D6", "C6", "A5", "G5", "E5"]):
    glock.append(n(0.2 * i, k, 0.45 + 0.05 * i, "1/16"))
# feuilles
glock += [n(4.0, "G5", 0.6), n(4.24, "A5", 0.6)]
# pétales : un tintement par pétale (70 ms = 0,14 temps)
for i, k in enumerate(["C6", "D6", "E6", "G6", "A6", "C7"]):
    glock.append(n(5.0 + 0.14 * i, k, 0.62 + 0.04 * i, "1/8"))
# « pop » final : accord de do majeur
glock += [n(6.6, k, 0.9, "1/2") for k in ("C6", "E6", "G6")]

violons = []
# impact
violons += [n(1.4, "C4", 0.9, "1/8"), n(1.4, "G4", 0.85, "1/8")]
# germination : arpège qui monte
for i, k in enumerate(["C4", "E4", "G4", "A4", "C5", "D5", "E5", "G5"]):
    violons.append(n(2.8 + 0.25 * i, k, 0.55 + 0.04 * i, "1/8"))
violons += [n(6.6, k, 0.9, "1/4") for k in ("C5", "E5", "G5", "C6")]

violoncelles = [n(1.4, "C2", 0.95, "1/4"), n(2.8, "C3", 0.6, "1/8"), n(4.0, "F2", 0.7, "1/8"),
                n(5.0, "G2", 0.75, "1/8"), n(6.6, "C2", 0.95, "1/2")]
marimba = [n(1.4, "C3", 0.8, "1/8"), n(6.6, "C4", 0.7, "1/4"), n(6.6, "G4", 0.7, "1/4")]


def inst(id_, sfz, db):
    return {"id": id_, "type": "multisample", "source": str(BANQUE / sfz).replace("\\", "/"), "level_db": db}


projet = {
    "format": "onde/1", "name": "Jingle graine de bonheur", "tempo": 120, "time_signature": [4, 4],
    "sample_rate": 48000, "key": "Do majeur",
    "instruments": [inst("glock", "Glockenspiel.sfz", -2), inst("violons", "ViolinEnsPizz.sfz", 0),
                    inst("violoncelles", "CelloEnsPizz.sfz", 0), inst("marimba", "Marimba.sfz", -4)],
    "patterns": [{"id": "jingle", "length": "2bar", "humanize_ms": 4, "chords": {},
                  "notes": {"glock": glock, "violons": violons, "violoncelles": violoncelles, "marimba": marimba}}],
    "arrangement": [{"pattern": "jingle", "start": "0bar"}],
    "audio": [], "mixer": [], "master": {"volume_db": -4, "effects": [], "mastering": "streaming"},
    "automation": [], "end": 9, "markers": [],
}
(ICI / "jingle_graine.json").write_text(json.dumps(projet, ensure_ascii=False, indent=1), encoding="utf-8")
print("projet écrit :", ICI / "jingle_graine.json")
