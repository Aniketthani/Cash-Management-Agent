import pandas as pd
from datetime import datetime
import uuid

year=2025
data_folder="../data/"
EMPLOYEES = [
    ("E001","Rahul Sharma","Engineer","Technology",30000),
    ("E002","Neha Verma","Engineer","Technology",35000),
    ("E003","Amit Singh","Sales Exec","Sales",25000),
    ("E004","Pooja Mehta","HR Manager","HR",20000),
    ("E005","Suman Patel","Admin","Admin",20000),
]

rows = []

for month in range(1,13):
    for emp in EMPLOYEES:
        tax = round(emp[4] * 0.1, 2)
        net = emp[4] - tax
        rows.append([
            str(uuid.uuid4()),
            emp[0], emp[1], emp[2], emp[3],
            f"{year}-{month:02d}",
            emp[4], tax, net,
            "Paid",
            f"SAL-{year}-{month:02d}"
        ])

df = pd.DataFrame(rows, columns=[
    "payroll_id","employee_id","employee_name",
    "designation","department","pay_period",
    "gross_salary","tax_deduction","net_salary",
    "payment_status","payment_reference"
])

df.to_csv(f"{data_folder}payroll.csv", index=False)
print("✅ Payroll data generated")
