from app.model.taxa_entrega_model import TaxaEntregaModel

_model = TaxaEntregaModel()


def listar_taxas() -> list:
    return _model.listar_todas()


def buscar_taxa_por_bairro(bairro: str) -> dict | None:
    return _model.buscar_por_bairro(bairro)


def salvar_taxa(dados: dict) -> int | None:
    return _model.salvar(dados)


def excluir_taxa(id_taxa: int) -> bool:
    return _model.excluir(id_taxa)
