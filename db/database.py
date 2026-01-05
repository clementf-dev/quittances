# Ce fichier sert à ouvrir la DB

import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "quittances.db"

def get_connection():
    return sqlite3.connect(DB_FILE)