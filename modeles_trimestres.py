import streamlit as st
import os

def telecharger_modele_trimestre(trimestre):
    """
    Affiche un bouton de téléchargement du modèle correspondant au trimestre.
    Les fichiers sont stockés dans le dossier 'modeles'.
    """
    dossier_modeles = "modeles"
    modele_map = {
        "T1": "modele_T1.xlsx",
        "T2": "modele_T2.xlsx",
        "T3": "modele_T3.xlsx",
        "T4": "modele_T4.xlsx"
    }

    modele_fichier = modele_map.get(trimestre)
    chemin_fichier = os.path.join(dossier_modeles, modele_fichier)

    with st.expander("📥 Télécharger le modèle du trimestre"):
        try:
            with open(chemin_fichier, "rb") as f:
                st.download_button(
                    label=f"📄 Télécharger le modèle {trimestre}",
                    data=f.read(),
                    file_name=modele_fichier,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.error(f"❌ Le fichier modèle '{chemin_fichier}' est introuvable.")
