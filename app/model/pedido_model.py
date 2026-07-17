import time
from app.database.db_config import conectar
from app.utils.usuario_atual import usuario_atual


class PedidoModel:

    def buscar_pedido(self, id_pedido: int) -> dict | None:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id_pedido, p.tipo_de_pedido, p.status_do_pedido, p.data_do_pedido,
                p.tempo_estimado, p.timer_iniciado_em, p.timer_status, p.timer_concluido_em,
                p.valor_total, p.taxa_entrega, p.origem, p.num_mesa, p.observacoes,
                p.num_revertido, p.momento_cobranca, p.id_entregador,
                f.nome AS entregador_nome,
                c.nome AS cliente_nome
            FROM pedido p
            LEFT JOIN funcionario f ON p.id_entregador = f.id_funcionario
            LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_pedido = %s
        """, (id_pedido,))
        pedido = cursor.fetchone()

        if not pedido:
                return None

        itens = self._buscar_itens_pedido(id_pedido, cursor)
        pagamentos = self._buscar_pagamentos_pedido(id_pedido, cursor)
        historico = self.buscar_historico(id_pedido, cursor)


        return {
            "id_pedido": pedido[0],
            "tipo_pedido": pedido[1],
            "status_pedido": pedido[2],
            "data_pedido": pedido[3],
            "tempo_estimado": pedido[4],
            "timer_iniciado_em": pedido[5],
            "timer_status": pedido[6],
            "timer_concluido_em": pedido[7],
            "valor_total": float(pedido[8]),
            "taxa_entrega": float(pedido[9]),
            "origem": pedido[10],
            "num_mesa": pedido[11],
            "observacoes": pedido[12],
            "num_revertido": pedido[13] or 0,
            "momento_cobranca": pedido[14],
            "id_entregador":    pedido[15],
            "entregador_nome":  pedido[16] or "—",
            "cliente_nome":     pedido[17] or "—",
            "itens": itens,
            "pagamentos": pagamentos,
            "historico": historico,
            "subtotal": sum(i["preco"] * i["quantidade"] for i in itens),
        }

    def _buscar_itens_pedido(self, id_pedido: int, cursor) -> list:
        cursor.execute("""
            SELECT ip.id_item, ip.id_produto, ip.quantidade, ip.preco_unitario,
                   ip.observacoes, p.nome, p.foto
            FROM item_pedido ip
            JOIN produto p ON ip.id_produto = p.id_produto
            WHERE ip.id_pedido = %s
        """, (id_pedido,))
        rows = cursor.fetchall()
        return [
            {
                "id_item": r[0],
                "id_produto": r[1],
                "quantidade": r[2],
                "preco": float(r[3]),
                "observacoes": r[4],
                "nome": r[5],
                "foto": r[6],
            }
            for r in rows
        ]

    def _buscar_pagamentos_pedido(self, id_pedido: int, cursor) -> list:
        cursor.execute("""
            SELECT id_pagamento, valor, tipo_de_pagamento, detalhes,
                   status_pagamento, data_pagamento
            FROM pagamento
            WHERE id_pedido = %s
        """, (id_pedido,))
        rows = cursor.fetchall()
        return [
            {
                "id_pagamento": r[0],
                "valor": float(r[1]),
                "tipo": r[2],
                "detalhes": r[3],
                "status": r[4],
                "data": r[5],
            }
            for r in rows
        ]

    def criar_pedido(self, tipo_pedido: str, origem: str, num_mesa: int = None,
                     observacoes: str = None, valor_total: float = 0.0,
                     taxa_entrega: float = 0.0, id_cliente: int = None,
                     momento_cobranca: str = None , id_entregador: int = None,
                     id_endereco: int = None)  -> int | None:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor()
        id_funcionario = usuario_atual.get("id") or 1

        cursor.execute("""
            INSERT INTO pedido (tipo_de_pedido, status_do_pedido, origem, num_mesa,
                               observacoes, valor_total, taxa_entrega,
                               id_cliente, id_funcionario, momento_cobranca, id_entregador, id_endereco)
            VALUES (%s, 'criado', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (tipo_pedido, origem, num_mesa, observacoes, valor_total,
              taxa_entrega, id_cliente, id_funcionario, momento_cobranca, id_entregador, id_endereco))
        conn.commit()
        id_pedido = cursor.lastrowid
        self.registrar_historico(id_pedido, "criado", cursor=cursor)
        return id_pedido

    def adicionar_item_pedido(self, id_pedido: int, id_produto: int,
                             quantidade: int, preco_unitario: float,
                             observacoes: str = None) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO item_pedido (id_pedido, id_produto, quantidade, preco_unitario, observacoes)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_pedido, id_produto, quantidade, preco_unitario, observacoes))
        conn.commit()
        afetadas = cursor.rowcount
        return afetadas > 0

    def adicionar_itens_pedido(self, id_pedido: int, itens: list) -> bool:
        if not itens:
            return False
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        for item in itens:
            cursor.execute("""
                INSERT INTO item_pedido (id_pedido, id_produto, quantidade, preco_unitario, observacoes)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_pedido, item["id_produto"], item["quantidade"],
                  item["preco_unitario"], item.get("observacoes")))
        conn.commit()
        return True

    def atualizar_valor_total(self, id_pedido: int, valor_total: float) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE pedido SET valor_total = %s WHERE id_pedido = %s
        """, (valor_total, id_pedido))
        conn.commit()
        afetadas = cursor.rowcount
        return afetadas > 0

    def confirmar_pagamento(self, id_pedido: int, pagamentos: list) -> bool:
        if not pagamentos:
            return False
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        for pag in pagamentos:
            metodo = pag.get("metodo", "Dinheiro")
            detalhes = pag.get("detalhes", "")
            valor = pag.get("valor", 0)
            tipo_map = {"Dinheiro": "dinheiro", "PIX": "pix"}
            tipo_db = "cartao"
            for chave, tipo_val in tipo_map.items():
                if chave in metodo:
                    tipo_db = tipo_val
                    break
            cursor.execute("""
                INSERT INTO pagamento (id_pedido, valor, tipo_de_pagamento, detalhes, status_pagamento)
                VALUES (%s, %s, %s, %s, 'pago')
            """, (id_pedido, valor, tipo_db, detalhes))
        conn.commit()
        return True

    def atualizar_status(self, id_pedido: int, novo_status: str) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()

        sql = "UPDATE pedido SET status_do_pedido = %s"
        params = [novo_status]

        if novo_status in ("em_preparo",):
            sql += ", timer_iniciado_em = NOW()"
        elif novo_status in ("concluido", "cancelado"):
            sql += ", timer_iniciado_em = NULL"

        sql += " WHERE id_pedido = %s"
        params.append(id_pedido)

        cursor.execute(sql, params)
        conn.commit()
        afetadas = cursor.rowcount
        if afetadas > 0:
            self.registrar_historico(id_pedido, novo_status, cursor=cursor)
        return afetadas > 0

    def iniciar_timer(self, id_pedido: int, tempo_estimado: int = None) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        if tempo_estimado is not None:
            cursor.execute("""
                UPDATE pedido
                SET timer_iniciado_em = NOW(), status_do_pedido = 'em_preparo',
                    tempo_estimado = %s, timer_status = NULL,
                    timer_concluido_em = NULL
                WHERE id_pedido = %s
            """, (tempo_estimado, id_pedido))
        else:
            cursor.execute("""
                UPDATE pedido
                SET timer_iniciado_em = NOW(), status_do_pedido = 'em_preparo',
                    timer_status = NULL, timer_concluido_em = NULL
                WHERE id_pedido = %s
            """, (id_pedido,))
        conn.commit()
        afetadas = cursor.rowcount
        if afetadas > 0:
            self.registrar_historico(id_pedido, "em_preparo", cursor=cursor)
        return afetadas > 0

    def parar_timer(self, id_pedido: int, timer_status: str) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pedido
            SET timer_concluido_em = NOW(), timer_status = %s
            WHERE id_pedido = %s
        """, (timer_status, id_pedido))
        conn.commit()
        afetadas = cursor.rowcount
        return afetadas > 0

    def cancelar_pedido(self, id_pedido: int) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pedido
            SET status_do_pedido = 'cancelado', timer_iniciado_em = NULL
            WHERE id_pedido = %s
        """, (id_pedido,))
        conn.commit()
        afetadas = cursor.rowcount
        if afetadas > 0:
            self.registrar_historico(id_pedido, "cancelado", cursor=cursor)
        return afetadas > 0

    def excluir_pedido(self, id_pedido: int) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM historico_status WHERE id_pedido = %s""", (id_pedido,))
        cursor.execute("""DELETE FROM pagamento WHERE id_pedido = %s""", (id_pedido,))
        cursor.execute("""DELETE FROM item_pedido WHERE id_pedido = %s""", (id_pedido,))
        cursor.execute("""DELETE FROM pedido WHERE id_pedido = %s""", (id_pedido,))
        conn.commit()
        afetadas = cursor.rowcount
        return afetadas > 0

    def reverter_status(self, id_pedido: int, status_anterior: str) -> bool:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()

        if status_anterior == "em_preparo":
            cursor.execute("""
                UPDATE pedido
                SET status_do_pedido = %s, num_revertido = num_revertido + 1,
                    timer_concluido_em = NULL, timer_status = NULL
                WHERE id_pedido = %s
            """, (status_anterior, id_pedido))
        elif status_anterior == "pronto":
            cursor.execute("""
                UPDATE pedido
                SET status_do_pedido = %s, num_revertido = num_revertido + 1,
                    timer_iniciado_em = DATE_SUB(NOW(), INTERVAL
                        COALESCE(TIMESTAMPDIFF(SECOND, timer_iniciado_em, timer_concluido_em), 0)
                    SECOND),
                    timer_concluido_em = NULL, timer_status = NULL
                WHERE id_pedido = %s
            """, (status_anterior, id_pedido))
        else:
            cursor.execute("""
                UPDATE pedido
                SET status_do_pedido = %s, num_revertido = num_revertido + 1
                WHERE id_pedido = %s
            """, (status_anterior, id_pedido))
        conn.commit()
        afetadas = cursor.rowcount
        if afetadas > 0:
            self.registrar_historico(id_pedido, status_anterior, cursor=cursor)
        return afetadas > 0

    def pode_reverter(self, id_pedido: int, nivel_acesso: str) -> bool:
        if nivel_acesso == "administrador":
            return True
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("""
            SELECT num_revertido FROM pedido WHERE id_pedido = %s
        """, (id_pedido,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0] < 2
        return False

    def registrar_historico(self, id_pedido: int, status: str, id_funcionario: int = None, cursor=None) -> bool:
        if id_funcionario is None:
            id_funcionario = usuario_atual.get("id")
        if not id_funcionario:
            return False
        _cursor = cursor
        _conn = None
        if _cursor is None:
            _conn = conectar()
            if not _conn:
                return False
            _cursor = _conn.cursor()
        _cursor.execute("""
            INSERT INTO historico_status (id_pedido, status, id_funcionario)
            VALUES (%s, %s, %s)
        """, (id_pedido, status, id_funcionario))
        if _conn:
            _conn.commit()
        afetadas = _cursor.rowcount
        return afetadas > 0

    def buscar_historico(self, id_pedido: int, cursor=None) -> list:
        _cursor = cursor
        if _cursor is None:
            conn = conectar()
            if not conn:
                return []
            _cursor = conn.cursor()
        _cursor.execute("""
            SELECT hs.status, f.nome, hs.data_hora
            FROM historico_status hs
            JOIN funcionario f ON hs.id_funcionario = f.id_funcionario
            WHERE hs.id_pedido = %s
            ORDER BY hs.data_hora ASC
        """, (id_pedido,))
        rows = _cursor.fetchall()
        return [
            {
                "status": r[0],
                "funcionario": r[1],
                "data_hora": r[2],
            }
            for r in rows
        ]

    def buscar_timer_iniciado_em(self, id_pedido: int) -> 'datetime | None':
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("""
            SELECT data_hora FROM historico_status
            WHERE id_pedido = %s AND status = 'em_preparo'
            ORDER BY data_hora DESC LIMIT 1
        """, (id_pedido,))
        row = cursor.fetchone()
        return row[0] if row else None

    def listar_pedidos(self, pagina=1, itens_por_pagina=12,
                       filtro_status=None, filtro_origem=None, busca=None) -> list:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor()

        where_clauses = []
        params = []

        if filtro_status:
            placeholders = ", ".join(["%s"] * len(filtro_status))
            where_clauses.append(f"p.status_do_pedido IN ({placeholders})")
            params.extend(filtro_status)

        if filtro_origem:
            placeholders = ", ".join(["%s"] * len(filtro_origem))
            where_clauses.append(f"p.origem IN ({placeholders})")
            params.extend(filtro_origem)

        if busca:
            where_clauses.append("(p.id_pedido LIKE %s OR CAST(p.num_mesa AS CHAR) LIKE %s OR DATE_FORMAT(p.data_do_pedido, '%%d/%%m/%%Y %%H:%%i') LIKE %s)")
            termo = f"%{busca}%"
            params.extend([termo, termo, termo])

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        offset = (pagina - 1) * itens_por_pagina

        cursor.execute(f"""
            SELECT p.id_pedido, p.status_do_pedido, p.data_do_pedido,
                   p.tempo_estimado, p.timer_iniciado_em, p.timer_status, p.timer_concluido_em,
                   p.origem, p.num_mesa, p.valor_total
            FROM pedido p
            {where_sql}
            ORDER BY p.data_do_pedido DESC
            LIMIT %s OFFSET %s
        """, params + [itens_por_pagina, offset])
        rows = cursor.fetchall()

        ids_pagina = [r[0] for r in rows]
        if ids_pagina:
            placeholders = ", ".join(["%s"] * len(ids_pagina))
            cursor.execute(f"""
                SELECT id_pedido, SUM(valor)
                FROM pagamento
                WHERE id_pedido IN ({placeholders}) AND status_pagamento = 'pago'
                GROUP BY id_pedido
            """, ids_pagina)
            pag_por_pedido = {r[0]: float(r[1]) for r in cursor.fetchall()}
        else:
            pag_por_pedido = {}

        pedidos = []
        for r in rows:
            id_pedido = r[0]
            total_pago = pag_por_pedido.get(id_pedido, 0.0)
            valor_total = float(r[9])
            restante = valor_total - total_pago

            if total_pago >= valor_total and valor_total > 0:
                status_pagamento = "pago"
            elif total_pago > 0:
                status_pagamento = "parcial"
            else:
                status_pagamento = "pendente"

            pedidos.append({
                "id_pedido": id_pedido,
                "status_pedido": r[1],
                "data_pedido": r[2],
                "tempo_estimado": r[3],
                "timer_iniciado_em": r[4],
                "timer_status": r[5],
                "timer_concluido_em": r[6],
                "origem": r[7],
                "num_mesa": r[8],
                "valor_total": valor_total,
                "total_pago": total_pago,
                "restante": restante,
                "status_pagamento": status_pagamento,
            })

        return pedidos

    def listar_pedidos_delivery(self, pagina=1, itens_por_pagina=12,
                                 filtro_status=None, busca=None) -> list:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor()

        where_clauses = ["p.origem = 'delivery'"]
        params = []

        if filtro_status:
            placeholders = ", ".join(["%s"] * len(filtro_status))
            where_clauses.append(f"p.status_do_pedido IN ({placeholders})")
            params.extend(filtro_status)

        if busca:
            where_clauses.append("""(
                p.id_pedido LIKE %s
                OR c.nome LIKE %s
                OR DATE_FORMAT(p.data_do_pedido, '%%d/%%m/%%Y %%H:%%i') LIKE %s
            )""")
            termo = f"%{busca}%"
            params.extend([termo, termo, termo])

        where_sql = " AND ".join(where_clauses)
        offset = (pagina - 1) * itens_por_pagina

        cursor.execute(f"""
            SELECT p.id_pedido, p.status_do_pedido, p.data_do_pedido,
                   p.tempo_estimado, p.timer_iniciado_em, p.timer_status, p.timer_concluido_em,
                   p.origem, p.num_mesa, p.valor_total, p.tipo_de_pedido,
                   c.id_cliente, c.nome AS cliente_nome
            FROM pedido p
            LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE {where_sql}
            ORDER BY p.data_do_pedido DESC
            LIMIT %s OFFSET %s
        """, params + [itens_por_pagina, offset])
        rows = cursor.fetchall()

        ids_pagina = [r[0] for r in rows]
        if ids_pagina:
            placeholders = ", ".join(["%s"] * len(ids_pagina))
            cursor.execute(f"""
                SELECT id_pedido, SUM(valor)
                FROM pagamento
                WHERE id_pedido IN ({placeholders}) AND status_pagamento = 'pago'
                GROUP BY id_pedido
            """, ids_pagina)
            pag_por_pedido = {r[0]: float(r[1]) for r in cursor.fetchall()}
        else:
            pag_por_pedido = {}

        pedidos = []
        for r in rows:
            id_pedido = r[0]
            total_pago = pag_por_pedido.get(id_pedido, 0.0)
            valor_total = float(r[9])
            restante = valor_total - total_pago

            if total_pago >= valor_total and valor_total > 0:
                status_pagamento = "pago"
            elif total_pago > 0:
                status_pagamento = "parcial"
            else:
                status_pagamento = "pendente"

            pedidos.append({
                "id_pedido": id_pedido,
                "status_pedido": r[1],
                "data_pedido": r[2],
                "tempo_estimado": r[3],
                "timer_iniciado_em": r[4],
                "timer_status": r[5],
                "timer_concluido_em": r[6],
                "origem": r[7],
                "num_mesa": r[8],
                "valor_total": valor_total,
                "tipo_de_pedido": r[10],
                "id_cliente": r[11],
                "cliente_nome": r[12] or "—",
                "total_pago": total_pago,
                "restante": restante,
                "status_pagamento": status_pagamento,
            })

        return pedidos

    def contar_pedidos_delivery(self, filtro_status=None, busca=None) -> int:
        conn = conectar()
        if not conn:
            return 0
        cursor = conn.cursor()

        where_clauses = ["p.origem = 'delivery'"]
        params = []

        if filtro_status:
            placeholders = ", ".join(["%s"] * len(filtro_status))
            where_clauses.append(f"p.status_do_pedido IN ({placeholders})")
            params.extend(filtro_status)

        if busca:
            where_clauses.append("""(
                p.id_pedido LIKE %s
                OR c.nome LIKE %s
                OR DATE_FORMAT(p.data_do_pedido, '%%d/%%m/%%Y %%H:%%i') LIKE %s
            )""")
            termo = f"%{busca}%"
            params.extend([termo, termo, termo])

        where_sql = " AND ".join(where_clauses)

        cursor.execute(f"""
            SELECT COUNT(*) FROM pedido p
            LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE {where_sql}
        """, params)
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    def contar_pedidos(self, filtro_status=None, filtro_origem=None, busca=None) -> int:
        conn = conectar()
        if not conn:
            return 0
        cursor = conn.cursor()

        where_clauses = []
        params = []

        if filtro_status:
            placeholders = ", ".join(["%s"] * len(filtro_status))
            where_clauses.append(f"p.status_do_pedido IN ({placeholders})")
            params.extend(filtro_status)

        if filtro_origem:
            placeholders = ", ".join(["%s"] * len(filtro_origem))
            where_clauses.append(f"p.origem IN ({placeholders})")
            params.extend(filtro_origem)

        if busca:
            where_clauses.append("(p.id_pedido LIKE %s OR CAST(p.num_mesa AS CHAR) LIKE %s OR DATE_FORMAT(p.data_do_pedido, '%%d/%%m/%%Y %%H:%%i') LIKE %s)")
            termo = f"%{busca}%"
            params.extend([termo, termo, termo])

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        cursor.execute(f"SELECT COUNT(*) FROM pedido p {where_sql}", params)
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    def carregar_resumo_cards(self) -> dict:
        conn = conectar()
        if not conn:
            return {
                "vendas_dia": 0, "pedidos_ativos": 0, "atrasados": 0, "pendentes": 0,
                "ticket_medio": 0, "total_pedidos": 0,
                "em_preparo": 0, "prontos": 0, "entregues": 0, "cancelados": 0,
                "em_preparo_delivery": 0, "em_preparo_presencial": 0,
                "prontos_delivery": 0, "prontos_presencial": 0,
                "entregues_delivery": 0, "entregues_presencial": 0,
                "cancelados_delivery": 0, "cancelados_presencial": 0,
                "delivery_andamento": 0, "presencial_andamento": 0,
                "vendas_ontem": 0,
            }
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN status_do_pedido = 'concluido' AND DATE(data_do_pedido) = CURDATE() THEN valor_total ELSE 0 END), 0) as vendas_dia,
                COALESCE(SUM(CASE WHEN status_do_pedido NOT IN ('concluido', 'cancelado') THEN 1 ELSE 0 END), 0) as pedidos_ativos,
                COALESCE(SUM(CASE WHEN timer_status = 'atrasado' THEN 1 ELSE 0 END), 0) as atrasados,
                COALESCE(SUM(CASE WHEN status_do_pedido NOT IN ('concluido', 'cancelado') AND valor_total > 0 AND (
                    SELECT COALESCE(SUM(valor), 0) FROM pagamento
                    WHERE id_pedido = pedido.id_pedido AND status_pagamento = 'pago'
                ) = 0 THEN 1 ELSE 0 END), 0) as pendentes,
                COALESCE(AVG(CASE WHEN status_do_pedido = 'concluido' THEN valor_total END), 0) as ticket_medio,
                COUNT(*) as total_pedidos,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'em_preparo' THEN 1 ELSE 0 END), 0) as em_preparo,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'em_preparo' AND origem = 'delivery' THEN 1 ELSE 0 END), 0) as em_preparo_delivery,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'em_preparo' AND origem IN ('mesa', 'balcao') THEN 1 ELSE 0 END), 0) as em_preparo_presencial,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'pronto' THEN 1 ELSE 0 END), 0) as prontos,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'pronto' AND origem = 'delivery' THEN 1 ELSE 0 END), 0) as prontos_delivery,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'pronto' AND origem IN ('mesa', 'balcao') THEN 1 ELSE 0 END), 0) as prontos_presencial,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'entregue' THEN 1 ELSE 0 END), 0) as entregues,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'entregue' AND origem = 'delivery' THEN 1 ELSE 0 END), 0) as entregues_delivery,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'entregue' AND origem IN ('mesa', 'balcao') THEN 1 ELSE 0 END), 0) as entregues_presencial,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'cancelado' THEN 1 ELSE 0 END), 0) as cancelados,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'cancelado' AND origem = 'delivery' THEN 1 ELSE 0 END), 0) as cancelados_delivery,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'cancelado' AND origem IN ('mesa', 'balcao') THEN 1 ELSE 0 END), 0) as cancelados_presencial,
                COALESCE(SUM(CASE WHEN status_do_pedido NOT IN ('concluido', 'cancelado') AND origem = 'delivery' THEN 1 ELSE 0 END), 0) as delivery_andamento,
                COALESCE(SUM(CASE WHEN status_do_pedido NOT IN ('concluido', 'cancelado') AND origem IN ('mesa', 'balcao') THEN 1 ELSE 0 END), 0) as presencial_andamento,
                COALESCE(SUM(CASE WHEN status_do_pedido = 'concluido' AND DATE(data_do_pedido) = CURDATE() - INTERVAL 1 DAY THEN valor_total ELSE 0 END), 0) as vendas_ontem
            FROM pedido
        """)
        row = cursor.fetchone()

        return {
            "vendas_dia": float(row[0]) if row else 0,
            "pedidos_ativos": int(row[1]) if row else 0,
            "atrasados": int(row[2]) if row else 0,
            "pendentes": int(row[3]) if row else 0,
            "ticket_medio": float(row[4]) if row else 0,
            "total_pedidos": int(row[5]) if row else 0,
            "em_preparo": int(row[6]) if row else 0,
            "em_preparo_delivery": int(row[7]) if row else 0,
            "em_preparo_presencial": int(row[8]) if row else 0,
            "prontos": int(row[9]) if row else 0,
            "prontos_delivery": int(row[10]) if row else 0,
            "prontos_presencial": int(row[11]) if row else 0,
            "entregues": int(row[12]) if row else 0,
            "entregues_delivery": int(row[13]) if row else 0,
            "entregues_presencial": int(row[14]) if row else 0,
            "cancelados": int(row[15]) if row else 0,
            "cancelados_delivery": int(row[16]) if row else 0,
            "cancelados_presencial": int(row[17]) if row else 0,
            "delivery_andamento": int(row[18]) if row else 0,
            "presencial_andamento": int(row[19]) if row else 0,
            "vendas_ontem": float(row[20]) if row else 0,
        }

    def carregar_atrasados_por_origem(self) -> dict:
        conn = conectar()
        if not conn:
            return {"delivery": 0, "presencial": 0}
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN origem = 'delivery' THEN 1 ELSE 0 END), 0) as delivery,
                COALESCE(SUM(CASE WHEN origem IN ('mesa', 'balcao') THEN 1 ELSE 0 END), 0) as presencial
            FROM pedido
            WHERE timer_status = 'atrasado'
              AND status_do_pedido NOT IN ('concluido', 'cancelado')
        """)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return {
            "delivery": int(row[0]) if row else 0,
            "presencial": int(row[1]) if row else 0,
        }

    def vendas_por_hora(self) -> list:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                HOUR(data_do_pedido) as hora,
                COUNT(*) as total_pedidos,
                COALESCE(SUM(valor_total), 0) as total_vendas
            FROM pedido
            WHERE data_do_pedido >= CURDATE()
              AND data_do_pedido < CURDATE() + INTERVAL 1 DAY
              AND status_do_pedido = 'concluido'
            GROUP BY HOUR(data_do_pedido)
            ORDER BY hora
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"hora": int(r[0]), "pedidos": int(r[1]), "vendas": float(r[2])} for r in rows]

    def listar_entregadores(self) -> list:
        """Retorna todos os funcionários marcados como entregador e ativos."""
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_funcionario, nome
            FROM funcionario
            WHERE is_entregador = 1 AND ativo = 1
            ORDER BY nome ASC
        """)
        rows = cursor.fetchall()
        return [{"id_funcionario": r[0], "nome": r[1]} for r in rows]
        
    def vendas_por_datas(self, datas: list) -> dict:
        if not datas:
            return {}
        conn = conectar()
        if not conn:
            return {}
        cursor = conn.cursor()
        placeholders = ", ".join(["%s"] * len(datas))
        query = f"""
            SELECT
                DATE(data_do_pedido) as data,
                HOUR(data_do_pedido) as hora,
                COUNT(*) as total_pedidos,
                COALESCE(SUM(valor_total), 0) as total_vendas
            FROM pedido
            WHERE DATE(data_do_pedido) IN ({placeholders})
              AND status_do_pedido = 'concluido'
            GROUP BY DATE(data_do_pedido), HOUR(data_do_pedido)
            ORDER BY data, hora
        """
        cursor.execute(query, datas)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        from collections import defaultdict
        agrupado = defaultdict(dict)
        for r in rows:
            agrupado[str(r[0])][int(r[1])] = {"vendas": float(r[3]), "pedidos": int(r[2])}

        resultado = {}
        for data_str in datas:
            hora_dict = agrupado.get(data_str, {})
            resultado[data_str] = [
                {
                    "hora": h,
                    "vendas": hora_dict.get(h, {}).get("vendas", 0),
                    "pedidos": hora_dict.get(h, {}).get("pedidos", 0),
                }
                for h in range(24)
            ]
        return resultado
