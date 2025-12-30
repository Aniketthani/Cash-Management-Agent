import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

year=2025
data_folder="../data/"
CATEGORIES = [
    ("Travel","Uber"),
    ("Food","Restaurant"),
    ("Office Supplies","Staples"),
    ("Maintenance","Service Center"),
    ("Client Entertainment","Hotel")
]

rows = []

for _ in range(6500):
    cat = random.choice(CATEGORIES)
    date = datetime(year,1,1) + timedelta(days=random.randint(0,364))
    amount = random.randint(300, 8000)
    tax = round(amount * 0.05, 2)

    rows.append([
        str(uuid.uuid4()),
        date.date(),
        cat[1],
        cat[0],
        amount,
        tax,
        random.choice(["Cash","UPI","Card"]),
        None
    ])

df = pd.DataFrame(rows, columns=[
    "receipt_id","expense_date","merchant_name",
    "expense_category","amount","tax_amount",
    "payment_mode","linked_transaction_id"
])

df.to_csv(f"{data_folder}expense_receipts.csv", index=False)
print("✅ Expense receipts generated")
