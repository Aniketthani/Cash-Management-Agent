import sqlite3
import os

from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DB_PATH")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS bank_statements (
        transaction_id TEXT,
        account_number TEXT,
        transaction_date TEXT,
        transaction_type TEXT,
        amount REAL,
        balance_after REAL,
        counterparty_name TEXT,
        narration TEXT,
        category TEXT,
        payment_mode TEXT
    );

    CREATE TABLE IF NOT EXISTS vendor_invoices (
        invoice_id TEXT,
        vendor_name TEXT,
        invoice_date TEXT,
        due_date TEXT,
        net_amount REAL,
        payment_status TEXT
    );

    CREATE TABLE IF NOT EXISTS client_invoices (
        invoice_id TEXT,
        client_name TEXT,
        invoice_date TEXT,
        due_date TEXT,
        net_amount REAL,
        collection_status TEXT
    );

    CREATE TABLE IF NOT EXISTS payroll (
        employee_name TEXT,
        pay_period TEXT,
        net_salary REAL,
        payment_status TEXT
    );

    CREATE TABLE IF NOT EXISTS expense_receipts (
        expense_date TEXT,
        merchant_name TEXT,
        expense_category TEXT,
        amount REAL
    );
    """)

    conn.commit()
    conn.close()
