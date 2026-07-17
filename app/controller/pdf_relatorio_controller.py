# pdf_relatorio_controller.py - Controller para geração de relatórios
from app.model.estoque_model import buscar_todos_itens

def buscar_dados_balanco_estoque() -> list:
    """
    Retorna todos os itens do estoque para o relatório de balanço.
    """
    itens = buscar_todos_itens()
    return [
        {
            "nome":              item.get("nome",""),
            "categoria":         item.get("categoria",""),
            "quantidade":        item.get("quantidade",0),
            "quantidade_minima": item.get("quantidade_minima",0),
            "unidade":           item.get("unidade",""),
            }
        for item in itens    
    ]
    
def buscar_dados_estoque_minimo() -> list:
    """
    Retorna apenas os itens abaixo ou igual ao estoque mínima.
    """
    itens = buscar_todos_itens()
    return [
        {
            "nome":              item.get("nome",""),
            "categoria":         item.get("categoria",""),
            "quantidade":        item.get("quantidade",0),
            "quantidade_minima": item.get("quantidade_minima",0),
            "unidade":           item.get("unidade",""),
            }
        for item in itens    
        if item.get("quantidade",0) < item.get("quantidade_minima",0)
    ]
    