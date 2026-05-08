def format_dataframe(df):
    """
    Formate automatiquement les colonnes numériques et pourcentages
    d'un DataFrame selon le style français.
    """

    # ------------------------------------------------------------
    # Fonction interne : formate un nombre classique
    # Exemple : 12345.67 → "12 345,67"
    # ------------------------------------------------------------
    def format_number(x):
        if isinstance(x, (int, float)):  # Vérifie que la valeur est numérique
            return f"{x:,.2f}".replace(",", " ").replace(".", ",")  
            # 1) format US → "12,345.67"
            # 2) remplace virgules → espaces → "12 345.67"
            # 3) remplace point → virgule → "12 345,67"
        return x  # Si ce n'est pas un nombre, on retourne tel quel

    # ------------------------------------------------------------
    # Fonction interne : formate un pourcentage
    # Exemple : 0.2175 → "21,75 %"
    # ------------------------------------------------------------
    def format_percent(x):
        if isinstance(x, (int, float)):  # Vérifie que la valeur est numérique
            return f"{x*100:,.2f} %".replace(",", " ").replace(".", ",")
            # Multiplie par 100 → format → remplace séparateurs → ajoute "%"
        return x

    # ------------------------------------------------------------
    # Copie du DataFrame pour éviter de modifier l’original
    # ------------------------------------------------------------
    df_affichage = df.copy()

    # ------------------------------------------------------------
    # Détection automatique des colonnes de pourcentage
    # Toute colonne contenant "Variation" ou "Part" sera formatée en %
    # ------------------------------------------------------------
    cols_pourcent = [c for c in df.columns if "Variation" in c or "Part" in c]

    # ------------------------------------------------------------
    # Détection automatique des colonnes numériques classiques
    # On exclut les colonnes texte comme "Instrument" ou "Banque"
    # ------------------------------------------------------------
    cols_nombres = [
        c for c in df.columns 
        if c not in cols_pourcent and c not in ["Instrument", "Banque"]
    ]

    # ------------------------------------------------------------
    # Application du formatage pour les colonnes numériques
    # ------------------------------------------------------------
    for col in cols_nombres:
        df_affichage[col] = df_affichage[col].apply(format_number)

    # ------------------------------------------------------------
    # Application du formatage pour les colonnes en pourcentage
    # ------------------------------------------------------------
    for col in cols_pourcent:
        df_affichage[col] = df_affichage[col].apply(format_percent)

    # ------------------------------------------------------------
    # Retourne le DataFrame formaté, prêt pour affichage Streamlit
    # ------------------------------------------------------------
    return df_affichage
