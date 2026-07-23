# ============================================================
# 🔹 Fonction d'exportation Excel
# ============================================================
import pandas as pd 
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
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
    

#####################################################
# 🔹 Fonction universelle : choix PNG ou PDF
#####################################################
def telecharger_graphique(fig, nom_base, key):
    """
    Affiche un selectbox pour choisir le format (PNG ou PDF)
    puis propose le bouton de téléchargement correspondant.
    nom_base : nom du fichier sans extension
    key : identifiant unique pour Streamlit
    """

    choix = st.selectbox(
        "Choix d'enregistrement",
        ["PNG", "PDF"],
        key=f"{key}_select"
    )

    buffer = BytesIO()

    if choix == "PNG":
        fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        buffer.seek(0)

        st.download_button(
            label="📥 Télécharger en PNG",
            data=buffer,
            file_name=f"{nom_base}.png",
            mime="image/png",
            key=f"{key}_png"
        )

    else:  # PDF
        with PdfPages(buffer) as pdf:
            pdf.savefig(fig, dpi=300, bbox_inches="tight")

        buffer.seek(0)

        st.download_button(
            label="📥 Télécharger en PDF",
            data=buffer,
            file_name=f"{nom_base}.pdf",
            mime="application/pdf",
            key=f"{key}_pdf"
        )
        
def charger_css(fichier_css):
    with open(fichier_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
