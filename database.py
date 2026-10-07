"""
Module : database.py
Projet : AEGIS-CORE — OS IA Sécurisé à profil hautes responsabilités
Description : Gestion de la base de données SQLite locale pour l'historique des missions.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Any

DB_NAME = "aegis_secure.db"

def init_db() -> None:
    """
    Initialise la base de données locale et crée la table 'missions_logs' 
    si elle n'existe pas encore.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missions_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            directive_user TEXT NOT NULL,
            aegis_response TEXT NOT NULL,
            security_status TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def log_interaction(directive_user: str, aegis_response: str, security_status: str) -> None:
    """
    Enregistre une nouvelle interaction dans la table 'missions_logs'.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO missions_logs (timestamp, directive_user, aegis_response, security_status)
        VALUES (?, ?, ?, ?)
    """, (directive_user, aegis_response, security_status, timestamp))
    
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 10) -> List[Tuple[Any, ...]]:
    """
    Récupère les derniers rapports de mission enregistrés.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, timestamp, directive_user, aegis_response, security_status
        FROM missions_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    logs = cursor.fetchall()
    conn.close()
    return logs
