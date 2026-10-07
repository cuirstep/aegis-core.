class MetaRouter:
    """
    Le Meta-Router d'AEGIS-CORE : Analyse la requête de l'utilisateur,
    détermine la stratégie de réponse et coordonne les modules.
    """
    def __init__(self):
        self.version = "2.0-beta"

    def analyser_requete(self, prompt):
        """Analyse le texte pour adapter le comportement d'AEGIS."""
        prompt_lower = prompt.lower()
        
        # Détection du domaine ou de l'intention
        if "code" in prompt_lower or "python" in prompt_lower or "script" in prompt_lower:
            return {"mode": "TECHNIQUE", "priorite": "Haute", "description": "Génération ou analyse de code source."}
        elif "stratégie" in prompt_lower or "projet" in prompt_lower or "plan" in prompt_lower:
            return {"mode": "STRATÉGIQUE", "priorite": "Maximale", "description": "Planification et structuration de projet étape par étape."}
        elif "qui es-tu" in prompt_lower or "aegis" in prompt_lower:
            return {"mode": "IDENTITÉ", "priorite": "Standard", "description": "Rappel des directives système AEGIS-CORE."}
        else:
            return {"mode": "STANDARD", "priorite": "Normale", "description": "Discussion générale et assistance polyvalente."}

    def router_reponse(self, prompt, bibliotheque_instance):
        """Gère l'acheminement de la réponse en fonction de l'analyse."""
        contexte_analyse = self.analyser_requete(prompt)
        
        # Si la requête concerne un personnage ou une figure de la base
        kb = bibliotheque_instance.charger_connaissances()
        characters = kb.get("characters", [])
        
        reponse_specifique = None
        for char in characters:
            if char["name"].lower() in prompt.lower() or char["id_code"] in prompt.lower():
                reponse_specifique = f"📊 **Profil identifié dans les archives** : {char['name']} ({char['classification']})\n- **Domaine** : {char['operational_domain']}\n- **Biographie** : {char['biography_summary']}\n- *Citation signature* : \"{char['signature_quote']}\""
                break

        return {
            "analyse": contexte_analyse,
            "information_archive": reponse_specifique
        }
