import hashlib
import mysql.connector
import traceback
from app.database.db_config import conectar


def autenticar_usuario(email: str, senha: str) -> dict | None:
    """
    Valida email e senha contra o banco de funcionários.
    Retorna os dados do usuário se autenticado, None se inválido.
    """
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    # Conecta ao banco e busca o usuário; trata erros de conexão/consulta
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_funcionario, nome, email, telefone, cargo, nivel_acesso, ativo
            FROM funcionario
            WHERE email = %s AND senha_hash = %s AND ativo = 1
            """,
            (email, senha_hash),
        )
        resultado = cursor.fetchone()
        return resultado
    except mysql.connector.Error:
        traceback.print_exc()
        return None

def autenticar_admin_por_senha(senha: str) -> bool:
    """Verifica se a senha informada pertence a algum administrador ativo."""
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_funcionario FROM funcionario
            WHERE senha_hash = %s AND nivel_acesso = 'administrador' AND ativo = 1
            """,
            (senha_hash,)
        )
        return cursor.fetchone() is not None
    except mysql.connector.Error:
        traceback.print_exc()
        return False