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
# 🔹 Fonction Semestrielle : S1 = T1 + T2
# ============================================================
def analyse_semestrielle(fichier_T1, fichier_T2):

    st.header("Analyse Semestrielle ACP/ACH")

    # Choix de l’instrument
    instrument = st.selectbox(
        "Choisir un instrument :",
        ["virements", "chèques", "chèques représenté", "lettre de change"]
    )

    # Lecture des fichiers T1 et T2
    df_T1 = pd.read_excel(fichier_T1, sheet_name=instrument)
    df_T2 = pd.read_excel(fichier_T2, sheet_name=instrument)

    # Nettoyage des colonnes
    for df in [df_T1, df_T2]:
        df.columns = (
            df.columns.astype(str)
            .str.replace("\n", "")
            .str.replace("\t", "")
            .str.replace("\xa0", "")
            .str.replace("\u202f", "")
            .str.strip()
        )

    # Nettoyage général
    df_T1 = nettoyer(df_T1)
    df_T2 = nettoyer(df_T2)

    # Fusion T1 + T2 sur la colonne Banque
    df = df_T1.merge(df_T2, on="Banque", how="outer", suffixes=("_T1", "_T2"))

    # Détection automatique des colonnes Nombre/Montant
    colonnes_nombre = [c for c in df.columns if "Nombre" in c]
    colonnes_montant = [c for c in df.columns if "Montant" in c]

    # Détection des années
    annees = sorted({
        extraire_annee(c)
        for c in colonnes_nombre + colonnes_montant
        if extraire_annee(c)
    })

    if len(annees) < 2:
        st.error("Impossible de détecter les années.")
        st.write(df.columns.tolist())
        return

    annee1, annee2 = annees[-2], annees[-1]

    # Colonnes T1 et T2
    col_T1_nb_annee1 = [c for c in colonnes_nombre if f"T1_{annee1}" in c][0]
    col_T2_nb_annee1 = [c for c in colonnes_nombre if f"T2_{annee1}" in c][0]

    col_T1_nb_annee2 = [c for c in colonnes_nombre if f"T1_{annee2}" in c][0]
    col_T2_nb_annee2 = [c for c in colonnes_nombre if f"T2_{annee2}" in c][0]

    col_T1_mt_annee1 = [c for c in colonnes_montant if f"T1_{annee1}" in c][0]
    col_T2_mt_annee1 = [c for c in colonnes_montant if f"T2_{annee1}" in c][0]

    col_T1_mt_annee2 = [c for c in colonnes_montant if f"T1_{annee2}" in c][0]
    col_T2_mt_annee2 = [c for c in colonnes_montant if f"T2_{annee2}" in c][0]

    # Conversion numérique
    T1_nb_annee1 = convertir(df, col_T1_nb_annee1)
    T2_nb_annee1 = convertir(df, col_T2_nb_annee1)
    T1_nb_annee2 = convertir(df, col_T1_nb_annee2)
    T2_nb_annee2 = convertir(df, col_T2_nb_annee2)

    T1_mt_annee1 = convertir(df, col_T1_mt_annee1)
    T2_mt_annee1 = convertir(df, col_T2_mt_annee1)
    T1_mt_annee2 = convertir(df, col_T1_mt_annee2)
    T2_mt_annee2 = convertir(df, col_T2_mt_annee2)

    # Calcul S1 = T1 + T2
    S1_nb_annee1 = T1_nb_annee1 + T2_nb_annee1
    S1_nb_annee2 = T1_nb_annee2 + T2_nb_annee2

    S1_mt_annee1 = T1_mt_annee1 + T2_mt_annee1
    S1_mt_annee2 = T1_mt_annee2 + T2_mt_annee2

    # Variation %
    var_nb = ((S1_nb_annee2 - S1_nb_annee1) / S1_nb_annee1.replace(0, np.nan)) * 100
    var_mt = ((S1_mt_annee2 - S1_mt_annee1) / S1_mt_annee1.replace(0, np.nan)) * 100

    var_nb = var_nb.fillna(0).round(2)
    var_mt = var_mt.fillna(0).round(2)

    # Tableau final
    df_aff = pd.DataFrame({
        "Banque": df["Banque"],
        f"Nombre_S1_{annee1}": S1_nb_annee1,
        f"Montant_S1_{annee1}": S1_mt_annee1,
        f"Nombre_S1_{annee2}": S1_nb_annee2,
        f"Montant_S1_{annee2}": S1_mt_annee2,
        "Variation Nombre (%)": var_nb.map(lambda x: f"{x:.2f}%".replace(".", ",")),
        "Variation Montant (%)": var_mt.map(lambda x: f"{x:.2f}%".replace(".", ","))
    })

    # Totaux
    total_nb1 = S1_nb_annee1.sum()
    total_nb2 = S1_nb_annee2.sum()
    total_mt1 = S1_mt_annee1.sum()
    total_mt2 = S1_mt_annee2.sum()

    total_var_nb = ((total_nb2 - total_nb1) / total_nb1 * 100) if total_nb1 != 0 else 0
    total_var_mt = ((total_mt2 - total_mt1) / total_mt1 * 100) if total_mt1 != 0 else 0

    ligne_total = pd.DataFrame([{
        "Banque": "TOTAUX",
        f"Nombre_S1_{annee1}": total_nb1,
        f"Montant_S1_{annee1}": total_mt1,
        f"Nombre_S1_{annee2}": total_nb2,
        f"Montant_S1_{annee2}": total_mt2,
        "Variation Nombre (%)": f"{total_var_nb:.2f}%".replace(".", ","),
        "Variation Montant (%)": f"{total_var_mt:.2f}%".replace(".", ",")
    }])

    df_aff = pd.concat([df_aff, ligne_total], ignore_index=True)

    # Affichage tableau
    st.subheader(f"📊 Analyse Semestre 1 — {annee1} vs {annee2} — {instrument.capitalize()}")
    st.dataframe(format_dataframe(df_aff))

    # Graphiques
    df_graph = df_aff[df_aff["Banque"] != "TOTAUX"]

    # Graphique Nombre
    fig1, ax1 = plt.subplots(figsize=(14, 5))
    x = range(len(df_graph))
    width = 0.35

    ax1.bar([i - width/2 for i in x], df_graph[f"Nombre_S1_{annee1}"], width, label=str(annee1))
    ax1.bar([i + width/2 for i in x], df_graph[f"Nombre_S1_{annee2}"], width, label=str(annee2))

    ax1.set_title(f"Évolution des nombres — S1 ({annee1} → {annee2}) — {instrument.capitalize()}")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig1)

    # Graphique Montant
    fig2, ax2 = plt.subplots(figsize=(14, 5))

    ax2.bar([i - width/2 for i in x], df_graph[f"Montant_S1_{annee1}"], width, label=str(annee1))
    ax2.bar([i + width/2 for i in x], df_graph[f"Montant_S1_{annee2}"], width, label=str(annee2))

    ax2.set_title(f"Évolution des montants — S1 ({annee1} → {annee2}) — {instrument.capitalize()}")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")
    ax2.legend()
    ax2.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig2)

    # ============================================================
    # 🔹 COMPARAISON TRIMESTRIELLE — T1 vs T2 (année la plus récente)
    # ============================================================
    st.subheader(f"📈 Analyse trimestrielle — T1 vs T2 ({annee2})")

    fig, ax1 = plt.subplots(figsize=(16, 6))
    x = np.arange(len(df_graph))

    # --- Axe Y1 : VOLUMES ---
    ax1.set_ylabel("Volumes (Nombre)", color="tab:blue")
    ax1.plot(x, T1_nb_annee2, marker="o", color="tab:blue")
    ax1.plot(x, T2_nb_annee2, marker="o", linestyle="--", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    # --- Axe Y2 : MONTANTS ---
    ax2 = ax1.twinx()
    ax2.set_ylabel("Montants (GNF)", color="tab:orange")
    ax2.plot(x, T1_mt_annee2, marker="s", color="tab:orange")
    ax2.plot(x, T2_mt_annee2, marker="s", linestyle="--", color="tab:orange")
    ax2.tick_params(axis="y", labelcolor="tab:orange")

    # --- Axe X ---
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")

    # --- Légende simplifiée ---
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', linestyle='-', linewidth=2, label='Volumes (T1/T2)'),
        Line2D([0], [0], marker='s', linestyle='-', linewidth=2, label='Montants (T1/T2)')
    ]
    ax1.legend(handles=legend_elements, loc="upper left")

    # --- Titre ---
    plt.title(f"Comparaison T1 vs T2 — Volumes & Montants ({annee2}) — {instrument.capitalize()}")

    ax1.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

