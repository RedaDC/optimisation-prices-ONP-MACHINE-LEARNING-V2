import pandas as pd

excel_file = "New Report(2024-2025) -DR (3).xlsx"
print(f"Searching for 467283 in {excel_file}...")

try:
    xl = pd.ExcelFile(excel_file)
    for sheet in xl.sheet_names:
        print(f"\nChecking sheet: {sheet}")
        df = pd.read_excel(excel_file, sheet_name=sheet)
        # Search for the value in the entire dataframe
        matches = df[df.apply(lambda row: row.astype(str).str.contains('467283|467 283').any(), axis=1)]
        if not matches.empty:
            print(f"Found matches in sheet '{sheet}':")
            print(matches)
        
        # Also check if the sum of any column is close to 467283
        for col in df.select_dtypes(include=['number']).columns:
            if abs(df[col].sum() - 467283) < 1000:
                print(f"Sum of column '{col}' in sheet '{sheet}' is {df[col].sum():.2f} (close to 467283)")

except Exception as e:
    print(f"Error: {e}")
