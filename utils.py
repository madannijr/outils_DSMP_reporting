# ============================================================
# 🔹 Fonction d'exportation Excel
# ============================================================
import pandas as pd
from io import BytesIO
import xlsxwriter 
import streamlit as st

def telecharger_excel(df, nom_fichier="Analyse_Semestrielle_ACPACH.xlsx", nom_feuille="Analyse_Semestrielle"):
    """
    Génère un bouton Streamlit pour télécharger un DataFrame au format Excel.
    """
    # Création du buffer mémoire
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name=nom_feuille)
    writer.close()
    excel_data = output.getvalue()

    # Bouton de téléchargement
    st.download_button(
        label="⬇️ Télécharger le tableau semestriel",
        data=excel_data,
        file_name=nom_fichier,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
