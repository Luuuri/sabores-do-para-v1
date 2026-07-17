# relatorio_controller.py - Controller de relatórios
from datetime import datetime
from tkinter import messagebox
from app.model.relatorio_model import (
    buscar_balanco_estoque,
    buscar_estoque_minimo,
    buscar_extrato_vendas,
    buscar_evolucao_vendas,
    buscar_taxa_servico,
    buscar_deliveries,
    buscar_vendas_produto,
    buscar_totais_caixa,
    buscar_formas_pagamento,
)


def _normalizar_data(data_str: str) -> str | None:
    if not data_str or not data_str.strip():
        return None
    data_str = data_str.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(data_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _validar_periodo(data_inicio: str, data_fim: str) -> tuple:
    warnings = []
    inicio = _normalizar_data(data_inicio)
    if data_inicio and not inicio:
        warnings.append("Data inicial em formato inválido. Use DD/MM/AAAA ou AAAA-MM-DD.")
    fim = _normalizar_data(data_fim)
    if data_fim and not fim:
        warnings.append("Data final em formato inválido. Use DD/MM/AAAA ou AAAA-MM-DD.")
    if inicio and fim and inicio > fim:
        warnings.append("Data inicial não pode ser maior que a final.")
    for w in warnings:
        messagebox.showwarning("Aviso", w)
    if warnings:
        return None, None
    return inicio, fim


def carregar_balanco_estoque(produto: str = None) -> list:
    try:
        return buscar_balanco_estoque(produto)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar balanço de estoque:\n{e}")
        return []


def carregar_estoque_minimo(produto: str = None, categoria: str = None) -> list:
    try:
        return buscar_estoque_minimo(produto, categoria)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar estoque mínimo:\n{e}")
        return []


def carregar_extrato_vendas(data_inicio: str = None, data_fim: str = None,
                            tipo_venda: str = None) -> list:
    try:
        inicio, fim = _validar_periodo(data_inicio, data_fim)
        if (data_inicio and not inicio) or (data_fim and not fim):
            return []
        return buscar_extrato_vendas(inicio, fim, tipo_venda)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar extrato de vendas:\n{e}")
        return []


def carregar_evolucao_vendas(data_inicio: str = None, data_fim: str = None) -> list:
    try:
        inicio, fim = _validar_periodo(data_inicio, data_fim)
        if (data_inicio and not inicio) or (data_fim and not fim):
            return []
        return buscar_evolucao_vendas(inicio, fim)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar evolução de vendas:\n{e}")
        return []


def carregar_taxa_servico(data_inicio: str = None, data_fim: str = None) -> list:
    try:
        inicio, fim = _validar_periodo(data_inicio, data_fim)
        if (data_inicio and not inicio) or (data_fim and not fim):
            return []
        return buscar_taxa_servico(inicio, fim)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar taxa de serviço:\n{e}")
        return []


def carregar_deliveries(data_inicio: str = None, data_fim: str = None,
                        nome_cliente: str = None) -> list:
    try:
        inicio, fim = _validar_periodo(data_inicio, data_fim)
        if (data_inicio and not inicio) or (data_fim and not fim):
            return []
        return buscar_deliveries(inicio, fim, nome_cliente)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar deliveries:\n{e}")
        return []


def carregar_vendas_produto() -> list:
    try:
        return buscar_vendas_produto()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar vendas por produto:\n{e}")
        return []


def carregar_totais_caixa(data_inicio: str = None, data_fim: str = None) -> dict:
    try:
        inicio, fim = _validar_periodo(data_inicio, data_fim)
        if (data_inicio and not inicio) or (data_fim and not fim):
            return {"resumo": None, "detalhes": []}
        return buscar_totais_caixa(inicio, fim)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar totais de caixa:\n{e}")
        return {"resumo": None, "detalhes": []}


def carregar_formas_pagamento(data_inicio: str = None, data_fim: str = None) -> list:
    try:
        inicio, fim = _validar_periodo(data_inicio, data_fim)
        if (data_inicio and not inicio) or (data_fim and not fim):
            return []
        return buscar_formas_pagamento(inicio, fim)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar formas de pagamento:\n{e}")
        return []
