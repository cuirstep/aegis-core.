import json
import os

class BibliothequeMemoire:
    """
    La Grande Bibliothèque d'AEGIS-CORE : Gère l'archivage, 
    la lecture et l'écriture des connaissances et des historiques.
    """
    def __init__(self, base_path="base_de_connaissances.json"):
        self.base_path = base_path

    def charger_connaissances(self):
        """Charge l'intégralité de la base de connaissances (personnages, directives)."""
        if os.path.exists(self.base_path):
            with open(self.base_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"erreur": "Fichier JSON corrompu"}
        return {}

    def rechercher_personnage(self, id_code_recherche):
        """Recherche un profil spécifique par son id_code dans la base."""
        data = self.charger_connaissances()
        characters = data.get("characters", [])
        for char in characters:
            if char.get("id_code") == id_code_recherche:
                return char
        return None

    def sauvegarder_donnees(self, data):
        """Sauvegarde de nouvelles données dans la base."""
        with open(self.base_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
