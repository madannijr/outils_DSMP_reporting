import streamlit as st   # Import de Streamlit pour créer l'interface utilisateur


# ============================
# FONCTION : Page de connexion DSMP
# ============================
def login():
    # Injection de CSS pour améliorer le design de la page de connexion
    st.markdown(
        """
        <style>
        .centered {
            display: flex;                     /* Active Flexbox */
            flex-direction: column;            /* Empile les éléments verticalement */
            align-items: center;               /* Centre horizontalement */
            justify-content: center;           /* Centre verticalement */
            margin-top: 50px;                  /* Espace en haut */
        }
        .login-box {
            background-color: #1e1e1e;         /* Fond sombre */
            padding: 30px;                     /* Marges internes */
            border-radius: 10px;               /* Coins arrondis */
            width: 350px;                      /* Largeur fixe */
            
        }
        .logo {
            width: 120px;                      /* Taille du logo */
            margin-bottom: 20px;               /* Espace sous le logo */
        }
        </style>
        """,
        unsafe_allow_html=True                 # Autorise HTML/CSS dans Streamlit
    )

    # Conteneur centré pour tout le contenu
    st.markdown('<div class="centered">', unsafe_allow_html=True)

    # Affichage du logo BCRG (doit être dans le même dossier que ton app)
    st.image("BCRG_LOGO.png", width=120)

    # Boîte contenant le formulaire de connexion
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    # Titre de la page de connexion
    st.markdown("<h3 style='text-align:center;'>Authentification</h3>", unsafe_allow_html=True)

    # Champs de saisie pour l'utilisateur et le mot de passe
    user = st.text_input("Identifiant ")
    pwd = st.text_input("Mot de passe", type="password")  # Mot de passe masqué

    # Bouton de connexion
    if st.button("Se connecter"):
        # Vérification des identifiants dans secrets.toml
        if user == st.secrets["auth"]["username"] and pwd == st.secrets["auth"]["password"]:
            st.session_state["logged"] = True   # On enregistre que l'utilisateur est connecté
        else:
            st.error("Identifiants incorrects") # Message d'erreur si mauvais identifiants

    # Fermeture des balises HTML ouvertes
    st.markdown("</div></div>", unsafe_allow_html=True)



# ============================
# FONCTION : Vérification d'accès
# ============================
def check_auth():
    """
    Cette fonction vérifie si l'utilisateur est connecté.
    Si ce n'est pas le cas, elle affiche la page de login
    et arrête l'exécution du reste de l'application.
    """
    if "logged" not in st.session_state or not st.session_state["logged"]:
        login()     # Affiche la page de connexion
        st.stop()   # Stoppe l'exécution du reste de l'application tant que non connecté
