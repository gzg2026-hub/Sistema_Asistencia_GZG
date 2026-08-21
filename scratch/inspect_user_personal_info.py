import os
import pandas as pd

file_path = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter\Información personal_2026_08_20_09_43_12_084\Información personal_2026_08_20_09_43_12_084.xlsx"

print("File exists:", os.path.exists(file_path))
excel = pd.ExcelFile(file_path)
print("Sheet names:", excel.sheet_names)

df = pd.read_excel(file_path)
print("\nColumns:", list(df.columns))
print("Total rows:", len(df))
print("\nFirst 10 rows:")
print(df.head(10).to_string())
