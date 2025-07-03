# File : app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import sqlite3
import os
from collections import defaultdict
from sqlalchemy import text, create_engine, inspect

app = Flask(__name__)
engine = create_engine('sqlite:///grand_livre.db')

app.secret_key = 'unspoken_greatness_silent_success'






def load_sheet1(needed_cols, engine):
    insp = inspect(engine)
    all_cols = [c['name'] for c in insp.get_columns('Sheet1')]
    cols = [c for c in needed_cols if c in all_cols]
    if not cols:
        raise ValueError(f"Aucune des colonnes demandées {needed_cols} n'existe dans Sheet1.")
    select_clause = ", ".join(f"`{c}`" for c in cols)
    sql = f"SELECT {select_clause} FROM Sheet1"
    return pd.read_sql_query(sql, engine)

def get_accounts():
    raw = pd.read_excel('plan_comptable.xlsx', dtype=str)
    df = raw.iloc[:, :2].dropna(how='all')
    df = df.rename(columns={df.columns[0]: 'num_compte', df.columns[1]: 'intitule'})
    return df.to_dict(orient='records')

# @app.errorhandler(404)
# def not_found(e):
  #  return render_template('construction.html'), 200

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






from flask import render_template, send_from_directory, request, redirect, url_for, flash
import os
import pandas as pd
import sqlite3


@app.route('/administration')
def administration():
    return render_template('templates_administration/administration.html')



# → Téléchargement d’une BD existante
@app.route('/download/<path:fname>')
def download_file(fname):
    # envoie le fichier fname depuis la racine du projet
    return send_from_directory(app.root_path, fname, as_attachment=True)

# → Import (upload) d’une nouvelle version de la même BD
@app.route('/upload/<path:fname>', methods=['POST'])
def upload_file(fname):
    f = request.files.get('file')
    if not f:
        flash("Aucun fichier sélectionné", "error")
    else:
        target = os.path.join(app.root_path, fname)
        f.save(target)
        flash(f"{fname} importé avec succès", "success")
    return redirect(url_for('administration'))






# 1) Plan comptable (Excel)
@app.route('/bd_plan_comptable')
def bd_plan_comptable():
    fp = os.path.join(app.root_path, 'plan_comptable.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_plan_comptable.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

# 2) Fournisseurs (Excel)
@app.route('/bd_fournisseurs')
def bd_fournisseurs():
    fp = os.path.join(app.root_path, 'bd_fournisseurs.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_fournisseurs.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

# 3) Factures fournisseurs (Excel)
@app.route('/bd_factures_fournisseurs')
def bd_factures_fournisseurs():
    fp = os.path.join(app.root_path, 'bd_factures_fournisseurs.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_factures_fournisseurs.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

# 4) Grand livre (SQLite)
@app.route('/bd_grand_livre')
def bd_grand_livre():
    dbp = os.path.join(app.root_path, 'grand_livre.db')
    conn = sqlite3.connect(dbp)
    df = pd.read_sql_query('SELECT * FROM grand_livre', conn)
    conn.close()
    return render_template('bd_grand_livre.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

# 5) Clients (Excel)
@app.route('/bd_clients')
def bd_clients():
    fp = os.path.join(app.root_path, 'bd_clients.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_clients.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

# 6) Factures clients (Excel)
@app.route('/bd_factures_clients')
def bd_factures_clients():
    fp = os.path.join(app.root_path, 'bd_factures_clients.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_factures_clients.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

# 7) TVA (Excel)
@app.route('/bd_tva')
def bd_tva():
    fp = os.path.join(app.root_path, 'bd_tva.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_tva.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))

# 8) Délais de paiement (Excel)
@app.route('/bd_delai_paiement')
def bd_delai_paiement():
    fp = os.path.join(app.root_path, 'bd_delai_de_paiement.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)
    return render_template('bd_delai_paiement.html',
                           columns=df.columns,
                           rows=df.to_dict(orient='records'))













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



@app.route("/modifier", methods=["POST"])
def modifier_fournisseur():
    data = request.form.to_dict()
    code = data.get("Code fournisseur","").strip()
    if not code:
        return jsonify({"message":"Code fournisseur manquant !"}),400
    idx = df_fournisseurs[df_fournisseurs["Code fournisseur"]==code].index
    if idx.empty:
        return jsonify({"message":"Fournisseur non trouvé !"}),404
    for k,v in data.items():
        df_fournisseurs.at[idx[0], k] = v
    df_fournisseurs.to_excel("bd_fournisseurs.xlsx", index=False)
    return jsonify({"message":"Fournisseur modifié avec succès !"}),200

@app.route("/creer", methods=["POST"])
def creer_fournisseur():
    global df_fournisseurs
    data = request.form.to_dict()
    mandatory = ["Code fournisseur","Nom du fournisseur","No téléphone 1",
                 "Compte à créditer","Compte à débiter","Taux TVA 1","Délai de paiement"]
    for f in mandatory:
        if not data.get(f,"").strip():
            return jsonify({"message":f"Champ obligatoire manquant: {f}"}),400
    if not df_fournisseurs[df_fournisseurs["Code fournisseur"]==data["Code fournisseur"]].empty:
        return jsonify({"message":"Fournisseur existe déjà !"}),400
    df_fournisseurs = pd.concat([df_fournisseurs,pd.DataFrame([data])],ignore_index=True)
    df_fournisseurs.to_excel("bd_fournisseurs.xlsx", index=False)
    return jsonify({"message":"Fournisseur créé avec succès !"}),200

@app.route("/supprimer", methods=["POST"])
def supprimer_fournisseur():
    global df_fournisseurs
    code = request.form.get("Code fournisseur","").strip()
    if not code:
        return jsonify({"message":"Champ obligatoire manquant: Code fournisseur (pour supprimer)"}),400
    idx = df_fournisseurs[df_fournisseurs["Code fournisseur"]==code].index
    if idx.empty:
        return jsonify({"message":"Fournisseur non trouvé !"}),404
    df_fournisseurs = df_fournisseurs.drop(idx)
    df_fournisseurs.to_excel("bd_fournisseurs.xlsx", index=False)
    return jsonify({"message":"Fournisseur supprimé avec succès !"}),200

@app.route('/liste_fournisseurs')
def liste_fournisseurs():
    df = pd.read_excel(os.path.join(app.root_path,'bd_fournisseurs.xlsx'))
    table_html = df.to_html(classes="table table-striped table-hover table-bordered", index=False, justify="center")
    return render_template('templates_fournisseurs/liste_fournisseurs.html', table_html=table_html)






















@app.route('/details_fournisseur')
def details():
    nom = request.args['nom']
    df  = pd.read_excel('bd_fournisseurs.xlsx')
    row = df.loc[df["Nom du fournisseur"]==nom].iloc[0]
    return jsonify({
      "compteFournisseur": row["Compte à créditer"],
      "conditionPaiement": row["Délai de paiement"],
      "compteADebiter":   row["Compte à débiter"],
      "tauxTVA1":         row["Taux TVA 1"],
      "compteTVA":        row["Compte TVA"]
    })

















@app.route('/grand_livre_accueil')
def grand_livre_accueil():
    return render_template('templates_comptabilite/grand_livre_accueil.html')

@app.route('/grand_livre_full')
def grand_livre_full():
    needed = ['N° compte','Période','Date','Libellé',"Numéro d'écriture",'Fournisseur','Débit','Crédit']
    df = load_sheet1(needed, engine)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'Numéro d\'écriture':'num_ecriture',
                             'N° compte':'num_compte','Période':'periode',
                             'Date':'date','Libellé':'libelle',
                             'Fournisseur':'fournisseur','Débit':'debit','Crédit':'credit'})
    df_plan = pd.read_excel("plan_comptable.xlsx")
    df_plan.columns = df_plan.columns.str.strip()
    title_map = dict(zip(df_plan['N° compte'].astype(str), df_plan['Intitulé du compte'].astype(str)))
    df['intitule'] = df['num_compte'].astype(str).map(title_map)
    entries = df.to_dict(orient='records')
    comptes = [f"{nc} – {title_map.get(nc,'')}" for nc in sorted(df['num_compte'].astype(str).unique())]
    return render_template('templates_comptabilite/grand_livre_full.html', entries=entries, comptes=comptes)

@app.route('/grand_livre_recherche')
def grand_livre_recherche():
    df_plan = pd.read_excel("plan_comptable.xlsx")
    intitules_dict = dict(zip(df_plan["N° compte"].astype(str), df_plan["Intitulé du compte"].astype(str)))
    comptes = [f"{str(r['N° compte']).strip()} - {str(r['Intitulé du compte']).strip()}"
               for _,r in df_plan.iterrows() if str(r['N° compte']).strip()]
    return render_template("templates_comptabilite/grand_livre_recherche.html", comptes=comptes)

@app.route('/grand_livre_result')
def grand_livre_result():
    needed = ['N° compte','Période','Date','Libellé',"Numéro d'écriture",'Fournisseur','Débit','Crédit']
    df = load_sheet1(needed, engine)
    df_plan = pd.read_excel("plan_comptable.xlsx", dtype=str)
    df_plan.columns = df_plan.columns.str.strip()
    dict_intitule = dict(zip(df_plan["N° compte"], df_plan["Intitulé du compte"]))
    cd = request.args.get('compte_de') or None
    ca = request.args.get('compte_a') or None
    pd_ = request.args.get('periode_de') or None
    pa = request.args.get('periode_a') or None
    if cd: df = df[df['N° compte'] >= cd]
    if ca: df = df[df['N° compte'] <= ca]
    if pd_: df = df[df['Période'] >= pd_]
    if pa: df = df[df['Période'] <= pa]
    rows = pd.DataFrame(df).groupby('N° compte')
    # ... reste de la fonction inchangé ...
    return render_template("templates_comptabilite/pp_bilan_result.html")








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









































@app.route('/recherche_factures_fournisseurs')
def recherche_factures_fournisseurs():
    fournisseurs = df_fournisseurs.to_dict(orient='records')
    comptes_plan  = get_accounts()  # liste de dicts {'num_compte': ..., 'intitule': ...}
    return render_template(
        'templates_fournisseurs/recherche_factures_fournisseurs.html',
        df_fournisseurs=fournisseurs,
        comptes_plan=comptes_plan
    )




@app.route("/autocomplete_factures_fournisseurs", methods=["GET"])
def autocomplete_factures_fournisseurs():
    q = request.args.get("query", "").strip().lower()
    if not q:
        return jsonify([])
    res = df_fournisseurs[
        df_fournisseurs["Nom du fournisseur"].str.lower().str.startswith(q)
    ].to_dict(orient='records')
    return jsonify(res)















# app.py

# app.py – route mise à jour factures
@app.route('/mettre_a_jour_facture', methods=['POST'])
def mettre_a_jour_facture():
    import pandas as pd, os
    data = request.form.to_dict()
    file_path = os.path.join(app.root_path, 'bd_factures_fournisseurs.xlsx')
    df = pd.read_excel(file_path, dtype=str, keep_default_na=False)
    # récupère l’ancien numéro ou tombe sur le nouveau si absent
    original = data.get('original_num_facture') or data.get('No de facture')
    idx = df[df['No de facture'] == original].index
    if idx.empty:
        return jsonify({'message':'Facture non trouvée !'}), 404
    for k, v in data.items():
        df.at[idx[0], k] = v
    df.to_excel(file_path, index=False)
    return jsonify({'message':'Facture mise à jour avec succès !'}), 200







@app.route('/liste_factures_fournisseurs')
def liste_factures_fournisseurs():
    import pandas as pd, os
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






















@app.route('/ajouter_facture', methods=['POST'])
def ajouter_facture():
    import pandas as pd, os
    from flask import request, jsonify

    # pour debug : afficher en console ce qui arrive
    
    print("📥 /ajouter_facture reçu, form keys/vals =", request.form.lists())

    # 1) Charger l’Excel
    fp = os.path.join(app.root_path, 'bd_factures_fournisseurs.xlsx')
    df = pd.read_excel(fp, dtype=str, keep_default_na=False)

    # 2) Construire le dict de TOUTES les données du formulaire
    data = {
        key: (';'.join(vals) if len(vals) > 1 else vals[0])
        for key, vals in request.form.lists()
    }

    # 3) Ajouter et sauvegarder
    # juste avant l’ajout
    print("→ Taille avant insertion :", df.shape)
    # insertion
    df.loc[len(df)] = data
    # juste après
    print("→ Taille après insertion :", df.shape)
    print("→ Nouvelle ligne :", data)
    df.to_excel(fp, index=False)
    print("✔️ Sauvegarde écrite dans", fp)


    return jsonify({"message": "Facture ajoutée avec succès !"})


if __name__ == "__main__":
    app.run(debug=True, port=5005)