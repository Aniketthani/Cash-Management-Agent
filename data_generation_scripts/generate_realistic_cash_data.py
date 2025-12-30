import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

random.seed(42)
year=2025
data_folder="../data/"
START = datetime(year, 1, 1)
END = datetime(year, 12, 31)
DATES = pd.date_range(START, END)

ACCOUNT_NO = "HDFC-CA-29833423"
CURRENCY = "INR"

CLIENTS = [
    "Alpha Corp", "Beta Solutions", "Gamma Technologies",
    "Delta Systems", "Epsilon Infotech"
]

VENDORS = [
    "AWS India Pvt Ltd", "BESCOM", "ACT Fibernet",
    "Prestige Office Rentals", "Staples India",
    "Uber India", "Swiggy", "Zomato"
]

balance = 1_200_000
rows = []

def add_txn(date, ttype, amt, party, narration, category, mode):
    global balance
    if ttype == "DEBIT":
        balance -= amt
    else:
        balance += amt

    rows.append([
        str(uuid.uuid4()),
        ACCOUNT_NO,
        date.date(),
        date.date(),
        ttype,
        amt,
        balance,
        CURRENCY,
        party,
        narration,
        category,
        mode
    ])

for d in DATES:

    # -------------------------------
    # Fixed transactions
    # -------------------------------
    if d.day == 1:   # Rent
        add_txn(
            d, "DEBIT", 40000,
            "Prestige Office Rentals",
            "ACH-OFFICE-RENT",
            "Rent",
            "ACH"
        )

    if d.day == 5:   # Salary
        add_txn(
            d, "DEBIT", 180000,
            "ABC Tech Payroll",
            f"NEFT-SALARY-{d.strftime('%b%y')}",
            "Salary",
            "NEFT"
        )

    # -------------------------------
    # Client collections (2–6 per day)
    # -------------------------------
    for _ in range(random.randint(2, 6)):
        amt = random.randint(25_000, 2_50_000)
        add_txn(
            d, "CREDIT", amt,
            random.choice(CLIENTS),
            f"IMPS-CLIENT-{random.randint(1000,9999)}",
            "Client Collection",
            "IMPS"
        )

    # -------------------------------
    # Vendor payments (1–4 per day)
    # -------------------------------
    for _ in range(random.randint(1, 4)):
        amt = random.randint(3_000, 80_000)
        add_txn(
            d, "DEBIT", amt,
            random.choice(VENDORS),
            f"NEFT-VENDOR-{random.randint(1000,9999)}",
            "Vendor Payment",
            "NEFT"
        )

    # -------------------------------
    # Operating expenses (3–10 per day)
    # -------------------------------
    for _ in range(random.randint(3, 10)):
        amt = random.randint(200, 7_000)
        add_txn(
            d, "DEBIT", amt,
            random.choice(VENDORS),
            f"UPI-EXP-{random.randint(10000,99999)}",
            "Operating Expense",
            "UPI"
        )

bank_df = pd.DataFrame(rows, columns=[
    "transaction_id",
    "account_number",
    "transaction_date",
    "value_date",
    "transaction_type",
    "amount",
    "balance_after",
    "currency",
    "counterparty_name",
    "narration",
    "category",
    "payment_mode"
])

bank_df.to_csv(f"{data_folder}bank_statements.csv", index=False)

print(f"✅ Generated {len(bank_df)} realistic bank transactions for 2025")
