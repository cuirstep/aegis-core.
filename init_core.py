"""
Module : init_core.py
Description : Charge la base de connaissances initiale dans la base SQLite.
"""

import json
from database import init_db, log_interaction

def load_initial_knowledge():
    init_db()
    
    try:
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            kb = json.load(f)
            
        identity = kb.get("system_identity", {})
        welcome_msg = f"Système initialisé : {identity.get('name')} v{identity.get('version')}. Prêt pour le traitement multi-sujets."
        
        log_interaction(
            directive_user="[SYSTEM_INIT] Chargement du socle de connaissances",
            aegis_response=welcome_msg,
            security_status="VALIDÉ"
        )
        print("[+] Base de connaissances de base injectée avec succès dans AEGIS-CORE.")
        
    except FileNotFoundError:
        print("[-] Fichier knowledge_base.json introuvable.")

if __name__ == "__main__":
    load_initial_knowledge()
