import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

random.seed(42)
year=2025
data_folder="../data/"
CLIENTS = [
    ("C001", "Alpha Corp"),
    ("C002", "Beta Solutions"),
    ("C003", "Gamma Technologies"),
    ("C004", "Delta Systems"),
    ("C005", "Epsilon Infotech")
]

rows = []

for _ in range(3800):
    client = random.choice(CLIENTS)
    inv_date = datetime(year, 1, 1) + timedelta(days=random.randint(0, 364))
    due_date = inv_date + timedelta(days=random.choice([30, 45]))
    gross = random.randint(50000, 300000)
    tax = round(gross * 18 / 100, 2)
    net = gross + tax

    rows.append([
        str(uuid.uuid4()),
        client[0],
        client[1],
        f"{client[0]}-INV-{random.randint(10000,99999)}",
        inv_date.date(),
        due_date.date(),
        "IT Consulting",
        gross,
        tax,
        net,
        random.choice(["Collected", "Pending", "Overdue"])
    ])

df = pd.DataFrame(rows, columns=[
    "invoice_id","client_id","client_name","invoice_number",
    "invoice_date","due_date","service_type",
    "gross_amount","tax_amount","net_amount",
    "collection_status"
])

df.to_csv(f"{data_folder}client_invoices.csv", index=False)
print("✅ Client invoices generated")
