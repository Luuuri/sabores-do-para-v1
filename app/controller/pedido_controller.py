from app.model.pedido_model import PedidoModel


class PedidoController:

    def __init__(self):
        self.model = PedidoModel()

    def buscar_pedido(self, id_pedido: int) -> dict | None:
        return self.model.buscar_pedido(id_pedido)

    def criar_pedido(self, tipo_pedido: str, origem: str, num_mesa: int = None,
                     observacoes: str = None, valor_total: float = 0.0,
                     taxa_entrega: float = 0.0, id_cliente: int = None,
                     momento_cobranca: str = None , id_entregador: int = None,
                     id_endereco: int = None) -> int | None:
        return self.model.criar_pedido(tipo_pedido, origem, num_mesa, observacoes,
                                         valor_total, taxa_entrega, id_cliente,
                                         momento_cobranca , id_entregador, id_endereco)

    def adicionar_item_pedido(self, id_pedido: int, id_produto: int,
                             quantidade: int, preco_unitario: float,
                             observacoes: str = None) -> bool:
        return self.model.adicionar_item_pedido(id_pedido, id_produto, quantidade, preco_unitario, observacoes)

    def adicionar_itens_pedido(self, id_pedido: int, itens: list) -> bool:
        return self.model.adicionar_itens_pedido(id_pedido, itens)

    def atualizar_valor_total(self, id_pedido: int, valor_total: float) -> bool:
        return self.model.atualizar_valor_total(id_pedido, valor_total)

    def confirmar_pagamento(self, id_pedido: int, pagamentos: list) -> bool:
        return self.model.confirmar_pagamento(id_pedido, pagamentos)

    def atualizar_status(self, id_pedido: int, novo_status: str) -> bool:
        status_validos = ("criado", "confirmado", "em_preparo", "pronto", "entregue", "concluido", "cancelado")
        if novo_status not in status_validos:
            return False
        return self.model.atualizar_status(id_pedido, novo_status)

    def iniciar_timer(self, id_pedido: int, tempo_estimado: int = None) -> bool:
        return self.model.iniciar_timer(id_pedido, tempo_estimado)

    def parar_timer(self, id_pedido: int, timer_status: str) -> bool:
        return self.model.parar_timer(id_pedido, timer_status)

    def cancelar_pedido(self, id_pedido: int) -> bool:
        return self.model.cancelar_pedido(id_pedido)

    def excluir_pedido(self, id_pedido: int) -> bool:
        return self.model.excluir_pedido(id_pedido)

    def reverter_status(self, id_pedido: int, status_anterior: str) -> bool:
        return self.model.reverter_status(id_pedido, status_anterior)

    def pode_reverter(self, id_pedido: int, nivel_acesso: str) -> bool:
        return self.model.pode_reverter(id_pedido, nivel_acesso)

    def listar_pedidos(self, pagina=1, itens_por_pagina=12,
                       filtro_status=None, filtro_origem=None, busca=None) -> list:
        return self.model.listar_pedidos(
            pagina=pagina, itens_por_pagina=itens_por_pagina,
            filtro_status=filtro_status, filtro_origem=filtro_origem, busca=busca
        )

    def listar_pedidos_delivery(self, pagina=1, itens_por_pagina=12,
                                 filtro_status=None, busca=None) -> list:
        return self.model.listar_pedidos_delivery(
            pagina=pagina, itens_por_pagina=itens_por_pagina,
            filtro_status=filtro_status, busca=busca
        )

    def contar_pedidos(self, filtro_status=None, filtro_origem=None, busca=None) -> int:
        return self.model.contar_pedidos(
            filtro_status=filtro_status, filtro_origem=filtro_origem, busca=busca
        )

    def contar_pedidos_delivery(self, filtro_status=None, busca=None) -> int:
        return self.model.contar_pedidos_delivery(
            filtro_status=filtro_status, busca=busca
        )

    def carregar_resumo_cards(self) -> dict:
        return self.model.carregar_resumo_cards()

    def vendas_por_hora(self) -> list:
        return self.model.vendas_por_hora()

    def vendas_por_datas(self, datas: list) -> dict:
        return self.model.vendas_por_datas(datas)

    def carregar_atrasados_por_origem(self) -> dict:
        return self.model.carregar_atrasados_por_origem()

    def buscar_historico(self, id_pedido: int) -> list:
        return self.model.buscar_historico(id_pedido)

    def buscar_timer_iniciado_em(self, id_pedido: int):
        return self.model.buscar_timer_iniciado_em(id_pedido)
    
    def listar_entregadores(self) -> list:
        return self.model.listar_entregadores()
