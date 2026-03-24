
import streamlit as st
import sys
import traceback

# Configuration must be the absolute first streamlit call
try:
    st.set_page_config(
        page_title="ONP - Optimisation des Prix",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    pass

try:
    # Attempt to import the main application
    from app_premium import main
    if __name__ == "__main__":
        main()
except Exception as e:
    st.error("🚀 Une erreur s'est produite lors du démarrage de l'application ONP.")
    st.error(f"Détails de l'erreur : {str(e)}")
    st.markdown("### Traceback Complet")
    st.code(traceback.format_exc())
    
    # Debug info
    st.write("---")
    st.write("📁 Fichiers présents :", os.listdir('.') if 'os' in globals() else "Import 'os' failed")
    import os
    st.write("📁 Liste des fichiers :", os.listdir('.'))
    if os.path.exists('Extraction_2024_2025_traitee.xlsx'):
        st.write("✅ Fichier Excel trouvé.")
    else:
        st.write("❌ Fichier Excel MANQUANT.")
