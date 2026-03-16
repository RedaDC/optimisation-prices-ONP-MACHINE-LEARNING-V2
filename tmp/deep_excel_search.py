import pandas as pd

excel_file = "New Report(2024-2025) -DR (3).xlsx"
xl = pd.ExcelFile(excel_file)
print(f"Sheets in {excel_file}:")
print(xl.sheet_names)

for sheet in xl.sheet_names:
    print(f"\nAnalyzing sheet: {sheet}")
    df = pd.read_excel(excel_file, sheet_name=sheet)
    # Search for anything matching 467283
    mask = df.apply(lambda x: x.astype(str).str.contains('467283|467284|467282|467 283', na=False)).any(axis=1)
    if mask.any():
        print(f"FOUND MATCH in sheet {sheet}!")
        print(df[mask])
    
    # Check if sum of any col is 467283
    for col in df.select_dtypes(include=['number']).columns:
        if abs(df[col].sum() - 467283) < 1000:
             print(f"Column '{col}' sum: {df[col].sum():.2f}")
