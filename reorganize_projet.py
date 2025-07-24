#!/usr/bin/env python3
# reorganize_projet.py (version finale)
import os
import re
import shutil
from collections import Counter

MODULE_SECTIONS = [
    ('/factures_fournisseurs', 'MODULE FOURNISSEURS'),
    ('/api/autocomplete',    'MODULE FOURNISSEURS'),
    ('/menu_comptabilite',   'MODULE COMPTABILITE'),
    ('/grand_livre',         'MODULE COMPTABILITE'),
    ('/pp_bilan',            'MODULE COMPTABILITE'),
]

def reorganize_app_py(src, dst):
    lines = open(src, encoding='utf-8', errors='ignore').read().splitlines()
    # Détection de routes dupliquées
    routes = [m.group(1) for l in lines if (m:=re.match(r"\s*@app\.route\('([^']+)'", l))]
    dupes = [r for r, c in Counter(routes).items() if c > 1]

    out = open(dst, 'w', encoding='utf-8')
    out.write('# ======= ROUTES ORGANISÉES (auto généré) =======\n\n')
    if dupes:
        out.write('# Routes dupliquées détectées:\n')
        for d in dupes:
            out.write(f'#   DUPLIQUE: {d}\n')
        out.write('\n')

    current = None
    previous_blank = False
    for line in lines:
        # Section par module
        if (m:=re.match(r"\s*@app\.route\('([^']+)'", line)):
            route = m.group(1)
            for prefix, section in MODULE_SECTIONS:
                if route.startswith(prefix) and current != section:
                    out.write(f'\n# ===== {section} =====\n')
                    current = section
                    break

        # Nettoyage des lignes vides multiples
        if line.strip() == '':
            if previous_blank:
                continue
            previous_blank = True
        else:
            previous_blank = False

        out.write(line + '\n')

    out.close()
    print(f'-> {dst} généré avec détection de duplicata et nettoyage.')

def insert_html_separators(src, dst):
    lines = open(src, encoding='latin-1', errors='ignore').read().splitlines()
    form_count = sum(1 for l in lines if '<form' in l and 'method' in l)
    table_count = sum(1 for l in lines if '<table' in l)
    out = open(dst, 'w', encoding='utf-8')
    out.write('<!-- ===== TEMPLATE ORGANISÉ (auto généré) ===== -->\n')
    if form_count > 1:
        out.write(f'<!-- DUPLIQUÉS de <form>: {form_count} occurrences ===== -->\n')
    if table_count > 1:
        out.write(f'<!-- DUPLIQUÉS de <table>: {table_count} occurrences ===== -->\n')

    previous_blank = False
    for line in lines:
        if '<form' in line and 'method=' in line:
            out.write('\n<!-- ==== SECTION: FORMULAIRE ==== -->\n')
        if '<table' in line:
            out.write('\n<!-- ==== SECTION: TABLEAU ==== -->\n')

        if line.strip() == '':
            if previous_blank:
                continue
            previous_blank = True
        else:
            previous_blank = False

        out.write(line + '\n')

    out.close()
    print(f'-> {dst} généré avec marqueurs et nettoyage.')

def main():
    # 1) Traiter app.py
    src_app = 'app.py'
    dst_app = 'reorganized_app.py'
    if os.path.exists(src_app):
        shutil.copyfile(src_app, dst_app)
        reorganize_app_py(src_app, dst_app)
    else:
        print(f'Erreur : {src_app} introuvable.')

    # 2) Traiter tous les templates HTML
    for root, _, files in os.walk('templates'):
        for fname in files:
            if fname.endswith('.html'):
                src = os.path.join(root, fname)
                dst = os.path.join(root, 'reorg_' + fname)
                insert_html_separators(src, dst)

if __name__ == '__main__':
    main()
