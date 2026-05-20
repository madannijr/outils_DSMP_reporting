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
    colonnes = " ".join([str(c).upper() for c in df.columns])

    if "_T1_" in colonnes or "T1_" in colonnes or "_T1" in colonnes:
        return "T1"
    if "_T2_" in colonnes or "T2_" in colonnes or "_T2" in colonnes:
        return "T2"
    if "_T3_" in colonnes or "T3_" in colonnes or "_T3" in colonnes:
        return "T3"
    if "_T4_" in colonnes or "T4_" in colonnes or "_T4" in colonnes:
        return "T4"

    return None

# ============================================================
# 🔹 Nettoyage DataFrame
# ============================================================
def nettoyer(df):
    df = df.loc[:, ~df.columns.str.contains("Unnamed", case=False)]
    if "Banque" not in df.columns:
        return pd.DataFrame()  # signaler plus haut
    df = df[df["Banque"].notna()]
    df["Banque"] = df["Banque"].astype(str).str.strip()
    df = df[df["Banque"] != ""]
    df = df[~df["Banque"].str.contains("TOTAL|TOTAUX", case=False, na=False)]
    return df

# ============================================================
# 🔹 Analyse Semestrielle : S1 = T1 + T2 ou S2 = T3 + T4
# ============================================================
def analyse_semestrielle(fichier_A, fichier_B):
    """
    Cette fonction accepte deux fichiers Excel et vérifie automatiquement
    s'il s'agit d'un couple (T1,T2) ou (T3,T4). Elle refuse les paires invalides.
    """

    st.header("Analyse Semestrielle ACP/ACH")

    # Choix de l’instrument
    instrument = st.selectbox(
        "Choisir un instrument :",
        ["virements", "chèques", "chèques représenté", "lettre de change"]
    )

    # Vérifier que les feuilles existent dans les deux fichiers
    try:
        feuilles_A = pd.ExcelFile(fichier_A).sheet_names
        feuilles_B = pd.ExcelFile(fichier_B).sheet_names
    except Exception as e:
        st.error(f"Erreur lors de la lecture des fichiers : {e}")
        return

    if instrument not in feuilles_A or instrument not in feuilles_B:
        st.error(f"❌ Les fichiers fournis ne contiennent pas la feuille '{instrument}'.")
        st.write("Feuilles disponibles dans fichier A :", feuilles_A)
        st.write("Feuilles disponibles dans fichier B :", feuilles_B)
        return

    # Lecture des feuilles choisies
    try:
        df_A = pd.read_excel(fichier_A, sheet_name=instrument)
        df_B = pd.read_excel(fichier_B, sheet_name=instrument)
    except Exception as e:
        st.error(f"Erreur lors de la lecture des feuilles '{instrument}' : {e}")
        return

    # Nettoyage des noms de colonnes (avant détection pour être sûr)
    for df in [df_A, df_B]:
        df.columns = (
            df.columns.astype(str)
            .str.replace("\n", "")
            .str.replace("\t", "")
            .str.replace("\xa0", "")
            .str.replace("\u202f", "")
            .str.strip()
        )

    # Détection des trimestres réels dans chaque fichier
    tri_A = detecter_trimestre(df_A)
    tri_B = detecter_trimestre(df_B)

    # Vérifier que la paire est valide : soit {T1,T2} soit {T3,T4}
    paire = {tri_A, tri_B}
    if paire == {"T1", "T2"}:
        semestre_label = "S1"
        tA, tB = ("T1", "T2")
    elif paire == {"T3", "T4"}:
        semestre_label = "S2"
        tA, tB = ("T3", "T4")
    else:
        st.error(
            "❌ Les fichiers fournis ne forment pas une paire valide pour un semestre.\n"
            "Attendu : (T1 + T2) pour S1 ou (T3 + T4) pour S2.\n"
            f"Trimestre détecté fichier A : {tri_A}\n"
            f"Trimestre détecté fichier B : {tri_B}"
        )
        return

    # Nettoyage général
    df_A = nettoyer(df_A)
    df_B = nettoyer(df_B)

    if df_A.empty or df_B.empty:
        st.error("❌ Les fichiers doivent contenir la colonne 'Banque' et des lignes valides.")
        return

    # Fusion sur la colonne Banque
    df = df_A.merge(df_B, on="Banque", how="outer", suffixes=(f"_{tA}", f"_{tB}"))

    # Détection automatique des colonnes Nombre/Montant
    colonnes_nombre = [c for c in df.columns if "Nombre" in c]
    colonnes_montant = [c for c in df.columns if "Montant" in c]

    if not colonnes_nombre or not colonnes_montant:
        st.error("❌ Impossible de trouver les colonnes 'Nombre' ou 'Montant' dans la fusion.")
        st.write("Colonnes disponibles :", df.columns.tolist())
        return

    # Détection des années présentes dans les colonnes
    annees = sorted({
        extraire_annee(c)
        for c in colonnes_nombre + colonnes_montant
        if extraire_annee(c)
    })

    if len(annees) < 2:
        st.error("❌ Impossible de détecter au moins deux années dans les colonnes.")
        st.write(df.columns.tolist())
        return

    annee1, annee2 = annees[-2], annees[-1]

    # Construire les noms de colonnes attendus dynamiquement selon tA/tB
    try:
        col_A_nb_annee1 = [c for c in colonnes_nombre if f"{tA}_{annee1}" in c][0]
        col_B_nb_annee1 = [c for c in colonnes_nombre if f"{tB}_{annee1}" in c][0]

        col_A_nb_annee2 = [c for c in colonnes_nombre if f"{tA}_{annee2}" in c][0]
        col_B_nb_annee2 = [c for c in colonnes_nombre if f"{tB}_{annee2}" in c][0]

        col_A_mt_annee1 = [c for c in colonnes_montant if f"{tA}_{annee1}" in c][0]
        col_B_mt_annee1 = [c for c in colonnes_montant if f"{tB}_{annee1}" in c][0]

        col_A_mt_annee2 = [c for c in colonnes_montant if f"{tA}_{annee2}" in c][0]
        col_B_mt_annee2 = [c for c in colonnes_montant if f"{tB}_{annee2}" in c][0]
    except IndexError:
        st.error(
            "❌ Les colonnes attendues pour les trimestres/années n'ont pas été trouvées.\n"
            "Vérifiez que les colonnes contiennent les mentions T1_/T2_/T3_/T4_ suivies de l'année."
        )
        st.write("Colonnes détectées :", df.columns.tolist())
        return

    # Conversion numérique
    A_nb_annee1 = convertir(df, col_A_nb_annee1)
    B_nb_annee1 = convertir(df, col_B_nb_annee1)
    A_nb_annee2 = convertir(df, col_A_nb_annee2)
    B_nb_annee2 = convertir(df, col_B_nb_annee2)

    A_mt_annee1 = convertir(df, col_A_mt_annee1)
    B_mt_annee1 = convertir(df, col_B_mt_annee1)
    A_mt_annee2 = convertir(df, col_A_mt_annee2)
    B_mt_annee2 = convertir(df, col_B_mt_annee2)

    # Calcul Semestre = somme des deux trimestres
    S_nb_annee1 = A_nb_annee1 + B_nb_annee1
    S_nb_annee2 = A_nb_annee2 + B_nb_annee2

    S_mt_annee1 = A_mt_annee1 + B_mt_annee1
    S_mt_annee2 = A_mt_annee2 + B_mt_annee2

    # Variation %
    var_nb = ((S_nb_annee2 - S_nb_annee1) / S_nb_annee1.replace(0, np.nan)) * 100
    var_mt = ((S_mt_annee2 - S_mt_annee1) / S_mt_annee1.replace(0, np.nan)) * 100

    var_nb = var_nb.fillna(0).round(2)
    var_mt = var_mt.fillna(0).round(2)

    # Tableau final
    df_aff = pd.DataFrame({
        "Banque": df["Banque"],
        f"Nombre_{semestre_label}_{annee1}": S_nb_annee1,
        f"Montant_{semestre_label}_{annee1}": S_mt_annee1,
        f"Nombre_{semestre_label}_{annee2}": S_nb_annee2,
        f"Montant_{semestre_label}_{annee2}": S_mt_annee2,
        "Variation Nombre (%)": var_nb.map(lambda x: f"{x:.2f}%".replace(".", ",")),
        "Variation Montant (%)": var_mt.map(lambda x: f"{x:.2f}%".replace(".", ","))
    })

    # Totaux
    total_nb1 = S_nb_annee1.sum()
    total_nb2 = S_nb_annee2.sum()
    total_mt1 = S_mt_annee1.sum()
    total_mt2 = S_mt_annee2.sum()

    total_var_nb = ((total_nb2 - total_nb1) / total_nb1 * 100) if total_nb1 != 0 else 0
    total_var_mt = ((total_mt2 - total_mt1) / total_mt1 * 100) if total_mt1 != 0 else 0

    ligne_total = pd.DataFrame([{
        "Banque": "TOTAUX",
        f"Nombre_{semestre_label}_{annee1}": total_nb1,
        f"Montant_{semestre_label}_{annee1}": total_mt1,
        f"Nombre_{semestre_label}_{annee2}": total_nb2,
        f"Montant_{semestre_label}_{annee2}": total_mt2,
        "Variation Nombre (%)": f"{total_var_nb:.2f}%".replace(".", ","),
        "Variation Montant (%)": f"{total_var_mt:.2f}%".replace(".", ",")
    }])

    df_aff = pd.concat([df_aff, ligne_total], ignore_index=True)

    # ====== VISUEL 1 : TABLEAU ======
    st.subheader(f"📊 Analyse {semestre_label} — {annee1} vs {annee2} — {instrument.capitalize()}")
    st.dataframe(format_dataframe(df_aff))

    df_graph = df_aff[df_aff["Banque"] != "TOTAUX"]

    # ====== VISUEL 2 : BARRES NOMBRE ======
    fig1, ax1 = plt.subplots(figsize=(14, 5))
    x = range(len(df_graph))
    width = 0.35

    ax1.bar([i - width/2 for i in x], df_graph[f"Nombre_{semestre_label}_{annee1}"], width, label=str(annee1))
    ax1.bar([i + width/2 for i in x], df_graph[f"Nombre_{semestre_label}_{annee2}"], width, label=str(annee2))

    ax1.set_title(f"Évolution des nombres — {semestre_label} ({annee1} → {annee2}) — {instrument.capitalize()}")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig1)

    # ====== VISUEL 3 : BARRES MONTANT ======
    fig2, ax2 = plt.subplots(figsize=(14, 5))

    ax2.bar([i - width/2 for i in x], df_graph[f"Montant_{semestre_label}_{annee1}"], width, label=str(annee1))
    ax2.bar([i + width/2 for i in x], df_graph[f"Montant_{semestre_label}_{annee2}"], width, label=str(annee2))

    ax2.set_title(f"Évolution des montants — {semestre_label} ({annee1} → {annee2}) — {instrument.capitalize()}")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")
    ax2.legend()
    ax2.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig2)

    # ============================================================
    # 🔹 VISUEL 4 : COMPARAISON TRIMESTRIELLE
    # ============================================================
    st.subheader(f"📈 Comparaison {tA} vs {tB} — Volumes & Montants ({annee2})")

    fig, ax1 = plt.subplots(figsize=(16, 6))
    x = np.arange(len(df_graph))

    # --- AXE Y1 : VOLUMES ---
    ax1.set_ylabel("Volumes (Nombre)", color="tab:blue")
    ax1.plot(x, A_nb_annee2, marker="o", linestyle="-",  linewidth=2, color="tab:blue")
    ax1.plot(x, B_nb_annee2, marker="o", linestyle="--", linewidth=2, color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    # --- AXE Y2 : MONTANTS ---
    ax2 = ax1.twinx()
    ax2.set_ylabel("Montants (GNF)", color="tab:orange")
    ax2.plot(x, A_mt_annee2, marker="s", linestyle="-",  linewidth=2, color="tab:orange")
    ax2.plot(x, B_mt_annee2, marker="s", linestyle="--", linewidth=2, color="tab:orange")
    ax2.tick_params(axis="y", labelcolor="tab:orange")

    # --- AXE X ---
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_graph["Banque"], rotation=45, ha="right")

    # --- LEGENDE DYNAMIQUE ---
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', linestyle='-', linewidth=2,
            color='tab:blue', label=f'Volumes ({tA}/{tB})'),
        Line2D([0], [0], marker='s', linestyle='-', linewidth=2,
            color='tab:orange', label=f'Montants ({tA}/{tB})')
    ]
    ax1.legend(handles=legend_elements, loc="upper left")

    # --- TITRE + GRILLE ---
    plt.title(f"Comparaison {tA} vs {tB} — Volumes & Montants ({annee2}) — {instrument.capitalize()}")
    ax1.grid(True, linestyle="--", alpha=0.5)

    st.pyplot(fig)
