# =============================================================
# cliente_controller.py  —  CONTROLLER DE CLIENTES
# =============================================================
# Camada intermediária entre a TELA e o BANCO DE DADOS.
#============================================================================

from app.model.crud_clientes import ClienteCrud

cliente_crud = ClienteCrud()


def salvar_cliente(dados: dict):
    """
    Cria ou atualiza um cliente.
    Apenas campos presentes em 'dados' são persistidos (endereços são gerenciados via tabela enderecos).
    """
    campos_fixos = ["nome", "telefone", "cpf", "email"]
    dados_formatados = {k: dados[k] for k in campos_fixos if k in dados}
    for campo in ["cep", "numero", "cidade", "bairro", "logradouro", "complemento"]:
        if campo in dados:
            dados_formatados[campo] = dados[campo]
    if dados.get("id"):
        cliente_crud.atualizar(dados["id"], dados_formatados)
    else:
        cliente_crud.criar(dados_formatados)


def excluir_cliente(id_cliente: int):
    """Remove um cliente pelo ID."""
    cliente_crud.deletar(id_cliente)


def buscar_cliente(id_cliente: int) -> dict | None:
    """Busca um cliente pelo ID (inclui endereços de entrega)."""
    return cliente_crud.buscar_por_id(id_cliente)


def listar_clientes() -> list:
    """Retorna todos os clientes."""
    return cliente_crud.listar_todos()


def buscar_clientes(termo: str) -> list:
    """Busca clientes por termo (nome, telefone, cpf ou email)."""
    if not termo or termo.strip() == "":
        return cliente_crud.listar_todos()
    return cliente_crud.buscar_por_termo(termo)