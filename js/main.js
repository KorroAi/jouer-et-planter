// Jouer et Planter — scripts communs

// Adresse qui reçoit les messages du formulaire de contact
const EMAIL_CONTACT = "contact@jouer-et-planter.fr";
// Page de paiement (HelloAsso, etc.) — à remplacer par votre vraie page de don
const LIEN_PAIEMENT = "https://www.helloasso.com/";
// Coût d'un arbre planté, en euros
const PRIX_ARBRE = 5;

// Menu mobile
const boutonMenu = document.querySelector(".menu-bouton");
const nav = document.querySelector(".nav");
if (boutonMenu && nav) {
  boutonMenu.addEventListener("click", () => {
    const ouvert = nav.classList.toggle("ouvert");
    boutonMenu.setAttribute("aria-expanded", ouvert);
    boutonMenu.textContent = ouvert ? "Fermer" : "Menu";
  });
  nav.addEventListener("click", (e) => {
    if (e.target.closest("a") && nav.classList.contains("ouvert")) boutonMenu.click();
  });
}

// Formulaire de contact : ouvre la messagerie avec le message pré-rempli
const formContact = document.querySelector(".formulaire-contact");
if (formContact) {
  formContact.addEventListener("submit", (e) => {
    e.preventDefault();
    const d = new FormData(formContact);
    const sujet = `[Site] ${d.get("sujet") || "Message"} — ${d.get("nom")}`;
    const corps = `${d.get("message")}\n\n${d.get("nom")}\n${d.get("email")}`;
    window.location.href =
      `mailto:${EMAIL_CONTACT}?subject=${encodeURIComponent(sujet)}&body=${encodeURIComponent(corps)}`;
    formContact.querySelector(".message-envoi").textContent =
      "Votre messagerie s'ouvre avec le message prêt à envoyer.";
  });
}

// Liens « #contact » qui pré-choisissent le sujet du message
document.querySelectorAll("[data-sujet]").forEach((lien) => {
  lien.addEventListener("click", () => {
    const sujet = document.querySelector("#c-sujet");
    if (sujet) sujet.value = lien.dataset.sujet;
  });
});

// Formulaire de don : montant → nombre d'arbres
const formDon = document.querySelector(".formulaire-don");
if (formDon) {
  const libre = formDon.querySelector("#montant-libre");
  const sortieArbres = formDon.querySelector("[data-arbres]");
  const sortieMontant = formDon.querySelectorAll("[data-montant]");
  const sortieApres = formDon.querySelector("[data-apres-impot]");

  const montant = () => {
    const v = parseFloat(libre.value);
    if (v > 0) return v;
    const choisi = formDon.querySelector('input[name="montant"]:checked');
    return choisi ? parseFloat(choisi.value) : 0;
  };
  const mensuel = () => formDon.querySelector('input[name="frequence"]:checked').value === "mensuel";

  const maj = () => {
    const m = montant();
    const arbres = Math.floor(m / PRIX_ARBRE);
    sortieArbres.textContent = arbres <= 1 ? `${arbres} arbre` : `${arbres} arbres`;
    sortieMontant.forEach((el) => (el.textContent = `${m.toLocaleString("fr-FR")} €${mensuel() ? " par mois" : ""}`));
    const apres = m * 0.34;
    const decimales = Number.isInteger(apres) ? 0 : 2;
    sortieApres.textContent = `${apres.toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales })} €`;
  };

  formDon.addEventListener("change", (e) => {
    if (e.target.name === "montant") libre.value = "";
    maj();
  });
  libre.addEventListener("input", () => {
    if (libre.value) formDon.querySelectorAll('input[name="montant"]').forEach((r) => (r.checked = false));
    maj();
  });
  formDon.addEventListener("submit", (e) => {
    e.preventDefault();
    if (montant() <= 0) {
      libre.focus();
      return;
    }
    window.location.href = LIEN_PAIEMENT;
  });
  maj();
}

// Plateau du challenge : 100 cases, chaque case = 1 % de l'objectif
const plateau = document.querySelector(".plateau");
if (plateau) {
  const plantes = Number(plateau.dataset.plantes);
  const objectif = Number(plateau.dataset.objectif);
  const pleines = Math.floor((plantes / objectif) * 100);
  for (let i = 0; i < 100; i++) {
    const c = document.createElement("span");
    if (i < pleines) c.className = "plantee";
    else if (i === pleines) c.className = "en-cours";
    plateau.appendChild(c);
  }
}
