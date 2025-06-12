function verifierChampsObligatoires() {
    let champs = ["nom_fournisseur", "personne_responsable", "adresse", "npa_ville", "telephone1"];
    for (let champ of champs) {
        if (document.getElementById(champ).value.trim() === "") {
            alert("Veuillez compléter les zones obligatoires");
            return false;
        }
    }
    return true;
}

function creerFournisseur() {
    if (!verifierChampsObligatoires()) return;

    fetch("/creer", {
        method: "POST",
        body: new FormData(document.getElementById("fournisseurForm"))
    }).then(response => response.text())
      .then(alert);
}

function modifierFournisseur() {
    if (!verifierChampsObligatoires()) return;

    fetch("/modifier", {
        method: "POST",
        body: new FormData(document.getElementById("fournisseurForm"))
    }).then(response => response.text())
      .then(alert);
}

function rechercherFournisseur() {
    let nom = document.getElementById("nom_fournisseur").value;
    fetch("/rechercher?nom=" + nom)
      .then(response => response.text())
      .then(alert);
}

function supprimerFournisseur() {
    let nom = document.getElementById("nom_fournisseur").value;
    fetch("/supprimer?nom=" + nom, { method: "DELETE" })
      .then(response => response.text())
      .then(alert);
}
