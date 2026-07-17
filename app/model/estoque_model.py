# estoque_model.py - operações MYSQL para estoque
from app.database.db_config import conectar


def buscar_todos_itens() -> list:
    """
    Retorna todos os itens do estoque ordenados por nome.
    """
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_estoque, nome, descricao, quantidade, quantidade_minima, unidade, categoria, preco_unitario "
        "FROM estoque "
        "ORDER BY nome"
    )
    
    
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def inserir_item(nome: str, descricao: str, quantidade: int, unidade: str, 
                 categoria: str, quantidade_minima: int = 0, preco_unitario: float = 0.0) -> int:
    """
    Insere um novo item no estoque.
    Retorna o id gerado.
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO estoque (nome, descricao, quantidade, unidade, categoria, quantidade_minima, preco_unitario) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (nome, descricao, quantidade, unidade, categoria, quantidade_minima, preco_unitario)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    return novo_id


def atualizar_item(id_estoque: int, nome: str, descricao: str, quantidade: int, 
                   unidade: str, categoria: str, quantidade_minima: int = 0, preco_unitario: float = 0.0):
    """
    Atualiza todos os campos de um item pelo id.
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE estoque "
        "SET nome = %s, descricao = %s, quantidade = %s, unidade = %s, categoria = %s, quantidade_minima = %s, preco_unitario = %s"
        "WHERE id_estoque = %s",
        (nome, descricao, quantidade, unidade, categoria, quantidade_minima, preco_unitario, id_estoque)
    )
    conn.commit()
    cursor.close()


def atualizar_quantidade(id_estoque: int, quantidade: int):
    """
    Atualiza apenas a quantidade de um item pelo id.
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE estoque SET quantidade = %s WHERE id_estoque = %s",
        (quantidade, id_estoque)
    )
    conn.commit()
    cursor.close()


def deletar_item(id_estoque: int):
    """
    Remove um item do estoque pelo id.
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque WHERE id_estoque = %s", (id_estoque,))
    conn.commit()
    cursor.close()