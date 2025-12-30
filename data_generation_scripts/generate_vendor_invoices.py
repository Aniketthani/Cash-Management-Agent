import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

data_folder="../data/"
random.seed(42)
year=2025
START = datetime(year, 1, 1)
END = datetime(year, 12, 31)

VENDORS = [
    ("V001", "AWS India Pvt Ltd", "Cloud Services", 18),
    ("V002", "BESCOM", "Electricity", 5),
    ("V003", "ACT Fibernet", "Internet", 18),
    ("V004", "Prestige Office Rentals", "Rent", 0),
    ("V005", "Staples India", "Office Supplies", 18),
]

rows = []

for _ in range(3600):
    vendor = random.choice(VENDORS)
    inv_date = START + timedelta(days=random.randint(0, 364))
    due_date = inv_date + timedelta(days=random.choice([15, 30]))
    gross = random.randint(3000, 80000)
    tax = round(gross * vendor[3] / 100, 2)
    net = gross + tax

    rows.append([
        str(uuid.uuid4()),
        vendor[0],
        vendor[1],
        f"{vendor[0]}-{random.randint(10000,99999)}",
        inv_date.date(),
        due_date.date(),
        vendor[2],
        gross,
        tax,
        net,
        random.choice(["Paid", "Unpaid", "Late"]),
        "Bank Transfer"
    ])

df = pd.DataFrame(rows, columns=[
    "invoice_id","vendor_id","vendor_name","invoice_number",
    "invoice_date","due_date","category",
    "gross_amount","tax_amount","net_amount",
    "payment_status","expected_payment_mode"
])

df.to_csv(f"{data_folder}vendor_invoices.csv", index=False)
print("✅ Vendor invoices generated")
