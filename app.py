from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import sqlite3
import os
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy import inspect

app = Flask(__name__)
















engine = create_engine('sqlite:///grand_livre.db')


def load_sheet1(needed_cols, engine):
    """
    Retourne un DataFrame pandas ne contenant que les colonnes de
    needed_cols qui existent réellement dans la table Sheet1.
    """
    insp = inspect(engine)
    # récupère la liste de toutes les colonnes existantes
    all_cols = [col['name'] for col in insp.get_columns('Sheet1')]
    # ne garde que celles qui sont demandées ET réellement présentes
    cols = [c for c in needed_cols if c in all_cols]
    if not cols:
        raise ValueError(f"Aucune des colonnes demandées {needed_cols} n'existe dans Sheet1.")
    # construit la requête SQL
    select_clause = ", ".join(f"`{c}`" for c in cols)
    sql = f"SELECT {select_clause} FROM Sheet1"
    # exécute et retourne le DataFrame
    return pd.read_sql_query(sql, engine)









# ---------------------------------------------------------------
#  utilitaire commun : lit plan_comptable.xlsx   (AJOUTER ICI)
# ---------------------------------------------------------------
# utilitaire commun : lit plan_comptable.xlsx
def get_accounts():
    """
    Retourne une liste de dictionnaires
    [{'num_compte':'1000', 'intitule':'Capital'}, …]
    """
    raw = pd.read_excel('plan_comptable.xlsx', dtype=str)   # lecture brute

    # on garde les 2 premières colonnes remplies
    df  = raw.iloc[:, :2].dropna(how='all')

    df = df.rename(columns={
        df.columns[0]: 'num_compte',
        df.columns[1]: 'intitule'
    })

    return df.to_dict(orient='records')



@app.route('/')
def index():
    return render_template('index.html')



























































@app.route('/menu_principal')
def menu_principal():
    return render_template('menu_principal.html')

@app.route('/menu_comptabilite')
def menu_comptabilite():
    return render_template('menu_comptabilite.html')

@app.route('/comptabilite_fournisseurs')
def comptabilite_fournisseurs():
    return render_template('templates_fournisseurs/comptabilite_fournisseurs.html')

@app.route('/recherche_factures_fournisseurs')
def recherche_factures_fournisseurs():
    return render_template('templates_fournisseurs/recherche_factures_fournisseurs.html')

# Chargement des bases de données
df_fournisseurs = pd.read_excel("bd_fournisseurs.xlsx", dtype=str, keep_default_na=False)
df_tva = pd.read_excel("bd_tva.xlsx", dtype=str, keep_default_na=False)
df_delai = pd.read_excel("bd_delai_de_paiement.xlsx", dtype=str, keep_default_na=False)

# Pour les comptes, on charge chacun depuis son fichier
df_crediter = pd.read_excel("plan_comptable_crediter.xlsx", dtype=str, keep_default_na=False)
df_debiter = pd.read_excel("plan_comptable_debiter.xlsx", dtype=str, keep_default_na=False)

@app.route('/recherche_fournisseurs')
def recherche_fournisseurs():
    print("==> Page recherche_fournisseurs rechargée <==")
    # Conversion des DataFrames en listes de dictionnaires
    tva_options = df_tva.to_dict(orient="records")
    delai_options = df_delai.to_dict(orient="records")
    crediter_options = df_crediter.to_dict(orient="records")
    debiter_options = df_debiter.to_dict(orient="records")

    print("✅ Options envoyées :", {
        "tva": tva_options[:5],  # Montre les 5 premiers éléments pour vérifier
        "delai": delai_options[:5],
        "crediter": crediter_options[:5],
        "debiter": debiter_options[:5]
})

    print("🔎 Vérification : TVA options envoyées :", tva_options)

    return render_template('templates_fournisseurs/recherche_fournisseurs.html',
    tva_options=tva_options,
    delai_options=delai_options,
    crediter_options=crediter_options,
    debiter_options=debiter_options
)

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("query", "").strip().lower()
    if not query:
        return jsonify([])

    results = df_fournisseurs[
        df_fournisseurs["Code fournisseur"].str.lower().str.startswith(query) |
        df_fournisseurs["Nom du fournisseur"].str.lower().str.startswith(query)
        ].to_dict(orient="records")
    return jsonify(results)

@app.route("/modifier", methods=["POST"])
def modifier():
    try:
        data = request.form.to_dict()
        code = data.get("Code fournisseur")
        if not code:
            return jsonify({"message": "Code fournisseur manquant !"}), 400

        idx = df_fournisseurs[df_fournisseurs["Code fournisseur"] == code].index
        if idx.empty:
            return jsonify({"message": "Fournisseur non trouvé !"}), 404

        for key, value in data.items():
            df_fournisseurs.at[idx[0], key] = value

        df_fournisseurs.to_excel("bd_fournisseurs.xlsx", index=False)
        return jsonify({"message": "Fournisseur modifié avec succès !"}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 500

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
    

@app.route('/comptabilite_clients')
def comptabilite_clients():
        return render_template('templates_clients/comptabilite_clients.html')

@app.route('/recherche_clients')
def recherche_clients():
    return render_template('templates_clients/recherche_clients.html')

@app.route('/recherche_factures_clients')
def recherche_factures_clients():
    return render_template('templates_clients/recherche_factures_clients.html')

@app.route('/salaires_rh_menu')
def salaires_rh_menu():
    return render_template('templates_rh/salaires_rh_menu.html')

@app.route('/gestion_employes')
def gestion_employes():
    return render_template('templates_rh/gestion_employes.html')

@app.route('/traitement_salaires')
def traitement_salaires():
    return render_template('templates_rh/traitement_salaires.html')







@app.route('/grand_livre_accueil')
def grand_livre_accueil():
    return render_template('templates_comptabilite/grand_livre_accueil.html')



@app.route('/grand_livre_full')
def grand_livre_full():
    # 1. Charger dynamiquement Sheet1
    needed = [
       'N° compte','Période','Date','Libellé',
       "Numéro d'écriture",'Fournisseur','Débit','Crédit'
    ]
    df = load_sheet1(needed, engine)
    df = df.rename(columns={"Numéro d'écriture": "num_ecriture"})
    # 2. Nettoyer & renommer
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'N° compte':         'num_compte',
        'Période':           'periode',
        'Date':              'date',
        'Libellé':           'libelle',
        "Numéro d'écriture": 'num_ecriture',
        'Fournisseur':       'fournisseur',
        'Débit':             'debit',
        'Crédit':            'credit'
    })

    # 3. Injecter l’intitulé du compte à partir du plan comptable
    df_plan = pd.read_excel("plan_comptable.xlsx")
    df_plan.columns = df_plan.columns.str.strip()
    title_map = dict(zip(
        df_plan['N° compte'].astype(str),
        df_plan['Intitulé du compte'].astype(str)
    ))
    df['intitule'] = df['num_compte'].astype(str).map(title_map)

    # 4. Transformer en liste de dicts
    entries = df.to_dict(orient='records')

    # 5. Passer également la liste "comptes" si votre template en a besoin
    comptes = [f"{nc} – {title_map.get(nc,'')}"
               for nc in sorted(df['num_compte'].astype(str).unique())]

    return render_template(
        'templates_comptabilite/grand_livre_full.html',
        entries=entries,
        comptes=comptes       # facultatif, selon votre template
    )






@app.route('/grand_livre_recherche')
def grand_livre_recherche():
    # Lecture du plan comptable
    df_plan = pd.read_excel("plan_comptable.xlsx")
    intitules_dict = dict(zip(
        df_plan["N° compte"].astype(str),
        df_plan["Intitulé du compte"].astype(str)
    ))

    comptes = [
        f"{str(row['N° compte']).strip()} - {str(row['Intitulé du compte']).strip()}"
        for _, row in df_plan.iterrows()
        if str(row['N° compte']).strip() != ''
    ]
    

    # On ne passe plus que la liste des comptes au template
    return render_template(
        "templates_comptabilite/grand_livre_recherche.html",
        comptes=comptes
    )






























@app.route('/grand_livre_result')
def grand_livre_result():
    # 1) Lecture dynamique de Sheet1 (tolère les ajouts/suppressions de colonnes)
    needed = [
        'N° compte', 'Période', 'Date', 'Libellé',
        "Numéro d'écriture", 'Fournisseur', 'Débit', 'Crédit'
    ]
    df = load_sheet1(needed, engine)
        # normaliser le nom de la colonne pour Jinja et url_for
    


    # 2) Reconstruction de la liste "comptes" (numéro + intitulé) pour le formulaire
    df_plan = pd.read_excel("plan_comptable.xlsx")
    df_plan.columns = df_plan.columns.str.strip()
    df_plan = df_plan.rename(columns={
        'N° compte': 'NumCompte',
        'Intitulé du compte': 'IntituleCompte'
    })
    comptes = [
        f"{row['NumCompte']} – {row['IntituleCompte']}"
        for _, row in df_plan.iterrows()
        if str(row['NumCompte']).strip() != ''
    ]

    # 3) Récupérer les filtres GET et appliquer
    cd  = request.args.get('compte_de')  or None
    ca  = request.args.get('compte_a')   or None
    pd_ = request.args.get('periode_de') or None
    pa  = request.args.get('periode_a')  or None

    if cd:  df = df[df['N° compte'] >= cd]
    if ca:  df = df[df['N° compte'] <= ca]
    if pd_: df = df[df['Période'] >= pd_]
    if pa:  df = df[df['Période'] <= pa]

    # 4) Grouper par compte pour construire resultats
     # 4) Grouper par compte pour construire resultats
    #    → on force la clef en str pour matcher vos templates
    resultats = {
        str(compte): grp.to_dict(orient='records')
        for compte, grp in df.groupby('N° compte')
    }

    # 5) Dictionnaire des intitulés pour chaque compte
    intitulés_comptes = {
        str(row['NumCompte']): row['IntituleCompte']
        for _, row in df_plan.iterrows()
    }

    # 6) On transmet tout au template
    return render_template(
        'templates_comptabilite/grand_livre_result.html',
        comptes=comptes,
        resultats=resultats,
        intitulés_comptes=intitulés_comptes
    )
















































































@app.route('/grand_livre_ecriture')
def grand_livre_ecriture():
    # --- lecture + nettoyage minimal du plan comptable ---
    with pd.ExcelFile("plan_comptable.xlsx") as xls:
        feuille = xls.sheet_names[0]  # première feuille trouvée
        df_plan = (
            pd.read_excel(xls, sheet_name=feuille, dtype=str)  # tout en texte
            .loc[:, ['N° compte', 'Intitulé du compte']]  # on ne garde que ces 2 colonnes
            .dropna(subset=['N° compte', 'Intitulé du compte'])  # vire les lignes incomplètes
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
    # ligne concernée
    row = pd.read_sql_query(
        'SELECT * FROM Sheet1 WHERE "Numéro d\'écriture" = ?',
        engine,
        params=(num_ecriture,),   # ← tuple à 1 élément
    ).iloc[0]


    # mêmes clefs que celles attendues par le JS
    ecriture = {
        'num_ecriture': row["Numéro d'écriture"],
        'date'        : row['Date'],
        'periode'     : row['Période'],
        'libelle'     : row['Libellé'],
        'compte'      : row['N° compte'],
        'intitule'    : row['Fournisseur'],   # ou row['Intitulé du compte'] si dispo
        'debit'       : row['Débit'],
        'credit'      : row['Crédit']
    }

    # comptes pour le menu déroulant + écriture pré‑remplie
    return render_template(
        'templates_comptabilite/grand_livre_ecriture.html',
        accounts=get_accounts(),
        current=ecriture
    )






@app.route('/submit_ecriture', methods=['POST'])
def submit_ecriture():
    try:
        # ---------- lecture des champs ----------
        date_comp = request.form['date_comptabilisation']
        periode   = request.form['periode']
        libelle   = request.form['libelle']
        comptes   = request.form.getlist('N° compte[]')
        debits    = request.form.getlist('debit[]')
        credits   = request.form.getlist('credit[]')

        # ---------- contrôle d’équilibre ----------
        if sum(float(d) if d else 0 for d in debits) \
            != sum(float(c) if c else 0 for c in credits):
                return jsonify(success=False, reason='Débit ≠ Crédit'), 400

        # ---------- numéro d’écriture suivant ----------
        cur  = engine.raw_connection().cursor()

        # ---------- insertion ----------
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

        # ---------- réponse ----------
        if request.accept_mimetypes['application/json']:
            return jsonify(success=True, num_ecriture=new_id)

        return redirect(url_for('grand_livre'))

    except Exception as e:
        print("Erreur dans /submit_ecriture :", e)
        return jsonify({'success': False, 'error': str(e)}), 500
















# ------------------------
# 🧾 PP / BILAN - MODULE FINAL- 
# ------------------------


# On préprare le matériel pour l'utilitaire:
from sqlalchemy import inspect
import pandas as pd
from utils import load_sheet1
from sqlalchemy import create_engine

engine = create_engine('sqlite:///grand_livre.db')








def get_connection():
    conn = sqlite3.connect('grand_livre.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/pp_bilan_search')
def pp_bilan_search():
    return render_template("templates_comptabilite/pp_bilan_search.html")






@app.route('/pp_bilan_result', methods=['POST'])
def pp_bilan_result():
    periode_de  = request.form['periode_de']
    periode_a   = request.form['periode_a']
    type_etat   = request.form['type'].strip().upper()


    filtre1 = 'filtre1' in request.form
    filtre2 = 'filtre2' in request.form
    filtre3 = 'filtre3' in request.form
    filtre4 = 'filtre4' in request.form


    exclure_sans_mouvement = 'filtre1' in request.form
    exclure_solde_zero     = 'filtre2' in request.form
    inclure_tous           = 'filtre3' in request.form
    total_annuel           = 'filtre4' in request.form  # Récupération des cases à cocher (renvoie '' si décochée, sinon 'on')


   




    conn = get_connection()



    
    insp = inspect(engine)
    colonnes = [col['name'] for col in insp.get_columns('Sheet1')]
    app.logger.debug("Colonnes dans Sheet1 : %s", colonnes)





   


      # ─── AVANT TOUT : charger votre plan pour récupérer l'intitulé selon le N° de compte ─────
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
        WHERE   (substr(s1.[N° compte],1,1) = '3'
                OR substr(s1.[N° compte],1,1) = '4' 
                OR substr(s1.[N° compte], 1, 1) = '5'
                OR substr(s1.[N° compte], 1, 1) = '6'
                OR substr(s1.[N° compte], 1, 1) = '7'
                OR substr(s1.[N° compte], 1, 1) = '8'
        )
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
                'mouvement':         row['debit'] > 0 or row['credit'] > 0  # ✅ AJOUT ICI
            }
    else:
        if row['debit'] != 0 or row['credit'] != 0:
            meta[c]['mouvement'] = True
            

       # ─── Construction de l'affichage hiérarchique strictement ordonnée ────────────
       # ─── Construction deux niveaux : Groupe + Comptes ────────────
    lignes = []
    vues    = set()

    # Pour chaque groupe unique, afficher son sous-total puis ses comptes
    groupes = sorted({(meta[c]['groupe'], meta[c]['groupe_label']) for c in comptes})
    for grp_code, grp_label in groupes:
        # 1) Ligne de sous-total du groupe
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

        # 2) Comptes enfants indentés
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
    # ────────────────────────────────────────────────────────────────


    # ────────────────────────────────────────────────────────────────





    # Filtres visuels
    if exclure_sans_mouvement:
        lignes = [l for l in lignes if not (l['niveau'] == 'indent-3' and not meta[l['compte']]['mouvement'])]

    if exclure_solde_zero:
        lignes = [
            l for l in lignes 
            if l['niveau'] != 'indent-3' or round(l['total'], 2) != 0.0
        ]

    if inclure_tous:
        pass  # on affiche tout (aucun filtre)




    if total_annuel and type_etat == 'PP':
        toutes_les_periodes = [
            '2025-01', '2025-02', '2025-03', '2025-04',
            '2025-05', '2025-06', '2025-07', '2025-08',
            '2025-09', '2025-10', '2025-11', '2025-12'
        ]
        periodes = toutes_les_periodes

        for l in lignes:

            if l['niveau'] == 'total-general':
                continue
            if l['niveau'] == 'indent-3':
                l['montants'] = [comptes.get(l['compte'], {}).get(p, 0.0) for p in periodes]
                l['montants'].append(sum(l['montants']))
            else:
                monts = [
                    sum(comptes[c][p] for c in comptes if meta[c][l['niveau'].split('-')[0]] == l['compte'])
                    for p in periodes
                ]
                l['montants'] = monts + [sum(monts)]





        # ─── NOUVEAU TOTAL Général ──────────────────────────────────────
    max_cols = len(periodes) + (1 if total_annuel and type_etat == 'PP' else 1)
    total_gen_par_per = [
        sum(
            l['montants'][i]
            for l in lignes
            if l['niveau'] != 'indent-3' and i < len(l['montants'])
        )
        for i in range(max_cols)
    ]
    lignes.append({
        'compte':      '',
        'description': 'TOTAL Général',
        'montants':    total_gen_par_per,
        'total':       sum(total_gen_par_per),
        'niveau':      'total-general'
    })
    # ────────────────────────────────────────────────────────────────








    
    return render_template("templates_comptabilite/pp_bilan_result.html",
        lignes= lignes,
        periodes= periodes,
        periode_de=periode_de,
        periode_a=periode_a,
        type_etat=type_etat,


        filtre1=filtre1,
        filtre2=filtre2,
        filtre3=filtre3,
        filtre4=filtre4,
        total_annuel=total_annuel,  # POUR LE HTML

    )






























# ——— Multilingue après flags ———

# ——— Routes multilingues ———

@app.route('/en/')
def en_home():
    return render_template('en_templates/en_index.html')

@app.route('/chde/')
def chde_home():
    return render_template('chde_templates/chde_index.html')

# ————————————————————————















if __name__ == "__main__":
    app.run(debug=True, port=5005)

