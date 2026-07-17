import hashlib


def salvar_funcionario(dados: dict):
    """
    Cria ou atualiza um funcionário.
    """
    from app.model.painel_funcionarios_model import FuncionarioCrud
    from app.utils.usuario_atual import usuario_atual
    crud = FuncionarioCrud()
    
    dados_convertidos = {
        "nome":         dados["nome"],
        "email":        dados["email"],
        "telefone":     dados["telefone"],
        "cargo":        dados["cargo"],
        "nivel_acesso": _mapear_cargo(dados["cargo"]),
        "ativo":        dados.get("ativo", True),
        "is_entregador": dados.get("is_entregador", False),
    }

    if dados.get("senha"):
        dados_convertidos["senha_hash"] = hash_senha(dados["senha"])

    if dados.get("id"):
        id_funcionario = dados["id"]
        crud.atualizar(id_funcionario, dados_convertidos)
        if _mesmo_funcionario(id_funcionario, usuario_atual.get("id")):
            _sincronizar_usuario_atual(usuario_atual, id_funcionario, dados_convertidos)
    else:
        crud.criar(dados_convertidos)


def excluir_funcionario(id_funcionario: int):
    """
    Remove um funcionário pelo ID.
    """
    from app.model.painel_funcionarios_model import FuncionarioCrud
    crud = FuncionarioCrud()
    crud.deletar(id_funcionario)


def buscar_funcionario(id_funcionario: int) -> dict | None:
    """
    Busca um funcionário pelo ID.
    """
    from app.model.painel_funcionarios_model import FuncionarioCrud
    crud = FuncionarioCrud()
    return crud.buscar_por_id(id_funcionario)


def listar_funcionarios() -> list:
    """
    Retorna todos os funcionários para popular a tabela na tela.
    """
    from app.model.painel_funcionarios_model import FuncionarioCrud
    crud = FuncionarioCrud()
    return crud.listar_todos()


# =============================================================
# HELPERS INTERNOS
# =============================================================

def hash_senha(senha: str) -> str:
    """Gera hash SHA-256 da senha antes de salvar no banco."""
    return hashlib.sha256(senha.encode()).hexdigest()


def _mapear_cargo(cargo_ui: str) -> str:
    """
    Converte o label exibido na UI para o valor salvo no banco.
        "Administrador" → "administrador"
        qualquer outro  → "funcionario"
    """
    return "administrador" if cargo_ui == "Administrador" else "funcionario"


def _mesmo_funcionario(id_a, id_b) -> bool:
    if id_a is None or id_b is None:
        return False
    return str(id_a) == str(id_b)


def _sincronizar_usuario_atual(usuario_atual: dict, id_funcionario, dados: dict):
    usuario_atual.update({
        "id": id_funcionario,
        "id_funcionario": id_funcionario,
        "nome": dados["nome"],
        "email": dados["email"],
        "telefone": dados["telefone"],
        "cargo": dados["cargo"],
        "nivel_acesso": dados["nivel_acesso"],
        "ativo": dados["ativo"],
    })
