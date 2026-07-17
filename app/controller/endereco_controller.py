from app.model.endereco_model import EnderecoModel

_model = EnderecoModel()


def listar_enderecos(id_cliente: int) -> list:
    return _model.listar_por_cliente(id_cliente)


def buscar_endereco(id_endereco: int) -> dict | None:
    return _model.buscar(id_endereco)


def salvar_endereco(dados: dict) -> int | None:
    return _model.salvar(dados)


def excluir_endereco(id_endereco: int) -> bool:
    return _model.excluir(id_endereco)


def definir_endereco_principal(id_endereco: int, id_cliente: int) -> bool:
    return _model.definir_principal(id_endereco, id_cliente)
