"""Testes rápidos para Módulo 1 (índices) e Módulo 2 (listagem paginada)

Uso: python -m tests.test_modulo1_2
"""
from app.model.pedido_model import PedidoModel
from app.model.produto_model import ProdutoModel
import time


def testar_conexao():
    print("1. Conexão com banco...")
    m = PedidoModel()
    r = m.listar_pedidos(pagina=1)
    print(f"   OK - {len(r)} pedidos na página 1")


def testar_paginacao():
    print("\n2. Paginação (listar_pedidos)...")
    m = PedidoModel()
    pag1 = m.listar_pedidos(pagina=1, itens_por_pagina=15)
    pag2 = m.listar_pedidos(pagina=2, itens_por_pagina=15)
    print(f"   Página 1: {len(pag1)} pedidos")
    print(f"   Página 2: {len(pag2)} pedidos")
    assert len(pag1) <= 15
    assert len(pag2) <= 15
    # Verificar se não repetiu IDs entre páginas
    ids1 = {p["id_pedido"] for p in pag1}
    ids2 = {p["id_pedido"] for p in pag2}
    assert ids1.isdisjoint(ids2), "ERRO: IDs repetidos entre páginas!"
    print("   OK - Paginação funcionando, sem repetição")


def testar_filtros():
    print("\n3. Filtros no SQL...")
    m = PedidoModel()
    filtro = m.listar_pedidos(filtro_status=["em_preparo"])
    for p in filtro:
        assert p["status_pedido"] == "em_preparo", f"ERRO: status {p['status_pedido']}"
    print(f"   OK - {len(filtro)} pedidos 'em_preparo'")


def testar_cards():
    print("\n4. Resumo dos cards...")
    m = PedidoModel()
    cards = m.carregar_resumo_cards()
    print(f"   Vendas do dia: R$ {cards['vendas_dia']:.2f}")
    print(f"   Pedidos ativos: {cards['pedidos_ativos']}")
    print(f"   Atrasados: {cards['atrasados']}")
    print(f"   Pendentes: {cards['pendentes']}")
    assert isinstance(cards["vendas_dia"], float)
    assert isinstance(cards["pedidos_ativos"], int)
    print("   OK - Cards retornaram dados corretos")


def testar_performance():
    print("\n5. Performance (com índices)...")
    m = PedidoModel()
    inicio = time.time()
    for _ in range(10):
        m.listar_pedidos(pagina=1, itens_por_pagina=15)
    total = time.time() - inicio
    media = total / 10
    print(f"   10 consultas em {total:.3f}s (média {media:.4f}s por consulta)")


def testar_produtos():
    print("\n6. Listagem de produtos...")
    m = ProdutoModel()
    r = m.listar_produtos()
    print(f"   OK - {len(r)} produtos carregados")


if __name__ == "__main__":
    print("=" * 50)
    print("TESTES - Módulo 1 e 2")
    print("=" * 50)
    try:
        testar_conexao()
        testar_paginacao()
        testar_filtros()
        testar_cards()
        testar_performance()
        testar_produtos()
        print("\n" + "=" * 50)
        print(" TODOS OS TESTES PASSARAM ")
        print("=" * 50)
    except AssertionError as e:
        print(f"\nFALHA: {e}")
    except Exception as e:
        print(f"\nERRO: {e}")
