from app.database.db_config import conectar


class TaxaEntregaModel:

    def listar_todas(self) -> list:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM taxa_entrega ORDER BY bairro ASC")
        resultado = cursor.fetchall()
        cursor.close()
        return resultado

    def buscar_por_bairro(self, bairro: str) -> dict | None:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM taxa_entrega WHERE bairro = %s AND ativo = 1",
            (bairro,)
        )
        resultado = cursor.fetchone()
        cursor.close()
        return resultado

    def salvar(self, dados: dict) -> int | None:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor()
        id_taxa = dados.get("id_taxa")
        if id_taxa:
            campos = [f"{k} = %s" for k in dados.keys() if k != "id_taxa"]
            valores = [v for k, v in dados.items() if k != "id_taxa"]
            valores.append(id_taxa)
            cursor.execute(
                f"UPDATE taxa_entrega SET {', '.join(campos)} WHERE id_taxa = %s",
                valores
            )
        else:
            cursor.execute(
                "INSERT INTO taxa_entrega (bairro, valor, ativo) VALUES (%s, %s, %s)",
                (dados.get("bairro"), dados.get("valor", 0.0), dados.get("ativo", 1))
            )
            id_taxa = cursor.lastrowid
        conn.commit()
        cursor.close()
        return id_taxa

    def excluir(self, id_taxa: int) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM taxa_entrega WHERE id_taxa = %s", (id_taxa,))
        conn.commit()
        cursor.close()
        return True
