import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from auth import check_auth

check_auth()


# ============================
# AUTHENTIFICATION DSMP
# ============================

def extraire_annee(texte):
    match = re.search(r"\d{4}", str(texte))
    return int(match.group()) if match else None

#-------------------------------------
# CONFIGURATION DE LA PAGE STREAMLIT
#-------------------------------------
st.set_page_config(page_title="DSMP – Outil de Reporting", layout="wide")
st.image("BCRG_LOGO.png", width=120)
st.markdown("""
<div style="
    background-color:#004d40;
    padding:18px;
    border-radius:8px;
    margin-bottom:25px;
    display:flex;
    align-items:center;
">
    <div style="color:white;">
        <h2 style="margin:0; padding:0;">Banque Centrale de la République de Guinée</h2>
        <p style="margin:0; padding:0; font-size:16px;">Direction des Systèmes et Moyens de Paiement (DSMP)</p>
    </div>
</div>
""", unsafe_allow_html=True)




##########################################################""
st.markdown("""
<style>

    /* Titres */
    h1, h2, h3 {
        color: #0b3d2e;
        font-weight: 700;
    }

    /* Texte */
    p, label, span {
        font-size: 15px !important;
    }

    /* Onglets */
    .stTabs [data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
        color: #ffffff;
        background-color: #00695c;
        border-radius: 5px;
        padding: 8px 12px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #004d40;
    }

    /* DataFrames */
    .dataframe {
        font-size: 14px;
    }

</style>
""", unsafe_allow_html=True)


# Titre principal de l'application
st.title("DSMP – Outil de Reporting des Systèmes de Paiement")
st.write("Analyse automatique des flux ACP/ACH et RTGS à partir du fichier Excel annuel.")

#################################################
# telechargement du fichier d'aide 
################################################
st.markdown("### 🆘 Aide")

with st.expander("📥 Télécharger le modèle de fichier DSMP"):
    st.write("Téléchargez le fichier modèle pour remplir les données conformément au format attendu.")

    try:
        with open("modele_dsmp.xlsx", "rb") as f:
            st.download_button(
                label="📄 Télécharger le fichier modèle",
                data=f.read(),
                file_name="modele_dsmp.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except FileNotFoundError:
        st.error("❌ Le fichier 'modele_dsmp.xlsx' est introuvable.")

#-------------------------------------
# UPLOAD DU FICHIER EXCEL
#-------------------------------------
uploaded_file = st.file_uploader("Importer le fichier Excel DSMP", type=["xlsx"])

if not uploaded_file:
    st.stop()

#-------------------------------------
# CREATION DES ONGLET PRINCIPAUX
#-------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Évolution Globale ACP/ACH",
    "Parts de Marché",
    "Rejets",
    "Matrice de positionnement",
    "Analyse Global RTGS",
    "Répartition par devise de règlement (RTGS)",
    "Contribution SNP"   
])

# =========================================================
# 1) ONGLET : ÉVOLUTION GLOBALE ACP/ACH
# =========================================================
with tab1:

    st.header("Évolution Globale ACP/ACH")

    df_raw = pd.read_excel(uploaded_file, sheet_name="Evolution Globale ACPACH")

    colonnes_volume = [c for c in df_raw.columns if "Volume" in c]
    annee1 = colonnes_volume[0].split()[1]
    annee2 = colonnes_volume[1].split()[1]

    st.success(f"Années détectées : {annee1} et {annee2}")

    df_raw.columns = [
        "Instrument",
        f"Volume_{annee1}",
        f"Volume_{annee2}",
        "Variation_Volume",
        f"Valeur_{annee1}",
        f"Valeur_{annee2}",
        "Variation_Valeur"
    ]
    df = df_raw.copy()

    # 🔥 Supprimer la ligne TOTAL
    df = df[df["Instrument"] != "TOTAL"]

    st.subheader("Tableau des indicateurs")
    st.dataframe(df)

    instruments = df["Instrument"]
    x = np.arange(len(instruments))
    width = 0.35

    st.subheader(f"Volumes ACP/ACH ({annee1} vs {annee2})")
    fig1, ax1 = plt.subplots(figsize=(10, 2.8))
    ax1.bar(x - width/2, df[f"Volume_{annee1}"], width, label=annee1)
    ax1.bar(x + width/2, df[f"Volume_{annee2}"], width, label=annee2)
    ax1.set_xticks(x)
    ax1.set_xticklabels(instruments)
    ax1.legend()
    st.pyplot(fig1)

    st.subheader(f"Valeurs ACP/ACH ({annee1} vs {annee2})")
    fig2, ax2 = plt.subplots(figsize=(10, 2.8))
    ax2.bar(x - width/2, df[f"Valeur_{annee1}"], width, label=annee1)
    ax2.bar(x + width/2, df[f"Valeur_{annee2}"], width, label=annee2)
    ax2.set_xticks(x)
    ax2.set_xticklabels(instruments)
    ax2.legend()
    st.pyplot(fig2)


    

# =========================================================
# 2) ONGLET : PARTS DE MARCHÉ
# =========================================================
with tab2:

    st.header("Parts de Marché par Instrument")

    choix = st.selectbox("Choisir l’instrument :", ["Chèques", "Virements"])

    df_banque = pd.read_excel(uploaded_file, sheet_name="Evolution par Banque ACPACH")

    df_banque.columns = [
        "N", "Banque",
        "Chq_Nombre", "Chq_Montant",
        "Vir_Nombre", "Vir_Montant",
        "LC_Nombre", "LC_Montant",
        "Total_Nombre", "Total_Montant"
    ]
    
    if choix == "Chèques":
        df = df_banque[["Banque", "Chq_Nombre", "Chq_Montant"]].copy()
        df.columns = ["Banque", "Volume", "Valeur"]
    else:
        df = df_banque[["Banque", "Vir_Nombre", "Vir_Montant"]].copy()
        df.columns = ["Banque", "Volume", "Valeur"]

    # Suppression de la ligne TOTAL
    df = df[df["Banque"] != "Total"]

    #-------------------------------------
    # NETTOYAGE AVANCÉ (ÉLIMINE LE “nan”)
    #-------------------------------------
    for col in ["Volume", "Valeur"]:
        df[col] = (
            df[col].astype(str)
            .str.replace(" ", "", regex=False)
            .str.replace("—", "0", regex=False)
            .str.replace("-", "0", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Suppression des banques invalides
    df = df[df["Banque"].notna()]
    df = df[df["Banque"] != ""]
    df = df[df["Valeur"] > 0]  # élimine les banques à 0
    df = df.dropna(subset=["Valeur"])

    #-------------------------------------
    # CALCUL DES PARTS DE MARCHÉ
    #-------------------------------------
    total_valeur = df["Valeur"].sum()
    df["Part_Valeur"] = df["Valeur"] / total_valeur * 100

    st.subheader("Tableau des parts de marché")
    st.dataframe(df)

    #-------------------------------------
    # DONUT CHART (TOP 5 + AUTRES)
    #-------------------------------------
    df_sorted = df.sort_values("Part_Valeur", ascending=False)

    top5 = df_sorted.head(7)
    autres_valeur = df_sorted["Part_Valeur"].iloc[7:].sum()

    labels = list(top5["Banque"]) + ["Autres"]
    valeurs = list(top5["Part_Valeur"]) + [autres_valeur]

    fig, ax = plt.subplots(figsize=(4.5, 2.8))

    wedges, texts, autotexts = ax.pie(
        valeurs,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.78,
        labeldistance=1.15,
        wedgeprops=dict(width=0.28)
    )

    plt.setp(autotexts, size=7)
    plt.setp(texts, size=7)

    centre = plt.Circle((0,0), 0.55, color='white')
    fig.gca().add_artist(centre)

    ax.set_title(f"Parts de Marché {choix} (en Valeur)", fontsize=11)

    plt.tight_layout()
    st.pyplot(fig)
    
 
# =========================================================
# 3) ONGLET : REJETS (IMPAYÉS)
# =========================================================
with tab3:  
    # Ouvre l’onglet "Rejets (Impayés)"
    st.header("Analyse des Rejets (Impayés)")

    # -------------------------------------
    # LECTURE DE LA FEUILLE REJETS
    # -------------------------------------

    # Lecture de la feuille Excel contenant les rejets
    df_rejets_impayes = pd.read_excel(uploaded_file, sheet_name="Rejets Impayés")

    # Suppression des colonnes entièrement vides (souvent causées par Excel)
    df_rejets_impayes = df_rejets_impayes.dropna(axis=1, how="all")

    # Renommage des colonnes pour avoir des noms propres et cohérents
    df_rejets_impayes.columns = [
        "Instrument",        # Nom de l’instrument (Chèques, Virements…)
        "Volume_Nombre",     # Nombre de rejets en volume
        "Volume_Taux",       # Taux de rejets en volume
        "Valeur_Nombre",     # Montant des rejets en valeur
        "Valeur_Taux"        # Taux de rejets en valeur
    ]

    # -------------------------------------
    # NETTOYAGE DES TAUX (4,93% → 4.93)
    # -------------------------------------

    # Boucle sur les colonnes contenant des taux
    for col in ["Volume_Taux", "Valeur_Taux"]:
        # Conversion en texte pour nettoyage
        df_rejets_impayes[col] = df_rejets_impayes[col].astype(str)

        # Suppression du symbole %
        df_rejets_impayes[col] = df_rejets_impayes[col].str.replace("%", "", regex=False)

        # Remplacement de la virgule par un point (format numérique)
        df_rejets_impayes[col] = df_rejets_impayes[col].str.replace(",", ".", regex=False)

        # Conversion finale en nombre décimal
        df_rejets_impayes[col] = pd.to_numeric(df_rejets_impayes[col], errors="coerce")

    # -------------------------------------
    # AFFICHAGE DU TABLEAU
    # -------------------------------------

    # Titre du tableau dans Streamlit
    st.subheader("Tableau des rejets par instrument")

    # Affichage du DataFrame nettoyé
    st.dataframe(df_rejets_impayes)

    # -------------------------------------
    # GRAPHIQUE COMPARATIF (CHÈQUES vs VIREMENTS)
    # -------------------------------------

    # Titre du graphique
    st.subheader("Comparaison des taux de rejets : Chèques vs Virements")

    # Filtrage : on garde uniquement les instruments Chèques et Virements
    df_comparaison = df_rejets_impayes[df_rejets_impayes["Instrument"].isin(["Chèques", "Virements"])]

    # Extraction des noms d’instruments (pour l’axe X)
    instruments = df_comparaison["Instrument"]

    # Création des positions X (0, 1)
    x = np.arange(len(instruments))

    # Largeur des barres du graphique
    largeur = 0.35

    # Création de la figure Matplotlib
    fig, ax = plt.subplots(figsize=(6, 3))

    # -------------------------------------
    # BARRES POUR LES TAUX EN VOLUME
    # -------------------------------------

    # Barre pour les taux en volume (décalée à gauche)
    ax.bar(
        x - largeur/2,                     # Position X décalée vers la gauche
        df_comparaison["Volume_Taux"],     # Valeurs des taux en volume
        largeur,                           # Largeur de la barre
        label="Taux de Rejets en Volume"   # Légende
    )

    # -------------------------------------
    # BARRES POUR LES TAUX EN VALEUR
    # -------------------------------------

    # Barre pour les taux en valeur (décalée à droite)
    ax.bar(
        x + largeur/2,                     # Position X décalée vers la droite
        df_comparaison["Valeur_Taux"],     # Valeurs des taux en valeur
        largeur,                           # Largeur de la barre
        label="Taux de Rejets en Valeur"   # Légende
    )

    # -------------------------------------
    # CONFIGURATION DES AXES ET ÉTIQUETTES
    # -------------------------------------

    # Position des étiquettes sur l’axe X
    ax.set_xticks(x)

    # Texte affiché sous chaque barre (Chèques, Virements)
    ax.set_xticklabels(instruments)

    # Nom de l’axe Y
    ax.set_ylabel("Taux (%)")

    # Titre du graphique
    ax.set_title("Comparaison des taux de rejets : Chèques vs Virements")

    # Affichage de la légende
    ax.legend()

    # -------------------------------------
    # AFFICHAGE DU GRAPHIQUE DANS STREAMLIT
    # -------------------------------------

    # Envoi du graphique dans l’interface Streamlit
    st.pyplot(fig)

    
# =========================================================
# # 4) MATRICE DE POSITIONNEMENT DES BANQUES (ACP/ACH)
# =========================================================
with tab4:

    # Titre affiché dans l’onglet
    st.header("Matrice de Positionnement des Banques (ACP/ACH)")

    # -----------------------------------------------------
    # 1) LECTURE DE LA FEUILLE BANQUES
    # -----------------------------------------------------

    # Lecture de la feuille Excel contenant les données par banque
    df_banque = pd.read_excel(uploaded_file, sheet_name="Evolution par Banque ACPACH")

    # Renommage des colonnes pour avoir des noms propres et cohérents
    df_banque.columns = [
        "N", "Banque",
        "Chq_Nombre", "Chq_Montant",
        "Vir_Nombre", "Vir_Montant",
        "LC_Nombre", "LC_Montant",
        "Total_Nombre", "Total_Montant"
    ]

    # Suppression de la ligne "Total" qui n’est pas une banque
    df_banque = df_banque[df_banque["Banque"] != "Total"]

    # Suppression des lignes où le nom de la banque est vide ou NaN
    df_banque = df_banque[df_banque["Banque"].notna()]
    df_banque = df_banque[df_banque["Banque"].astype(str).str.strip() != ""]

    # -----------------------------------------------------
    # 2) NETTOYAGE DES VALEURS (ANTI-NAN)
    # -----------------------------------------------------

    # Nettoyage des colonnes numériques Total_Nombre et Total_Montant
    # On enlève les espaces, tirets, caractères spéciaux, etc.
    for col in ["Total_Nombre", "Total_Montant"]:
        df_banque[col] = (
            df_banque[col]
            .astype(str)                 # conversion en texte
            .str.replace(" ", "", regex=False)   # suppression des espaces
            .str.replace("—", "0", regex=False)  # remplacement du tiret long
            .str.replace("-", "0", regex=False)  # remplacement du tiret normal
            .str.replace(",", "", regex=False)   # suppression des virgules
        )
        # Conversion finale en nombre, remplacement des erreurs par 0
        df_banque[col] = pd.to_numeric(df_banque[col], errors="coerce").fillna(0)

    # Conversion du montant en milliards GNF pour correspondre au rapport
    df_banque["Montant_Milliards"] = df_banque["Total_Montant"] / 1e9

    # -----------------------------------------------------
    # 3) CALCUL DES MOYENNES
    # -----------------------------------------------------

    # Moyenne du volume total
    moyenne_volume = df_banque["Total_Nombre"].mean()

    # Moyenne de la valeur totale (en milliards)
    moyenne_valeur = df_banque["Montant_Milliards"].mean()

    # -----------------------------------------------------
    # 4) CREATION DU SCATTER PLOT (VERSION RAPPORT)
    # -----------------------------------------------------

    # Création d’une figure Matplotlib de taille 10x6
    fig, ax = plt.subplots(figsize=(10, 6))

    # Tracé des points (chaque point = une banque)
    ax.scatter(
        df_banque["Total_Nombre"],       # Axe X = volume total
        df_banque["Montant_Milliards"],  # Axe Y = valeur totale en milliards
        color="blue",
        s=70                              # Taille des points
    )

    # -----------------------------------------------------
    # 5) LABELS SUR CHAQUE POINT
    # -----------------------------------------------------

    # On ajoute le nom de chaque banque à côté de son point
    for i, row in df_banque.iterrows():
        ax.text(
            row["Total_Nombre"] + (df_banque["Total_Nombre"].max() * 0.01),  # décalage horizontal
            row["Montant_Milliards"] + (df_banque["Montant_Milliards"].max() * 0.01),  # décalage vertical
            row["Banque"],               # nom de la banque
            fontsize=9                   # taille du texte
        )

    # -----------------------------------------------------
    # 6) LIGNES DE MOYENNE
    # -----------------------------------------------------

    # Ligne verticale = moyenne du volume
    ax.axvline(moyenne_volume, color="red", linestyle="--", label="Moyenne Volume")

    # Ligne horizontale = moyenne de la valeur
    ax.axhline(moyenne_valeur, color="black", linestyle="--", label="Moyenne Valeur")

    # -----------------------------------------------------
    # 7) DÉZOOM AUTOMATIQUE (ÉTALER LES POINTS)
    # -----------------------------------------------------

    # On calcule une marge de 15% autour des valeurs max/min
    marge_x = df_banque["Total_Nombre"].max() * 0.15
    marge_y = df_banque["Montant_Milliards"].max() * 0.15

    # On applique les nouvelles limites pour dézoomer
    ax.set_xlim(
        df_banque["Total_Nombre"].min() - marge_x,
        df_banque["Total_Nombre"].max() + marge_x
    )

    ax.set_ylim(
        df_banque["Montant_Milliards"].min() - marge_y,
        df_banque["Montant_Milliards"].max() + marge_y
    )

    # -----------------------------------------------------
    # 8) CONFIGURATION DU GRAPHIQUE
    # -----------------------------------------------------

    ax.set_xlabel("Volume total de transactions (Nombre)")   # Nom de l’axe X
    ax.set_ylabel("Valeur totale échangée (Milliards GNF)")  # Nom de l’axe Y
    ax.set_title("Matrice de Positionnement : Activité des Banques sur ACP/ACH (2025)")  # Titre
    ax.legend()                                              # Affichage de la légende

    # Affichage final dans Streamlit
    st.pyplot(fig)

#=======================================
# Évolution globale des opérations du RTGS
# ==========================================

with tab5:

    # Titre principal de la section RTGS
    st.header("Analyse du Système RTGS")

   

    # -----------------------------------------------------
    # 1) LECTURE DES FEUILLES
    # -----------------------------------------------------
    # Lecture du tableau global RTGS (années)
    df_global_rtgs = pd.read_excel(uploaded_file, sheet_name="Global RTGS")
    # Lecture du tableau mensuel RTGS (variations)
    df_raw = pd.read_excel(uploaded_file, sheet_name="Variation Mensuel RTGS ", header=None)

    # -----------------------------------------------------
    # 2) NETTOYAGE DES NOMS DE COLONNES
    # -----------------------------------------------------
    # Nettoyer toutes les colonnes pour enlever les caractères invisibles
    df_global_rtgs.columns = [
        str(c).replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("\xa0", " ").strip()
        for c in df_global_rtgs.columns
    ]

    # -----------------------------------------------------
    # 3) EXTRACTION DES ANNÉES DANS LES COLONNES
    # -----------------------------------------------------
    # Récupérer les deux colonnes contenant les années
    col_A = df_global_rtgs.columns[1]   # Exemple : "Réalisations_2025"
    col_B = df_global_rtgs.columns[2]   # Exemple : "Réalisations_2026"

    # Extraire les années avec la fonction
    annee_A = extraire_annee(col_A)
    annee_B = extraire_annee(col_B)

    # DEBUG : afficher les années détectées
    st.write("Année A détectée :", annee_A)
    st.write("Année B détectée :", annee_B)

    # Si une année n'est pas trouvée → arrêter l'exécution
    if annee_A is None or annee_B is None:
        st.error("Impossible d'extraire les années dans la feuille Global RTGS.")
        st.stop()

    # -----------------------------------------------------
    # 4) EXTRACTION DES 12 MOIS (colonnes 0 à 6)
    # -----------------------------------------------------
    # On prend les lignes 2 à 13 (12 mois) et les colonnes 0 à 6 (7 colonnes utiles)
    df_var_rtgs = df_raw.iloc[2:14, 0:7].copy()

    # Renommer les colonnes avec les années détectées
    df_var_rtgs.columns = [
        "Mois",
        f"Volume_{annee_A}",
        f"Valeur_{annee_A}",
        f"Volume_{annee_B}",
        f"Valeur_{annee_B}",
        "Var_Volume",
        "Var_Valeur"
    ]

    # -----------------------------------------------------
    # 5) NORMALISATION DES MOIS
    # -----------------------------------------------------
    # Dictionnaire pour convertir les mois Excel → mois abrégés
    mois_map = {
        "janv..24": "Jan", "févr..24": "Fév", "mars .24": "Mar", "avr. .24": "Avr",
        "mai  .24": "Mai", "juin .24": "Juin", "juil..24": "Juil", "août .24": "Août",
        "sept..24": "Sep", "oct. .24": "Oct", "nov. .24": "Nov", "déc. .24": "Déc",
        "janv..25": "Jan", "févr..25": "Fév", "mars .25": "Mar", "avr. .25": "Avr",
        "mai  .25": "Mai", "juin .25": "Juin", "juil..25": "Juil", "août .25": "Août",
        "sept..25": "Sep", "oct. .25": "Oct", "nov. .25": "Nov", "déc. .25": "Déc"
    }

    # Remplacer les mois bruts par des mois normalisés
    df_var_rtgs["Mois"] = df_var_rtgs["Mois"].replace(mois_map)

    # -----------------------------------------------------
    # 6) NETTOYAGE DES VALEURS
    # -----------------------------------------------------
    # Convertir toutes les colonnes numériques en float (gestion des virgules, espaces)
    for col in df_var_rtgs.columns[1:]:
        df_var_rtgs[col] = pd.to_numeric(df_var_rtgs[col], errors="coerce").fillna(0)

    # -----------------------------------------------------
    # 7) AFFICHAGE DU TABLEAU
    # -----------------------------------------------------
    st.subheader(f"Évolution Mensuelle RTGS ({annee_A} vs {annee_B})")
    st.dataframe(df_var_rtgs)

    # -----------------------------------------------------
    # 8) GRAPHIQUE
    # -----------------------------------------------------
    st.subheader(f"Dynamique Mensuelle du RTGS en Réalisations {annee_B} : Volume vs Valeur")

    # Création du graphique
    fig, ax1 = plt.subplots(figsize=(12, 4))

    # Barres pour la valeur
    ax1.bar(df_var_rtgs["Mois"], df_var_rtgs[f"Valeur_{annee_B}"], color="steelblue")
    ax1.set_ylabel("Valeur (Milliards GNF)", color="blue")

    # Courbe pour le volume
    ax2 = ax1.twinx()
    ax2.plot(df_var_rtgs["Mois"], df_var_rtgs[f"Volume_{annee_B}"], color="red", marker="o")
    ax2.set_ylabel("Volume (Nombre d'opérations)", color="red")

    # Mise en forme
    plt.xticks(rotation=60, ha='right', fontsize=8)
    plt.title(f"Dynamique Mensuelle du RTGS en {annee_B}")

    st.pyplot(fig)

    

with tab6:

    # -----------------------------------------------------
    # 1) LECTURE DU TABLEAU (5 colonnes)
    # -----------------------------------------------------
    df_devise = pd.read_excel(
        uploaded_file,
        sheet_name="Variation Devise RTGS",
        usecols="A:E"
    )

    # -----------------------------------------------------
    # 2) NETTOYAGE DES NOMS DE COLONNES
    # -----------------------------------------------------
    df_devise.columns = (
        df_devise.columns
        .astype(str)
        .str.replace("\n", " ")
        .str.replace("\r", " ")
        .str.replace("\t", " ")
        .str.replace("\xa0", " ")
        .str.strip()
    )

    # -----------------------------------------------------
    # 3) EXTRACTION AUTOMATIQUE DE L’ANNÉE (ROBUSTE)
    # -----------------------------------------------------
    # Essayer d’extraire l’année dans la 2e colonne
    annee = extraire_annee(df_devise.columns[1])

    # Si None → essayer la 3e colonne
    if annee is None:
        annee = extraire_annee(df_devise.columns[2])

    # Si toujours None → afficher une erreur propre
    if annee is None:
        st.error("Impossible de détecter l’année dans la feuille 7‑Var Devise RTGS.")
        st.write("Colonnes détectées :", df_devise.columns.tolist())
        st.stop()

    # -----------------------------------------------------
    # TITRE DYNAMIQUE
    # -----------------------------------------------------
    st.header(f"Répartition des Règlements RTGS par Devise – Année {annee}")

    # -----------------------------------------------------
    # 4) SUPPRESSION DES LIGNES VIDES
    # -----------------------------------------------------
    df_devise = df_devise.dropna(subset=[df_devise.columns[0]])

    # -----------------------------------------------------
    # 5) RENOMMAGE DYNAMIQUE DES COLONNES
    # -----------------------------------------------------
    df_devise.columns = [
        "Devise",
        f"Volume_{annee}",
        f"Valeur_{annee}_devise",
        "ContreValeur_GNF",
        "Part_marche"
    ]

    # -----------------------------------------------------
    # 6) NETTOYAGE DES VALEURS NUMÉRIQUES
    # -----------------------------------------------------
    for col in [f"Volume_{annee}", f"Valeur_{annee}_devise", "ContreValeur_GNF"]:
        df_devise[col] = (
            df_devise[col]
            .astype(str)
            .str.replace(" ", "")
            .str.replace(",", ".")
        )
        df_devise[col] = pd.to_numeric(df_devise[col], errors="coerce")

    df_devise["Part_marche"] = (
        df_devise["Part_marche"]
        .astype(str)
        .str.replace("%", "")
        .str.replace(",", ".")
    )
    df_devise["Part_marche"] = pd.to_numeric(df_devise["Part_marche"], errors="coerce")

    # -----------------------------------------------------
    # 7) SUPPRESSION DES NaN ET DE LA LIGNE TOTAL
    # -----------------------------------------------------
    df_devise = df_devise.dropna(subset=["Part_marche"])
    df_devise = df_devise[df_devise["Devise"] != "TOTAL"]

    # -----------------------------------------------------
    # 8) AFFICHAGE DU TABLEAU
    # -----------------------------------------------------
    st.subheader(f"Tableau – Répartition par devise de règlement ({annee})")
    st.dataframe(df_devise)

    # -----------------------------------------------------
    # 9) GRAPHIQUE DONUT AVEC LÉGENDE
    # -----------------------------------------------------
    st.subheader(f"Répartition des Règlements RTGS par Devise (en Valeur) – {annee}")

    labels = df_devise["Devise"]
    valeurs = df_devise["Part_marche"]

    couleurs = ["#4CAF50", "#2196F3", "#9C27B0"]  # GNF, USD, EUR

    fig, ax = plt.subplots(figsize=(6, 6))

    wedges, texts, autotexts = ax.pie(
        valeurs,
        labels=None,
        colors=couleurs,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.85
    )

    centre = plt.Circle((0, 0), 0.60, fc="white")
    fig.gca().add_artist(centre)

    ax.legend(
        labels,
        title="Devise",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    plt.title(f"Répartition des Règlements RTGS par Devise (en Valeur) – {annee}")
    st.pyplot(fig)
    

# =========================================================
# 7) ONGLET : CONTRIBUTION DES BANQUES AU SNP
# =========================================================

with tab7:

    st.header("Contribution des Banques au Système National de Paiement (SNP)")

    # -----------------------------------------------------
    # 1) LECTURE SANS HEADER
    # -----------------------------------------------------
    df_raw = pd.read_excel(uploaded_file, sheet_name="Variation Contribution SNP", header=None)

    # -----------------------------------------------------
    # 2) EXTRACTION DES ANNÉES DANS LA LIGNE 1
    # -----------------------------------------------------
    ligne_annees = df_raw.iloc[1].astype(str).fillna("")

    annees = []
    for val in ligne_annees:
        match = re.search(r"(20\d{2})", val)
        if match:
            annees.append(match.group(1))

    # Supprimer doublons
    annees = list(dict.fromkeys(annees))

    # Vérification
    if len(annees) < 2:
        st.error("Impossible de détecter les années dans la feuille Contribution SNP.")
        st.write("Valeurs trouvées dans la ligne 2 :", ligne_annees.tolist())
        st.stop()

    annee1, annee2 = annees[:2]

    st.success(f"Années détectées : {annee1} et {annee2}")

    # -----------------------------------------------------
    # 3) RECONSTRUCTION DU DATAFRAME
    # -----------------------------------------------------
    df_snp = df_raw.iloc[2:].copy()

    df_snp.columns = [
        "N",
        "Banque",
        f"Contribution_{annee1}", f"Contribution_{annee2}",
        f"Service_Bureau_{annee1}", f"Service_Bureau_{annee2}",
        f"Total_{annee1}", f"Total_{annee2}",
        "Variation"
    ]

    # -----------------------------------------------------
    # 4) NETTOYAGE
    # -----------------------------------------------------
    for col in [f"Contribution_{annee1}", f"Contribution_{annee2}",
                f"Service_Bureau_{annee1}", f"Service_Bureau_{annee2}",
                f"Total_{annee1}", f"Total_{annee2}"]:

        df_snp[col] = (
            df_snp[col].astype(str)
            .str.replace(" ", "")
            .str.replace(",", ".")
            .str.replace("-", "0")
        )
        df_snp[col] = pd.to_numeric(df_snp[col], errors="coerce")

    df_snp["Variation"] = (
        df_snp["Variation"].astype(str)
        .str.replace("%", "")
        .str.replace(",", ".")
    )
    df_snp["Variation"] = pd.to_numeric(df_snp["Variation"], errors="coerce")

    df_snp = df_snp.dropna(subset=["Banque"])

    # -----------------------------------------------------
    # 5) TABLEAU
    # -----------------------------------------------------
    st.subheader(f"Tableau – Contribution SNP ({annee1}–{annee2})")
    st.dataframe(df_snp)

    # -----------------------------------------------------
    # 6) GRAPHIQUE
    # -----------------------------------------------------
    df_plot = df_snp.sort_values(f"Total_{annee2}", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 10))
    ax.barh(df_plot["Banque"], df_plot[f"Total_{annee2}"])
    ax.set_title(f"Classement SNP {annee2}")

    st.pyplot(fig)

    # -----------------------------------------------------
    # 7) ANALYSE AUTO
    # -----------------------------------------------------
    total_annee1 = df_snp[f"Total_{annee1}"].sum()
    total_annee2 = df_snp[f"Total_{annee2}"].sum()

    croissance = (total_annee2 - total_annee1) / total_annee1 * 100

    top = df_plot.iloc[-1]

    st.write(f"""
    Total {annee2} : {total_annee2:,.0f} GNF  
    Croissance : {croissance:.2f} %  
    Leader : {top["Banque"]} ({top[f"Total_{annee2}"]:,.0f} GNF)
    """)
