// Site statique Jouer et Planter : menu mobile + inscription newsletter (Brevo).

(function () {
  // ---------- Menu mobile (remplace le script « navigation » de WordPress) ----------
  document.querySelectorAll('.wp-block-navigation').forEach(function (nav) {
    var ouvrir = nav.querySelector('.wp-block-navigation__responsive-container-open');
    var conteneur = nav.querySelector('.wp-block-navigation__responsive-container');
    if (!ouvrir || !conteneur) return;
    var fermer = conteneur.querySelector('.wp-block-navigation__responsive-container-close');
    var dialogue = conteneur.querySelector('.wp-block-navigation__responsive-dialog');

    function etat(ouvert) {
      conteneur.classList.toggle('has-modal-open', ouvert);
      conteneur.classList.toggle('is-menu-open', ouvert);
      document.documentElement.classList.toggle('has-modal-open', ouvert);
      if (dialogue) {
        if (ouvert) {
          dialogue.setAttribute('aria-modal', 'true');
          dialogue.setAttribute('role', 'dialog');
          dialogue.setAttribute('aria-label', 'Menu');
        } else {
          dialogue.removeAttribute('aria-modal');
          dialogue.removeAttribute('role');
        }
      }
      (ouvert ? fermer : ouvrir) && (ouvert ? fermer : ouvrir).focus();
    }

    ouvrir.addEventListener('click', function () { etat(true); });
    if (fermer) fermer.addEventListener('click', function () { etat(false); });
    conteneur.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && conteneur.classList.contains('is-menu-open')) etat(false);
    });
    conteneur.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { if (conteneur.classList.contains('is-menu-open')) etat(false); });
    });
  });

  // ---------- Newsletter : formulaire Brevo envoyé sans quitter la page ----------
  document.querySelectorAll('form.jp-brevo').forEach(function (form) {
    var message = form.querySelector('.jp-brevo-message');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var action = form.getAttribute('action');
      if (!action) {
        message.textContent = "Les inscriptions rouvrent très bientôt. Merci de repasser plus tard !";
        return;
      }
      form.classList.add('is-envoi');
      message.textContent = '';
      fetch(action + (action.indexOf('?') < 0 ? '?' : '&') + 'isAjax=1', { method: 'POST', body: new FormData(form) })
        .then(function (r) { return r.json(); })
        .then(function (rep) {
          if (rep && rep.success) {
            form.reset();
            message.textContent = 'Merci ! Ouvre l’email que nous venons de t’envoyer pour confirmer ton inscription.';
          } else {
            message.textContent = 'L’inscription n’a pas fonctionné. Vérifie ton adresse email et réessaie.';
          }
        })
        .catch(function () { form.submit(); }) // si l'envoi discret échoue, envoi classique vers Brevo
        .finally(function () { form.classList.remove('is-envoi'); });
    });
  });
})();

// ---------- Compteurs de l'accueil : animation jusqu'aux vrais chiffres ----------
(function () {
  var nombres = document.querySelectorAll('.jp2-compteur b[data-cible]');
  if (!nombres.length || !('IntersectionObserver' in window)) return;
  var obs = new IntersectionObserver(function (entrees) {
    entrees.forEach(function (e) {
      if (!e.isIntersecting) return;
      obs.unobserve(e.target);
      var cible = +e.target.getAttribute('data-cible'), t0 = null;
      e.target.textContent = '0';
      function pas(t) {
        t0 = t0 || t;
        var p = Math.min(1, (t - t0) / 1400);
        e.target.textContent = Math.round(cible * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(pas);
      }
      requestAnimationFrame(pas);
    });
  }, { threshold: 0.4 });
  nombres.forEach(function (n) { obs.observe(n); });
})();

// ---------- Carte des actions (accueil, dons, /carte/) ----------
window.addEventListener('load', function () {
  if (!window.L) return;
  // Décalage des points quand une ville a plusieurs catégories (Barcelonnette...)
  var DECALAGES = [[0, 0], [16, 0], [-16, 0], [0, 16]];
  document.querySelectorAll('.jp2-section--carte').forEach(function (section) {
    var zone = section.querySelector('.jp2-carte-map'), data = section.querySelector('.jp2-carte-data');
    if (!zone || !data) return;
    var c = JSON.parse(data.textContent);
    var carte = L.map(zone, { scrollWheelZoom: false });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '&copy; contributeurs <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(carte);
    var liste = section.querySelector('.jp2-villes'), points = [];
    c.lieux.forEach(function (lieu) {
      var marqueurs = [];
      lieu.cat.forEach(function (k, i) {
        var cat = c.categories[k], d = DECALAGES[i % DECALAGES.length];
        var icone = L.divIcon({
          className: '',
          html: '<span style="display:block;width:20px;height:20px;border-radius:50%;background:' + cat.couleur + ';border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.35)"></span>',
          iconSize: [20, 20], iconAnchor: [10 - d[0], 10 - d[1]], popupAnchor: [d[0], d[1] - 10]
        });
        var m = L.marker([lieu.lat, lieu.lng], { icon: icone, title: lieu.nom }).addTo(carte)
          .bindPopup('<b>' + lieu.nom + '</b><br>' + (cat.nom ? cat.nom + ' (' + cat.texte + ')' : cat.texte));
        marqueurs.push(m);
      });
      points.push([lieu.lat, lieu.lng]);
      if (liste) {
        var li = document.createElement('li'), b = document.createElement('button');
        b.type = 'button'; b.textContent = lieu.nom;
        b.addEventListener('click', function () {
          carte.setView([lieu.lat, lieu.lng], 11); marqueurs[0].openPopup();
          zone.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
        li.appendChild(b); liste.appendChild(li);
      }
    });
    if (points.length) carte.fitBounds(points, { padding: [30, 30] });
  });
});

// ---------- Page dons : « chaque don devient une graine de bonheur » ----------
// Chaque image est une fonction pure du temps t (ms). ?t=2.5 dans l'adresse fige l'instant 2,5 s.
// Musique : jingle composé avec Onde (/assets/audio/jingle-graine.mp3), calé sur l'image (impact 0,7 s, pétales 2,5 s, pop 3,3 s).
// Bruitages : générés en Web Audio, 1 image (16 ms) après l'image correspondante. Le son ne part qu'après un clic.
(function () {
  var bouton = document.querySelector('.jp2-graine');
  if (!bouton) return;
  var svg = bouton.querySelector('svg');
  var q = function (s) { return svg.querySelector(s); };
  var tous = function (s) { return svg.querySelectorAll(s); };
  var piece = q('.jp2-g-piece'), face = q('.jp2-g-piece-face'), graine = q('.jp2-g-graine'), tige = q('.jp2-g-tige');
  var ombre = q('.jp2-g-ombre'), onde = q('.jp2-g-onde');
  var feuilles = tous('.jp2-g-feuille'), petales = tous('.jp2-g-petale'), coeurs = tous('.jp2-g-petit-coeur');
  var coeur = q('.jp2-g-coeur'), fleur = q('.jp2-g-fleur'), plante = q('.jp2-g-plante');
  var mottes = tous('.jp2-g-motte');
  var L = tige.getTotalLength();
  tige.style.strokeDasharray = L;

  function lim(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function prog(t, a, d) { return lim((t - a) / d); }
  function easeIn(p) { return p * p * p; }
  function easeOut(p) { return 1 - Math.pow(1 - p, 3); }
  function ressort(t, a, zeta, w) {
    var s = (t - a) / 1000;
    if (s <= 0) return 0;
    var wd = w * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * w * s) * (Math.cos(wd * s) + zeta / Math.sqrt(1 - zeta * zeta) * Math.sin(wd * s));
  }
  function echelle(el, cx, cy, sx, sy) {
    el.setAttribute('transform', 'translate(' + cx + ' ' + cy + ') scale(' + sx + ' ' + (sy === undefined ? sx : sy) + ') translate(' + (-cx) + ' ' + (-cy) + ')');
  }

  function rendre(t) {
    // 1. La pièce tombe en tournant sur elle même (0 à 700 ms), s'écrase, puis rétrécit en graine
    var pc = easeIn(prog(t, 0, 700));
    var yChute = -30 + 205 * pc;
    var ecrase = t < 700 ? 0 : Math.sin(Math.PI * prog(t, 700, 260)) * (1 - prog(t, 700, 300));
    var reste = 1 - easeIn(prog(t, 880, 270));
    piece.style.display = reste > 0.01 ? '' : 'none';
    piece.setAttribute('transform', 'translate(160 ' + (yChute + ecrase * 4) + ') scale(' + (reste * (1 + 0.22 * ecrase)) + ' ' + (reste * (1 - 0.25 * ecrase)) + ')');
    var tour = t < 700 ? Math.cos(Math.PI * 2 * 2.5 * prog(t, 0, 700)) : 1; // 2,5 tours, finit face visible
    face.setAttribute('transform', 'scale(' + (Math.abs(tour) < 0.08 ? 0.08 : Math.abs(tour)) + ' 1)');
    // Ombre de contact : grandit à l'approche, disparaît après l'impact
    var o = t < 700 ? pc : 1 - prog(t, 700, 250);
    ombre.style.display = o > 0.02 && t < 950 ? '' : 'none';
    ombre.setAttribute('transform', 'translate(160 192) scale(' + (0.3 + 0.9 * o) + ' 1) translate(-160 -192)');
    ombre.setAttribute('opacity', 0.35 * o);
    // Onde de choc à l'impact (700 à 1150 ms)
    var po = prog(t, 700, 450);
    onde.style.display = po > 0 && po < 1 ? '' : 'none';
    var ro = 12 + 70 * easeOut(po); onde.setAttribute('rx', ro); onde.setAttribute('ry', ro * 0.2);
    onde.setAttribute('stroke-width', 5 * (1 - po));
    // Trois mottes projetées en arc
    var dirs = [[-30, 22], [28, 26], [10, 32]];
    for (var i = 0; i < mottes.length; i++) {
      var p = prog(t, 700, 450);
      mottes[i].style.display = p > 0 && p < 1 ? '' : 'none';
      mottes[i].setAttribute('cx', 160 + dirs[i][0] * p);
      mottes[i].setAttribute('cy', 188 - dirs[i][1] * 4 * p * (1 - p) + 6 * p);
    }
    // 2. La graine apparaît pendant que la pièce disparaît, puis se tasse au pied de la tige
    var g = easeOut(prog(t, 980, 320)) * (1 - 0.45 * easeOut(prog(t, 1700, 500)));
    graine.style.display = g > 0.01 ? '' : 'none';
    graine.setAttribute('transform', 'translate(160 ' + (190 + 5 * easeOut(prog(t, 980, 420))) + ') scale(' + g + ')');
    // 3. La tige pousse (1400 à 2400 ms)
    tige.style.strokeDashoffset = L * (1 - easeOut(prog(t, 1400, 1000)));
    // 4. Les feuilles s'ouvrent en ressort
    for (var f = 0; f < feuilles.length; f++) {
      echelle(feuilles[f], +feuilles[f].dataset.x, +feuilles[f].dataset.y, Math.max(0, ressort(t, 2000 + 120 * f, 0.55, 11)));
    }
    // 5. Les pétales s'ouvrent un par un, puis « pop » de la fleur (3300 ms)
    for (var k = 0; k < petales.length; k++) {
      var a = +petales[k].dataset.a, sp = Math.max(0, ressort(t, 2500 + 70 * k, 0.55, 12));
      petales[k].setAttribute('transform', 'rotate(' + a + ' 160 112) translate(160 112) scale(' + sp + ') translate(-160 -112)');
    }
    echelle(coeur, 160, 112, Math.max(0, ressort(t, 2450, 0.7, 12)));
    echelle(fleur, 160, 112, 1 + 0.08 * Math.sin(Math.PI * prog(t, 3300, 220)));
    // 6. Petits cœurs qui s'envolent de la fleur au « pop » (3300 à 4700 ms)
    for (var c = 0; c < coeurs.length; c++) {
      var h = coeurs[c], pcoeur = prog(t, 3300 + (+h.dataset.d), 1300);
      h.style.display = pcoeur > 0 && pcoeur < 1 ? '' : 'none';
      var x = 160 + (+h.dataset.dx) * easeOut(pcoeur) + 4 * Math.sin(pcoeur * 9 + c);
      var y = 104 - (+h.dataset.h) * easeOut(pcoeur);
      var sc = Math.max(0, ressort(t, 3300 + (+h.dataset.d), 0.5, 14)) * (1 - easeIn(prog(pcoeur, 0.7, 0.3)));
      h.setAttribute('transform', 'translate(' + x + ' ' + y + ') scale(' + sc + ')');
    }
    // 7. Balancement lent de la plante (±2,5°, période 3,2 s)
    var amp = 2.5 * easeOut(prog(t, 3400, 1000));
    plante.setAttribute('transform', 'rotate(' + (amp * Math.sin(2 * Math.PI * (t - 3400) / 3200)) + ' 160 192)');
  }

  // ---------- Son ----------
  var musique = null, ctx = null;
  function jouerSons() {
    try {
      if (!musique) { musique = new Audio('/assets/audio/jingle-graine.mp3'); musique.volume = 0.35; }
      musique.currentTime = 0;
      var p = musique.play(); if (p && p.catch) p.catch(function () {});
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      if (ctx.state === 'suspended') ctx.resume();
      var t0 = ctx.currentTime + 0.016;
      souffle(t0, 0.7);          // chute
      boum(t0 + 0.7);            // impact
      bulle(t0 + 3.3);           // « pop » de la fleur
    } catch (e) { /* pas de son : l'animation continue */ }
  }
  function bruit(duree) {
    var b = ctx.createBuffer(1, Math.ceil(ctx.sampleRate * duree), ctx.sampleRate), d = b.getChannelData(0), s = 7;
    for (var i = 0; i < d.length; i++) { s = (s * 16807) % 2147483647; d[i] = s / 1073741823.5 - 1; } // aléatoire à graine fixe
    var src = ctx.createBufferSource(); src.buffer = b; return src;
  }
  function souffle(t, d) {
    var n = bruit(d), f = ctx.createBiquadFilter(), g = ctx.createGain();
    f.type = 'bandpass'; f.Q.value = 1.2; f.frequency.setValueAtTime(2400, t); f.frequency.exponentialRampToValueAtTime(500, t + d);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.07, t + d * 0.8); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    n.connect(f); f.connect(g); g.connect(ctx.destination); n.start(t); n.stop(t + d);
  }
  function boum(t) {
    var o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.setValueAtTime(140, t); o.frequency.exponentialRampToValueAtTime(48, t + 0.18);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.22, t + 0.008); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.3);
    o.connect(g); g.connect(ctx.destination); o.start(t); o.stop(t + 0.32);
    var n = bruit(0.12), f = ctx.createBiquadFilter(), gn = ctx.createGain();
    f.type = 'lowpass'; f.frequency.value = 900;
    gn.gain.setValueAtTime(0.1, t); gn.gain.exponentialRampToValueAtTime(0.0001, t + 0.12);
    n.connect(f); f.connect(gn); gn.connect(ctx.destination); n.start(t); n.stop(t + 0.12);
  }
  function bulle(t) {
    var o = ctx.createOscillator(), g = ctx.createGain();
    o.type = 'sine'; o.frequency.setValueAtTime(420, t); o.frequency.exponentialRampToValueAtTime(1300, t + 0.09);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.12, t + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.16);
    o.connect(g); g.connect(ctx.destination); o.start(t); o.stop(t + 0.18);
  }

  // ---------- Lecture ----------
  var fige = new URLSearchParams(location.search).get('t');
  if (fige !== null) { rendre(parseFloat(fige) * 1000); return; }
  var calme = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  rendre(3400); // image d'attente : la fleur épanouie
  var t0 = null, enCours = false;
  function boucle(now) {
    if (t0 === null) t0 = now;
    var t = now - t0;
    rendre(t);
    if (t < 6000) requestAnimationFrame(boucle); else enCours = false;
  }
  function planter(avecSon) {
    if (avecSon) jouerSons();
    t0 = null;
    if (!enCours) { enCours = true; requestAnimationFrame(boucle); }
  }
  // Le visiteur clique : animation + musique (même si les animations sont réduites : c'est son choix explicite)
  bouton.addEventListener('click', function () { planter(true); });
  // Une pièce tombe dès qu'un visiteur commence son don dans le formulaire HelloAsso ou clique sur « Faire un don »
  window.addEventListener('blur', function () {
    setTimeout(function () {
      var a = document.activeElement;
      if (a && a.tagName === 'IFRAME' && /helloasso/.test(a.src || '')) planter(false);
    }, 0);
  });
  document.querySelectorAll('a[href="#don"], a[href="/faire-un-dons/"]').forEach(function (b) {
    b.addEventListener('click', function () { planter(true); });
  });
  // Arrivée à l'écran : lecture muette (les navigateurs interdisent le son sans clic)
  if (calme || !('IntersectionObserver' in window)) return;
  var vu = false;
  new IntersectionObserver(function (e) {
    if (e[0].isIntersecting && !vu) { vu = true; planter(false); }
    if (!e[0].isIntersecting) vu = false;
  }, { threshold: 0.4 }).observe(svg);
})();

// ---------- Page « Ma commune veut une fête » : candidature par email, partage ----------
(function () {
  var form = document.getElementById('jp2-candidature');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (n) { return (form.elements[n].value || '').trim(); };
      var sujet = 'Ma commune veut une fête : ' + v('commune') + ' (' + v('departement') + ')';
      var corps = 'Commune : ' + v('commune') + '\nDépartement : ' + v('departement') + '\nNom : ' + v('nom') +
        '\nEmail : ' + v('email') + '\nJe suis : ' + v('role') + '\n\nPourquoi notre commune :\n' + v('pourquoi') + '\n';
      location.href = 'mailto:joueretplanter@proton.me?subject=' + encodeURIComponent(sujet) + '&body=' + encodeURIComponent(corps);
      form.querySelector('.jp2-form__message').textContent = 'Ton logiciel d’email s’ouvre avec ta candidature. Il ne reste plus qu’à l’envoyer. Merci !';
    });
  }
  document.querySelectorAll('.jp2-partager').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = location.origin + '/ma-commune/#' + b.dataset.ancre;
      if (navigator.share) { navigator.share({ title: b.dataset.titre, url: url }).catch(function () {}); return; }
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { b.textContent = 'Lien copié !'; });
    });
  });
})();
