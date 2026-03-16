import pandas as pd
excel_file = 'New Report(2024-2025) -DR (3).xlsx'
try:
    xl = pd.ExcelFile(excel_file)
    for sheet in xl.sheet_names:
        print(f"--- Sheet: {sheet} ---")
        df = pd.read_excel(excel_file, sheet_name=sheet, nrows=20)
        print("Columns:", df.columns.tolist()[:10])
        print(df.iloc[:5, :5].to_string())
except Exception as e:
    print(e)
