import pandas as pd
from core.db import get_conn

def load_csv(table, path):
    df = pd.read_csv(path)
    conn = get_conn()
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()
