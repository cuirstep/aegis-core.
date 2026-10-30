import os
import time

class AegisAgentCore:
    def __init__(self):
        self.rules = self.load_rules()
        self.status = "ACTIF"

    def load_rules(self):
        """Charge le règlement de l'agent."""
        if os.path.exists("rules.txt"):
            with open("rules.txt", "r", encoding="utf-8") as f:
                return f.read()
        return "Aucun règlement trouvé."

    def execute_workflow(self):
        """Boucle d'exécution continue des tâches."""
        print("[AEGIS CORE] Démarrage du système autonome...")
        print(f"[RÈGLES CHARGÉES] :\n{self.rules[:150]}...")
        
        while True:
            # Ici l'agent exécute ses tâches en arrière-plan
            # S'il a besoin de l'humain, il bascule self.status = "EN_PAUSE"
            time.sleep(15)

if __name__ == "__main__":
    agent = AegisAgentCore()
    agent.execute_workflow()
