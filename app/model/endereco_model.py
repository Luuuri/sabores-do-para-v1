from app.database.db_config import conectar


class EnderecoModel:

    def _executar(self, sql, params=None):
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        conn.commit()
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado

    def listar_por_cliente(self, id_cliente: int) -> list:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM enderecos WHERE id_cliente = %s ORDER BY principal DESC, id_endereco ASC",
            (id_cliente,)
        )
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado

    def buscar(self, id_endereco: int) -> dict | None:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM enderecos WHERE id_endereco = %s", (id_endereco,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return resultado

    def salvar(self, dados: dict) -> int | None:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor()
        id_endereco = dados.get("id_endereco")
        if id_endereco:
            campos = [f"{k} = %s" for k in dados.keys() if k != "id_endereco"]
            valores = [v for k, v in dados.items() if k != "id_endereco"]
            valores.append(id_endereco)
            cursor.execute(
                f"UPDATE enderecos SET {', '.join(campos)} WHERE id_endereco = %s",
                valores
            )
        else:
            cursor.execute("""
                INSERT INTO enderecos (id_cliente, apelido, cep, logradouro, numero,
                                       bairro, cidade, complemento, principal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados.get("id_cliente"),
                dados.get("apelido"),
                dados.get("cep"),
                dados.get("logradouro"),
                dados.get("numero"),
                dados.get("bairro"),
                dados.get("cidade"),
                dados.get("complemento"),
                dados.get("principal", 0),
            ))
            id_endereco = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return id_endereco

    def excluir(self, id_endereco: int) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM enderecos WHERE id_endereco = %s", (id_endereco,))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def definir_principal(self, id_endereco: int, id_cliente: int) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE enderecos SET principal = 0 WHERE id_cliente = %s", (id_cliente,)
        )
        cursor.execute(
            "UPDATE enderecos SET principal = 1 WHERE id_endereco = %s", (id_endereco,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
