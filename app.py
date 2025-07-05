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
    return render_template('index.html')

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

@app.route('/recherche_fournisseurs')
def recherche_fournisseurs():
    pass

@app.route('/autocomplete')
def autocomplete():
    pass

@app.route('/modifier', methods=['POST'])
def modifier_fournisseur():
    pass

@app.route('/creer', methods=['POST'])
def creer_fournisseur():
    pass

@app.route('/supprimer', methods=['POST'])
def supprimer_fournisseur():
    pass

@app.route('/liste_fournisseurs')
def liste_fournisseurs():
    pass

@app.route('/details_fournisseur')
def details_fournisseur():
    pass

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
@app.route('/recherche_factures_fournisseurs')
def recherche_factures_fournisseurs():
    fournisseurs = df_fournisseurs.to_dict(orient='records')
    comptes_plan  = get_accounts()
    return render_template(
        'templates_fournisseurs/recherche_factures_fournisseurs.html',
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

# ——— Route : ajouter une nouvelle facture ———
@app.route('/ajouter_facture', methods=['POST'])
def ajouter_facture():
    fp = os.path.join(app.root_path, 'bd_factures_fournisseurs.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    data = {
        key: (';'.join(vals) if len(vals) > 1 else vals[0])
        for key, vals in request.form.lists()
    }
    df.loc[len(df)] = data
    df.to_excel(fp, index=False)
    return jsonify({"message": "Facture ajoutée avec succès !"})

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


@app.route('/grand_livre_ecriture/<num_ecriture>')
def grand_livre_ecriture_id(num_ecriture):
    num_ecriture = int(num_ecriture)
    # Récupère la ligne correspondante dans la table Sheet1
    row = pd.read_sql_query(
        'SELECT * FROM Sheet1 WHERE "Numéro d\'écriture" = ?',
        engine,
        params=(num_ecriture,),
    ).iloc[0]

    # On reformate les clés pour votre template JS / Jinja
    ecriture = {
        'num_ecriture': row["Numéro d'écriture"],
        'date'        : row['Date'],
        'periode'     : row['Période'],
        'libelle'     : row['Libellé'],
        'compte'      : row['N° compte'],
        'intitule'    : row['Fournisseur'],  # ou row['Intitulé du compte'] si vous préférez
        'debit'       : row['Débit'],
        'credit'      : row['Crédit']
    }

    # On passe la liste des comptes pour le menu déroulant
    return render_template(
        'templates_comptabilite/grand_livre_ecriture.html',
        accounts=get_accounts(),
        current=ecriture
    )




@app.route('/submit_ecriture', methods=['POST'])
def submit_ecriture():
    date_comp = request.form['date_comptabilisation']
    periode   = request.form['periode']
    libelle   = request.form['libelle']
    comptes   = request.form.getlist('N° compte[]')
    debits    = request.form.getlist('debit[]')
    credits   = request.form.getlist('credit[]')

    if sum(float(d or 0) for d in debits) != sum(float(c or 0) for c in credits):
        return jsonify(success=False, reason='Débit ≠ Crédit'), 400

    cur = engine.raw_connection().cursor()
    for cpt, d, c in zip(comptes, debits, credits):
        cur.execute("""
            INSERT INTO Sheet1(
              "N° compte","Période","Date",
              "Libellé","Fournisseur","Débit","Crédit")
            VALUES (?,?,?,?,?,?,?)
        """, (cpt, periode, date_comp, libelle, '', d or 0, c or 0))
    cur.connection.commit()
    new_id = cur.lastrowid
    cur.close()

    return jsonify(success=True, num_ecriture=new_id)

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





if __name__ == "__main__":
    app.run(debug=True, port=5006)
