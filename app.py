import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from auth import check_auth
from fonctions_utils import format_dataframe
from analyse_trimestrielle import analyse_trimestrielle
from analyse_semestrielle import analyse_semestrielle
from modeles_trimestres import telecharger_modele_trimestre



# ============================================================
# 🔹 AUTHENTIFICATION
check_auth()
# ============================================================

# ============================================================
# 🔹 SESSION STATE POUR GARDER LES FICHIERS
# ============================================================
if "fichier_trimestriel" not in st.session_state:
    st.session_state.fichier_trimestriel = None

if "fichier_T1" not in st.session_state:
    st.session_state.fichier_T1 = None

if "fichier_T2" not in st.session_state:
    st.session_state.fichier_T2 = None

if "fichier_T3" not in st.session_state:
    st.session_state.fichier_T3 = None

if "fichier_T4" not in st.session_state:
    st.session_state.fichier_T4 = None


# ============================================================
# 🔹 Fonction utilitaire : extraire année
# ============================================================
def extraire_annee(texte):
    match = re.search(r"\d{4}", str(texte))
    return int(match.group()) if match else None


# ============================================================
# 🔹 CONFIGURATION PAGE
# ============================================================
st.set_page_config(
    page_title="DSMP – Outil de Reporting",
    layout="wide"
)

# ============================================================
# 🔹 LOGO
# ============================================================
st.image("BCRG_LOGO.png", width=120)

# ============================================================
# 🔹 HEADER
# ============================================================
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
        <h2 style="margin:0; padding:0;">
            Banque Centrale de la République de Guinée
        </h2>
        <p style="margin:0; padding:0; font-size:16px;">
            Direction des Systèmes et Moyens de Paiement (DSMP)
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 🔹 CSS PERSONNALISÉ
# ============================================================
st.markdown("""
<style>
h1, h2, h3 {
    color: #0b3d2e;
    font-weight: 700;
}
p, label, span {
    font-size: 15px !important;
}
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
.dataframe {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔹 TITRE PRINCIPAL
# ============================================================
st.title("DSMP – Outil de Reporting des flux des Systèmes de Paiement")
st.write("""
Analyse automatique des flux ACP/ACH, RTGS, Trimestriels, Semestriels et Annuels.
""")


# ============================================================
# 🔹 MENU SIDEBAR
# ============================================================
st.sidebar.title("📌 Choisir une analyse")

menu_principal = st.sidebar.radio(
    "Type d'analyse",
    [
        "Analyse Trimestrielle",
        "Analyse Semestrielle",
        "Analyse Annuelle"
    ]
)

# ============================================================
# 🔹 ANALYSE TRIMESTRIELLE
# ============================================================
if menu_principal == "Analyse Trimestrielle":

    # Choix du type de flux
    type_flux = st.radio(
        "Choisir le type de flux à analyser",
        ["ACP/ACH", "RTGS"],
        horizontal=True
    )

    # Choix du trimestre
    sous_menu = st.sidebar.radio(
        "Choisir le trimestre",
        ["T1", "T2", "T3", "T4"]
    )

    # TITRE DYNAMIQUE
    st.markdown(
        f"<h1 style='text-align:center;color:#00BFFF;margin-top:20px;'>"
        f"🧮 Analyse du trimestre {sous_menu} — {type_flux}"
        f"</h1>",
        unsafe_allow_html=True
    )

    # ========================================================
    # 🔹 AFFICHAGE DU MODELE SELON LE TYPE DE FLUX
    # ========================================================
    if type_flux == "ACP/ACH":
        telecharger_modele_trimestre(sous_menu)
    else:
        st.info("📄 Le modèle RTGS n’est pas encore disponible.")

    # ========================================================
    # 🔹 RTGS non disponible
    # ========================================================
    if type_flux == "RTGS":
        st.info("🔧 L’analyse RTGS n'est pas encore disponible.")
        st.stop()

    # ========================================================
    # 🔹 UPLOAD ET ANALYSE
    # ========================================================
    # Mapping des clés pour stocker les fichiers
    key_map = {
        "T1": "fichier_T1_TRI",
        "T2": "fichier_T2_TRI",
        "T3": "fichier_T3_TRI",
        "T4": "fichier_T4_TRI"
    }

    fichier = st.file_uploader(
        f"Importer le fichier {sous_menu} ({type_flux})",
        type=["xlsx"],
        key=f"upload_TRI_{sous_menu}"
    )
    # Stockage dans la session
    if fichier:
        st.session_state[key_map[sous_menu]] = fichier
    # Récupération du fichier stocké
    fichier_charge = st.session_state.get(key_map[sous_menu])
     # Lancement de l’analyse si un fichier est chargé
    if fichier_charge:
        analyse_trimestrielle(fichier_charge, sous_menu)

    st.stop()   # Empêche Streamlit d’exécuter la suite du script



# ============================================================
# 🔹 ANALYSE SEMESTRIELLE
# ============================================================
elif menu_principal == "Analyse Semestrielle":

    st.markdown(
        """
        <h1 style='text-align: center; color: #00BFFF; margin-top:20px;'>
            🧮 Analyse des flux semestriels
        </h1>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # 🔹 CHOIX FLUX
    # ========================================================
    type_flux = st.radio(
        "Choisir le type de flux à analyser",
        ["ACP/ACH", "RTGS"],
        horizontal=True
    )

    # ========================================================
    # 🔹 CHOIX SEMESTRE
    # ========================================================
    sous_menu = st.sidebar.radio(
        "Choisir le semestre",
        ["S1", "S2"]
    )

    # ========================================================
    # 🔹 RTGS
    # ========================================================
    if type_flux == "RTGS":

        st.info("🔧 L’analyse RTGS sera bientôt disponible.")
        st.stop()

    # ========================================================
    # 🔹 SEMESTRE 1
    # ========================================================
    if sous_menu == "S1":

        st.subheader("📂 Importation des fichiers T1 et T2")
        st.info("Utiliser les fichiers modèles des trimestres pour le semestre correspondant")

        fichier_T1 = st.file_uploader(
            f"Importer le fichier T1 ({type_flux})",
            type=["xlsx"],
            key="T1_S1"
        )

        fichier_T2 = st.file_uploader(
            f"Importer le fichier T2 ({type_flux})",
            type=["xlsx"],
            key="T2_S1"
        )

        if fichier_T1:
            st.session_state.fichier_T1 = fichier_T1

        if fichier_T2:
            st.session_state.fichier_T2 = fichier_T2

        if st.session_state.fichier_T1:
            st.success(
                f"✅ Fichier T1 chargé : "
                f"{st.session_state.fichier_T1.name}"
            )

        if st.session_state.fichier_T2:
            st.success(
                f"✅ Fichier T2 chargé : "
                f"{st.session_state.fichier_T2.name}"
            )

        if (
            st.session_state.fichier_T1
            and st.session_state.fichier_T2
        ):

            analyse_semestrielle(
                st.session_state.fichier_T1,
                st.session_state.fichier_T2
            )

        st.stop()

    # ========================================================
    # 🔹 SEMESTRE 2
    # ========================================================
    if sous_menu == "S2":

        st.subheader("📂 Importation des fichiers T3 et T4")

        fichier_T3 = st.file_uploader(
            f"Importer le fichier T3 ({type_flux})",
            type=["xlsx"],
            key="T3_S2"
        )

        fichier_T4 = st.file_uploader(
            f"Importer le fichier T4 ({type_flux})",
            type=["xlsx"],
            key="T4_S2"
        )

        if fichier_T3:
            st.session_state.fichier_T3 = fichier_T3

        if fichier_T4:
            st.session_state.fichier_T4 = fichier_T4

        if st.session_state.fichier_T3:
            st.success(
                f"✅ Fichier T3 chargé : "
                f"{st.session_state.fichier_T3.name}"
            )

        if st.session_state.fichier_T4:
            st.success(
                f"✅ Fichier T4 chargé : "
                f"{st.session_state.fichier_T4.name}"
            )

        if (
            st.session_state.fichier_T3
            and st.session_state.fichier_T4
        ):

            analyse_semestrielle(
                st.session_state.fichier_T3,
                st.session_state.fichier_T4
            )

        st.stop()
# ============================================================
# 🔹 ANALYSE ANNUELLE
# ============================================================
elif menu_principal == "Analyse Annuelle":

    st.header("📊 Analyse Annuelle ACP/ACH")

    st.markdown("### 🆘 Aide")

    # ========================================================
    # 🔹 MODELE
    # ========================================================
    with st.expander("📥 Télécharger le modèle de fichier DSMP"):

        try:

            with open("modele_dsmp.xlsx", "rb") as f:

                st.download_button(
                    label="📄 Télécharger le fichier modèle",
                    data=f.read(),
                    file_name="modele_dsmp.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except FileNotFoundError:

            st.error(
                "❌ Le fichier 'modele_dsmp.xlsx' est introuvable."
            )

    # ========================================================
    # 🔹 UPLOAD ANNUEL
    # ========================================================
    uploaded_file = st.file_uploader(
        "Importer le fichier Excel DSMP (annuel)",
        type=["xlsx"],
        key="annuel"
    )

    if not uploaded_file:

        st.info(
            "Veuillez importer le fichier annuel "
            "pour afficher les analyses."
        )

        st.stop()

# ============================================================
# 🔹 TABS ANNUELLES
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Évolution Globale ACP/ACH",
    "Parts de Marché",
    "Rejets",
    "Matrice de positionnement",
    "Analyse Global RTGS",
    "Répartition par devise de règlement (RTGS)",
    "Contribution SNP",
])



# =========================================================
# 1) ONGLET : ÉVOLUTION GLOBALE ACP/ACH
# =========================================================
with tab1:

    # -----------------------------------------------------
    # Titre principal de l’onglet
    # -----------------------------------------------------
    st.header("Évolution Globale ACP/ACH")

    # -----------------------------------------------------
    # Lecture du fichier Excel et sélection de la feuille
    # -----------------------------------------------------
    df_raw = pd.read_excel(uploaded_file, sheet_name="Evolution Globale ACPACH")

    # -----------------------------------------------------
    # Détection automatique des années dans les colonnes
    # -----------------------------------------------------
    colonnes_volume = [c for c in df_raw.columns if "Volume" in c]
    annee1 = colonnes_volume[0].split()[1]  # première année détectée
    annee2 = colonnes_volume[1].split()[1]  # deuxième année détectée

    # -----------------------------------------------------
    # Affichage des années détectées
    # -----------------------------------------------------
    st.success(f"Années détectées : {annee1} et {annee2}")

    # -----------------------------------------------------
    # Renommage des colonnes pour uniformiser le DataFrame
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Suppression de la ligne TOTAL pour éviter les doublons
    # -----------------------------------------------------
    df = df[df["Instrument"] != "TOTAL"]

    # -----------------------------------------------------
    # Affichage du tableau des indicateurs formaté
    # -----------------------------------------------------
    st.subheader("Tableau des indicateurs")
    df_affichage = format_dataframe(df)  # formatage en style français
    st.dataframe(df_affichage)

    # -----------------------------------------------------
    # Préparation des variables pour les graphiques
    # -----------------------------------------------------
    instruments = df["Instrument"]
    x = np.arange(len(instruments))
    width = 0.35

    # =====================================================
    # 🔹 PREMIER GRAPHIQUE : COMPARAISON DES VOLUMES
    # =====================================================
    st.subheader(f"Volumes ACP/ACH ({annee1} vs {annee2})")

    fig, ax = plt.subplots(figsize=(8, 3.5))

    # 🔹 Couleurs cohérentes et harmonisées
    couleur_annee1 = "#1F77B4"  # Bleu pour 2024
    couleur_annee2 = "#F39C12"  # Orange pour 2025
    bar_height = 0.35

    # 🔹 Barres côte à côte (non superposées)
    x = np.arange(len(instruments))
    ax.barh(x - bar_height/2, df[f"Volume_{annee1}"], height=bar_height, color=couleur_annee1, label=f"{annee1}")
    ax.barh(x + bar_height/2, df[f"Volume_{annee2}"], height=bar_height, color=couleur_annee2, label=f"{annee2}")

    # 🔹 Personnalisation du graphique
    ax.set_yticks(x)
    ax.set_yticklabels(instruments, fontsize=10)
    ax.set_xlabel("Volume des transactions", fontsize=10)
    ax.set_ylabel("Instrument", fontsize=10)
    ax.set_title("Comparaison des volumes ACP/ACH par instrument", fontsize=12, fontweight="bold")

    # 🔹 Légende encadrée à droite (comme l’ancien style)
    legend = ax.legend(
        loc="upper right",      # position à droite
        frameon=True,           # cadre visible
        edgecolor="black",      # bordure noire
        facecolor="white",      # fond blanc
        fontsize=9
    )
    legend.get_frame().set_linewidth(0.8)  # finesse du cadre

    # 🔹 Nettoyage visuel : fond clair + suppression des cadres inutiles
    ax.set_facecolor("#F8F9F9")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # 🔹 Ajustement de la mise en page
    plt.tight_layout()
    st.pyplot(fig)

    


    # =====================================================
    # 🔹 DEUXIÈME GRAPHIQUE : ÉVOLUTION DES VOLUMES
    # =====================================================
    st.subheader(f"Évolution des volumes ACP/ACH ({annee1} → {annee2})")

    fig, ax1 = plt.subplots(figsize=(8, 3.5))
    x = np.arange(len(instruments))
    width = 0.35

    # Barres pour les volumes des deux années
    ax1.bar(x - width/2, df[f"Volume_{annee1}"], width, label=annee1, color="#1f77b4")
    ax1.bar(x + width/2, df[f"Volume_{annee2}"], width, label=annee2, color="#ff7f0e")
    ax1.set_xticks(x)
    ax1.set_xticklabels(instruments)
    ax1.set_ylabel("Volume des transactions")
    ax1.legend(loc="upper left")

    # Ligne verte pour la variation en pourcentage
    ax2 = ax1.twinx()
    ax2.plot(x, df["Variation_Volume"] * 100, color="green", marker="o", label="Variation (%)")
    ax2.set_ylabel("Variation en %")
    ax2.legend(loc="upper right")

    # Ajout des annotations de taux de variation au-dessus des points
    for i, val in enumerate(df["Variation_Volume"] * 100):
        ax2.text(x[i], val + 0.5, f"{val:.2f}%", color="green", ha="center", fontsize=8)

    # Affichage du graphique final
    st.pyplot(fig)

# =========================================================
# 2) ONGLET : PARTS DE MARCHÉ
# =========================================================
with tab2:

    # -----------------------------------------------------
    # TITRE PRINCIPAL DE L’ONGLET
    # -----------------------------------------------------
    st.header("Parts de Marché par Instrument")  
    # Affiche le titre de la section

    # -----------------------------------------------------
    # CHOIX DE L’INSTRUMENT (Chèques, Virements, Lettre de change)
    # -----------------------------------------------------
    choix = st.selectbox(
        "Choisir l’instrument :",
        ["Chèques", "Virements", "Lettre de change"]  
        # Ajout de "Lettre de change" sans modifier le reste du code
    )

    # -----------------------------------------------------
    # CHOIX DU TYPE DE VISUEL (Barres ou Pareto)
    # -----------------------------------------------------
    type_graph = st.selectbox(
        "Type de visuel :",
        ["Barres horizontales", "Pareto"]
    )
    # L’utilisateur choisit le type de graphique

    # -----------------------------------------------------
    # LECTURE DU FICHIER EXCEL (feuille ACP/ACH)
    # -----------------------------------------------------
    df_banque = pd.read_excel(uploaded_file, sheet_name="Evolution par Banque ACPACH")
    # Charge la feuille contenant les données par banque

    # -----------------------------------------------------
    # RENOMMAGE DES COLONNES POUR SIMPLIFIER LES TRAITEMENTS
    # -----------------------------------------------------
    df_banque.columns = [
        "N", "Banque",
        "Chq_Nombre", "Chq_Montant",
        "Vir_Nombre", "Vir_Montant",
        "LC_Nombre", "LC_Montant",
        "Total_Nombre", "Total_Montant"
    ]
    # On renomme les colonnes pour avoir des noms cohérents

    # -----------------------------------------------------
    # SÉLECTION DES COLONNES SELON L’INSTRUMENT CHOISI
    # -----------------------------------------------------
    if choix == "Chèques":
        # Si l’utilisateur choisit Chèques → on prend les colonnes Chq
        df = df_banque[["Banque", "Chq_Nombre", "Chq_Montant"]].copy()
        df.columns = ["Banque", "Volume", "Valeur"]

    elif choix == "Virements":
        # Si l’utilisateur choisit Virements → on prend les colonnes Vir
        df = df_banque[["Banque", "Vir_Nombre", "Vir_Montant"]].copy()
        df.columns = ["Banque", "Volume", "Valeur"]

    else:
        # Si l’utilisateur choisit Lettre de change → on prend les colonnes LC
        df = df_banque[["Banque", "LC_Nombre", "LC_Montant"]].copy()
        df.columns = ["Banque", "Volume", "Valeur"]

    # -----------------------------------------------------
    # SUPPRESSION DE LA LIGNE "TOTAL"
    # -----------------------------------------------------
    df = df[df["Banque"] != "Total"]
    # On retire la ligne TOTAL qui fausse les parts de marché

    # -----------------------------------------------------
    # NETTOYAGE DES DONNÉES
    # -----------------------------------------------------
    for col in ["Volume", "Valeur"]:
        df[col] = (
            df[col].astype(str)
            .str.replace(" ", "", regex=False)   # Supprime les espaces
            .str.replace("—", "0", regex=False)  # Tiret long → 0
            .str.replace("-", "0", regex=False)  # Tiret court → 0
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        # Convertit en numérique et remplace les erreurs par 0

    # -----------------------------------------------------
    # SUPPRESSION DES LIGNES VIDES OU INVALIDES
    # -----------------------------------------------------
    df = df[df["Banque"].notna()]      # Supprime les lignes sans nom
    df = df[df["Banque"] != ""]        # Supprime les lignes vides
    df = df[df["Valeur"] > 0]          # Supprime les banques sans valeur

    # -----------------------------------------------------
    # CALCUL DES PARTS DE MARCHÉ
    # -----------------------------------------------------
    total_valeur = df["Valeur"].sum()  
    # Somme totale des montants pour calculer les parts

    df["Part_Valeur"] = df["Valeur"] / total_valeur  
    # Part de marché = valeur banque / valeur totale

    # -----------------------------------------------------
    # TRI DÉCROISSANT DES BANQUES
    # -----------------------------------------------------
    df_sorted = df.sort_values("Part_Valeur", ascending=False).reset_index(drop=True)
    df_sorted.index = df_sorted.index + 1  # commence à 1
    df_sorted["Rang"] = df_sorted.index


    # -----------------------------------------------------
    # FORMATAGE POUR L’AFFICHAGE
    # -----------------------------------------------------
    df_sorted["Part_Valeur"] = df_sorted["Part_Valeur"].apply(
        lambda x: f"{x*100:.2f}%"
    )
    # Conversion en pourcentage lisible

    # -----------------------------------------------------
    # AFFICHAGE DU TABLEAU
    # -----------------------------------------------------
    st.subheader("Tableau des parts de marché")
    df_affichage = format_dataframe(df_sorted)
    st.dataframe(df_affichage)
    # Affiche le tableau formaté

    # =====================================================
    # 🔹 VISUEL 1 : BARRES HORIZONTALES
    # =====================================================
    if type_graph == "Barres horizontales":

        fig, ax = plt.subplots(figsize=(7, 4))

        ax.barh(
            df_sorted["Banque"],
            df_sorted["Part_Valeur"].str.replace("%", "").astype(float),
            color="#1F77B4"
        )
        # Barres horizontales représentant la part de marché

        ax.set_xlabel("Part de marché (%)")
        ax.set_title(f"Parts de Marché {choix} (en Valeur)", fontweight="bold")

        ax.set_facecolor("#F8F9F9")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Ajout des pourcentages à droite des barres
        for i, v in enumerate(df_sorted["Part_Valeur"].str.replace("%", "").astype(float)):
            ax.text(v + 0.3, i, f"{v:.2f}%", va="center", fontsize=8)

        plt.tight_layout()
        st.pyplot(fig)

    # =====================================================
    # 🔹 VISUEL 2 : PARETO (barres + cumul)
    # =====================================================
    else:

        fig, ax1 = plt.subplots(figsize=(7, 4))

        ax1.bar(
            df_sorted["Banque"],
            df_sorted["Part_Valeur"].str.replace("%", "").astype(float),
            color="#1F77B4",
            label="Part individuelle"
        )
        ax1.set_ylabel("Part de marché (%)")
        ax1.set_xticklabels(df_sorted["Banque"], rotation=45, ha="right")

        # Ligne cumulative
        ax2 = ax1.twinx()
        cumul = df_sorted["Part_Valeur"].str.replace("%", "").astype(float).cumsum()
        ax2.plot(df_sorted["Banque"], cumul, color="green", marker="o", label="Cumul (%)")
        ax2.set_ylabel("Cumul des parts (%)")

        ax1.legend(loc="upper left", frameon=True, edgecolor="black", facecolor="white")
        ax2.legend(loc="upper right", frameon=True, edgecolor="black", facecolor="white")

        plt.title(f"Concentration des parts de marché ({choix} en valeur)", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)




# =========================================================
# 3) ONGLET : REJETS (IMPAYÉS)
# =========================================================
with tab3:  
    # Titre principal de l’onglet
    st.header("Analyse des Rejets (Impayés)")

    # -------------------------------------
    # LECTURE DE LA FEUILLE REJETS
    # -------------------------------------
    # Lecture du fichier Excel (feuille "Rejets Impayés")
    df_rejets_impayes = pd.read_excel(uploaded_file, sheet_name="Rejets Impayés")

    # Suppression des colonnes vides (souvent créées par Excel)
    df_rejets_impayes = df_rejets_impayes.dropna(axis=1, how="all")

    # Renommage des colonnes pour plus de clarté
    df_rejets_impayes.columns = [
        "Instrument",        # Type d’instrument (Chèques, Virements…)
        "Volume_Nombre",     # Nombre de rejets en volume
        "Volume_Taux",       # Taux de rejets en volume
        "Valeur_Nombre",     # Montant des rejets en valeur
        "Valeur_Taux"        # Taux de rejets en valeur
    ]

    # -------------------------------------
    # NETTOYAGE DES TAUX (ex: "4,93%" → 4.93)
    # -------------------------------------
    for col in ["Volume_Taux", "Valeur_Taux"]:
        df_rejets_impayes[col] = df_rejets_impayes[col].astype(str)              # Conversion en texte
        df_rejets_impayes[col] = df_rejets_impayes[col].str.replace("%", "")     # Suppression du symbole %
        df_rejets_impayes[col] = df_rejets_impayes[col].str.replace(",", ".")    # Remplacement virgule → point
        df_rejets_impayes[col] = pd.to_numeric(df_rejets_impayes[col], errors="coerce")  # Conversion en nombre

    # -------------------------------------
    # AFFICHAGE DU TABLEAU NETTOYÉ
    # -------------------------------------
    st.subheader("Tableau des rejets par instrument")
    df_affichage = format_dataframe(df_rejets_impayes)
    st.dataframe(df_affichage)

    # -------------------------------------
    # CHOIX DU TYPE DE GRAPHIQUE
    # -------------------------------------
    type_graph = st.selectbox("Type de visuel :", ["Barres groupées", "Lignes comparatives"])

    # Filtrage : on garde uniquement les instruments Chèques et Virements
    df_comparaison = df_rejets_impayes[df_rejets_impayes["Instrument"].isin(["Chèques", "Virements"])]

    # Extraction des instruments pour l’axe X
    instruments = df_comparaison["Instrument"]
    x = np.arange(len(instruments))  # Positions X (0, 1)
    largeur = 0.35                   # Largeur des barres

        # =====================================================
    # 🔹 VISUEL 1 : BARRES GROUPÉES AVEC ANNOTATIONS
    # =====================================================
    if type_graph == "Barres groupées":
        # Si l’utilisateur choisit l’option "Barres groupées", on affiche ce graphique

        fig, ax = plt.subplots(figsize=(6, 3.5))
        # Création de la figure et de l’axe pour le graphique (taille 6x3.5)

        # Barres pour les taux en volume (bleu)
        ax.bar(
            x - largeur/2,                         # Position des barres légèrement à gauche
            df_comparaison["Volume_Taux"],         # Valeurs des taux en volume
            largeur,                                # Largeur des barres
            label="Taux de Rejets en Volume",       # Légende
            color="#1F77B4"                         # Couleur bleue
        )

        # Barres pour les taux en valeur (orange)
        ax.bar(
            x + largeur/2,                         # Position des barres légèrement à droite
            df_comparaison["Valeur_Taux"],         # Valeurs des taux en valeur
            largeur,                                # Largeur des barres
            label="Taux de Rejets en Valeur",       # Légende
            color="#F39C12"                         # Couleur orange
        )

        # 🔹 Ajout des annotations au-dessus des barres
        for i in range(len(instruments)):
            # Annotation pour le taux en volume
            ax.text(
                x[i] - largeur/2,                                   # Position horizontale
                df_comparaison["Volume_Taux"].iloc[i] + 0.001,      # Position verticale légèrement au-dessus de la barre
                f"{df_comparaison['Volume_Taux'].iloc[i]*100:.2f}%",# Texte affiché (en %)
                ha="center", fontsize=8
            )

            # Annotation pour le taux en valeur
            ax.text(
                x[i] + largeur/2,
                df_comparaison["Valeur_Taux"].iloc[i] + 0.001,
                f"{df_comparaison['Valeur_Taux'].iloc[i]*100:.2f}%",
                ha="center", fontsize=8
            )

        # Configuration des axes
        ax.set_xticks(x)                     # Position des étiquettes sur l’axe X
        ax.set_xticklabels(instruments)      # Noms des instruments (Chèques, Virements)
        ax.set_ylabel("Taux (%)")            # Label de l’axe Y
        ax.set_title(
            "Comparaison des taux de rejets : Chèques vs Virements",
            fontweight="bold"
        )                                     # Titre du graphique

        # Légende encadrée
        ax.legend(
            frameon=True, edgecolor="black", facecolor="white"
        )                                     # Légende avec cadre visible

        # Nettoyage visuel
        ax.set_facecolor("#F8F9F9")           # Fond clair
        ax.spines["top"].set_visible(False)   # Suppression de la bordure supérieure
        ax.spines["right"].set_visible(False) # Suppression de la bordure droite

        plt.tight_layout()                    # Ajustement automatique des marges
        st.pyplot(fig)                        # Affichage du graphique dans Streamlit

    # =====================================================
    # 🔹 VISUEL 2 : LIGNES COMPARATIVES (ÉVOLUTION VISUELLE)
    # =====================================================
    else:
        # Si l’utilisateur choisit un autre type de graphique, on affiche les lignes comparatives

        fig, ax = plt.subplots(figsize=(6, 3.5))
        # Création de la figure et de l’axe

        # Ligne bleue pour les taux en volume
        ax.plot(
            instruments,                           # Axe X : instruments
            df_comparaison["Volume_Taux"] * 100,   # Axe Y : taux en %
            marker="o",                             # Marqueurs ronds
            color="#1F77B4",                        # Couleur bleue
            label="Taux de Rejets en Volume"        # Légende
        )

        # Ligne orange pour les taux en valeur
        ax.plot(
            instruments,
            df_comparaison["Valeur_Taux"] * 100,
            marker="o",
            color="#F39C12",
            label="Taux de Rejets en Valeur"
        )

        # Configuration des axes
        ax.set_ylabel("Taux (%)")                  # Label axe Y
        ax.set_title(
            "Évolution comparative des taux de rejets",
            fontweight="bold"
        )                                          # Titre du graphique

        # Légende encadrée
        ax.legend(
            frameon=True, edgecolor="black", facecolor="white"
        )                                          # Légende avec cadre

        # Grille légère pour lisibilité
        ax.grid(alpha=0.3)                         # Grille discrète (alpha = transparence)

        plt.tight_layout()                         # Ajustement des marges
        st.pyplot(fig)                             # Affichage du graphique


# =========================================================
# 4) MATRICE DE POSITIONNEMENT DES BANQUES (ACP/ACH)
# =========================================================
with tab4:

    st.header("Matrice de Positionnement des Banques (ACP/ACH)")

    # -----------------------------------------------------
    # 1) LECTURE DE LA FEUILLE BANQUES
    # -----------------------------------------------------
    df_banque = pd.read_excel(uploaded_file, sheet_name="Evolution par Banque ACPACH")

    df_banque.columns = [
        "N", "Banque",
        "Chq_Nombre", "Chq_Montant",
        "Vir_Nombre", "Vir_Montant",
        "LC_Nombre", "LC_Montant",
        "Total_Nombre", "Total_Montant"
    ]

    df_banque = df_banque[df_banque["Banque"] != "Total"]
    df_banque = df_banque[df_banque["Banque"].notna()]
    df_banque = df_banque[df_banque["Banque"].astype(str).str.strip() != ""]

        # -----------------------------------------------------
    # 2) NETTOYAGE DES VALEURS
    # -----------------------------------------------------
    for col in ["Total_Nombre", "Total_Montant"]:
        # On parcourt les deux colonnes à nettoyer : nombre total et montant total
        df_banque[col] = (
            df_banque[col]
            .astype(str)                      # Conversion en chaîne de caractères pour appliquer les remplacements
            .str.replace(" ", "", regex=False)  # Suppression des espaces (ex : "1 234" → "1234")
            .str.replace("—", "0", regex=False) # Remplacement du tiret long par 0 (valeurs manquantes)
            .str.replace("-", "0", regex=False) # Remplacement du tiret court par 0
            .str.replace(",", "", regex=False)  # Suppression des virgules éventuelles dans les nombres
        )
        df_banque[col] = pd.to_numeric(df_banque[col], errors="coerce").fillna(0)
        # Conversion en numérique ; les valeurs non convertibles deviennent NaN puis remplacées par 0

    df_banque["Montant_Milliards"] = df_banque["Total_Montant"] / 1e9
    # Création d’une nouvelle colonne exprimant le montant en milliards (GNF ou autre devise)


    # -----------------------------------------------------
    # 3) CALCUL DES MOYENNES
    # -----------------------------------------------------
    moyenne_volume = df_banque["Total_Nombre"].mean()
    moyenne_valeur = df_banque["Montant_Milliards"].mean()

    # -----------------------------------------------------
    # 4) CREATION DU SCATTER PLOT AMÉLIORÉ
    # -----------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))

    # Points des banques
    ax.scatter(df_banque["Total_Nombre"], df_banque["Montant_Milliards"], color="royalblue", s=70)

    # Labels des banques
    for i, row in df_banque.iterrows():
        ax.text(row["Total_Nombre"], row["Montant_Milliards"], row["Banque"], fontsize=8, ha="left")

    # Quadrants colorés
    ax.fill_betweenx([0, moyenne_valeur], 0, moyenne_volume, color="#FDEDEC", alpha=0.3)  # Faible activité
    ax.fill_betweenx([moyenne_valeur, df_banque["Montant_Milliards"].max()], 0, moyenne_volume, color="#FCF3CF", alpha=0.3)  # Valeur forte
    ax.fill_betweenx([0, moyenne_valeur], moyenne_volume, df_banque["Total_Nombre"].max(), color="#D6EAF8", alpha=0.3)  # Volume fort
    ax.fill_betweenx([moyenne_valeur, df_banque["Montant_Milliards"].max()], moyenne_volume, df_banque["Total_Nombre"].max(), color="#D5F5E3", alpha=0.3)  # Performantes

    # Lignes de moyenne
    ax.axvline(moyenne_volume, color="red", linestyle="--", label="Moyenne Volume")
    ax.axhline(moyenne_valeur, color="black", linestyle="--", label="Moyenne Valeur")

    # -----------------------------------------------------
    # 5) CONFIGURATION DU GRAPHIQUE
    # -----------------------------------------------------
    ax.set_xlabel("Volume total de transactions (Nombre)")
    ax.set_ylabel("Valeur totale échangée (Milliards GNF)")
    ax.set_title("Matrice de Positionnement : Activité des Banques sur ACP/ACH (2025)", fontweight="bold")

    # 🔹 Légende déplacée au-dessus du milieu (haut centre-droit)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.75, 1.15),  # position légèrement au-dessus et à droite
        frameon=True,
        edgecolor="black",
        facecolor="white",
        fontsize=9
    )

    plt.tight_layout()
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
    #st.dataframe(df_var_rtgs)
    df_affichage = format_dataframe(df_var_rtgs)
    st.dataframe(df_affichage)

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
    
        # -----------------------------------------------------
    # 9) COURBES SUPERPOSÉES : VOLUME 2024 vs 2025
    # -----------------------------------------------------
    st.subheader(f"Comparaison des Volumes RTGS : {annee_A} vs {annee_B}")

    fig3, ax = plt.subplots(figsize=(12, 4))

    # Courbe Volume année A (ex : 2024)
    ax.plot(
        df_var_rtgs["Mois"],
        df_var_rtgs[f"Volume_{annee_A}"],
        marker="o",
        color="red",
        linewidth=2,
        label=f"Volume {annee_A}"
    )

    # Courbe Volume année B (ex : 2025)
    ax.plot(
        df_var_rtgs["Mois"],
        df_var_rtgs[f"Volume_{annee_B}"],
        marker="o",
        color="green",
        linewidth=2,
        label=f"Volume {annee_B}"
    )

    # Mise en forme
    ax.set_ylabel("Volume (Nombre d'opérations)")
    ax.set_title(f"Tendance des Volumes RTGS : {annee_A} vs {annee_B}")
    ax.legend()
    plt.xticks(rotation=60, ha='right')

    st.pyplot(fig3)


# =========================================================
# 6) RÉPARTITION DES RÈGLEMENTS RTGS PAR DEVISE
# =========================================================    
with tab6:

    # -----------------------------------------------------
    # 1) LECTURE DU TABLEAU (5 colonnes)
    # -----------------------------------------------------
    df_devise = pd.read_excel(
        uploaded_file,
        sheet_name="Variation Devise RTGS",   # Feuille contenant les données par devise
        usecols="A:E"                         # On ne lit que les colonnes A à E
    )

    # -----------------------------------------------------
    # 2) NETTOYAGE DES NOMS DE COLONNES
    # -----------------------------------------------------
    df_devise.columns = (
        df_devise.columns
        .astype(str)                          # Convertit les noms en chaînes
        .str.replace("\n", " ")               # Supprime les retours à la ligne
        .str.replace("\r", " ")               # Supprime les retours chariot
        .str.replace("\t", " ")               # Supprime les tabulations
        .str.replace("\xa0", " ")             # Supprime les espaces insécables
        .str.strip()                          # Supprime les espaces en début/fin
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
        st.stop()                             # On arrête l’exécution proprement

    # -----------------------------------------------------
    # TITRE DYNAMIQUE
    # -----------------------------------------------------
    st.header(f"Répartition des Règlements RTGS par Devise – Année {annee}")
    # Affiche un titre contenant l’année détectée automatiquement

    # -----------------------------------------------------
    # 4) SUPPRESSION DES LIGNES VIDES
    # -----------------------------------------------------
    df_devise = df_devise.dropna(subset=[df_devise.columns[0]])
    # Supprime les lignes où la colonne "Devise" est vide

    # -----------------------------------------------------
    # 5) RENOMMAGE DYNAMIQUE DES COLONNES
    # -----------------------------------------------------
    df_devise.columns = [
        "Devise",                              # Nom de la devise (GNF, USD, EUR)
        f"Volume_{annee}",                     # Volume des transactions
        f"Valeur_{annee}_devise",              # Valeur dans la devise d’origine
        "ContreValeur_GNF",                    # Valeur convertie en GNF
        "Part_marche"                          # Part de marché en %
    ]

    # -----------------------------------------------------
    # 6) NETTOYAGE DES VALEURS NUMÉRIQUES
    # -----------------------------------------------------
    for col in [f"Volume_{annee}", f"Valeur_{annee}_devise", "ContreValeur_GNF"]:
        df_devise[col] = (
            df_devise[col]
            .astype(str)                       # Convertit en texte pour nettoyage
            .str.replace(" ", "")              # Supprime les espaces
            .str.replace(",", ".")             # Remplace virgule → point
        )
        df_devise[col] = pd.to_numeric(df_devise[col], errors="coerce")
        # Convertit en nombre ; remplace les erreurs par NaN

    # Nettoyage de la colonne Part_marche (%)
    df_devise["Part_marche"] = (
        df_devise["Part_marche"]
        .astype(str)
        .str.replace("%", "")                  # Supprime le symbole %
        .str.replace(",", ".")                 # Remplace virgule → point
    )
    df_devise["Part_marche"] = pd.to_numeric(df_devise["Part_marche"], errors="coerce")
    # Convertit en nombre décimal (ex : 12.5)

    # -----------------------------------------------------
    # 7) SUPPRESSION DES NaN ET DE LA LIGNE TOTAL
    # -----------------------------------------------------
    df_devise = df_devise.dropna(subset=["Part_marche"])
    # Supprime les lignes où la part de marché est vide

    df_devise = df_devise[df_devise["Devise"] != "TOTAL"]
    # Supprime la ligne TOTAL qui fausserait les graphiques

    # -----------------------------------------------------
    # 8) AFFICHAGE DU TABLEAU
    # -----------------------------------------------------
    st.subheader(f"Tableau – Répartition par devise de règlement ({annee})")
    df_affichage = format_dataframe(df_devise)  # Mise en forme (séparateurs, alignement)
    st.dataframe(df_affichage)                  # Affichage dans Streamlit

    # -----------------------------------------------------
    # 9) GRAPHIQUE DONUT AVEC LÉGENDE
    # -----------------------------------------------------
    st.subheader(f"Répartition des Règlements RTGS par Devise (en Valeur) – {annee}")

    labels = df_devise["Devise"]               # Liste des devises
    valeurs = df_devise["Part_marche"]         # Part de marché en %

    couleurs = ["#4CAF50", "#2196F3", "#9C27B0"]  # Couleurs : GNF, USD, EUR

    fig, ax = plt.subplots(figsize=(6, 6))     # Création du graphique

    wedges, texts, autotexts = ax.pie(
        valeurs,                               # Valeurs à représenter
        labels=None,                           # Pas de labels sur le donut
        colors=couleurs,                       # Couleurs définies
        autopct="%1.1f%%",                     # Format des pourcentages
        startangle=90,                         # Rotation du graphique
        pctdistance=0.85                       # Position du texte
    )

    # Ajout du cercle blanc au centre → donut
    centre = plt.Circle((0, 0), 0.60, fc="white")
    fig.gca().add_artist(centre)

    # Légende à droite
    ax.legend(
        labels,
        title="Devise",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    plt.title(f"Répartition des Règlements RTGS par Devise (en Valeur) – {annee}")
    st.pyplot(fig)                             # Affichage final du graphique


# =========================================================
# 7) ONGLET : CONTRIBUTION DES BANQUES AU SNP
# =========================================================
with tab7:
    # On ouvre le 7ᵉ onglet de l’application Streamlit

    st.header("Contribution des Banques au Système National de Paiement (SNP)")
    # Titre principal affiché en haut de l’onglet

    # -----------------------------------------------------
    # 1) LECTURE SANS HEADER
    # -----------------------------------------------------
    df_raw = pd.read_excel(uploaded_file, sheet_name="Variation Contribution SNP", header=None)
    # Lecture brute de la feuille : pas d’en-têtes → header=None

    # -----------------------------------------------------
    # 2) EXTRACTION DES ANNÉES DANS LA LIGNE 1
    # -----------------------------------------------------
    ligne_annees = df_raw.iloc[1].astype(str).fillna("")
    # On récupère la ligne 2 (index 1) qui contient les années, convertie en texte

    annees = []
    for val in ligne_annees:
        match = re.search(r"(20\d{2})", val)   # Recherche d’une année au format 20XX
        if match:
            annees.append(match.group(1))      # Ajout de l’année trouvée

    annees = list(dict.fromkeys(annees))       # Suppression des doublons en conservant l’ordre

    if len(annees) < 2:
        st.error("Impossible de détecter les années dans la feuille Contribution SNP.")
        st.write("Valeurs trouvées dans la ligne 2 :", ligne_annees.tolist())
        st.stop()                              # Arrêt propre si les années ne sont pas détectées

    annee1, annee2 = annees[:2]                # On prend les deux premières années détectées
    st.success(f"Années détectées : {annee1} et {annee2}")

    # -----------------------------------------------------
    # 3) RECONSTRUCTION DU DATAFRAME
    # -----------------------------------------------------
    df_snp = df_raw.iloc[2:].copy()            # On prend les lignes à partir de la ligne 3
    df_snp.columns = [
        "N",
        "Banque",
        f"Contribution_{annee1}", f"Contribution_{annee2}",
        f"Service_Bureau_{annee1}", f"Service_Bureau_{annee2}",
        f"Total_{annee1}", f"Total_{annee2}",
        "Variation"
    ]
    # Attribution manuelle des noms de colonnes avec les années détectées

    # -----------------------------------------------------
    # 4) NETTOYAGE DES VALEURS
    # -----------------------------------------------------
    for col in [
        f"Contribution_{annee1}", f"Contribution_{annee2}",
        f"Service_Bureau_{annee1}", f"Service_Bureau_{annee2}",
        f"Total_{annee1}", f"Total_{annee2}"
    ]:
        df_snp[col] = (
            df_snp[col].astype(str)            # Conversion en texte pour nettoyage
            .str.replace(" ", "")              # Suppression des espaces
            .str.replace(",", ".")             # Remplacement virgule → point
            .str.replace("-", "0")             # Tirets remplacés par 0
        )
        df_snp[col] = pd.to_numeric(df_snp[col], errors="coerce")
        # Conversion en numérique ; erreurs → NaN

    df_snp["Variation"] = (
        df_snp["Variation"].astype(str)
        .str.replace("%", "")                  # Suppression du symbole %
        .str.replace(",", ".")                 # Remplacement virgule → point
    )
    df_snp["Variation"] = pd.to_numeric(df_snp["Variation"], errors="coerce")
    # Variation convertie en nombre décimal

    df_snp = df_snp.dropna(subset=["Banque"])
    # Suppression des lignes sans nom de banque

    # -----------------------------------------------------
    # 5) TABLEAU
    # -----------------------------------------------------
    st.subheader(f"Tableau – Contribution SNP ({annee1}–{annee2})")
    df_affichage = format_dataframe(df_snp)    # Mise en forme (séparateurs, alignement)
    st.dataframe(df_affichage)                 # Affichage du tableau

    # -----------------------------------------------------
    # 6) GRAPHIQUE EN BARRES HORIZONTALES AVEC VALEURS EN MILLIONS
    # -----------------------------------------------------
    df_plot = df_snp.sort_values(f"Total_{annee2}", ascending=True)
    # Tri des banques par contribution croissante (année 2)

    fig, ax = plt.subplots(figsize=(8, 10))
    couleurs = plt.cm.GnBu(df_plot[f"Total_{annee2}"] / df_plot[f"Total_{annee2}"].max())
    # Palette de couleurs graduelle selon la valeur

    bars = ax.barh(df_plot["Banque"], df_plot[f"Total_{annee2}"], color=couleurs)
    # Barres horizontales représentant la contribution totale

    ax.set_title(f"Classement des Contributions au SNP ({annee2})", fontweight="bold")
    ax.set_xlabel("Montant de la Contribution (GNF)")
    ax.set_ylabel("Banques")

    # Affichage des valeurs au-dessus des barres en millions
    for bar in bars:
        valeur_millions = bar.get_width() / 1e6
        ax.text(
            bar.get_width() + (df_plot[f"Total_{annee2}"].max() * 0.005),
            bar.get_y() + bar.get_height() / 2,
            f"{valeur_millions:.0f} M",
            va="center", fontsize=8, color="black"
        )
    # Ajoute la valeur en millions à droite de chaque barre

    plt.tight_layout()
    st.pyplot(fig)                             # Affichage du graphique

    # -----------------------------------------------------
    # 7) ANALYSE AUTOMATIQUE
    # -----------------------------------------------------
    total_annee1 = df_snp[f"Total_{annee1}"].sum()   # Somme totale année 1
    total_annee2 = df_snp[f"Total_{annee2}"].sum()   # Somme totale année 2
    croissance = (total_annee2 - total_annee1) / total_annee1 * 100
    # Calcul du taux de croissance global

    top = df_plot.iloc[-1]                           # Banque ayant la plus forte contribution

    st.write(f"""
    **Total {annee2} :** {total_annee2:,.0f} GNF  
    **Croissance :** {croissance:.2f} %  
    **Leader :** {top["Banque"]} ({top[f"Total_{annee2}"]/1e6:.0f} M GNF)
    """)
    # Analyse automatique affichée sous forme de texte
