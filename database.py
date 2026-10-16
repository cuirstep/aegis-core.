import sqlite3
import hashlib
import os

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
