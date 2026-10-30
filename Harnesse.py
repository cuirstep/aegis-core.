import json

class SecurityHarness:
    def __init__(self):
        # Liste des actions nécessitant une validation manuelle
        self.restricted_actions = [
            "delete_file", 
            "execute_external_script", 
            "access_network", 
            "modify_system"
        ]

    def request_permission(self, action_name: str, details: str) -> bool:
        """Demande au Commandant (toi) la permission d'exécuter une action."""
        if action_name in self.restricted_actions:
            print(f"\n[DEMANDE DE PERMISSION - JARVIS]")
            print(f"Action demandée : {action_name}")
            print(f"Détails : {details}")
            
            response = input("Autoriser cette action ? (o/n) : ").strip().lower()
            return response == 'o'
        return True
