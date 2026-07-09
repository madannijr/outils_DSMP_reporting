# ============================================================
# 🔹 Importation des librairies nécessaires
# ============================================================
import pandas as pd                  # Manipulation des données tabulaires
import streamlit as st               # Interface utilisateur Streamlit
import numpy as np                   # Calculs numériques
import matplotlib.pyplot as plt      # Graphiques
import re                            # Expressions régulières (extraction d'année)
from fonctions_utils import format_dataframe  # Formatage esthétique des tableaux
from utils import telecharger_excel


# ============================================================
# 🔹 Fonction : Conversion propre des montants
# ============================================================
def convertir(df, col):
    return (
        df[col]
        .astype(str)                         # Convertit en texte pour nettoyage
        .str.replace(" ", "", regex=False)   # Supprime les espaces
        .str.replace(",", ".", regex=False)  # Remplace virgule par point
        .str.replace("\xa0", "", regex=False)  # Supprime espace insécable
        .str.replace("\u202f", "", regex=False) # Supprime espace fine
        .apply(lambda x: pd.to_numeric(x, errors="coerce"))  # Convertit en numérique
        .fillna(0)                           # Remplace NaN par 0
    )

# ============================================================
# 🔹 Fonction : Extraction automatique des années
# ============================================================
def extraire_annee(col):
    match = re.search(r"(20\d{2})", str(col))  # Cherche une année dans le texte
    return int(match.group(1)) if match else None

# ============================================================
# 🔹 Fonction : Détection automatique du trimestre (T1, T2, T3, T4)
# ============================================================
def detecter_trimestre(df):
    colonnes = [str(c).upper().strip() for c in df.columns]

    trimestres = []

    for col in colonnes:
        if "_T1_" in col:
            trimestres.append("T1")
        elif "_T2_" in col:
            trimestres.append("T2")
        elif "_T3_" in col:
            trimestres.append("T3")
        elif "_T4_" in col:
            trimestres.append("T4")

    trimestres = list(set(trimestres))

    if len(trimestres) == 1:
        return trimestres[0]

    return None  # Aucun trimestre trouvé

# ============================================================
# 🔹 Fonction : Nettoyage général du DataFrame
# ============================================================
def nettoyer(df):
    df = df.loc[:, ~df.columns.str.contains("Unnamed", case=False)]  # Supprime colonnes inutiles
    if "Banque" not in df.columns:
        return pd.DataFrame()  # Retourne vide si colonne Banque absente
    df = df[df["Banque"].notna()]                                    # Supprime lignes vides
    df["Banque"] = df["Banque"].astype(str).str.strip()              # Nettoie les noms
    df = df[df["Banque"] != ""]                                      # Supprime lignes vides
    df = df[~df["Banque"].str.contains("TOTAL|TOTAUX", case=False)]  # Supprime totaux
    return df

# ============================================================
# 🔹 Fonction principale : Analyse Semestrielle
# ============================================================
def analyse_semestrielle(fichier_A, fichier_B, semestre):

    st.header("Analyse Semestrielle ACP/ACH")  # Titre principal

    # Choix de l’instrument
    instrument = st.selectbox(
        "Choisir un instrument :",
        ["virements", "chèques", "chèques représenté", "lettre de change"]
    )

    # Vérification des feuilles disponibles dans les deux fichiers
    try:
        feuilles_A = pd.ExcelFile(fichier_A).sheet_names
        feuilles_B = pd.ExcelFile(fichier_B).sheet_names
    except Exception as e:
        st.error(f"Erreur lors de la lecture des fichiers : {e}")
        return

    # Vérifie que l’instrument existe dans les deux fichiers
    if instrument not in feuilles_A or instrument not in feuilles_B:
        st.error(f"❌ Les fichiers fournis ne contiennent pas la feuille '{instrument}'.")
        st.write("Feuilles disponibles dans fichier A :", feuilles_A)
        st.write("Feuilles disponibles dans fichier B :", feuilles_B)
        return

    # Lecture des deux feuilles
    try:
        df_A = pd.read_excel(fichier_A, sheet_name=instrument)
        df_B = pd.read_excel(fichier_B, sheet_name=instrument)
    except Exception as e:
        st.error(f"Erreur lors de la lecture des feuilles '{instrument}' : {e}")
        return

    # Nettoyage des noms de colonnes
    for df in [df_A, df_B]:
        df.columns = (
            df.columns.astype(str)
            .str.replace("\n", "")
            .str.replace("\t", "")
            .str.replace("\xa0", "")
            .str.replace("\u202f", "")
            .str.strip()
        )

    # ====================================================
    # Détermination directe du semestre choisi
    # ====================================================

    semestre_label = semestre

    if semestre == "S1":
        tA = "T1"
        tB = "T2"

    elif semestre == "S2":
        tA = "T3"
        tB = "T4"

    else:
        st.error("Semestre invalide")
        return

    st.success(f"Analyse {semestre_label} : {tA} + {tB}")

    # Nettoyage général
    df_A = nettoyer(df_A)
    df_B = nettoyer(df_B)

    if df_A.empty or df_B.empty:
        st.error("❌ Les fichiers doivent contenir la colonne 'Banque' et des lignes valides.")
        return

    # Fusion des deux trimestres sur la colonne Banque
    df = df_A.merge(df_B, on="Banque", how="outer", suffixes=(f"_{tA}", f"_{tB}"))

    # Détection automatique des colonnes Nombre/Montant
    colonnes_nombre = [c for c in df.columns if "Nombre" in c]
    colonnes_montant = [c for c in df.columns if "Montant" in c]

    if not colonnes_nombre or not colonnes_montant:
        st.error("❌ Impossible de trouver les colonnes 'Nombre' ou 'Montant' dans la fusion.")
        st.write("Colonnes disponibles :", df.columns.tolist())
        return

    # Détection des années présentes
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

    # Construction dynamique des noms de colonnes attendus
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
            "❌ Les fichiers importés ne correspondent pas au semestre attendu.\n"
            "Pour S1, seuls les fichiers des trimestres T1 et T2 sont acceptés.\n"
            "Pour S2, seuls les fichiers des trimestres T3 et T4 sont acceptés.\n"
            "Veuillez vérifier que vous avez bien sélectionné les fichiers du bon trimestre pour le semestre choisi."
        )
        #st.write("Colonnes détectées :", df.columns.tolist())
        return

    # Conversion numérique des colonnes
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

    # Ligne des totaux
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
    st.subheader("📥 Télécharger le tableau semestriel")
    telecharger_excel(df_aff) # Button de telechargement en fichier Excel
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

   