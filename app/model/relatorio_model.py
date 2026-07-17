# relatorio_model.py - operações MYSQL para relatórios
from app.database.db_config import conectar


# ── Estoque ────────────────────────────────────────────────────────────────────

def buscar_balanco_estoque(produto: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    if produto:
        cursor.execute(
            "SELECT id_estoque, nome, descricao, quantidade, quantidade_minima, "
            "unidade, categoria "
            "FROM estoque WHERE nome LIKE %s ORDER BY nome",
            (f"%{produto}%",)
        )
    else:
        cursor.execute(
            "SELECT id_estoque, nome, descricao, quantidade, quantidade_minima, "
            "unidade, categoria "
            "FROM estoque ORDER BY nome"
        )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_estoque_minimo(produto: str = None, categoria: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    condicoes = ["quantidade < quantidade_minima"]
    params = []
    if produto:
        condicoes.append("nome LIKE %s")
        params.append(f"%{produto}%")
    if categoria:
        condicoes.append("categoria = %s")
        params.append(categoria)
    where = " AND ".join(condicoes)
    cursor.execute(
        f"SELECT id_estoque, nome, descricao, quantidade, quantidade_minima, "
        f"unidade, categoria "
        f"FROM estoque WHERE {where} ORDER BY nome",
        params
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


# ── Vendas / Pedidos ────────────────────────────────────────────────────────────

def buscar_extrato_vendas(data_inicio: str = None, data_fim: str = None,
                          tipo_venda: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    condicoes = []
    params = []
    if data_inicio and data_fim:
        condicoes.append("DATE(data_do_pedido) BETWEEN %s AND %s")
        params.extend([data_inicio, data_fim])
    if tipo_venda:
        condicoes.append("tipo_de_pedido = %s")
        params.append(tipo_venda)
    where = ("WHERE " + " AND ".join(condicoes)) if condicoes else ""
    cursor.execute(
        f"SELECT * FROM pedido {where} ORDER BY data_do_pedido DESC", params
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_evolucao_vendas(data_inicio: str = None, data_fim: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    where = ""
    params = []
    if data_inicio and data_fim:
        where = "WHERE DATE(data_do_pedido) BETWEEN %s AND %s "
        params = [data_inicio, data_fim]
    cursor.execute(
        f"SELECT DATE(data_do_pedido) AS data, "
        "COUNT(*) AS total_pedidos, "
        "SUM(valor_total) AS total_vendas "
        f"FROM pedido {where} "
        "GROUP BY DATE(data_do_pedido) ORDER BY data",
        params
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_taxa_servico(data_inicio: str = None, data_fim: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    where = ""
    params = []
    if data_inicio and data_fim:
        where = "WHERE DATE(data_do_pedido) BETWEEN %s AND %s "
        params = [data_inicio, data_fim]
    cursor.execute(
        f"SELECT COUNT(*) AS total_pedidos, "
        "SUM(valor_total) AS total_vendas, "
        "AVG(valor_total) AS ticket_medio "
        f"FROM pedido {where}",
        params
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_deliveries(data_inicio: str = None, data_fim: str = None,
                      nome_cliente: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    condicoes = ["p.tipo_de_pedido = 'delivery'", "p.status_do_pedido = 'entregue'"]
    params = []
    if data_inicio and data_fim:
        condicoes.append("DATE(p.data_do_pedido) BETWEEN %s AND %s")
        params.extend([data_inicio, data_fim])
    if nome_cliente:
        condicoes.append("c.nome LIKE %s")
        params.append(f"%{nome_cliente}%")
    where = " AND ".join(condicoes)
    cursor.execute(
        f"SELECT p.*, c.nome AS cliente_nome, c.telefone AS cliente_telefone, "
        f"c.bairro AS cliente_bairro, c.cidade AS cliente_cidade, "
        f"c.logradouro AS cliente_logradouro, c.numero AS cliente_numero "
        f"FROM pedido p "
        f"LEFT JOIN clientes c ON p.id_cliente = c.id_cliente "
        f"WHERE {where} "
        f"ORDER BY p.data_do_pedido DESC", params
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_vendas_produto(data_inicio: str = None, data_fim: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    where = ""
    params = []
    if data_inicio and data_fim:
        where = "AND DATE(p.data_do_pedido) BETWEEN %s AND %s "
        params = [data_inicio, data_fim]
    cursor.execute(
        "SELECT pr.nome AS produto, "
        "SUM(ip.quantidade) AS quantidade_vendida, "
        "SUM(ip.quantidade * ip.preco_unitario) AS total_vendas "
        "FROM item_pedido ip "
        "JOIN pedido p ON ip.id_pedido = p.id_pedido "
        "JOIN produto pr ON ip.id_produto = pr.id_produto "
        f"WHERE p.status_do_pedido != 'cancelado' {where}"
        "GROUP BY pr.nome "
        "ORDER BY total_vendas DESC",
        params
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


# ── Caixa / Pagamentos ──────────────────────────────────────────────────────────

def buscar_totais_caixa(data_inicio: str = None, data_fim: str = None) -> dict:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    where = ""
    params = []
    if data_inicio and data_fim:
        where = "WHERE DATE(data_pagamento) BETWEEN %s AND %s "
        params = [data_inicio, data_fim]
    cursor.execute(
        f"SELECT "
        "COALESCE(SUM(CASE WHEN status_pagamento = 'pago' THEN valor END), 0) AS total_pago, "
        "COALESCE(SUM(CASE WHEN status_pagamento = 'pendente' THEN valor END), 0) AS total_pendente, "
        "COALESCE(SUM(CASE WHEN status_pagamento = 'nao_efetuado' THEN valor END), 0) AS total_cancelado, "
        "COUNT(*) AS total_transacoes "
        f"FROM pagamento {where}",
        params
    )
    resumo = cursor.fetchone()

    cursor.execute(
        f"SELECT * FROM pagamento {where} ORDER BY data_pagamento DESC",
        params
    )
    detalhes = cursor.fetchall()
    cursor.close()
    return {"resumo": resumo, "detalhes": detalhes}


def buscar_formas_pagamento(data_inicio: str = None, data_fim: str = None) -> list:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    where = ""
    params = []
    if data_inicio and data_fim:
        where = "WHERE DATE(data_pagamento) BETWEEN %s AND %s "
        params = [data_inicio, data_fim]
    cursor.execute(
        f"SELECT tipo_de_pagamento, "
        "COUNT(*) AS quantidade, "
        "SUM(valor) AS total "
        f"FROM pagamento {where} "
        "GROUP BY tipo_de_pagamento ORDER BY total DESC",
        params
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado
