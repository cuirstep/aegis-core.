import sqlite3
import hashlib
import os
import json

DB_FILE = "aegis_core.db"

def init_db():
    """Initialise la base de données SQLite avec une table sécurisée pour les profils."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            config TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    """Hache un mot de passe avec un sel pour la sécurité."""
    if not salt:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return pwd_hash, salt

def register_user(username, password):
    """Enregistre un nouvel utilisateur avec un mot de passe haché."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Vérifier si l'utilisateur existe déjà
    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Ce pseudo existe déjà."
    
    pwd_hash, salt = hash_password(password)
    cursor.execute('INSERT INTO users (username, password_hash, salt, config) VALUES (?, ?, ?, ?)',
                   (username, pwd_hash, salt, '{}'))
    conn.commit()
    conn.close()
    return True, "Compte créé avec succès."

def verify_user(username, password):
    """Vérifie les identifiants d'un utilisateur."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash, salt FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False
    
    stored_hash, salt = row
    pwd_hash, _ = hash_password(password, salt)
    return pwd_hash == stored_hash

def init_chat_db():
    """Initialise la table pour stocker les messages de chat."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            session_name TEXT,
            messages TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

def save_user_session(username, session_name, messages_list):
    """Sauvegarde ou met à jour les messages d'une session pour un utilisateur."""
    init_chat_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Convertir la liste des messages en format JSON texte
    messages_json = json.dumps(messages_list, ensure_ascii=False)
    
    # Vérifier si la session existe déjà pour cet utilisateur
    cursor.execute('SELECT id FROM chat_sessions WHERE username = ? AND session_name = ?', (username, session_name))
    row = cursor.fetchone()
    
    if row:
        cursor.execute('UPDATE chat_sessions SET messages = ? WHERE username = ? AND session_name = ?', 
                       (messages_json, username, session_name))
    else:
        cursor.execute('INSERT INTO chat_sessions (username, session_name, messages) VALUES (?, ?, ?)', 
                       (messages_json, username, session_name))
        
    conn.commit()
    conn.close()

def load_user_sessions(username):
    """Charge toutes les sessions de chat d'un utilisateur depuis SQLite."""
    init_chat_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT session_name, messages FROM chat_sessions WHERE username = ?', (username,))
    rows = cursor.fetchall()
    conn.close()
    
    sessions = {}
    for session_name, messages_json in rows:
        try:
            sessions[session_name] = json.loads(messages_json)
        except Exception:
            sessions[session_name] = []
            
    # Si l'utilisateur n'a aucune session, on lui en crée une par défaut
    if not sessions:
        sessions["Discussion 1"] = []
        
    return sessions
