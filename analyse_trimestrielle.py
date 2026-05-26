import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import re
from fonctions_utils import format_dataframe


# ============================================================
# 🔹 Conversion propre des montants
# ============================================================
def convertir(df, col):
    return (
        df[col]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("\xa0", "", regex=False)
        .str.replace("\u202f", "", regex=False)
        .apply(lambda x: pd.to_numeric(x, errors="coerce"))
        .fillna(0)
    )


# ============================================================
# 🔹 Extraction automatique des années
# ============================================================
def extraire_annee(col):
    match = re.search(r"(20\d{2})", str(col))
    return int(match.group(1)) if match else None


# ============================================================
# 🔹 Détection automatique du trimestre (T1, T2, T3, T4)
# ============================================================
def detecter_trimestre(df):
    colonnes = " ".join(df.columns).upper()

    if "T1" in colonnes:
        return "T1"
    if "T2" in colonnes:
        return "T2"
    if "T3" in colonnes:
        return "T3"
    if "T4" in colonnes:
        return "T4"

    return None


# ============================================================
# 🔹 Nettoyage DataFrame
# ============================================================
def nettoyer(df):
    df = df.loc[:, ~df.columns.str.contains("Unnamed", case=False)]
    df = df[df["Banque"].notna()]
    df["Banque"] = df["Banque"].astype(str).str.strip()
    df = df[df["Banque"] != ""]
    df = df[~df["Banque"].str.contains("TOTAL|TOTAUX", case=False, na=False)]
    return df


# ============================================================
# 🔹 Analyse Trimestrielle Dynamique
# ============================================================
def analyse_trimestrielle(uploaded_file, trimestre_attendu):

    st.header(f"Analyse Trimestrielle ACP/ACH — {trimestre_attendu}")

    instrument = st.selectbox(
        "Choisir un instrument :",
        ["virements", "chèques", "chèques représenté", "lettre de change"]
    )

    # Lecture fichier
    df = pd.read_excel(uploaded_file, sheet_name=instrument)

    # Nettoyage noms colonnes
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", "")
        .str.replace("\t", "")
        .str.replace("\xa0", "")
        .str.replace("\u202f", "")
        .str.strip()
    )

    # 🔥 Détection automatique du trimestre réel dans le fichier
    trimestre_detecte = detecter_trimestre(df)

    if trimestre_detecte is None:
        st.error("❌ Impossible de détecter le trimestre dans le fichier.")
        st.write(df.columns.tolist())
        return

    # 🔥 Vérification stricte
    if trimestre_detecte != trimestre_attendu:
        st.error(
            f"❌ Le fichier chargé appartient à **{trimestre_detecte}**, "
            f"mais vous êtes dans le menu **{trimestre_attendu}**."
        )
        st.stop()

    # Nettoyage général
    df = nettoyer(df)

    # Colonnes détectées
    colonnes_nombre = [c for c in df.columns if "Nombre" in c and trimestre_detecte in c]
    colonnes_montant = [c for c in df.columns if "Montant" in c and trimestre_detecte in c]

    # 🔥 Détection automatique des années
    annees = sorted({
        extraire_annee(c)
        for c in colonnes_nombre + colonnes_montant
        if extraire_annee(c)
    })

    if len(annees) < 2:
        st.error("Impossible de détecter les années.")
        st.write(df.columns.tolist())
        return

    # Les deux dernières années trouvées
    annee1, annee2 = annees[-2], annees[-1]

    # Colonnes correspondantes
    col_nb_annee1 = [c for c in colonnes_nombre if str(annee1) in c][0]
    col_nb_annee2 = [c for c in colonnes_nombre if str(annee2) in c][0]

    col_mt_annee1 = [c for c in colonnes_montant if str(annee1) in c][0]
    col_mt_annee2 = [c for c in colonnes_montant if str(annee2) in c][0]

    # Conversion numérique
    nb1 = convertir(df, col_nb_annee1)
    nb2 = convertir(df, col_nb_annee2)

    mt1 = convertir(df, col_mt_annee1)
    mt2 = convertir(df, col_mt_annee2)

    # Variations %
    variation_nombre = ((nb2 - nb1) / nb1.replace(0, np.nan)) * 100
    variation_montant = ((mt2 - mt1) / mt1.replace(0, np.nan)) * 100
    variation_nombre = variation_nombre.fillna(0).round(2)
    variation_montant = variation_montant.fillna(0).round(2)

    # Tableau final
    df_aff = pd.DataFrame({
        "Banque": df["Banque"],

        f"Nombre_{trimestre_detecte}_{annee1}": nb1,
        f"Montant_{trimestre_detecte}_{annee1}": mt1,

        f"Nombre_{trimestre_detecte}_{annee2}": nb2,
        f"Montant_{trimestre_detecte}_{annee2}": mt2,

        "Variation Nombre (%)": variation_nombre.map(lambda x: f"{x:.2f}%".replace(".", ",")),
        "Variation Montant (%)": variation_montant.map(lambda x: f"{x:.2f}%".replace(".", ","))
    })

    # Totaux
    total_nb1 = nb1.sum()
    total_nb2 = nb2.sum()
    total_mt1 = mt1.sum()
    total_mt2 = mt2.sum()

    total_var_nb = ((total_nb2 - total_nb1) / total_nb1 * 100) if total_nb1 != 0 else 0
    total_var_mt = ((total_mt2 - total_mt1) / total_mt1 * 100) if total_mt1 != 0 else 0

    ligne_total = pd.DataFrame([{
        "Banque": "TOTAUX",

        f"Nombre_{trimestre_detecte}_{annee1}": total_nb1,
        f"Montant_{trimestre_detecte}_{annee1}": total_mt1,

        f"Nombre_{trimestre_detecte}_{annee2}": total_nb2,
        f"Montant_{trimestre_detecte}_{annee2}": total_mt2,

        "Variation Nombre (%)": f"{total_var_nb:.2f}%".replace(".", ","),
        "Variation Montant (%)": f"{total_var_mt:.2f}%".replace(".", ",")
    }])

    df_aff = pd.concat([df_aff, ligne_total], ignore_index=True)

    # Affichage tableau
    st.subheader(f"📊 Analyse {trimestre_detecte} — {annee1} vs {annee2} — {instrument}")
    st.dataframe(format_dataframe(df_aff))

    # Graphique Nombre
    df_graph = df_aff[df_aff["Banque"] != "TOTAUX"]

    fig1, ax1 = plt.subplots(figsize=(14, 5))
    x = range(len(df_graph))
    width = 0.35

    ax1.bar([i - width/2 for i in x], df_graph[f"Nombre_{trimestre_detecte}_{annee1}"], width, label=str(annee1))
    ax1.bar([i + width/2 for i in x], df_graph[f"Nombre_{trimestre_detecte}_{annee2}"], width, label=str(annee2))

    ax1.set_title(f"Évolution des nombres — de {trimestre_detecte} ({annee1} → {annee2}) — {instrument.capitalize()}")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig1)

    # Graphique Montant
    fig2, ax2 = plt.subplots(figsize=(14, 5))

    ax2.bar([i - width/2 for i in x], df_graph[f"Montant_{trimestre_detecte}_{annee1}"], width, label=str(annee1))
    ax2.bar([i + width/2 for i in x], df_graph[f"Montant_{trimestre_detecte}_{annee2}"], width, label=str(annee2))

    ax2.set_title(f"Évolution des montants de {trimestre_detecte} ({annee1} → {annee2}) — {instrument.capitalize()}")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")
    ax2.legend()
    ax2.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig2)
