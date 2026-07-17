# estoque_controller.py - Controller de estoque
from tkinter import messagebox
from app.model.estoque_model import (
    buscar_todos_itens,
    inserir_item,
    atualizar_item,
    atualizar_quantidade,
    deletar_item,
)


def carregar_itens() -> list:
    """
    Retorna todos os itens do estoque.
    """
    return buscar_todos_itens()


def salvar_novo_item(nome: str, descricao: str, quantidade: str, unidade: str, 
                     categoria: str, quantidade_minima: str = "0", preco_unitario: str = "0") -> dict | None:
    """
    Valida e insere um novo item no estoque.
    Retorna o dicionário do item com id gerado, ou None se falhar.
    """
    if not nome.strip():
        messagebox.showwarning("Aviso", "O nome do item é obrigatório.")
        return None

    if not categoria.strip():
        messagebox.showwarning("Aviso", "A categoria é obrigatória.")
        return None

    try:
        qtd = int(quantidade or 0)
    except ValueError:
        messagebox.showwarning("Aviso", "Quantidade deve ser um número inteiro.")
        return None

    try:
        qtd_min = int(quantidade_minima or 0)
    except ValueError:
        messagebox.showwarning("Aviso", "Quantidade mínima deve ser um número inteiro.")
        return None
    
    try:
        preco = float((preco_unitario or "0").replace(",", "."))
    except ValueError:
        messagebox.showwarning("Aviso", "Preço unitário deve ser um número válido.")
        return None

    novo_id = inserir_item(nome.strip(), descricao.strip(), qtd, unidade, categoria.strip(), qtd_min, preco)

    return {
        "id_estoque": novo_id,
        "nome": nome.strip(),
        "descricao": descricao.strip(),
        "quantidade": qtd,
        "unidade": unidade,
        "categoria": categoria.strip(),
        "quantidade_minima": qtd_min,
        "preco_unitario": preco
    }


def salvar_edicao(id_estoque: int, nome: str, descricao: str, quantidade: str, 
                  unidade: str, categoria: str, quantidade_minima: str = "0", preco_unitario: str = "0") -> dict | None:
    if not nome.strip():
        messagebox.showwarning("Aviso", "O nome do item é obrigatório.")
        return None

    if not categoria.strip():
        messagebox.showwarning("Aviso", "A categoria é obrigatória.")
        return None

    try:
        qtd = int(quantidade or 0)
    except ValueError:
        messagebox.showwarning("Aviso", "Quantidade deve ser um número inteiro.")
        return None

    try:
        qtd_min = int(quantidade_minima or 0)
    except ValueError:
        messagebox.showwarning("Aviso", "Quantidade mínima deve ser um número inteiro.")
        return None
    
    try:
        preco = float((preco_unitario or "0").replace(",", "."))
    except ValueError:
        messagebox.showwarning("Aviso", "Preço unitário deve ser um número válido.")
        return None    

    atualizar_item(id_estoque, nome.strip(), descricao.strip(), qtd, unidade, categoria.strip(), qtd_min, preco)

    return {
        "id_estoque": id_estoque,
        "nome": nome.strip(),
        "descricao": descricao.strip(),
        "quantidade": qtd,
        "unidade": unidade,
        "categoria": categoria.strip(),
        "quantidade_minima": qtd_min,
        "preco_unitario": preco
    }

def salvar_quantidade(id_estoque: int, quantidade: int):
    """
    Atualiza apenas a quantidade de um item (botões + e −).
    """
    atualizar_quantidade(id_estoque, quantidade)


def excluir_item(id_estoque: int, nome: str) -> bool:
    """
    Pede confirmação e exclui o item.
    Retorna True se excluído, False se cancelado.
    """
    confirmado = messagebox.askyesno(
        "Confirmar exclusão",
        f'Tem certeza que deseja excluir "{nome}"?'
    )
    if confirmado:
        deletar_item(id_estoque)
        return True
    return False