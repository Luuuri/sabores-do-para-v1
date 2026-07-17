# =============================================================
# db_config.py  —  CONECTA COM .env
# =============================================================
# FLUXO:
#   .env → db_condig.py → CRUD → MySQL
#
# COMO CONECTAR COM O SQL:
#   Digite suas informações no .env
#   Use from app.backend.db_config import DB_CONFIG no seu CRUD
#   Rode connect.py ou no terminal: python -m database.connection.connect
# =============================================================

from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()  # lê o .env automaticamente

DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     os.getenv("DB_PORT"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

_conn = None

def conectar():
    global _conn
    try:
        if _conn is None or not _conn.is_connected():
            _conn = mysql.connector.connect(**DB_CONFIG)
            cursor = _conn.cursor()
            cursor.execute("SET session time_zone = 'America/Sao_Paulo'")
            cursor.close()
        return _conn
    except Exception as erro:
        print("Erro ao conectar:", erro)
        return None
