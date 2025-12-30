import pandas as pd
from core.db import get_conn

def get_daily_balance():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT transaction_date,
               SUM(CASE WHEN transaction_type='CREDIT' THEN amount ELSE -amount END) as net_flow
        FROM bank_statements
        GROUP BY transaction_date
    """, conn)

    df["balance"] = df["net_flow"].cumsum()
    return df

def detect_missing_vendor_payments():
    conn = get_conn()
    q = """
    SELECT v.vendor_name, v.net_amount
    FROM vendor_invoices v
    LEFT JOIN bank_statements b
    ON b.counterparty_name = v.vendor_name
    WHERE v.payment_status != 'Paid'
    """
    return pd.read_sql(q, conn)

def detect_unexpected_payments():
    conn = get_conn()
    q = """
    SELECT *
    FROM bank_statements
    WHERE category NOT IN ('Salary','Rent','Vendor Payment','Client Collection')
    """
    return pd.read_sql(q, conn)

def forecast_cash_shortage():
    conn = get_conn()
    cash = pd.read_sql("SELECT SUM(balance_after) as bal FROM bank_statements", conn)
    payroll = pd.read_sql("SELECT SUM(net_salary) as sal FROM payroll WHERE payment_status='Paid'", conn)
    return cash.iloc[0]["bal"] - payroll.iloc[0]["sal"]
