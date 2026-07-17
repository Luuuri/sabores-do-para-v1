# ==========================================================================
# crud_clientes.py  —  CREATE, READ, UPDATE, DELETE DE CLIENTES
# ==========================================================================
# CRUD completo para operações com o banco de dados
#============================================================================

from app.database.db_config import conectar
from app.model.endereco_model import EnderecoModel


class ClienteCrud:
    """
    Responsável por todas as operações SQL da tabela `cliente`.
    """
        
    def _get_conn(self):
        return conectar()

    def _proximo_id(self, conn) -> int:
        cursor = conn.cursor()
        cursor.execute("SELECT IFNULL(MAX(id_cliente), 0) + 1 FROM clientes")
        resultado = cursor.fetchone()[0]
        cursor.close()
        return resultado
    
    # =========================
    # CREATE
    # =========================
    def criar(self, dados: dict):
        conn = conectar()
        try:
            novo_id = self._proximo_id(conn)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes
                    (id_cliente, nome, telefone, cpf, email, cep, numero, cidade, bairro, logradouro, complemento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                novo_id,
                dados.get("nome"),
                dados.get("telefone"),
                dados.get("cpf"),
                dados.get("email"),
                dados.get("cep"),
                dados.get("numero"),
                dados.get("cidade"),
                dados.get("bairro"),
                dados.get("logradouro"),
                dados.get("complemento")
            ))
            conn.commit()
            cursor.close()
        finally:
            pass

    # =========================
    # UPDATE
    # =========================

    def atualizar(self, id_cliente: int, dados: dict):
        conn = self._get_conn()
        try:
            campos = [f"{chave} = %s" for chave in dados]
            valores = list(dados.values()) + [id_cliente]
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE clientes
                SET {', '.join(campos)}
                WHERE id_cliente = %s
            """, tuple(valores))
            conn.commit()
            cursor.close()
        finally:
            pass

    # =========================
    # DELETE
    # =========================

    def deletar(self, id_cliente: int):
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
            conn.commit()
            cursor.close()
        finally:
            pass
    # =========================
    # READ (1 registro)
    # =========================
    def buscar_por_id(self, id_cliente: int):
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
            resultado = cursor.fetchone()
            cursor.close()
            if resultado:
                endereco_model = EnderecoModel()
                resultado["enderecos"] = endereco_model.listar_por_cliente(id_cliente)
            return resultado
        finally:
            pass

    # =========================
    # READ (todos)
    # =========================
    def listar_todos(self) -> list:
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes ORDER BY id_cliente DESC")
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        finally:
            pass

    # =========================
    # READ (busca por termo)
    # =========================
    def buscar_por_termo(self, termo: str) -> list:
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            busca = f"%{termo}%"
            cursor.execute("""
                SELECT * FROM clientes
                WHERE nome LIKE %s
                   OR telefone LIKE %s
                   OR cpf LIKE %s
                   OR email LIKE %s
                ORDER BY id_cliente DESC
            """, (busca, busca, busca, busca))
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        finally:
            pass
