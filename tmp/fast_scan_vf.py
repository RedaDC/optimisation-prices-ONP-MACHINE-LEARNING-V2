import openpyxl

f = 'Extraction 2024-2025-traitée avec variation.xlsx'
wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
ws = wb['extraction retraitée VF']

print("High value rows (> 50,000 KDh in 2024):")
# Headers: Col 1(A)=dr, Col 2(B)=Entité, Col 5(E)=Espèce, Col 10(J)=CA 2024
# Wait, let's check indices. Previous run said CA 2024 is Index 9 (J)
for i, row in enumerate(ws.iter_rows(min_row=2, max_row=4500, values_only=True)):
    ca_2024 = row[9] if len(row) > 9 else 0
    if ca_2024 and isinstance(ca_2024, (int, float)) and ca_2024 > 50000:
        print(f"Row {i+2}: DR={row[0]}, Entité={row[1]}, Espèce={row[4]}, CA2024={ca_2024}")

wb.close()
