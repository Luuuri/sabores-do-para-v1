class ProdutoDuplicadoError(Exception):
    """Exceção lançada quando ocorre uma tentativa de criar ou atualizar um produto contendo 
    o mesmo nome e descrição de um registro já existente."""

    pass

