import time
from harness import SecurityHarness

class AegisAgent:
    def __init__(self):
        self.harness = SecurityHarness()
        self.status = "IDLE"

    def run_task_sequence(self, tasks):
        """Exécute une liste de tâches de manière autonome."""
        for task in tasks:
            print(f"\n[AEGIS] Traitement de la tâche : {task['name']}")
            
            # Vérification des permissions
            if task.get("requires_permission"):
                allowed = self.harness.request_permission(
                    task["name"], 
                    task.get("details", "Pas de détails")
                )
                if not allowed:
                    print(f"[AEGIS] Action bloquée par le Commandant. Pause du processus.")
                    self.status = "PAUSED_WAITING_FOR_COMMANDER"
                    return False
            
            # Simulation du travail
            print(f"[AEGIS] Exécution de : {task['name']}...")
            time.sleep(1)
            print(f"[AEGIS] Tâche terminée avec succès.")
            
        self.status = "COMPLETED"
        return True
