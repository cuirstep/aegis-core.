om agent_engine import AegisAgent

def main():
    agent = AegisAgent()
    
    print("==========================================")
    print("   INTERFACE AEGIS-JARVIS - IPAD READY    ")
    print("==========================================")
    
    # Définition d'un exemple de plan de travail
    todo_list = [
        {"name": "read_logs", "details": "Lecture des fichiers journaux", "requires_permission": False},
        {"name": "optimize_code", "details": "Nettoyage du code local", "requires_permission": False},
        {"name": "delete_file", "details": "Suppression d'anciens fichiers temporaires", "requires_permission": True}
    ]

    print("\nCommandant, AEGIS est prêt.")
    choice = input("Lancer la séquence de tâches ? (o/n) : ")
    
    if choice.lower() == 'o':
        agent.run_task_sequence(todo_list)

if __name__ == "__main__":
    main()
