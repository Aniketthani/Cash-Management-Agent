import pandas as pd
from datetime import datetime, timedelta
import random

rows = []
year=2025
data_folder="../data/"

for day in range(365):
    date = datetime(year,1,1) + timedelta(days=day)

    rows.append([
        date.date(),
        random.choice([0,50000,100000,200000]),
        random.choice([0,40000,80000,120000]),
        random.choice(["Client Invoice","Payroll","Rent","Utility"]),
        random.choice(["High","Medium","Low"])
    ])

df = pd.DataFrame(rows, columns=[
    "forecast_date","expected_inflow","expected_outflow",
    "source","confidence_level"
])

df.to_csv(f"{data_folder}cash_forecast.csv", index=False)
print("✅ Cash forecast generated")
