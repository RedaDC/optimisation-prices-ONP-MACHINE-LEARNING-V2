from fpdf import FPDF
from datetime import datetime
import pandas as pd

class ONP_PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'OFFICE NATIONAL DES PECHES', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_reduction_pdf(df_reduction, stats):
    pdf = ONP_PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'RAPPORT ANALYSE COMPARATIVE CA 2024-2025', 0, 1, 'C')
    pdf.ln(10)
    
    # Date
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'R')
    pdf.ln(5)
    
    # Summary Table (KPIs)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'RESUME GLOBAL', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    col_width = 60
    pdf.cell(col_width, 10, 'Indicateur', 1)
    pdf.cell(col_width, 10, 'Valeur', 1)
    pdf.ln()
    
    pdf.cell(col_width, 10, 'CA Total 2024', 1)
    pdf.cell(col_width, 10, f"{stats['ca_2024']/1000:.1f} MDH", 1)
    pdf.ln()
    
    pdf.cell(col_width, 10, 'CA Total 2025', 1)
    pdf.cell(col_width, 10, f"{stats['ca_2025']/1000:.1f} MDH", 1)
    pdf.ln()
    
    pdf.cell(col_width, 10, 'Variation', 1)
    pdf.cell(col_width, 10, f"{stats['diff']/1000:+.1f} MDH ({stats['diff_pct']:+.1f}%)", 1)
    pdf.ln(15)
    
    # Top 10 Reductions by Port
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'TOP 10 VARIATIONS PAR PORT (KDh)', 0, 1, 'L')
    pdf.set_font('Arial', 'B', 10)
    
    df_port = df_reduction.groupby('port')[['ca_2024_kdh', 'ca_2025_kdh', 'ca_diff_kdh']].sum().sort_values('ca_diff_kdh').head(10)
    
    # Table Header
    w_port = 70
    w_val = 40
    pdf.cell(w_port, 10, 'Port', 1)
    pdf.cell(w_val, 10, 'CA 2024', 1)
    pdf.cell(w_val, 10, 'CA 2025', 1)
    pdf.cell(w_val, 10, 'Variation', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    for port, row in df_port.iterrows():
        pdf.cell(w_port, 10, str(port), 1)
        pdf.cell(w_val, 10, f"{row['ca_2024_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.cell(w_val, 10, f"{row['ca_2025_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.cell(w_val, 10, f"{row['ca_diff_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.ln()
        
    pdf.ln(10)
    
    # Variation by Delegation
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'VARIATION PAR DELEGATION (KDh)', 0, 1, 'L')
    pdf.set_font('Arial', 'B', 10)
    
    df_del = df_reduction.groupby('delegation')[['ca_2024_kdh', 'ca_2025_kdh', 'ca_diff_kdh']].sum().sort_values('ca_diff_kdh')
    
    pdf.cell(w_port, 10, 'Delegation', 1)
    pdf.cell(w_val, 10, 'CA 2024', 1)
    pdf.cell(w_val, 10, 'CA 2025', 1)
    pdf.cell(w_val, 10, 'Variation', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    for dele, row in df_del.iterrows():
        pdf.cell(w_port, 10, str(dele), 1)
        pdf.cell(w_val, 10, f"{row['ca_2024_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.cell(w_val, 10, f"{row['ca_2025_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.cell(w_val, 10, f"{row['ca_diff_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.ln()

    pdf.ln(10)
    
    # Variation by Species (Top 15)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'TOP 15 VARIATIONS PAR ESPECE (KDh)', 0, 1, 'L')
    pdf.set_font('Arial', 'B', 10)
    
    df_esp = df_reduction.groupby('espece_categorie')[['ca_2024_kdh', 'ca_2025_kdh', 'ca_diff_kdh']].sum().sort_values('ca_diff_kdh').head(15)
    
    pdf.cell(w_port, 10, 'Espece / Categorie', 1)
    pdf.cell(w_val, 10, 'CA 2024', 1)
    pdf.cell(w_val, 10, 'CA 2025', 1)
    pdf.cell(w_val, 10, 'Variation', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    for esp, row in df_esp.iterrows():
        # Truncate species name if too long
        esp_display = str(esp)[:35] + '..' if len(str(esp)) > 35 else str(esp)
        pdf.cell(w_port, 10, esp_display, 1)
        pdf.cell(w_val, 10, f"{row['ca_2024_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.cell(w_val, 10, f"{row['ca_2025_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.cell(w_val, 10, f"{row['ca_diff_kdh']:,.0f}".replace(',', ' '), 1)
        pdf.ln()
        
    return pdf.output()
