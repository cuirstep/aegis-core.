class GrandeBibliotheque:
    def __init__(self):
        # Système de stockage mémoriel centralisé pour le MVP
        self.archives = {}
        print("[GRANDE BIBLIOTHÈQUE] Espace de stockage mémoriel initialisé.")

    def stocker(self, cle: str, contenu: str):
        self.archives[cle] = contenu
        print(f"[Grande Bibliothèque] Élément enregistré avec succès sous la clé : '{cle}'")

    def recuperer(self, cle: str):
        if cle in self.archives:
            print(f"[Grande Bibliothèque] Récupération de l'élément : '{cle}'")
            return self.archives[cle]
        else:
            return "Erreur : Élément introuvable dans les archives."
