import pandas as pd
from core.db import get_conn
from langchain.tools import tool

# =================================================
# PURE PYTHON FUNCTIONS (CALLABLE)
# =================================================

def _get_current_cash_balance():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT balance_after
        FROM bank_statements
        ORDER BY transaction_date DESC
        LIMIT 1
    """, conn)
    conn.close()

    if df.empty:
        return {"currency": "INR", "balance": 0.0}

    return {
        "currency": "INR",
        "balance": float(df.iloc[0]["balance_after"])
    }


def _get_top_cash_outflows_last_30_days():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            category,
            SUM(amount) AS total_spent
        FROM bank_statements
        WHERE transaction_type = 'DEBIT'
          AND transaction_date >= date('now', '-30 day')
        GROUP BY category
        ORDER BY total_spent DESC
        LIMIT 5
    """, conn)
    conn.close()

    return {
        "currency": "INR",
        "outflows": df.to_dict(orient="records")
    }

# =================================================
# TOOL WRAPPERS (FOR LLM ONLY)
# =================================================

@tool
def get_current_cash_balance():
    """Returns current cash balance in INR."""
    return _get_current_cash_balance()


@tool
def get_top_cash_outflows_last_30_days():
    """Returns top spending categories in last 30 days."""
    return _get_top_cash_outflows_last_30_days()
