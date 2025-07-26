# ────────────────────────────────────────────────────────────────────────────────
# Imports & Configuration
# ────────────────────────────────────────────────────────────────────────────────
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
import pandas as pd
import sqlite3
import os
from collections import defaultdict
from sqlalchemy import create_engine, inspect

app = Flask(__name__)
app.secret_key = 'unspoken_greatness_silent_success'
engine = create_engine('sqlite:///grand_livre.db')


# ── CHEMIN ABSOLU DU FICHIER EXCEL DES FACTURES ──
FACTURES_PATH = os.path.join(app.root_path, 'bd_factures_fournisseurs.xlsx')

# ────────────────────────────────────────────────────────────────────────────────
# UTILITAIRES GÉNÉRAUX
# ────────────────────────────────────────────────────────────────────────────────
def load_sheet1(needed_cols, engine):
    """
    Retourne un DataFrame pandas ne contenant que les colonnes de
    needed_cols qui existent réellement dans la table Sheet1.
    """
    insp = inspect(engine)
    all_cols = [col['name'] for col in insp.get_columns('Sheet1')]
    cols = [c for c in needed_cols if c in all_cols]
    if not cols:
        raise ValueError(f"Aucune des colonnes demandées {needed_cols} n'existe dans Sheet1.")
    select_clause = ", ".join(f"`{c}`" for c in cols)
    sql = f"SELECT {select_clause} FROM Sheet1"
    return pd.read_sql_query(sql, engine)

def get_accounts():
    """
    Retourne une liste de dicts [{'num_compte':'1000','intitule':'Capital'},…]
    """
    raw = pd.read_excel('plan_comptable.xlsx', dtype=str)
    df = raw.iloc[:, :2].dropna(how='all')
    df = df.rename(columns={df.columns[0]: 'num_compte', df.columns[1]: 'intitule'})
    return df.to_dict(orient='records')

def get_connection():
    """
    Ouvre une connexion SQLite sur grand_livre.db avec row_factory.
    """
    conn = sqlite3.connect('grand_livre.db')
    conn.row_factory = sqlite3.Row
    return conn
# ────────────────────────────────────────────────────────────────────────────────
# Squelette principal
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/en_construction')
def en_construction():
    return render_template('en_construction.html')


@app.route('/menu_principal')
def menu_principal():
    return render_template('menu_principal.html')

@app.route('/menu_comptabilite')
def menu_comptabilite():
    return render_template('menu_comptabilite.html')

# ────────────────────────────────────────────────────────────────────────────────
# ADMINISTRATION & Gestion des bases de données
# ────────────────────────────────────────────────────────────────────────────────

@app.route('/administration')
def administration():
    # Affiche la page d’administration (upload/download)
    return render_template('templates_administration/administration.html')

@app.route('/download/<path:fname>')
def download_file(fname):
    # Télécharge n’importe quel fichier du project root
    return send_from_directory(app.root_path, fname, as_attachment=True)

@app.route('/upload/<path:fname>', methods=['POST'])
def upload_file(fname):
    # Upload d’une nouvelle version de la même BD
    f = request.files.get('file')
    if not f:
        flash("Aucun fichier sélectionné", "error")
    else:
        target = os.path.join(app.root_path, fname)
        f.save(target)
        flash(f"{fname} importé avec succès", "success")
    return redirect(url_for('administration'))

@app.route('/bd_plan_comptable')
def bd_plan_comptable():
    # Affichage du contenu de plan_comptable.xlsx
    fp = os.path.join(app.root_path, 'plan_comptable.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_plan_comptable.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

@app.route('/bd_fournisseurs')
def bd_fournisseurs():
    fp = os.path.join(app.root_path, 'bd_fournisseurs.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_fournisseurs.html',
                           columns=df.columns, rows=df.to_dict(orient='records'))

# ────────────────────────────────────────────────────────────────────────────────
# Bases de données brutes (Excel / SQLite)
# ────────────────────────────────────────────────────────────────────────────────




@app.route('/bd_factures_fournisseurs')
def bd_factures_fournisseurs():
    pass

@app.route('/bd_grand_livre')
def bd_grand_livre():
    pass

@app.route('/bd_clients')
def bd_clients():
    pass

@app.route('/bd_factures_clients')
def bd_factures_clients():
    pass

@app.route('/bd_tva')
def bd_tva():
    pass

@app.route('/bd_delai_paiement')
def bd_delai_paiement():
    pass

# ────────────────────────────────────────────────────────────────────────────────
# Fournisseurs
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/comptabilite_fournisseurs')
def comptabilite_fournisseurs():
    return render_template('templates_fournisseurs/comptabilite_fournisseurs.html')




# Chargement des bases
df_fournisseurs = pd.read_excel("bd_fournisseurs.xlsx", dtype=str, keep_default_na=False)
df_tva          = pd.read_excel("bd_tva.xlsx", dtype=str, keep_default_na=False)
df_delai        = pd.read_excel("bd_delai_de_paiement.xlsx", dtype=str, keep_default_na=False)
df_crediter     = pd.read_excel("plan_comptable_crediter.xlsx", dtype=str, keep_default_na=False)
df_debiter      = pd.read_excel("plan_comptable_debiter.xlsx", dtype=str, keep_default_na=False)

@app.route('/recherche_fournisseurs')
def recherche_fournisseurs():
    fournisseurs      = df_fournisseurs.to_dict(orient='records')
    tva_options       = df_tva.to_dict(orient='records')
    delai_options     = df_delai.to_dict(orient='records')
    crediter_options  = df_crediter.to_dict(orient='records')
    debiter_options   = df_debiter.to_dict(orient='records')
    comptes_plan = get_accounts()  # <=== juste ici pour le compte TVA

    return render_template(
        'templates_fournisseurs/recherche_fournisseurs.html',
        df_fournisseurs=fournisseurs,
        tva_options=tva_options,
        delai_options=delai_options,
        crediter_options=crediter_options,
        debiter_options=debiter_options,
        comptes_plan=comptes_plan 
    )

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    q = request.args.get("query", "").strip().lower()
    if not q:
        return jsonify([])
    res = df_fournisseurs[
        df_fournisseurs["Code fournisseur"].str.lower().str.startswith(q) |
        df_fournisseurs["Nom du fournisseur"].str.lower().str.startswith(q)
    ].to_dict(orient='records')
    return jsonify(res)



@app.route("/autocomplete_code", methods=["GET"])
def autocomplete_code():
    q = request.args.get("query", "").strip().lower()
    if not q: return jsonify([])
    res = df_fournisseurs[
        df_fournisseurs["Code fournisseur"].str.lower().str.startswith(q)
    ].to_dict(orient="records")
    return jsonify(res)

@app.route("/autocomplete_nom", methods=["GET"])
def autocomplete_nom():
    q = request.args.get("query", "").strip().lower()
    if not q: return jsonify([])
    res = df_fournisseurs[
        df_fournisseurs["Nom du fournisseur"].str.lower().str.startswith(q)
    ].to_dict(orient="records")
    return jsonify(res)






@app.route("/creer", methods=["POST"])
def creer_fournisseur():
    global df_fournisseurs
    try:
        data = request.form.to_dict()
        print("📌 Données reçues pour création :", data)  # Debug

        mandatory_fields = [
            "Code fournisseur", "Nom du fournisseur", "No téléphone 1",
            "Compte à créditer", "Compte à débiter", "Taux TVA 1", "Délai de paiement"
        ]
        for field in mandatory_fields:
            if not data.get(field) or not data[field].strip():
                return jsonify({"message": f"Champ obligatoire manquant: {field}"}), 400
        if not df_fournisseurs[df_fournisseurs["Code fournisseur"] == data.get("Code fournisseur")].empty:
            return jsonify({"message": "Fournisseur existe déjà !"}), 400

        new_row_df = pd.DataFrame([data])
        df_fournisseurs = pd.concat([df_fournisseurs, new_row_df], ignore_index=True)
        df_fournisseurs.to_excel("bd_fournisseurs.xlsx", index=False)
        return jsonify({"message": "Fournisseur créé avec succès !"}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la création du fournisseur: {str(e)}"}), 500


@app.route("/supprimer", methods=["POST"])
def supprimer_fournisseur():
    global df_fournisseurs
    try:
        data = request.form.to_dict()
        code = data.get("Code fournisseur")
        if not code or not code.strip():
            return jsonify({"message": "Champ obligatoire manquant: Code fournisseur (pour supprimer)"}), 400
        index = df_fournisseurs[df_fournisseurs["Code fournisseur"] == code].index
        if index.empty:
            return jsonify({"message": "Fournisseur non trouvé !"}), 404
        df_fournisseurs = df_fournisseurs.drop(index)
        df_fournisseurs.to_excel("bd_fournisseurs.xlsx", index=False)
        return jsonify({"message": "Fournisseur supprimé avec succès !"}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression du fournisseur: {str(e)}"}), 500
    


@app.route('/liste_fournisseurs')
def liste_fournisseurs():
    df = pd.read_excel(os.path.join(app.root_path,'bd_fournisseurs.xlsx'))
    table_html = df.to_html(classes="table table-striped table-hover table-bordered", index=False, justify="center")
    return render_template('templates_fournisseurs/liste_fournisseurs.html', table_html=table_html)
    








# ────────────────────────────────────────────────────────────────────────────────
# Chargement global des données fournisseurs (en tête du fichier) (besoin contrôle si pas mieux en haut du bloc fournisseurs pour tout le module)
# ────────────────────────────────────────────────────────────────────────────────
df_fournisseurs = pd.read_excel(
    "bd_fournisseurs.xlsx",
    dtype=str,
    keep_default_na=False
)

def get_accounts():
    """
    Retourne une liste de dicts [{'num_compte':'1000','intitule':'Capital'},…]
    """
    raw = pd.read_excel('plan_comptable.xlsx', dtype=str)
    df = raw.iloc[:, :2].dropna(how='all')
    df = df.rename(columns={df.columns[0]: 'num_compte', df.columns[1]: 'intitule'})
    return df.to_dict(orient='records')

# ────────────────────────────────────────────────────────────────────────────────
# Factures fournisseurs
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/factures_fournisseurs_ecriture')
def factures_fournisseurs_ecriture():
    fournisseurs = df_fournisseurs.to_dict(orient='records')
    comptes_plan  = get_accounts()
    return render_template(
        'templates_fournisseurs/factures_fournisseurs_ecriture.html',
        df_fournisseurs=fournisseurs,
        comptes_plan=comptes_plan
    )

@app.route("/autocomplete_factures_fournisseurs", methods=["GET"])
def autocomplete_factures_fournisseurs():
    """
    Recherche en temps réel les fournisseurs dont le nom commence par la
    chaîne `query` fournie en paramètre GET, et renvoie la liste JSON
    des correspondances.
    """
    q = request.args.get("query", "").strip().lower()
    if not q:
        return jsonify([])

    # df_fournisseurs est défini en module, chargé depuis bd_fournisseurs.xlsx
    res = df_fournisseurs[
        df_fournisseurs["Nom du fournisseur"].str.lower().str.startswith(q)
    ].to_dict(orient="records")
    return jsonify(res)

# ——— Route : liste des factures fournisseurs ———
@app.route('/liste_factures_fournisseurs')
def liste_factures_fournisseurs():
    print("Clés reçues :", list(request.form.keys()))
    file_path = os.path.join(app.root_path, 'bd_factures_fournisseurs.xlsx')
    df = pd.read_excel(file_path, dtype=str, keep_default_na=False)
    table_html = df.to_html(
        classes="table table-striped table-hover table-bordered",
        index=False,
        justify="center"
    )
    return render_template(
        'templates_fournisseurs/liste_factures_fournisseurs.html',
        table_html=table_html
    )










# ────────────────────────────────────────────────────────────────────────────────
# Route dédiée à la publication dans le Grand Livre
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/publier_grand_livre_four', methods=['POST'])
def publier_grand_livre_four():
    # 1) Récupérer raw form data
    raw = { k: request.form.getlist(k) for k in request.form.keys() }

    # 2) Extraire listes
    fournisseurs   = raw.get('No compte Fournisseur', [])   # ["2000 – Caisse", …]
    comptes_ht     = raw.get('compte[]', [])                # ["4000 – Achats", …]
    base_ht_vals   = raw.get('base_ht[]', [])               # [ht1, ht2, …]
    comptes_tva    = raw.get('compte_tva[]', [])            # ["2100 – TVA", …]
    tva_vals       = raw.get('montant_tva[]', [])           # [tva1, tva2, …]

    # Champs unitaires (déclarés une fois pour toutes les lignes)
    periode    = raw.get('Période', [''])[0]
    date_fact  = raw.get('Date de facture', [''])[0]
    no_facture = raw.get('No de facture', [''])[0]
    montant    = float(raw.get('Montant', ['0'])[0] or 0)

    # 3) Ouvrir connexion et curseur
    conn = engine.raw_connection()
    cur  = conn.cursor()

    # 4) Ajouter la colonne "Intitulé du compte" si jamais elle n'existe pas
    try:
        cur.execute('ALTER TABLE Sheet1 ADD COLUMN "Intitulé du compte" TEXT')
    except:
        pass

    # 5) Pour chaque ligne détail => 3 écritures
    for i in range(len(comptes_ht)):
        # a) Créditer le compte Fournisseur
        raw_f      = fournisseurs[i]
        num_f, intit_f = raw_f.split(' – ', 1)
        cur.execute("""
            INSERT INTO Sheet1 (
                "N° compte","Intitulé du compte","Période","Date",
                "Libellé","Fournisseur","Débit","Crédit"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            num_f,
            intit_f,
            periode,
            date_fact,
            no_facture,
            raw.get('Fournisseur', [''])[0],
            0,
            montant
        ))

        # b) Débiter le compte HT
        raw_ht     = comptes_ht[i]
        num_ht, intit_ht = raw_ht.split(' – ', 1)
        debit_ht   = float(base_ht_vals[i] or 0)
        cur.execute("""
            INSERT INTO Sheet1 (
                "N° compte","Intitulé du compte","Période","Date",
                "Libellé","Fournisseur","Débit","Crédit"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            num_ht,
            intit_ht,
            periode,
            date_fact,
            no_facture,
            '',
            debit_ht,
            0
        ))

        # c) Débiter le compte TVA
        raw_tva    = comptes_tva[i]
        num_tva, intit_tva = raw_tva.split(' – ', 1)
        debit_tva  = float(tva_vals[i] or 0)
        cur.execute("""
            INSERT INTO Sheet1 (
                "N° compte","Intitulé du compte","Période","Date",
                "Libellé","Fournisseur","Débit","Crédit"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            num_tva,
            intit_tva,
            periode,
            date_fact,
            no_facture,
            '',
            debit_tva,
            0
        ))

    # 6) Valider et fermer
    conn.commit()
    cur.close()

    # 7) Répondre en JSON pour le front
    return jsonify({"message": "Grand Livre mis à jour !"})










  








   


# ——— Route : mettre à jour une facture existante ———
@app.route('/mettre_a_jour_facture', methods=['POST'])
def mettre_a_jour_facture():
    data = request.form.to_dict()
    fp = os.path.join(app.root_path, 'bd_factures_fournisseurs.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    original = data.get('original_num_facture') or data.get('No de facture')
    idx = df[df['No de facture'] == original].index
    if idx.empty:
        return jsonify({'message':'Facture non trouvée !'}), 404
    for k, v in data.items():
        df.at[idx[0], k] = v
    df.to_excel(fp, index=False)
    return jsonify({'message':'Facture mise à jour avec succès !'}), 200


# ────────────────────────────────────────────────────────────────────────────────
# Clients
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/comptabilite_clients')
def comptabilite_clients():
    return render_template('templates_clients/comptabilite_clients.html')

@app.route('/recherche_clients')
def recherche_clients():
    return render_template('templates_clients/recherche_clients.html')

@app.route('/recherche_factures_clients')
def recherche_factures_clients():
    return render_template('templates_clients/recherche_factures_clients.html')

# ────────────────────────────────────────────────────────────────────────────────
# RH / Salaires
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/salaires_rh_menu')
def salaires_rh_menu():
    return render_template('templates_rh/salaires_rh_menu.html')

@app.route('/gestion_employes')
def gestion_employes():
    return render_template('templates_rh/gestion_employes.html')

@app.route('/traitement_salaires')
def traitement_salaires():
    return render_template('templates_rh/traitement_salaires.html')

# ────────────────────────────────────────────────────────────────────────────────
# Grand Livre
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/grand_livre_accueil')
def grand_livre_accueil():
    return render_template('templates_comptabilite/grand_livre_accueil.html')


@app.route('/grand_livre_full')
def grand_livre_full():
    # Colonnes attendues
    needed = [
        'N° compte', 'Période', 'Date', 'Libellé',
        "Numéro d'écriture", 'Fournisseur', 'Débit', 'Crédit'
    ]
    # 1) Charger dynamiquement Sheet1
    df = load_sheet1(needed, engine)
    # 2) Nettoyer les en-têtes
    df.columns = df.columns.str.strip()
    # 3) Renommer pour matcher Jinja et url_for
    df = df.rename(columns={
        "Numéro d'écriture": "num_ecriture",
        "N° compte":         "num_compte",
        "Période":           "periode",
        "Date":              "date",
        "Libellé":           "libelle",
        "Fournisseur":       "fournisseur",
        "Débit":             "debit",
        "Crédit":            "credit"
    })
    # 4) Injecter l’intitulé depuis le plan comptable
    df_plan = pd.read_excel("plan_comptable.xlsx")
    df_plan.columns = df_plan.columns.str.strip()
    title_map = dict(zip(
        df_plan['N° compte'].astype(str),
        df_plan['Intitulé du compte'].astype(str)
    ))
    df['intitule'] = df['num_compte'].astype(str).map(title_map)
    # 5) Préparer les données pour le template
    entries = df.to_dict(orient='records')
    comptes = [
        f"{nc} – {title_map.get(nc, '')}"
        for nc in sorted(df['num_compte'].astype(str).unique())
    ]
    # 6) Renvoyer vers le template
    return render_template(
        'templates_comptabilite/grand_livre_full.html',
        entries=entries,
        comptes=comptes
    )



@app.route('/grand_livre_recherche')
def grand_livre_recherche():
    df_plan = pd.read_excel("plan_comptable.xlsx", dtype=str)
    df_plan.columns = df_plan.columns.str.strip()
    comptes = [
        f"{row['N° compte']} – {row['Intitulé du compte']}"
        for _, row in df_plan.iterrows()
        if row['N° compte']
    ]
    return render_template(
        "templates_comptabilite/grand_livre_recherche.html",
        comptes=comptes
    )


@app.route('/grand_livre_result')
def grand_livre_result():
    needed = [
        'N° compte','Période','Date','Libellé',
        "Numéro d'écriture",'Fournisseur','Débit','Crédit'
    ]
    df = load_sheet1(needed, engine)
    df_plan = pd.read_excel("plan_comptable.xlsx", dtype=str)
    df_plan.columns = df_plan.columns.str.strip()
    dict_intitule = dict(zip(
        df_plan['N° compte'], df_plan['Intitulé du compte']
    ))

    cd  = request.args.get('compte_de')
    ca  = request.args.get('compte_a')
    pd_ = request.args.get('periode_de')
    pa  = request.args.get('periode_a')
    if cd:  df = df[df['N° compte'] >= cd]
    if ca:  df = df[df['N° compte'] <= ca]
    if pd_: df = df[df['Période'] >= pd_]
    if pa:  df = df[df['Période'] <= pa]

    resultats = {
        str(compte): grp.to_dict(orient='records')
        for compte, grp in df.groupby('N° compte')
    }

    intitulés_comptes = {
        compte: dict_intitule.get(compte, '')
        for compte in resultats
    }

    return render_template(
        'templates_comptabilite/grand_livre_result.html',
        comptes=list(resultats.keys()),
        resultats=resultats,
        intitulés_comptes=intitulés_comptes
    )


@app.route('/grand_livre_ecriture')
def grand_livre_ecriture():
    # --- lecture + debug colonnes du plan comptable ---
    with pd.ExcelFile("plan_comptable.xlsx") as xls:
        feuille = xls.sheet_names[0]
        # on charge en brut
        df_tmp = pd.read_excel(xls, sheet_name=feuille, dtype=str)
        # debug : affiche les noms exacts
        print(">> Colonnes réelles :", df_tmp.columns.tolist())
        # ensuite on isole et renomme
        df_plan = (
            df_tmp
            .loc[:, ['N° compte', 'Intitulé du compte']]
            .dropna(subset=['N° compte', 'Intitulé du compte'])
            .rename(columns={'N° compte': 'num_compte', 'Intitulé du compte': 'intitule'})
        )

    accounts = df_plan.to_dict(orient='records')
    return render_template(
        'templates_comptabilite/grand_livre_ecriture.html',
        accounts=accounts
    )

# ────────────────────────────────────────────────────────────────────────────────
# ROUTE UNIFIÉE POUR LE FORMULAIRE D’ÉCRITURE (AVEC OU SANS NUMÉRO)
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/grand_livre/ecriture', defaults={'num_ecriture': None}, methods=['GET'])
@app.route('/grand_livre/ecriture/<int:num_ecriture>',          methods=['GET'])
def grand_livre_ecriture_id(num_ecriture):
    # Si aucun numéro, on affiche le formulaire vierge
    if num_ecriture is None:
        accounts = get_accounts()
        return render_template(
            'templates_comptabilite/grand_livre_ecriture.html',
            accounts=accounts
        )

    # Sinon, on charge l’écriture existante
    num_ecriture = int(num_ecriture)
    row = pd.read_sql_query(
        'SELECT * FROM Sheet1 WHERE "Numéro d\'écriture" = ?',
        engine, params=(num_ecriture,)
    ).iloc[0]

    ecriture = {
        'num_ecriture': row["Numéro d'écriture"],
        'date'        : row['Date'],
        'periode'     : row['Période'],
        'libelle'     : row['Libellé'],
        'compte'      : row['N° compte'],
        'intitule'    : row['Fournisseur'],
        'debit'       : row['Débit'],
        'credit'      : row['Crédit']
    }

    return render_template(
        'templates_comptabilite/grand_livre_ecriture.html',
        accounts=get_accounts(),
        current=ecriture
    )





@app.route('/submit_ecriture_man', methods=['POST'])
def submit_ecriture_man():
    try:
        conn = sqlite3.connect('grand_livre.db')
        cur = conn.cursor()

        # 🔵 Récupérer le prochain numéro d’écriture (en castant comme entier !)
        cur.execute("SELECT MAX(CAST(\"Numéro d'écriture\" AS INTEGER)) FROM Sheet1")
        result = cur.fetchone()[0]
        num_ecriture = int(result) + 1 if result else 1

        # 🔵 Données globales
        date_compta = request.form.get('date_comptabilisation')
        periode     = request.form.get('periode')
        libelle     = request.form.get('libelle')

        # 🔵 Données ligne par ligne
        comptes   = request.form.getlist('N° compte[]')
        intitules = request.form.getlist('Intitule[]')
        debits    = request.form.getlist('debit[]')
        credits   = request.form.getlist('credit[]')

        for i in range(len(comptes)):
            compte   = comptes[i]
            intitule = intitules[i]
            debit    = float(debits[i].replace(',', '.') or 0)
            credit   = float(credits[i].replace(',', '.') or 0)

            cur.execute("""INSERT INTO Sheet1 (
                "N° compte", "Intitulé du compte", "Période", "Date",
                "Libellé", "Numéro d'écriture", "Fournisseur", "Débit", "Crédit")
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                compte, intitule, periode, date_compta,
                libelle, num_ecriture, '', debit, credit
            ))

        conn.commit()
        return jsonify({"success": True, "num_ecriture": num_ecriture})

    except Exception as e:
        return jsonify({"success": False, "reason": str(e)})

    finally:
        cur.close()
        conn.close()










# Dans app.py, en haut du fichier :
import pandas as pd
from pathlib import Path
EXCEL_META = Path(app.root_path) / 'db_numero_ecriture.xlsx'

import pandas as pd
from pathlib import Path
from flask import abort, flash, redirect, url_for, render_template, request

# juste après la création de `app` et `engine` :
EXCEL_META = Path(app.root_path) / 'db_numero_ecriture.xlsx'

import pandas as pd
from pathlib import Path

EXCEL_META = Path(app.root_path) / 'db_numero_ecriture.xlsx'

# ────────────────────────────────────────────────────────────────────────────────
@app.route('/submit_ecriture', methods=['POST'])
def submit_ecriture():
    print("▶︎ [submit_ecriture] Début")
    cur = engine.raw_connection().cursor()
    # ... votre INSERT dans Sheet1 ici ...
    cur.connection.commit()
    new_id = cur.lastrowid
    cur.close()
    print(f"✔ [submit_ecriture] Créé en SQL avec new_id={new_id}")

    # MÉTA-EXCEL
    try:
        meta_df = pd.read_excel(EXCEL_META, dtype={'num_ecriture': int, 'source_type': str})
    except FileNotFoundError:
        print("⚠️ [submit_ecriture] Excel meta introuvable, création d’un fichier vide.")
        meta_df = pd.DataFrame(columns=['num_ecriture', 'source_type'])
    print("🔍 [submit_ecriture] Avant append:", meta_df.tail())

    meta_df = meta_df.append({
        'num_ecriture': new_id,
        'source_type' : 'manuelle'
    }, ignore_index=True)
    meta_df.to_excel(EXCEL_META, index=False)
    print("💾 [submit_ecriture] Après append:", meta_df.tail())

    return jsonify(success=True, num_ecriture=new_id)


# ────────────────────────────────────────────────────────────────────────────────
@app.route('/publier_grand_livre', methods=['POST'])
def publier_grand_livre():
    print("▶︎ [publier_grand_livre] Début")
    conn = engine.raw_connection(); cur = conn.cursor()
    # ... vos 3 INSERT dans Sheet1 ici ...
    conn.commit()
    last_id = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
    cur.close()
    print(f"✔ [publier_grand_livre] Inséré en SQL id={last_id}")

    # MÉTA-EXCEL
    try:
        meta_df = pd.read_excel(EXCEL_META, dtype={'num_ecriture': int, 'source_type': str})
    except FileNotFoundError:
        print("⚠️ [voir_grand_livre] Excel meta introuvable, création d’un fichier vide.")
        meta_df = pd.DataFrame(columns=['num_ecriture', 'source_type'])
    print("🔍 [voir_grand_livre] Avant append:", meta_df.tail())

    meta_df = meta_df.append({
        'num_ecriture': last_id,
        'source_type' : 'facture_fournisseurs'
    }, ignore_index=True)
    meta_df.to_excel(EXCEL_META, index=False)
    print("💾 [voir_grand_livre] Après append:", meta_df.tail())

    return jsonify({"message": "Grand Livre mis à jour !"})


# ────────────────────────────────────────────────────────────────────────────────









@app.route('/grand_livre_ecriture/<int:num_ecriture>', methods=['GET'])
@app.route('/editer/<int:num_ecriture>', methods=['GET'])
def editer_ecriture(num_ecriture):
    print(f"\n====== DÉBUT TRAITEMENT ÉCRITURE {num_ecriture} ======")


    conn_acc = sqlite3.connect('grand_livre.db', check_same_thread=False)
    df_acc = pd.read_sql_query(
        'SELECT DISTINCT "N° compte" AS num_compte, '
        '"Intitulé du compte" AS intitule '
        'FROM Sheet1 ORDER BY "N° compte"',
        conn_acc
    )
    accounts = df_acc.to_dict(orient='records')
    conn_acc.close()



    # 1) Chargement des fichiers Excel
    print("[INFO] Chargement des fichiers Excel...")
    df_four = pd.read_excel('bd_factures_fournisseurs.xlsx', dtype=str, keep_default_na=False)
    df_cli  = pd.read_excel('bd_factures_clients.xlsx',    dtype=str, keep_default_na=False)
    df_sal  = pd.read_excel('bd_salaires.xlsx',            dtype=str, keep_default_na=False)

    # 2) Détection séquentielle de la provenance
    source, tpl, df = None, None, None

    # --- fournisseurs
    col_four = pd.to_numeric(df_four["Numéro d'écriture"], errors="coerce").dropna().astype(int)
    if num_ecriture in col_four.values:
        print("[INFO] Écriture trouvée dans les fournisseurs.")
        source, tpl, df = 'four', 'templates_fournisseurs/factures_fournisseurs_ecriture.html', df_four

    # --- clients
    #if source is None:
        #col_cli = pd.to_numeric(df_cli["Numéro d'écriture"], errors="coerce").dropna().astype(int)
        #if num_ecriture in col_cli.values:
            #print("[INFO] Écriture trouvée dans les clients.")
            #source, tpl, df = 'cli', 'templates_clients/factures_clients_ecriture.html', df_cli

    # --- salaires
    #if source is None:
        #col_sal = pd.to_numeric(df_sal["Numéro d'écriture"], errors="coerce").dropna().astype(int)
        ##if num_ecriture in col_sal.values:
            #print("[INFO] Écriture trouvée dans les salaires.")
            #source, tpl, df = 'sal', 'templates_salaires/salaires_ecriture.html', df_sal

    # 3) Si trouvé en Excel
    if source:
        print(f"[INFO] Chargement de la ligne pour {source}.")
        numeric_series = pd.to_numeric(df["Numéro d'écriture"], errors="coerce")
        row = df.loc[numeric_series == num_ecriture]
        if row.empty:
            print(f"[ERREUR] Ligne introuvable dans {source}.")
            return "Erreur : ligne introuvable", 404
        data = row.iloc[0].to_dict()
        print("🔍 Valeurs Excel reçues :", data)
        return render_template(tpl, data=data, accounts=accounts, df_fournisseurs=df_four.to_dict(orient='records'))

    # 4) Fallback SQLite pour écriture manuelle
    print("[INFO] Aucune donnée Excel ; recherche SQLite...")
    conn = sqlite3.connect('grand_livre.db', check_same_thread=False)
    query = 'SELECT * FROM Sheet1 WHERE "Numéro d\'écriture" = ?'
    row = pd.read_sql_query(query, conn, params=(num_ecriture,))
    if row.empty:
        print(f"[ERREUR] Écriture {num_ecriture} non trouvée.")
        return "Erreur : écriture non trouvée", 404
    data = row.iloc[0].to_dict()
    print(f"[OK] SQLite data = {data}")
    print("[DEBUG] data keys:", list(data.keys()))
    print("[DEBUG] data content:", data)
    return render_template('templates_comptabilite/grand_livre_ecriture.html', data=data, accounts=accounts)














# ────────────────────────────────────────────────────────────────────────────────
# PP / Bilan
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/pp_bilan_search')
def pp_bilan_search():
    return render_template('templates_comptabilite/pp_bilan_search.html')

@app.route('/pp_bilan_result', methods=['POST'])
def pp_bilan_result():
    periode_de  = request.form['periode_de']
    periode_a   = request.form['periode_a']
    type_etat   = request.form['type'].strip().upper()

    filtre1 = 'filtre1' in request.form
    filtre2 = 'filtre2' in request.form
    filtre3 = 'filtre3' in request.form
    filtre4 = 'filtre4' in request.form

    exclure_sans_mouvement = filtre1
    exclure_solde_zero     = filtre2
    inclure_tous           = filtre3
    total_annuel           = filtre4  # Récupération des cases à cocher

    conn = get_connection()

    insp = inspect(engine)
    colonnes = [col['name'] for col in insp.get_columns('Sheet1')]
    app.logger.debug("Colonnes dans Sheet1 : %s", colonnes)

    # AVANT TOUT : charger le plan comptable pour l’intitulé
    df_plan = pd.read_excel("plan_comptable.xlsx", dtype=str)
    df_plan.columns = df_plan.columns.str.strip()
    dict_intitule = dict(zip(
        df_plan["N° compte"].astype(str),
        df_plan["Intitulé du compte"].astype(str)
    ))

    # Choix de la requête selon PP ou Bilan
    if type_etat == 'PP':
        sql = """
        SELECT
            s1.[Période], s1.[N° compte],
            SUM(s1.[Débit])  AS debit, SUM(s1.[Crédit]) AS credit,
            s2.classe, s2.classe_label,
            s2.groupe, s2.groupe_label,
            s2.sous_groupe, s2.sous_groupe_label
        FROM Sheet1 s1
        JOIN Sheet2 s2 ON s1.[N° compte] = s2.compte
        WHERE substr(s1.[N° compte],1,1) IN ('3','4','5','6','7','8')
          AND s1.[Période] BETWEEN ? AND ?
        GROUP BY s1.[Période], s1.[N° compte]
        """
        params = (periode_de, periode_a)
    else:  # Bilan
        sql = """
        SELECT
            s1.[Période], s1.[N° compte],
            SUM(s1.[Débit])  AS debit, SUM(s1.[Crédit]) AS credit,
            s2.classe, s2.classe_label,
            s2.groupe, s2.groupe_label,
            s2.sous_groupe, s2.sous_groupe_label
        FROM Sheet1 s1
        JOIN Sheet2 s2 ON s1.[N° compte] = s2.compte
        WHERE s2.destination = 'Bilan'
          AND s1.[Période] BETWEEN ? AND ?
        GROUP BY s1.[Période], s1.[N° compte]
        """
        params = (periode_de, periode_a)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    # Extraction des périodes et préparation des données
    periodes = sorted({row['Période'] for row in rows})
    comptes = defaultdict(lambda: defaultdict(float))
    meta    = {}

    for row in rows:
        c = row['N° compte']
        mont = row['debit'] - row['credit']
        comptes[c][row['Période']] += mont
        if c not in meta:
            meta[c] = {
                'description':       dict_intitule.get(str(c), ''),
                'classe':            row['classe'],
                'classe_label':      row['classe_label'],
                'groupe':            row['groupe'],
                'groupe_label':      row['groupe_label'],
                'sous_groupe':       row['sous_groupe'],
                'sous_groupe_label': row['sous_groupe_label'],
                'mouvement':         row['debit'] > 0 or row['credit'] > 0
            }

    # Construction de l’affichage hiérarchique
    lignes = []
    vues   = set()
    groupes = sorted({(meta[c]['groupe'], meta[c]['groupe_label']) for c in comptes})

    for grp_code, grp_label in groupes:
        # sous-total du groupe
        monts_grp = [
            sum(comptes[c][p] for c in comptes if meta[c]['groupe'] == grp_code)
            for p in periodes
        ]
        lignes.append({
            'compte':      grp_code,
            'description': grp_label,
            'montants':    monts_grp,
            'total':       sum(monts_grp),
            'niveau':      'groupe-level'
        })
        # comptes enfants
        for c in sorted(comptes):
            if meta[c]['groupe'] == grp_code and c not in vues:
                monts_c = [comptes[c].get(p, 0.0) for p in periodes]
                lignes.append({
                    'compte':      c,
                    'description': meta[c]['description'],
                    'montants':    monts_c,
                    'total':       sum(monts_c),
                    'niveau':      'indent-3'
                })
                vues.add(c)

    # Filtres visuels
    if exclure_sans_mouvement:
        lignes = [l for l in lignes if not (l['niveau']=='indent-3' and not meta[l['compte']]['mouvement'])]
    if exclure_solde_zero:
        lignes = [l for l in lignes if l['niveau']!='indent-3' or round(l['total'],2)!=0.0]

    # Total annuel (PP)
    if total_annuel and type_etat=='PP':
        toutes_les_periodes = [f"2025-{m:02d}" for m in range(1,13)]
        periodes = toutes_les_periodes
        for l in lignes:
            if l['niveau']=='indent-3':
                l['montants'] = [comptes[l['compte']].get(p,0.0) for p in periodes] + [sum(comptes[l['compte']].values())]
            else:
                monts = [sum(comptes[c][p] for c in comptes if meta[c]['groupe']==l['compte']) for p in periodes]
                l['montants'] = monts + [sum(monts)]

    # TOTAL Général
    max_cols = len(periodes) + (1 if total_annuel and type_etat=='PP' else 1)
    total_gen_par_per = [
        sum(l['montants'][i] for l in lignes if i < len(l['montants']) and l['niveau']!='indent-3')
        for i in range(max_cols)
    ]
    lignes.append({
        'compte':      '',
        'description': 'TOTAL Général',
        'montants':    total_gen_par_per,
        'total':       sum(total_gen_par_per),
        'niveau':      'total-general'
    })

    return render_template(
        "templates_comptabilite/pp_bilan_result.html",
        lignes=lignes,
        periodes=periodes,
        periode_de=periode_de,
        periode_a=periode_a,
        type_etat=type_etat,
        filtre1=filtre1,
        filtre2=filtre2,
        filtre3=filtre3,
        filtre4=filtre4,
        total_annuel=total_annuel,
    )



# ────────────────────────────────────────────────────────────────────────────────
# Multilingue
# ────────────────────────────────────────────────────────────────────────────────
@app.route('/en/')
def en_home():
    return render_template('en_templates/en_index.html')

@app.route('/chde/')
def chde_home():
    return render_template('chde_templates/chde_index.html')















EXCEL_PATH = 'bd_factures_fournisseurs.xlsx'
# Load suppliers once
df_fourn = pd.read_excel('bd_fournisseurs.xlsx', sheet_name=0, usecols=['Code fournisseur','Nom du fournisseur'])

# Load once at startup
DF_FOURN = pd.read_excel('bd_fournisseurs.xlsx', sheet_name=0)
DF_FACT  = pd.read_excel('bd_factures_fournisseurs.xlsx', sheet_name=0)

@app.route('/factures_fournisseurs_search', methods=['GET'])
def factures_fournisseurs_search():
    return render_template('templates_fournisseurs/factures_fournisseurs_search.html')

@app.route('/api/autocomplete/code_api', methods=['GET'])
def autocomplete_code_api():
    q = request.args.get('q', '').lower()
    matches = DF_FOURN[DF_FOURN['Code fournisseur'].str.lower().str.contains(q)]
    return jsonify(matches['Code fournisseur'].unique().tolist())

@app.route('/api/autocomplete/nom_api', methods=['GET'])
def autocomplete_nom_api():
    q = request.args.get('q', '').lower()
    matches = DF_FOURN[DF_FOURN['Nom du fournisseur'].str.lower().str.contains(q)]
    return jsonify(matches['Nom du fournisseur'].unique().tolist())



@app.route('/factures_fournisseurs_result', methods=['GET'])
def factures_fournisseurs_result():
    # 1) Récupérer et afficher tous les filtres GET reçus
    args = request.args.to_dict()
    print("[ARGS] reçus :", args)

    # 2) Charger la BD Excel et vérifier les types des colonnes date
    df = pd.read_excel('bd_factures_fournisseurs.xlsx')
    print("[LOAD] shape initial :", df.shape)
    print("[CHECK] dtypes avant strip :", df.dtypes.to_dict())

    # 3) Nettoyer les colonnes et initialiser ‘Documents’
    df.columns = df.columns.str.strip()
    df['Documents'] = ''
    cols = [
        'No de facture',
        'Nom du fournisseur',
        'Date de facture',
        "Date d'échéance",
        'Montant',
        'Documents',
        'Balance',
        'Statut',
        'Paiement'
    ]
    df = df[cols]
    print("[CLEAN] colonnes après strip :", df.columns.tolist())
    print("[MAP] shape après mapping :", df.shape)

    # 4) Pour chaque filtre, afficher sa valeur et l'appliquer
    # 4a) nom_fournisseur
    if args.get('nom_fournisseur'):
        val = args['nom_fournisseur']
        print("[FILTER] nom_fournisseur =", val)
        mask = df['Nom du fournisseur'].str.contains(val, case=False, na=False)
        print("         → lignes gardées :", mask.sum())
        df = df[mask]

    # 4b) statut_paye
    # Filtre statut de paiement (valeurs Oui/Non)
        # Filtre statut de paiement (valeurs Oui/Non)
    # Filtre statut de paiement (valeurs Oui/Non)
    if args.get('statut_paye') and args['statut_paye'] != 'ensemble':
        raw = args['statut_paye']
        print("[FILTER] brut statut_paye =", raw)
        # Ici raw vaut 'oui' ou 'non'
        mask = df['Paiement'].str.lower().eq(raw.lower())
        print("         → lignes gardées statut :", mask.sum())
        df = df[mask]



    # 4c) date_facture_de
    if args.get('date_facture_de'):
        print("[CHECK] min date_facture:", df['Date de facture'].min())
        print("[CHECK] max date_facture:", df['Date de facture'].max())

        val = args['date_facture_de']
        print("[FILTER] date_facture_de =", val)
        dt = pd.to_datetime(val)
        mask = df['Date de facture'] >= dt
        print("         → lignes gardées :", mask.sum())
        df = df[mask]

    # 4d) date_facture_a
    if args.get('date_facture_a'):
        val = args['date_facture_a']
        print("[FILTER] date_facture_a =", val)
        dt = pd.to_datetime(val)
        mask = df['Date de facture'] <= dt
        print("         → lignes gardées :", mask.sum())
        df = df[mask]

    # 4e) date_echeance_de
    if args.get('date_echeance_de'):
        val = args['date_echeance_de']
        print("[FILTER] date_echeance_de =", val)
        dt = pd.to_datetime(val)
        mask = df["Date d'échéance"] >= dt
        print("         → lignes gardées :", mask.sum())
        df = df[mask]

    # 4f) date_echeance_a
    if args.get('date_echeance_a'):
        val = args['date_echeance_a']
        print("[FILTER] date_echeance_a =", val)
        dt = pd.to_datetime(val)
        mask = df["Date d'échéance"] <= dt
        print("         → lignes gardées :", mask.sum())
        df = df[mask]

    # 5) Bilan final avant rendu
    print("[END] shape final :", df.shape)

    # 6) Retourner la page résultat
    return render_template(
        'templates_fournisseurs/factures_fournisseurs_result.html',
        factures=df.to_dict(orient='records'),
        filters=args
    )




@app.route('/double_creation', methods=['POST'])
def double_creation():
    import sqlite3

    print("▶▶▶ double_creation start") 

    # Bloc 1 : prochain numéro
    def get_next_num_ecriture():
        conn2 = sqlite3.connect("grand_livre.db")
        cur2  = conn2.cursor()
        try:
            cur2.execute(
                "SELECT MAX(CAST(`Numéro d'écriture` AS INTEGER)) FROM Sheet1"
            )
            res = cur2.fetchone()[0]
            return int(res) + 1 if res else 1
        finally:
            conn2.close()

    # Bloc 2 : lecture form
    raw = {k: request.form.getlist(k) for k in request.form.keys()}
    form_data = {k: (';'.join(v) if len(v) > 1 else v[0])
                 for k, v in raw.items()}
    
    print("DEBUG comptes_ht   =", raw.get('compte[]', []))
    print("DEBUG comptes_tva  =", raw.get('compte_tva[]', []))
    print("DEBUG base_ht_vals =", raw.get('base_ht[]', []))
    print("DEBUG tva_vals     =", raw.get('montant_tva[]', []))


    # Bloc 3 : connexion
    conn = engine.raw_connection()
    cur  = conn.cursor()
    num_ecriture  = get_next_num_ecriture()
    comptes_ht    = raw.get('compte[]', [])
    base_ht_vals  = raw.get('base_ht[]', [])
    comptes_tva   = raw.get('compte_tva[]', [])
    tva_vals      = raw.get('montant_tva[]', [])
    periode       = form_data.get('Période', '')
    date_fact     = form_data.get('Date de facture', '')
    no_facture    = form_data.get('No de facture', '')
    montant       = float(form_data.get('Montant', 0) or 0)

    # Bloc 4 : ajouter colonne si besoin
    try:
        cur.execute('ALTER TABLE Sheet1 ADD COLUMN "Intitulé du compte" TEXT')
    except:
        pass


        # juste après avoir calculé num_ecriture
    cur.execute(
    'DELETE FROM Sheet1 WHERE "Numéro d\'écriture" = ?',
    (num_ecriture,)
    )


    # Bloc 5 : écriture Fournisseur (une seule fois)
    raw_acc = raw.get('No compte Fournisseur', [form_data.get('No compte Fournisseur','')])[0]
    num_f, sep, intit_f = raw_acc.partition(' – ')
    num_f   = num_f.strip()
    intit_f = intit_f.strip() if sep else ''

    print("→ INSERT fournisseur")

    cur.execute(
        """INSERT INTO Sheet1
           ("N° compte","Intitulé du compte","Période","Date",
            "Libellé","Numéro d'écriture","Fournisseur","Débit","Crédit")
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (num_f, intit_f, periode, date_fact,
         no_facture, num_ecriture,
         form_data.get('Fournisseur',''), 0, montant)
    )

        # ── Bloc 6 : écriture HT unique ────────────────────────────────
    print("→ INSERT HT")  # debug
    if comptes_ht:
        num_ht, sep_ht, intit_ht = comptes_ht[0].partition(' – ')
        num_ht   = num_ht.strip()
        intit_ht = intit_ht.strip() if sep_ht else ''
        debit_ht = float(base_ht_vals[0] or 0)
        cur.execute(
            """INSERT INTO Sheet1
               ("N° compte","Intitulé du compte","Période","Date",
                "Libellé","Numéro d'écriture","Fournisseur","Débit","Crédit")
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                num_ht, intit_ht, periode, date_fact,
                no_facture, num_ecriture, '', debit_ht, 0
            )
        )

    # ── Bloc 7 : écriture TVA unique ───────────────────────────────
    print("→ INSERT TVA")  # debug
    if comptes_tva:
        num_tva, sep_tva, intit_tva = comptes_tva[0].partition(' – ')
        num_tva    = num_tva.strip()
        intit_tva  = intit_tva.strip() if sep_tva else ''
        debit_tva  = float(tva_vals[0] or 0)
        cur.execute(
            """INSERT INTO Sheet1
               ("N° compte","Intitulé du compte","Période","Date",
                "Libellé","Numéro d'écriture","Fournisseur","Débit","Crédit")
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                num_tva, intit_tva, periode, date_fact,
                no_facture, num_ecriture, '', debit_tva, 0
            )
        )


    # Bloc 8 : commit + fermeture
    conn.commit()
    cur.close()
    conn.close()

    # Bloc 9 : mise à jour Excel…
    df = pd.read_excel(FACTURES_PATH, dtype=str, keep_default_na=False)
    df.columns = [c.strip().replace("’","'") for c in df.columns]
    new_row = {
        'Nom du fournisseur'    : form_data.get('Fournisseur',''),
        'No compte Fournisseur' : form_data.get('No compte Fournisseur',''),
        'Condition de paiement' : form_data.get('Condition de paiement',''),
        'Date de facture'       : form_data.get('Date de facture',''),
        'Date d\'échéance'      : form_data.get('Date échéance',''),
        'Période'               : form_data.get('Période',''),
        'Montant'               : form_data.get('Montant',''),
        'No de facture'         : form_data.get('No de facture',''),
        'No de compte'          : ';'.join(comptes_ht),
        'Somme brute'           : ';'.join(base_ht_vals),
        'No de compte TVA'      : ';'.join(comptes_tva),
        'Montant TVA'           : ';'.join(tva_vals),
        'Numéro d\'écriture'    : str(num_ecriture)
    }
    df.loc[len(df)] = new_row
    df.to_excel(FACTURES_PATH, index=False)

    return jsonify({"num_ecriture": num_ecriture}), 200







if __name__ == "__main__":
    app.run(debug=True, port=5006)


