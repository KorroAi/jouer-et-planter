# Film interactif « Chaque don devient une graine de bonheur » : contrat de plan

Page : /faire-un-dons/, nouvelle section juste après « À quoi sert votre don ? » (remplace la petite animation actuelle).
Format : scène 16:9, 960 × 540 de base, adaptée à la largeur (jusqu'à 360 px sur téléphone). **Sans fond** : posée sur le crème de la page.
Moteur : SVG + JavaScript, chaque image = fonction pure du temps (`?t=` pour figer), 60 i/s.
Durée : 14 s, musique à 120 BPM (1 temps = 0,5 s, 1 mesure = 2 s) ; chaque coupe tombe sur un temps.
Son : musique composée avec Onde (−14 LUFS), bruitages en Web Audio ; le son démarre avec le clic du visiteur, bouton son marche/arrêt toujours visible.
Poids visé : moins de 400 Ko en tout (musique comprise).

| id | SUJET | ACTION | GAG / émotion | ÉCHELLES | APPUIS | LIEU + 3 détails | PIÈGES |
|---|---|---|---|---|---|---|---|
| P0 attente | Logo Jouer et Planter + graine dorée | La graine se balance doucement ; gros bouton rond « ▶ Plante ta graine » | Invitation à cliquer | logo 30 % de la largeur, bouton 64 px | logo posé sur une butte de terre | butte de terre, brins d'herbe, petite pancarte bois | pas de rectangle de fond ; rien de figé (balancement) |
| P1 0 à 2 s | Logo | Caméra très serrée sur le logo (×2,2), recul rapide jusqu'à ×1 ; les lettres rebondissent (ressort 0,6) | Le logo « saute » au premier temps | logo de 30 % à 60 % de la largeur | logo sur la butte | butte, herbe, pancarte | lettres coupées par le cadre en fin de plan |
| P2 2 à 4 s | Pièce orange au cœur blanc | Contre-plongée penchée (−6°) : la pièce tombe du ciel, la caméra la suit vers le bas, impact au 4e temps : écrasement, 3 mottes, secousse 3 px | Le « boum » du don qui touche la terre | pièce 40 px, butte 70 % de la largeur | la pièce finit SUR la butte | ciel (aucun aplat vide : 2 nuages, 1 oiseau stylisé au loin), butte, herbe | pièce qui traverse le sol ; son avant l'image |
| P3 4 à 6,5 s | Graine | Raccord de forme : la pièce rétrécit en graine qui s'enfonce ; vue en coupe du sol (3 couches de terre, cailloux, ver de terre) ; la graine se fend, 3 racines se dessinent, le germe monte ; la caméra remonte avec lui | Le ver de terre lève la tête au « crac » | graine 14 px, coupe 80 % de la largeur | graine dans la terre, racines dans la coupe | couches de terre, cailloux, ver de terre | racines qui sortent de la coupe ; terre en aplat vide |
| P4 6,5 à 10 s | Arbre qui grandit | Plan large, travelling latéral avec parallaxe (collines 0,2, village 0,5, herbe 1,0) : la pousse devient arbre, puis 12 fleurs orange s'ouvrent en cascade (60 ms d'écart), un « pop » sonore par fleur | Le village se réveille : guirlande de fête qui s'allume | arbre 55 % de la hauteur, maisons 18 % | arbre planté dans la butte, maisons sur les collines | village : clocher, toits, guirlande de fête | arbre qui flotte ; fleurs sans branche ; tout en fondu |
| P5 10 à 14 s | Arbre en fleurs + logo + phrase | La caméra recule et se pose ; la phrase « Transformer chaque don en graine de bonheur » s'écrit mot par mot (90 ms) ; bouton orange « Faire un don » qui fait un pop au dernier temps | Fin heureuse, envie de donner | phrase lisible à 360 px (≥ 18 px) | phrase et bouton à droite de l'arbre, jamais sur l'arbre | arbre, village, guirlande | texte qui bouge pendant la lecture ; texte clair sur fond clair |
| Fin interactive | Arbre | Chaque clic sur l'arbre fait éclore une fleur avec une note de musique (gamme pentatonique) ; boutons « Rejouer » et son | Le visiteur « plante » à son tour | — | — | — | clic qui bloque la page ; son qui démarre sans clic |

Interdits (motion design) : dégradés violet/bleu, halo, reflets d'objectif, particules décoratives, tout en fondu en même temps, texte qui bouge pendant la lecture, fond sombre, slogan inventé.
Accessibilité : si le visiteur a réduit les animations, image finale fixe + bouton « Faire un don » ; contraste du texte ≥ 4,5:1 ; aucun flash.
