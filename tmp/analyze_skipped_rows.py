import pandas as pd

f = 'Extraction 2024-2025-traitée avec variation.xlsx'
df = pd.read_excel(f, sheet_name='extraction retraitée VF', header=0)

# Identify Vol/CA columns for 2024
col_vol_2024 = [c for c in df.columns if 'Volume' in str(c) and '2024' in str(c)][0]
col_ca_2024 = [c for c in df.columns if 'CA' in str(c) and '2024' in str(c)][0]
col_port = 'Entité'
col_species = 'Espèce'

# Total sum for baseline
total_ca_2024 = df[col_ca_2024].fillna(0).sum()
print(f"Total CA 2024 in sheet: {total_ca_2024:,.2f} KDh")

# Check rows I would skip
# Filter 1: Port is empty or 'total'
skip_mask_port = df[col_port].astype(str).str.contains('total', case=False, na=True)
skipped_ca_port = df[skip_mask_port][col_ca_2024].fillna(0).sum()
print(f"CA skipped due to Port (Total/NaN): {skipped_ca_port:,.2f} KDh")

# Filter 2: Species is empty or 'total' (and NOT MG)
skip_mask_species = (df[col_species].astype(str).str.contains('total', case=False, na=True)) & (~df[col_port].astype(str).str.contains('MG ', case=False, na=False))
skipped_ca_species = df[skip_mask_species][col_ca_2024].fillna(0).sum()
print(f"CA skipped due to Species (Total/NaN) and NOT MG: {skipped_ca_species:,.2f} KDh")

# Show some skipped rows
print("\nSome skipped rows (Species Total/NaN):")
print(df[skip_mask_species][[col_port, col_species, col_ca_2024]].dropna(subset=[col_ca_2024]).head(20).to_string())

# Total captured with current logic (estimate)
# p_ok = not (null or total)
# s_ok = not (null or total) OR mg
mask_p_ok = ~df[col_port].astype(str).str.contains('total', case=False, na=True)
mask_s_ok = (~df[col_species].astype(str).str.contains('total', case=False, na=True)) | df[col_port].astype(str).str.contains('MG ', case=False, na=False)
captured_mask = mask_p_ok & mask_s_ok
captured_ca_2024 = df[captured_mask][col_ca_2024].fillna(0).sum()
print(f"\nEstimated captured CA 2024: {captured_ca_2024:,.2f} KDh")
print(f"Still missing: {total_ca_2024 - captured_ca_2024:,.2f} KDh")
