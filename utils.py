from sqlalchemy import inspect, create_engine
import pandas as pd

# ─── Engine unique pointant sur votre base grand_livre.db ────────────────────
engine = create_engine('sqlite:///grand_livre.db')

# ─── Utilitaire : ne renvoie que les colonnes demandées qui existent ─────────
def load_sheet1(needed_cols):
    """
    Retourne un DataFrame pandas ne contenant que les colonnes de
    needed_cols qui existent réellement dans la table Sheet1.
    """
    insp = inspect(engine)
    all_cols = [col["name"] for col in insp.get_columns("Sheet1")]
    cols = [c for c in needed_cols if c in all_cols]
    if not cols:
        raise ValueError(f"Aucune des colonnes demandées {needed_cols} n'existe dans Sheet1.")
    sql = "SELECT " + ", ".join(f"`{c}`" for c in cols) + " FROM Sheet1"
    return pd.read_sql_query(sql, engine)


