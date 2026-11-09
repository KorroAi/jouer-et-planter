# Jouer et Planter : site statique (sortie de WordPress)

Site de l'association joueretplanter.com, copié du WordPress.com en ligne pour être hébergé sur **Vercel**.
Newsletter : **Brevo** (remplace Jetpack). Domaine : transfert de WordPress.com vers Vercel.
**Avancement et étapes restantes : `MIGRATION.md`.**

## Fichiers
- `public/` : le site publié, tel quel. Mêmes adresses que WordPress.
  - Médias sous `/wp-content/uploads/…`, pour que les anciens emails gardent leurs images.
  - `assets/js/site.js` gère le menu mobile et l'envoi du formulaire Brevo ; `assets/css/ajouts.css` contient les styles ajoutés.
- `outils/exporter_wordpress.py` : recopie le site WordPress en ligne dans `public/` (le **vide** d'abord).
  Ne marche que tant que WordPress est en ligne ; ensuite, **ne plus le lancer**.
  Les fichiers de `outils/statique/` sont recopiés dans `public/`.
- `outils/comparer.py` : captures pleine page, local contre en ligne, sur ordinateur et téléphone, avec le pourcentage de pixels différents.
- `outils/brevo.py "<action>"` : branche le formulaire newsletter de toutes les pages sur Brevo (enregistré dans `outils/config.json`).
- `vercel.json` : publie `public/` sans compilation, avec les redirections des anciennes adresses WordPress.
- L'ancienne maquette (pages `index`, `actions`…) a été retirée le 09/11/2026 ; elle reste dans le commit `28bec21`.
- Le kit WordPress `../jouer-et-planter-wp/` reste la référence pour le contenu et l'historique (modèle de newsletter, règles).

## Pages ajoutées (09/11/2026) : `python outils/pages.py`
- WordPress n'existe plus derrière joueretplanter.com (DNS chez Vercel) : **ne plus lancer `exporter_wordpress.py`**. `public/` est la source.
- `outils/pages.py` (relançable) crée /jouer/, /planter/, /artistes/, /benevoles/, /carte/ depuis `outils/contenu/*.html`,
  refait le menu partout, ajoute compteurs + prochain rendez vous (accueil) et documents (/about/), titres/descriptions SEO,
  `sitemap.xml`, `robots.txt`. Chiffres, rendez vous, documents, villes, SEO : `outils/contenu/site.json`.
- Carte des actions (page /carte/, accueil, dons) : `site.json > carte` (catégories colorées + lieux, une ville peut avoir
  plusieurs catégories). La catégorie « fêtes » (rose) n'a encore aucun lieu : elle n'apparaît pas tant qu'il n'y en a pas.
- /about/ : bandeau WordPress d'origine + `outils/contenu/valeurs.html` + documents. Accueil, /challenges/, /faire-un-dons/
  ont été retouchés directement dans `public/` (pas de copie ailleurs : faire attention).
- Piège vu le 09/11 : des `\b` / `\1` écrits via heredoc bash dans du Python sont devenus des caractères invisibles
  (\x08, \x01) et ont cassé une page. Écrire le Python avec l'outil Write, pas en heredoc.
- /ma-commune/ (idée « Ma commune veut une fête », 10/11) : candidature par mailto (rien stocké), communes candidates
  dans `site.json > communes` [{nom, departement, texte}]. Pas encore de votes (il faudrait une base, ex. Upstash via Vercel).
- Règles de texte en plus : aucun point-virgule visible (`outils/retouches/points-virgules.py`, relançable).
- Animation de la fleur (accueil + dons) : `outils/contenu/graine.html` + bloc « Page dons » de site.js ; musique Onde
  `outils/musique/jingle_graine.py` → `public/assets/audio/jingle-graine.mp3` (calée : impact 0,7 s, pop 3,3 s).
- Styles et JS : modifier `outils/statique/assets/` puis copier dans `public/assets/`.
- PDF publics dans `public/documents/` (fiche bénévole : numéro de téléphone effacé, à la demande de l'utilisateur).
- Brevo : formulaire branché (`outils/config.json`), expéditeur newsletter@joueretplanter.com (réponses vers le Proton),
  domaine authentifié, modèle « Modèle de newsletter Jouer et Planter » (source `outils/newsletter/modele-newsletter.html`).
- Publier : `vercel deploy` (aperçu) puis `vercel deploy --prod`.

## Aperçu local
`python -m http.server 8765 --directory public` puis http://localhost:8765.

## Règles de l'association
- Aucun tiret dans les textes visibles.
- Ne rien inventer (chiffres, faits, contacts).
- Tutoiement dans la newsletter et les boutons, vouvoiement sur les pages de don.
- Couleurs : orange `#fd9a08` (don), vert `#2f6b17` (rejoindre), bleu `#2b2f9e` (newsletter), forêt `#1c3b10` (pied de page).
