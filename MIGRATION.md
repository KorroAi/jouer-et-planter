# Quitter WordPress : marche à suivre

Objectif : joueretplanter.com servi par Vercel, newsletter sur Brevo, domaine transféré chez Vercel, plus rien chez WordPress.com.

**L'ordre compte.** Le site WordPress doit rester en ligne jusqu'à l'étape 5 : c'est lui qui sert de source à l'export,
et c'est là que se trouvent les abonnés.

## État au 09/11/2026

- [x] Site statique copié du site en ligne dans `public/` (18 pages, médiathèque complète).
  Les 6 pages principales sont identiques au pixel près, sur ordinateur et sur téléphone (`outils/comparer.py`).
  Seul le bloc « Commentaires » des articles a disparu, car un site statique ne gère pas les commentaires.
- [x] Menu mobile et formulaire newsletter testés en local. Le formulaire attend l'adresse Brevo (étape 2).
- [x] Étape 1 faite : en ligne sur https://jouer-et-planter.vercel.app (projet Vercel `jouer-et-planter`, équipe korro).
  La comparaison donne le même résultat qu'en local.
- [x] Étape 4.1 faite le 09/11 : `joueretplanter.com` et `www` ajoutés au projet Vercel, www redirige vers joueretplanter.com (`vercel.json`).
  Zone DNS WordPress relevée avant bascule : pas de MX ; SPF `include:_spf.wpcloud.com` (envois WordPress, inutile ensuite) ;
  `_dmarc` TXT `v=DMARC1;p=none;` à recopier chez Vercel (refusé en mode auto, à faire par l'utilisateur).
  **Dès que les serveurs de noms pointent sur Vercel, `exporter_wordpress.py` ne doit plus être lancé** : joueretplanter.com ne sera plus WordPress.
- [x] 09/11 : serveurs de noms WordPress → Vercel (propagé) ; Brevo branché (formulaire, domaine authentifié, expéditeur
  newsletter@joueretplanter.com, modèle) ; ajouts du site en ligne (Jouer, Planter, Artistes, Bénévoles, Carte, compteurs, documents, SEO).
- [ ] **En pause à la demande de l'utilisateur** : transfert du domaine (12,03 $ chez Vercel, 1 an ajouté). Le compte WordPress
  crabsdutieks n'a pas d'option « Transférer » : le domaine semble appartenir à un autre compte WordPress.com. Code EPP obtenu
  par l'utilisateur, à saisir par lui (Vercel › Domains › Transfer In). À faire avant l'échéance 2027.
- [ ] Après le transfert : supprimer le site WordPress (et sa newsletter Jetpack), annuler le plan Personnel.
  D'ici là : ne rien publier sur l'ancien site WordPress (Jetpack enverrait l'article aux anciens abonnés).
- [ ] Étapes 2 à 6 ci-dessous (déjà faites, voir ci-dessus). Version illustrée pour l'utilisateur : `GUIDE-QUITTER-WORDPRESS.pdf`
  (source `outils/guide/guide.html`, régénérer avec `python outils/guide/faire_pdf.py`).

## 1. Mettre le site sur Vercel (adresse provisoire)

```
vercel login
vercel link          # créer un projet « joueretplanter »
vercel deploy        # aperçu, puis : vercel deploy --prod
```

`vercel.json` publie le dossier `public/` tel quel (aucune compilation) et garde les anciennes redirections WordPress.

Le plan gratuit Hobby est réservé à un usage « personnel, non commercial ». Pour une association qui reçoit des dons,
c'est flou. Le plan Pro coûte 20 $ par mois. Sinon, on peut basculer vers Cloudflare Pages sans rien changer au site.

## 2. Brevo (newsletter)

1. Créer un compte Brevo au nom de l'association (adresse joueretplanter@proton.me).
2. Contacts › Listes : créer une liste « Newsletter Jouer et Planter ».
3. Contacts › Formulaires : créer un formulaire d'inscription vers cette liste.
   - Activer la **double confirmation** (double opt in).
   - Langue : français. Textes en tutoiement, **sans tirets**.
   - Message de bienvenue : celui de Jetpack, dans `../jouer-et-planter-wp/etat-du-site-en-ligne.json` (`newsletter.welcome`).
4. Partager › Code HTML : copier l'adresse `action="https://….sibforms.com/serve/…"`, puis :
   ```
   python outils/brevo.py "https://….sibforms.com/serve/…"
   ```
   Tester une inscription sur l'aperçu Vercel, puis redéployer.
5. Expéditeur : Paramètres › Expéditeurs et domaines.
   - Ajouter le domaine joueretplanter.com.
   - Brevo donne des enregistrements DNS (code Brevo, DKIM, DMARC). Ils se mettent chez Vercel (étape 4) ; avant cela, chez WordPress.com.

## 3. Récupérer les abonnés Jetpack

1. WordPress.com › joueretplanter.com › Abonnés › Exporter (CSV).
2. Brevo › Contacts › Importer, dans la liste de l'étape 2.
   - Ils ont déjà accepté de recevoir la newsletter de l'association. Le dire dans le premier email Brevo, avec le lien de désinscription.
3. Garder le CSV hors du dépôt git : il contient des données personnelles.
4. Refaire le modèle d'email dans Brevo à partir de `../jouer-et-planter-wp/code/9-modele-newsletter.txt`.
   Logo des emails : `public/wp-content/uploads/2026/09/logo-jouer-et-planter-email.png`.

**Différence avec Jetpack** : Brevo n'envoie plus chaque article automatiquement. Une newsletter = une campagne
envoyée depuis Brevo. Plan gratuit : 300 emails par jour, logo Brevo en bas des emails.

## 4. Brancher le domaine sur Vercel (sans coupure)

1. Vercel › projet › Settings › Domains : ajouter `joueretplanter.com` et `www.joueretplanter.com`.
2. WordPress.com › Domaines › joueretplanter.com › Serveurs de noms : remplacer par ceux que Vercel indique
   (`ns1.vercel-dns.com`, `ns2.vercel-dns.com`).
3. Dans Vercel DNS, ajouter les enregistrements Brevo de l'étape 2.5.
4. Vérifier https://joueretplanter.com : c'est maintenant Vercel, avec le certificat HTTPS automatique.

## 5. Transférer le domaine chez Vercel

1. WordPress.com › Domaines › joueretplanter.com › Transférer › déverrouiller, puis demander le code d'autorisation (EPP).
   Impossible dans les 60 jours qui suivent l'achat du domaine.
2. `vercel domains transfer-in joueretplanter.com` avec ce code. Le transfert ajoute un an de renouvellement, payant : le prix s'affiche avant validation.
3. Valider l'email de confirmation éventuel. Le transfert prend jusqu'à 5 à 7 jours, et le site reste en ligne pendant ce temps.

## 6. Fermer WordPress.com (seulement quand 1 à 5 sont terminées)

- Garder une sauvegarde : Outils › Exporter (contenu) + `../jouer-et-planter-wp/` (déjà fait).
- Annuler le plan Personnel (renouvellement prévu le 25/06/2027). Le remboursement n'est possible que peu après un achat.
- Ton compte WordPress.com gère aussi un autre site : **n'annuler que ce qui concerne joueretplanter.com**.
- Désactiver la newsletter Jetpack du site, pour que personne ne reçoive d'email en double.

## Modifier le site ensuite

Le site n'a plus d'éditeur : on modifie directement les fichiers HTML de `public/`, puis on redéploie (`vercel deploy --prod`).
Tant que WordPress est en ligne, `python outils/exporter_wordpress.py` recopie tout ; après la fermeture, **ne plus le lancer**.
Il viderait `public/` et ne trouverait plus rien.
