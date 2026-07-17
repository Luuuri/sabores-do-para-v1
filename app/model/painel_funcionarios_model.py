from app.database.db_config import conectar


class FuncionarioCrud:
    """
    Responsável por todas as operações SQL da tabela `funcionario`.
    Nunca chame esta classe diretamente na tela — use o service.
    """

    def _get_conn(self):
        """
        Abre (ou reabre) a conexão com o banco a cada operação.
        Evita erros de conexão perdida após inatividade.
        """
        return conectar()

    def _proximo_id(self, conn) -> int:
        """
        Calcula o próximo ID manualmente.
        
        Regra:
          - Tabela vazia       → retorna 1
          - Tabela com dados   → retorna max(id) + 1
        
        Por que não usar AUTO_INCREMENT?
          AUTO_INCREMENT nunca reutiliza IDs deletados.
          Ex: deletou o 3, o próximo seria 4, não 3.
          Com este método, se deletar todos, o próximo é 1.
        """
        cursor = conn.cursor()
        cursor.execute("SELECT IFNULL(MAX(id_funcionario), 0) + 1 FROM funcionario")
        resultado = cursor.fetchone()[0]
        cursor.close()
        return resultado

    def _garantir_coluna_telefone(self, conn):
        cursor = conn.cursor()
        try:
            cursor.execute("SHOW COLUMNS FROM funcionario LIKE 'telefone'")
            if cursor.fetchone():
                return
            cursor.execute("ALTER TABLE funcionario ADD COLUMN telefone VARCHAR(20) NULL AFTER email")
            conn.commit()
        finally:
            cursor.close()

    # =========================
    # CREATE
    # =========================
    def criar(self, dados: dict):
        """
        Insere um novo funcionário no banco.
        
        O service chama: funcionario_crud.criar(dados_convertidos)
        SQL gerado:
          INSERT INTO funcionario (id_funcionario, nome, email, ...) VALUES (...)
        """
        conn = conectar()
        try:
            self._garantir_coluna_telefone(conn)
            novo_id = self._proximo_id(conn)   # ← ID calculado manualmente (fix do bug)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO funcionario
                    (id_funcionario, nome, email, telefone, senha_hash, cargo, nivel_acesso, ativo, is_entregador)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                novo_id,
                dados["nome"],
                dados["email"],
                dados["telefone"],
                dados["senha_hash"],
                dados["cargo"],
                dados.get("nivel_acesso", "funcionario"),
                dados.get("ativo", True),
                dados.get("is_entregador", False)
            ))
            conn.commit()
            cursor.close()
        finally:
            pass   # conexão compartilhada — não fechar

    # =========================
    # UPDATE
    # =========================
    def atualizar(self, id_funcionario: int, dados: dict):
        """
        Atualiza os campos de um funcionário existente.
        
        O service chama: funcionario_crud.atualizar(id, dados_convertidos)
        SQL gerado:
          UPDATE funcionario SET nome = %s, email = %s, ... WHERE id_funcionario = %s
        
        Só atualiza os campos presentes em `dados` — campos omitidos ficam intactos.
        """
        conn = self._get_conn()
        try:
            self._garantir_coluna_telefone(conn)
            campos = [f"{chave} = %s" for chave in dados]
            valores = list(dados.values()) + [id_funcionario]
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE funcionario
                SET {', '.join(campos)}
                WHERE id_funcionario = %s
            """, tuple(valores))
            conn.commit()
            cursor.close()
        finally:
            pass

    # =========================
    # DELETE
    # =========================
    def deletar(self, id_funcionario: int):
        """
        Remove um funcionário pelo ID, junto com seu histórico de status
        (para não violar a foreign key historico_status_ibfk_2).
        
        O service chama: funcionario_crud.deletar(id)
        SQL gerado:
          DELETE FROM historico_status WHERE id_funcionario = %s
          DELETE FROM funcionario WHERE id_funcionario = %s
        
        Após deletar, o _proximo_id() garante que o próximo INSERT
        use o menor ID disponível acima do máximo atual.
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM historico_status WHERE id_funcionario = %s",
                (id_funcionario,)
            )
            cursor.execute(
                "DELETE FROM funcionario WHERE id_funcionario = %s",
                (id_funcionario,)
            )
            conn.commit()
            cursor.close()
        finally:
            pass

    # =========================
    # READ (1 registro)
    # =========================
    def buscar_por_id(self, id_funcionario: int):
        """
        Busca um funcionário pelo ID e retorna no formato da UI.
        
        O service chama: funcionario_crud.buscar_por_id(id)
        SQL gerado:
          SELECT * FROM funcionario WHERE id_funcionario = %s
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)   # dictionary=True → retorna dict, não tupla
            self._garantir_coluna_telefone(conn)
            cursor.execute(
                "SELECT * FROM funcionario WHERE id_funcionario = %s",
                (id_funcionario,)
            )
            resultado = cursor.fetchone()
            cursor.close()
            return self._mapear_saida(resultado)
        finally:
            pass

    # =========================
    # READ (todos)
    # =========================
    def listar_todos(self) -> list:
        """
        Retorna todos os funcionários para popular a tabela na tela.
        
        O service chama: funcionario_crud.listar_todos()
        SQL gerado:
          SELECT * FROM funcionario ORDER BY id_funcionario DESC
        
        Retorna lista de dicts no formato da UI:
          [{"id": 1, "nome": "...", "email": "...", "cargo": "...", "ativo": True}, ...]
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor(dictionary=True)
            self._garantir_coluna_telefone(conn)
            cursor.execute("SELECT * FROM funcionario ORDER BY id_funcionario DESC")
            resultados = cursor.fetchall()
            cursor.close()
            return [self._mapear_saida(r) for r in resultados]
        finally:
            pass

    # =========================
    # MAPEAMENTO (banco → UI)
    # =========================
    def _mapear_saida(self, dados: dict) -> dict | None:
        """
        Converte o formato do banco para o formato que a tela espera.
        
        Banco:  {"id_funcionario": 1, "nivel_acesso": "administrador", ...}
        UI:     {"id": 1,             "cargo": "Administrador",         ...}
        """
        if not dados:
            return None

        return {
            "id":    dados["id_funcionario"],
            "nome":  dados["nome"],
            "email": dados["email"],
            "telefone": dados.get("telefone", ""),
            "cargo": self._mapear_cargo_saida(dados["nivel_acesso"]),
            "ativo": dados["ativo"],
            "is_entregador": bool(dados.get("is_entregador", False))
        }

    def _mapear_cargo_saida(self, nivel: str) -> str:
        """
        Converte o valor do banco para o label da UI.
          banco: "administrador"  → UI: "Administrador"
          banco: "funcionario"    → UI: "Funcionário"
        """
        return "Administrador" if nivel == "administrador" else "Funcionário"
