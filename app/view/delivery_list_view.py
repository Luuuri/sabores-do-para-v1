import os
import customtkinter as ctk
from datetime import datetime, timedelta
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import Frames, TabelaGenerica, Celulas, Barras, CardProduto, PASTA_PRODUTOS
from app.utils.cache import get_foto_ctk
from app.controller.pedido_controller import PedidoController
from app.controller.produto_controller import ProdutoController
from app.controller.endereco_controller import listar_enderecos, salvar_endereco, excluir_endereco, definir_endereco_principal


class DeliveryListView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Delivery")
        self.minsize(1100, 700)
        self.after(0, lambda: self.state('zoomed'))
        self.lift()
        self.focus_force()

        self.cores = get_cores()
        self.fontes = Fontes()
        self.icones = Icones()
        self.pedido_controller = PedidoController()
        self.controller = ProdutoController()

        self.configure(fg_color=self.cores.fundo.principal)

        self._telas = {"lista": None, "cad": None, "status": None, "pagamento": None}
        self._timers_ativos = {}
        self._id_tick_lista = None
        self._id_timer_central = None
        self._mostrar_lista()
        self.protocol("WM_DELETE_WINDOW", self._voltar_painel)
        self._iniciar_timer_central()

    def _voltar_painel(self):
        self.destroy()
        from app.view.tela_painel_controle import PainelControleView
        PainelControleView(self.master)

    def _recarregar_tema(self):
        self._cancelar_timers()
        self.cores = get_cores()
        self.configure(fg_color=self.cores.fundo.principal)
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass
        self._telas = {"lista": None, "cad": None, "status": None}
        self._mostrar_lista()

    def _abrir_caixa(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.caixa_view import CaixaView
        CaixaView(self.master)

    def _abrir_clientes(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.clientes_view import ClientesView
        ClientesView(self.master)

    def _abrir_estoque(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.estoque_view import EstoqueView
        EstoqueView(self.master)

    def _abrir_funcionarios(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.funcionarios_view import FuncionariosView
        FuncionariosView(self.master)

    def _abrir_produtos(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.produto_view_novo import ProdutosView
        ProdutosView(self.master)

    def _abrir_relatorios(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.relatorio_view import RelatoriosView
        RelatoriosView(self.master)

    def _cancelar_timers(self):
        if self._id_tick_lista:
            self.after_cancel(self._id_tick_lista)
            self._id_tick_lista = None
        if self._id_timer_central:
            self.after_cancel(self._id_timer_central)
            self._id_timer_central = None
        self._timers_ativos.clear()

    def destroy(self):
        self._cancelar_timers()
        self.withdraw()
        try:
            super().destroy()
        except Exception:
            pass

    def _iniciar_timer_central(self):
        if self._id_timer_central:
            return
        self._tick_timer_central()

    def _garantir_timer_central(self):
        if not self._id_timer_central:
            self._iniciar_timer_central()

    def _tick_timer_central(self):
        if not self.winfo_exists():
            self._id_timer_central = None
            return
        if not self._timers_ativos:
            self._id_timer_central = None
            return

        agora = datetime.now()
        vermelho = self.cores.texto.vermelho

        for id_pedido, timer_info in list(self._timers_ativos.items()):
            inicio = timer_info["timer_iniciado_em"]
            tempo_estimado = timer_info["tempo_estimado"]
            tempo_decorrido = int((agora - inicio).total_seconds())
            timer_info["tempo_decorrido_atual"] = tempo_decorrido

            restante = tempo_estimado * 60 - tempo_decorrido
            if restante < 0:
                sinal = "-"
                abs_rest = abs(restante)
            else:
                sinal = ""
                abs_rest = restante
            hrs = abs_rest // 3600
            mins = (abs_rest % 3600) // 60
            secs = abs_rest % 60
            tempo_fmt = f"{sinal}{hrs:02d}:{mins:02d}:{secs:02d}"

            if self._telas["lista"] and self._telas["lista"].winfo_exists():
                try:
                    cor = vermelho if restante <= 0 else None
                    self._telas["lista"].tabela.atualizar_celula(id_pedido, "tempo", tempo_fmt, cor=cor)
                except Exception:
                    pass

            if self._telas["status"] and self._telas["status"].winfo_exists():
                try:
                    id_atual = self._telas["status"]._dados_pedido.get("id_pedido")
                    if id_atual == id_pedido:
                        status_tela = self._telas["status"]
                        if hasattr(status_tela, "_lbl_tempo_decorrido") and status_tela._lbl_tempo_decorrido:
                            cor = vermelho if restante <= 0 else status_tela.cores.texto.principal
                            status_tela._lbl_tempo_decorrido.configure(text=tempo_fmt, text_color=cor)
                except Exception:
                    pass

        self._id_timer_central = self.after(1000, self._tick_timer_central)

    def _mostrar_lista(self):
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()
        if self._telas["status"]:
            self._telas["status"].pack_forget()
        if not self._telas["lista"]:
            self._telas["lista"] = TelaDeliveryLista(
                self, self.cores, self.fontes, self.icones,
                on_novo=self._abrir_cadastro,
                on_editar=self._abrir_status,
                on_excluir=self._excluir_pedido,
                on_home=self._voltar_painel,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._mostrar_lista,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                },
            )
            self._telas["lista"].set_controller(self.pedido_controller)
        self._telas["lista"].pack(fill="both", expand=True)
        self.after(0, self._telas["lista"].recarregar)
        self._telas["lista"]._iniciar_tick_lista()

    def _abrir_cadastro(self, dados=None, limpar=True):
        if self._telas["lista"]:
            self._telas["lista"].pack_forget()
        if self._id_tick_lista:
            self.after_cancel(self._id_tick_lista)
            self._id_tick_lista = None
        if self._telas["status"]:
            self._telas["status"].pack_forget()
        if not self._telas["cad"]:
            self._telas["cad"] = TelaDeliveryCad(
                self, self.cores, self.fontes, self.icones,
                on_voltar=self._mostrar_lista,
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._mostrar_lista,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                },
                pedido_controller=self.pedido_controller,
                controller=self.controller,
            )
        if limpar:
            self._telas["cad"].limpar_formulario()
        if dados:
            self._telas["cad"].preencher_dados(dados)
        elif limpar:
            self._telas["cad"].definir_modo("novo")
        if self._telas["cad"].id_pedido:
            self._telas["cad"].atualizar_info(f"Pedido #{self._telas['cad'].id_pedido:03d}")
        self._telas["cad"].pack(fill="both", expand=True)
        self.update()

    def _abrir_pagamento(self, dados_pedido):
        if self._telas["lista"]:
            self._telas["lista"].pack_forget()
        if self._id_tick_lista:
            self.after_cancel(self._id_tick_lista)
            self._id_tick_lista = None
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()
        if self._telas["status"]:
            self._telas["status"].pack_forget()
        if not self._telas["pagamento"]:
            from app.view.caixa_view import TelaCaixaPagamento
            self._telas["pagamento"] = TelaCaixaPagamento(
                self, self.cores, self.fontes, self.icones,
                on_voltar=lambda: self._abrir_cadastro(limpar=False),
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._mostrar_lista,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                },
            )
        self._telas["pagamento"].carregar_pedido(dados_pedido)
        self._telas["pagamento"].pack(fill="both", expand=True)
        self.update()

    def _abrir_status(self, dados_pedido):
        if self._telas["lista"]:
            self._telas["lista"].pack_forget()
        if self._id_tick_lista:
            self.after_cancel(self._id_tick_lista)
            self._id_tick_lista = None
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()
        if not self._telas["status"]:
            self._telas["status"] = TelaDeliveryStatus(
                self, self.cores, self.fontes, self.icones,
                on_voltar=self._mostrar_lista,
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._mostrar_lista,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                },
                pedido_controller=self.pedido_controller,
            )
        if dados_pedido and "id_pedido" in dados_pedido:
            id_pedido = dados_pedido["id_pedido"]
            pedido_db = self.pedido_controller.buscar_pedido(id_pedido)
            if pedido_db:
                dados_pedido = pedido_db
        self._telas["status"].carregar_pedido(dados_pedido)
        self._telas["status"].pack(fill="both", expand=True)
        self.update()

    def _excluir_pedido(self, id_pedido):
        from app.utils.componentes import DialogoConfirmacao
        DialogoConfirmacao(
            self, self.cores, self.fontes,
            titulo="Excluir Pedido",
            mensagem="Tem certeza que deseja excluir este pedido?",
            on_confirmar=lambda: (
                self.pedido_controller.excluir_pedido(id_pedido),
                self._mostrar_lista()
            )
        )


class TelaDeliveryLista(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_novo=None, on_editar=None, on_excluir=None, on_home=None,
                 menu_callbacks=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Delivery", icone=icones.delivery,
                         on_novo=on_novo, on_home=on_home,
                         menu_callbacks=menu_callbacks,
                         texto_novo="Novo Pedido")
        self.cores, self.fontes, self.icones = cores, fontes, icones
        self.on_editar, self.on_excluir = on_editar, on_excluir
        self.pedido_controller = None
        self._pagina_atual = 1
        self._total_paginas = 1
        self._total_pedidos = 0
        self._criar_area_conteudo()

    def set_controller(self, controller):
        self.pedido_controller = controller

    def _ir_para_pagina(self, n):
        self._pagina_atual = max(1, min(n, self._total_paginas))
        self.recarregar()

    def recarregar(self):
        dados = []
        if self.pedido_controller:
            total = self.pedido_controller.contar_pedidos_delivery()
            self._total_pedidos = total
            self._total_paginas = max(1, (total + 11) // 12)
            self._atualizar_botoes_pagina()
            pedidos = self.pedido_controller.listar_pedidos_delivery(pagina=self._pagina_atual, itens_por_pagina=12)
            for p in pedidos:
                if p.get("timer_iniciado_em") and not p.get("timer_concluido_em") and p.get("status_pedido") in ("em_preparo", "pronto"):
                    inicio = p["timer_iniciado_em"]
                    if hasattr(inicio, 'strftime'):
                        tempo_estimado = p.get("tempo_estimado", 30) or 30
                        if isinstance(tempo_estimado, timedelta):
                            tempo_estimado = int(tempo_estimado.total_seconds() // 60)
                        if p["id_pedido"] not in self.master._timers_ativos:
                            self.master._timers_ativos[p["id_pedido"]] = {
                                "timer_iniciado_em": inicio,
                                "tempo_estimado": tempo_estimado,
                            }
                            self.master._garantir_timer_central()
            for p in pedidos:
                id_pedido = p.get("id_pedido", "")
                tipo_entrega = p.get("tipo_de_pedido", "")
                tipo_label = {"delivery": "Delivery", "retirada": "Retirada"}.get(tipo_entrega, tipo_entrega)
                cliente = p.get("cliente_nome", "—")
                status = p.get("status_pedido", "")
                status_label = status.replace("_", " ").title()
                total = p.get("valor_total", 0) or 0
                total_pago = p.get("total_pago", 0) or 0
                restante = total - total_pago
                if restante <= 0 and total > 0:
                    status_pagamento = "Pago"
                elif total_pago > 0:
                    status_pagamento = "Parcial"
                else:
                    status_pagamento = "Aguardando"
                data = p.get("data_pedido", "")
                if hasattr(data, 'strftime'):
                    data = data.strftime("%d/%m/%Y %H:%M")
                else:
                    data = str(data)[:16] if data else ""
                tempo_estimado = p.get("tempo_estimado", 0) or 0
                if isinstance(tempo_estimado, timedelta):
                    tempo_estimado = int(tempo_estimado.total_seconds() // 60)
                atrasado = False
                timer_info = self.master._timers_ativos.get(id_pedido)
                if timer_info:
                    decorrido = timer_info.get("tempo_decorrido_atual",
                                int((datetime.now() - timer_info["timer_iniciado_em"]).total_seconds()))
                    estimado = timer_info["tempo_estimado"]
                    restante = estimado * 60 - decorrido
                    atrasado = restante <= 0
                    if restante < 0:
                        sinal = "-"
                        abs_rest = abs(restante)
                    else:
                        sinal = ""
                        abs_rest = restante
                    hrs = abs_rest // 3600
                    mins = (abs_rest % 3600) // 60
                    secs = abs_rest % 60
                    tempo = f"{sinal}{hrs:02d}:{mins:02d}:{secs:02d}"
                else:
                    inicio = p.get("timer_iniciado_em")
                    conclusao = p.get("timer_concluido_em")
                    atrasado = p.get("timer_status") == "atrasado"
                    if not inicio:
                        tempo = "--:--"
                    else:
                        if conclusao:
                            decorrido = int((conclusao - inicio).total_seconds())
                        else:
                            decorrido = int((datetime.now() - inicio).total_seconds())
                        if tempo_estimado > 0:
                            restante = tempo_estimado * 60 - decorrido
                            if restante < 0:
                                sinal = "-"
                                abs_rest = abs(restante)
                            else:
                                sinal = ""
                                abs_rest = restante
                            hrs = abs_rest // 3600
                            mins = (abs_rest % 3600) // 60
                            secs = abs_rest % 60
                            tempo = f"{sinal}{hrs:02d}:{mins:02d}:{secs:02d}"
                        else:
                            mins = decorrido // 60
                            secs = decorrido % 60
                            tempo = f"{mins:02d}:{secs:02d}"
                dados.append({
                    "id": id_pedido,
                    "cliente": cliente,
                    "tipo_entrega": tipo_label,
                    "tipo_entrega_filtro": tipo_entrega,
                    "status": status_label,
                    "status_pagamento": status_pagamento,
                    "data": data,
                    "tempo": tempo,
                    "atrasado": atrasado,
                    "acoes": {"id": id_pedido, "dados": p},
                })
        self.tabela.carregar(dados)
        self._atualizar_cards(dados, self.pedido_controller)

    def _criar_area_conteudo(self):
        frame_cards = ctk.CTkFrame(self.area_tela, fg_color="transparent")
        frame_cards.pack(fill="x", padx=30, pady=(20, 10))

        self.cards = {}
        self.cards["vendas_dia"] = self._criar_card(
            frame_cards, "Vendas do dia", self.icones.crescente,
            self.cores.botao.janelas, self.cores.texto.passivo,
            self.cores.texto.verde_jambu, "R$ 0,00"
        )
        self.cards["pedidos_ativos"] = self._criar_card(
            frame_cards, "Pedidos Ativos", self.icones.carteira,
            self.cores.botao.janelas, self.cores.texto.passivo,
            self.cores.texto.verde_jambu, "0"
        )
        self.cards["atrasados"] = self._criar_card(
            frame_cards, "Atrasados", self.icones.relogio,
            self.cores.card.atrasado_card, self.cores.texto.passivo,
            self.cores.texto.atrasado_txt, "0"
        )
        self.cards["pendentes"] = self._criar_card(
            frame_cards, "Pendentes", self.icones.confirmacao,
            self.cores.card.pendentes_card, self.cores.texto.passivo,
            self.cores.texto.laranja, "0"
        )

        frame_atualizar = ctk.CTkFrame(self.area_tela, fg_color="transparent")
        frame_atualizar.pack(fill="x", padx=30, pady=(0, 0))
        self._btn_atualizar = ctk.CTkButton(
            frame_atualizar, text="🔄",
            width=32, height=28, corner_radius=6,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self.recarregar
        )
        self._btn_atualizar.pack(side="right")

        frame_conteudo = Frames.FrameConteudoTabela(self.area_tela, self.cores)
        frame_conteudo.pack(expand=True, fill="both", padx=30, pady=10)

        self.tabela = TabelaGenerica(
            frame_conteudo,
            self.cores,
            self.fontes,
            self.icones,
            placeholder_busca="Pedido, Cliente, Data",
            colunas=[
                {
                    "titulo": "ID",
                    "campo": "id",
                    "peso": 1,
                    "min": 80,
                    "limite": 8,
                    "render": Celulas.CelulaIDCaixa,
                    "tipo": "numero"
                },
                {
                    "titulo": "Cliente",
                    "campo": "cliente",
                    "peso": 2,
                    "min": 150,
                    "limite": 25,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Tipo",
                    "campo": "tipo_entrega",
                    "peso": 1,
                    "min": 90,
                    "limite": 12,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Status",
                    "campo": "status",
                    "peso": 1,
                    "min": 110,
                    "limite": 15,
                    "render": Celulas.CelulaStatusPedido
                },
                {
                    "titulo": "Pagamento",
                    "campo": "status_pagamento",
                    "peso": 1,
                    "min": 100,
                    "limite": 15,
                    "render": Celulas.CelulaStatusPagamento
                },
                {
                    "titulo": "Data",
                    "campo": "data",
                    "peso": 1,
                    "min": 150,
                    "limite": 20,
                    "render": Celulas.CelulaTextoSimples,
                    "tipo": "data"
                },
                {
                    "titulo": "Tempo",
                    "campo": "tempo",
                    "peso": 1,
                    "min": 80,
                    "limite": 10,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Ações",
                    "campo": "acoes",
                    "limite": 5,
                    "align": "nw",
                    "render": Celulas.CelulaAcoes
                },
            ],
            on_editar=lambda d: self.master._abrir_status(d.get("acoes", {}).get("dados") if isinstance(d, dict) and "acoes" in d else d),
            on_excluir=lambda id: self._acao_excluir(id),
            mostrar_busca=True,
            filtros_inline=[
                {
                    "campo": "status",
                    "titulo": "Status",
                    "opcoes": [
                        {"label": "Criado", "valor": "Criado"},
                        {"label": "Confirmado", "valor": "Confirmado"},
                        {"label": "Em Preparo", "valor": "Em Preparo"},
                        {"label": "Pronto", "valor": "Pronto"},
                        {"label": "Entregue", "valor": "Entregue"},
                        {"label": "Concluído", "valor": "Concluido"},
                        {"label": "Cancelado", "valor": "Cancelado"},
                    ]
                },
                {
                    "campo": "tipo_entrega_filtro",
                    "titulo": "Tipo Entrega",
                    "opcoes": [
                        {"label": "Delivery", "valor": "delivery"},
                        {"label": "Retirada", "valor": "retirada"},
                    ]
                },
            ]
        )
        self.tabela.pack(expand=True, fill="both", padx=5, pady=(10, 0))

        self.frame_pag = ctk.CTkFrame(self.area_tela, fg_color="transparent")
        self.frame_pag.pack(fill="x", padx=30, pady=(8, 15))

        self._botoes_pag = []
        self._lbl_total = ctk.CTkLabel(
            self.frame_pag, text="", font=self.fontes.texto_info,
            text_color=self.cores.texto.passivo
        )
        self._lbl_total.pack(side="left", padx=(0, 15))

        self._btn_ant = ctk.CTkButton(
            self.frame_pag, text="<", width=32, height=28, corner_radius=6,
            fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal,
            font=self.fontes.pequeno, command=lambda: self._ir_para_pagina(self._pagina_atual - 1)
        )
        self._btn_ant.pack(side="left", padx=2)

        for i in range(5):
            btn = ctk.CTkButton(
                self.frame_pag, text=str(i + 1), width=32, height=28, corner_radius=6,
                fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal,
                font=self.fontes.pequeno, command=lambda n=i + 1: self._ir_para_pagina(n)
            )
            btn.pack(side="left", padx=2)
            self._botoes_pag.append(btn)

        self._btn_prox = ctk.CTkButton(
            self.frame_pag, text=">", width=32, height=28, corner_radius=6,
            fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal,
            font=self.fontes.pequeno, command=lambda: self._ir_para_pagina(self._pagina_atual + 1)
        )
        self._btn_prox.pack(side="left", padx=2)

    def _atualizar_botoes_pagina(self):
        total = self._total_paginas
        pag = self._pagina_atual
        self._btn_ant.configure(state="normal" if pag > 1 else "disabled")
        self._btn_prox.configure(state="normal" if pag < total else "disabled")
        meio = 2
        inicio = max(1, pag - meio)
        fim = min(total, pag + meio)
        while fim - inicio < 4 and fim < total:
            fim += 1
        while fim - inicio < 4 and inicio > 1:
            inicio -= 1
        for i, btn in enumerate(self._botoes_pag):
            n = inicio + i
            if n <= total:
                btn.configure(text=str(n), state="normal",
                              fg_color=self.cores.botao.novo if n == pag else self.cores.fundo.cinza_claro,
                               text_color=self.cores.texto.branco if n == pag else self.cores.texto.principal,
                              command=lambda p=n: self._ir_para_pagina(p))
                btn.pack(side="left", padx=2)
            else:
                btn.pack_forget()
        if self._lbl_total:
            pag_atual = self._pagina_atual
            itens_pag = min(12, self._total_pedidos - (pag_atual - 1) * 12)
            itens_pag = max(0, itens_pag)
            self._lbl_total.configure(text=f"{itens_pag} de {self._total_pedidos} pedidos")

    def _criar_card(self, parent, texto, icone, cor_card, cor_titulo, cor_valor, valor):
        card = Frames.MetricCard(
            parent, self.cores, self.fontes,
            icone=icone, titulo=texto, valor=valor,
            cor_card=cor_card, cor_titulo=cor_titulo, cor_valor=cor_valor,
        )
        card.pack(side="left", expand=True, fill="both", padx=10, pady=5)
        return card

    def _atualizar_cards(self, dados, pedido_controller=None):
        if pedido_controller:
            resumo = pedido_controller.carregar_resumo_cards()
            self.cards["vendas_dia"].valor_label.configure(text=f"R$ {resumo['vendas_dia']:.2f}")
            self.cards["pedidos_ativos"].valor_label.configure(text=str(resumo['delivery_andamento']))
            self.cards["pendentes"].valor_label.configure(text=str(resumo['pendentes']))
        atrasados = sum(1 for d in dados if d.get("atrasado"))
        self.cards["atrasados"].valor_label.configure(text=str(atrasados))

    def _acao_excluir(self, id_pedido):
        if self.on_excluir:
            self.on_excluir(id_pedido)

    def _iniciar_tick_lista(self):
        if hasattr(self.master, '_id_tick_lista') and self.master._id_tick_lista:
            return
        self.recarregar()
        self.master._id_tick_lista = self.after(30000, self._recarregar_periodico)

    def _recarregar_periodico(self):
        if not self.winfo_exists():
            self.master._id_tick_lista = None
            return
        try:
            self.recarregar()
        except Exception:
            pass
        self.master._id_tick_lista = self.after(30000, self._recarregar_periodico)


class TelaDeliveryCad(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_home=None, menu_callbacks=None,
                 pedido_controller=None, on_click_titulo=None,
                 controller=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Delivery", icone=icones.delivery,
                         on_novo=None, on_home=on_home,
                         menu_callbacks=menu_callbacks,
                         texto_info="Novo Pedido",
                         on_click_titulo=on_click_titulo)
        if self.label_info:
            self.label_info.configure(
                fg_color=self.cores.botao.id_badge,
                text_color=self.cores.botao.id_badge_txt,
                corner_radius=50,
                font=self.fontes.subtitulo,
            )
        self.cores, self.fontes, self.icones = cores, fontes, icones
        self.on_voltar = on_voltar
        self.on_home = on_home
        self.menu_callbacks = menu_callbacks
        self.on_click_titulo = on_click_titulo
        self.pedido_controller = pedido_controller or PedidoController()
        self.controller = controller or ProdutoController()

        self.id_pedido = None
        self._modo = "novo"
        self.etapa_atual = 1

        self._cliente_selecionado = None
        self._tipo_entrega = None
        self._momento_cobranca = None
        self._itens_pedido = []
        self._produto_selecionado_idx = None
        self._categoria_filtro = "Todos"
        self._texto_busca = ""
        self._id_timer_busca = None
        self._cards_produtos = {}
        self._botoes_categorias = {}
        self._resumo_widgets = {}
        self._categorias_hash = None

        self._criar_conteudo()
        self._validar_avancar()

    def definir_modo(self, modo: str):
        self._modo = modo
        if modo == "novo":
            self.atualizar_info("Novo Pedido")
            self._itens_pedido = []
            self._cliente_selecionado = None
            self._tipo_entrega = None
            self._momento_cobranca = None
            if hasattr(self, "_seg_tipo"):
                self._seg_tipo.set(None)
            if hasattr(self, "_seg_cobranca"):
                self._seg_cobranca.set(None)
            if hasattr(self, "_lbl_cliente_nome"):
                self._lbl_cliente_nome.configure(text="")
            self._atualizar_resumo()
            self._validar_avancar()
        elif self.id_pedido:
            self.atualizar_info(f"Pedido #{self.id_pedido}")

    def limpar_formulario(self):
        self.id_pedido = None
        self._modo = "novo"
        self.atualizar_info("Novo Pedido")
        self._itens_pedido = []
        self._cliente_selecionado = None
        self._tipo_entrega = None
        self._momento_cobranca = None
        self._resumo_widgets.clear()
        if hasattr(self, "_seg_tipo"):
            self._seg_tipo.set(None)
        if hasattr(self, "_seg_cobranca"):
            self._seg_cobranca.set(None)
        if hasattr(self, "_lbl_cliente_nome"):
            self._lbl_cliente_nome.configure(text="")

    def preencher_dados(self, dados: dict):
        self.id_pedido = dados.get("id_pedido")
        self._modo = "editar"
        if self.id_pedido:
            self.atualizar_info(f"Pedido #{self.id_pedido}")
        self._itens_pedido = [
            {"id_produto": i["id_produto"], "qtd": i.get("quantidade", 1),
             "preco": i.get("preco", 0), "nome": i.get("nome", ""),
             "foto": i.get("foto", "")}
            for i in dados.get("itens", [])
        ]
        self._atualizar_resumo()

    def _criar_conteudo(self):
        principal = ctk.CTkFrame(self.area_tela, fg_color="transparent")
        principal.pack(fill="both", expand=True, padx=50, pady=20)

        frame_stepper = ctk.CTkFrame(
            principal, fg_color=self.cores.fundo.branco,
            corner_radius=12, height=46
        )
        frame_stepper.pack(fill="x", pady=(0, 20))
        frame_stepper.pack_propagate(False)

        self.stepper = Frames.StepperPassos(
            frame_stepper, self.cores, self.fontes,
            etapas=[
                {"num": "1", "label": "Cliente"},
                {"num": "2", "label": "Itens"},
                {"num": "3", "label": "Pagamento"},
                {"num": "4", "label": "Status"},
            ],
            etapa_atual=self.etapa_atual,
            padx_circle=(60, 6), padx_label=(0, 120)
        )
        self.stepper.pack(expand=True)

        self._frame_etapas = ctk.CTkFrame(principal, fg_color="transparent")
        self._frame_etapas.pack(fill="both", expand=True)

        self._frame_etapa_cliente = ctk.CTkFrame(self._frame_etapas, fg_color="transparent")
        self._frame_etapa_itens = ctk.CTkFrame(self._frame_etapas, fg_color="transparent")
        self._frame_etapa_pagamento = ctk.CTkFrame(self._frame_etapas, fg_color="transparent")
        self._frame_etapa_status = ctk.CTkFrame(self._frame_etapas, fg_color="transparent")

        self._criar_etapa_cliente(self._frame_etapa_cliente)
        self._criar_etapa_itens(self._frame_etapa_itens)
        self._criar_etapa_pagamento(self._frame_etapa_pagamento)
        self._criar_etapa_status(self._frame_etapa_status)

        self._mostrar_etapa(1)

    def _mostrar_etapa(self, numero):
        self.etapa_atual = numero
        if hasattr(self, "stepper"):
            self.stepper.atualizar(numero)
        self._frame_etapa_cliente.pack_forget()
        self._frame_etapa_itens.pack_forget()
        if numero == 1:
            self._frame_etapa_cliente.pack(fill="both", expand=True)
        elif numero == 2:
            self._frame_etapa_itens.pack(fill="both", expand=True)
            self._recarregar_produtos_etapa2()

    def _criar_etapa_cliente(self, parent):
        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        frame_esq = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.branco,
            border_width=2, border_color=self.cores.card.borda_card,
            corner_radius=12
        )
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        frame_esq.grid_rowconfigure(2, weight=1)
        frame_esq.grid_columnconfigure(0, weight=1)

        frame_topo = ctk.CTkFrame(frame_esq, fg_color="transparent")
        frame_topo.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        ctk.CTkLabel(
            frame_topo, text="Selecionar Cliente",
            font=self.fontes.subtitulo, text_color=self.cores.texto.principal
        ).pack(side="left")

        ctk.CTkButton(
            frame_topo, text="+ Novo Cliente", height=28, corner_radius=8,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco, font=self.fontes.pequeno,
            command=self._abrir_novo_cliente
        ).pack(side="right")

        from app.utils.componentes import Barras
        self._entry_busca_cliente = Barras.HeaderBusca(
            frame_esq, self.cores, self.fontes, self.icones,
            placeholder="cliente...",
            search_callback=self._filtrar_clientes,
            altura=20
        )
        self._entry_busca_cliente.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))

        self._frame_lista_clientes = ctk.CTkScrollableFrame(
            frame_esq, fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.botao.scroll,
            scrollbar_button_hover_color=self.cores.botao.scroll_hover
        )
        self._frame_lista_clientes.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 8))

        self._carregar_clientes()

        frame_dir = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.branco,
            border_width=2, border_color=self.cores.card.borda_card,
            corner_radius=12
        )
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(
            frame_dir, text="Tipo de Pedido",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(12, 4))

        self._seg_tipo = ctk.CTkSegmentedButton(
            frame_dir, values=["Delivery", "Retirada"],
            height=28, corner_radius=8,
            selected_color=self.cores.botao.novo,
            selected_hover_color=self.cores.botao.novo_hover,
            unselected_color=self.cores.fundo.cinza_claro,
            unselected_hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._selecionar_tipo_entrega
        )
        self._seg_tipo.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(
            frame_dir, text="Momento da Cobrança",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(0, 4))

        self._seg_cobranca = ctk.CTkSegmentedButton(
            frame_dir, values=["Antecipado", "Na Entrega"],
            height=28, corner_radius=8,
            selected_color=self.cores.botao.novo,
            selected_hover_color=self.cores.botao.novo_hover,
            unselected_color=self.cores.fundo.cinza_claro,
            unselected_hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._selecionar_cobranca
        )
        self._seg_cobranca.pack(fill="x", padx=15, pady=(0, 8))

        self._frame_entregador = ctk.CTkFrame(frame_dir, fg_color="transparent")
        ctk.CTkLabel(
            self._frame_entregador, text="Entregador",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(0, 4))

        self._entregadores = self.pedido_controller.listar_entregadores()
        nomes = [e["nome"] for e in self._entregadores] if self._entregadores else ["Nenhum disponível"]

        self._combo_entregador = ctk.CTkOptionMenu(
            self._frame_entregador,
            values=nomes,
            height=28, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            button_color=self.cores.botao.novo,
            button_hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._selecionar_entregador
        )
        self._combo_entregador.pack(fill="x", padx=15, pady=(0, 4))
        self._entregador_selecionado = None

        frame_botoes_entregador = ctk.CTkFrame(self._frame_entregador, fg_color="transparent")
        frame_botoes_entregador.pack(fill="x", padx=15, pady=(0, 8))

        self._btn_editar_entregador = ctk.CTkButton(
            frame_botoes_entregador, text="Editar", height=24, corner_radius=6,
            fg_color=self.cores.fundo.cinza_claro,
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._editar_entregador
        )
        self._btn_editar_entregador.pack(side="left", padx=(0, 4), expand=True, fill="x")

        self._btn_excluir_entregador = ctk.CTkButton(
            frame_botoes_entregador, text="Remover", height=24, corner_radius=6,
            fg_color=self.cores.botao.excluir,
            hover_color=self.cores.fundo.vermelho,
            text_color=self.cores.texto.branco,
            font=self.fontes.pequeno,
            command=self._excluir_entregador
        )
        self._btn_excluir_entregador.pack(side="left", expand=True, fill="x")

        self._frame_taxa = ctk.CTkFrame(frame_dir, fg_color="transparent")
        ctk.CTkLabel(
            self._frame_taxa, text="Taxa de Entrega (R$)",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(0, 4))

        self._entry_taxa = ctk.CTkEntry(
            self._frame_taxa, height=28, corner_radius=8,
            fg_color=self.cores.entry.formulario,
            border_color=self.cores.input.borda_entry,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            placeholder_text="0,00"
        )
        self._entry_taxa.pack(fill="x", padx=15, pady=(0, 8))
        self._taxa_entrega = 0.0

        self._frame_endereco = ctk.CTkFrame(frame_dir, fg_color="transparent")
        ctk.CTkLabel(
            self._frame_endereco, text="Endereço de Entrega",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(0, 4))

        self._endereco_selecionado = None
        self._enderecos_cliente = []

        self._combo_endereco = ctk.CTkOptionMenu(
            self._frame_endereco,
            values=["Selecione um cliente"],
            height=28, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            button_color=self.cores.botao.novo,
            button_hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._selecionar_endereco
        )
        self._combo_endereco.pack(fill="x", padx=15, pady=(0, 4))

        frame_botoes_endereco = ctk.CTkFrame(self._frame_endereco, fg_color="transparent")
        frame_botoes_endereco.pack(fill="x", padx=15, pady=(0, 8))

        self._btn_novo_endereco = ctk.CTkButton(
            frame_botoes_endereco, text="+ Novo", height=24, corner_radius=6,
            fg_color=self.cores.botao.novo,
            hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco,
            font=self.fontes.pequeno,
            command=self._abrir_novo_endereco
        )
        self._btn_novo_endereco.pack(side="left", padx=(0, 4), expand=True, fill="x")

        self._btn_editar_endereco = ctk.CTkButton(
            frame_botoes_endereco, text="Editar", height=24, corner_radius=6,
            fg_color=self.cores.fundo.cinza_claro,
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._editar_endereco
        )
        self._btn_editar_endereco.pack(side="left", expand=True, fill="x")

        ctk.CTkFrame(frame_dir, height=1, fg_color=self.cores.card.borda_card).pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(
            frame_dir, text="Cliente Selecionado",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(4, 2))

        self._lbl_cliente_nome = ctk.CTkLabel(
            frame_dir, text="Nenhum selecionado",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        )
        self._lbl_cliente_nome.pack(anchor="w", padx=15, pady=(0, 8))

        self._btn_confirmar_etapa1 = ctk.CTkButton(
            frame_dir, text="Confirmar  →", height=34, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.passivo,
            font=self.fontes.texto_info,
            state="disabled",
            command=lambda: self._mostrar_etapa(2)
        )
        self._btn_confirmar_etapa1.pack(fill="x", padx=15, pady=(8, 15), side="bottom")

    def _carregar_clientes(self, busca=""):
        for w in self._frame_lista_clientes.winfo_children():
            w.destroy()
        from app.controller.cliente_controller import listar_clientes, buscar_clientes
        if busca and busca.strip():
            clientes = buscar_clientes(busca)
        else:
            clientes = listar_clientes()
        if not clientes:
            ctk.CTkLabel(
                self._frame_lista_clientes,
                text="Nenhum cliente encontrado",
                font=self.fontes.pequeno,
                text_color=self.cores.texto.passivo
            ).pack(pady=20)
            return
        for cliente in clientes:
            self._criar_card_cliente(cliente)

    def _criar_card_cliente(self, cliente):
        id_cliente = cliente.get("id_cliente") or cliente.get("id")
        nome = cliente.get("nome", "")
        telefone = cliente.get("telefone", "")
        selecionado = (
            self._cliente_selecionado is not None and
            (self._cliente_selecionado.get("id_cliente") or (self._cliente_selecionado.get("id_cliente") or self._cliente_selecionado.get("id"))) == id_cliente
        )
        cor_fundo = self.cores.fundo.roxo if selecionado else self.cores.fundo.secundario
        frame = ctk.CTkFrame(
            self._frame_lista_clientes,
            fg_color=cor_fundo,
            corner_radius=8,
            border_width=1,
            border_color=self.cores.card.borda_card,
            height=48, cursor="hand2"
        )
        frame.pack(fill="x", pady=2, padx=4)
        frame.pack_propagate(False)
        ctk.CTkLabel(
            frame, text=nome,
            font=self.fontes.pequeno, text_color=self.cores.texto.principal
        ).pack(side="left", padx=10, pady=4)
        ctk.CTkLabel(
            frame, text=telefone,
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(side="right", padx=10)
        frame.bind("<Button-1>", lambda e, c=cliente: self._selecionar_cliente(c))
        for widget in frame.winfo_children():
            widget.bind("<Button-1>", lambda e, c=cliente: self._selecionar_cliente(c))

    def _filtrar_clientes(self, termo):
        self._carregar_clientes(busca=termo)

    def _selecionar_cliente(self, dados):
        self._cliente_selecionado = dados
        nome = dados.get("nome", "")
        self._lbl_cliente_nome.configure(
            text=nome, text_color=self.cores.texto.verde_jambu
        )
        self._carregar_clientes()
        id_cliente = dados.get("id_cliente") or dados.get("id")
        self._carregar_enderecos_cliente(id_cliente)
        self._validar_etapa1()

    def _carregar_enderecos_cliente(self, id_cliente):
        if not id_cliente:
            self._enderecos_cliente = []
            self._combo_endereco.configure(values=["Nenhum cliente selecionado"])
            self._combo_endereco.set("Nenhum cliente selecionado")
            return

        from app.controller.endereco_controller import listar_enderecos
        self._enderecos_cliente = listar_enderecos(id_cliente) or []

        if not self._enderecos_cliente and self._cliente_selecionado:
            logradouro = self._cliente_selecionado.get("logradouro", "")
            if logradouro:
                self._enderecos_cliente = [{
                    "id_endereco": None,
                    "apelido": "Principal",
                    "cep": self._cliente_selecionado.get("cep", ""),
                    "logradouro": logradouro,
                    "numero": self._cliente_selecionado.get("numero", ""),
                    "bairro": self._cliente_selecionado.get("bairro", ""),
                    "cidade": self._cliente_selecionado.get("cidade", ""),
                    "complemento": self._cliente_selecionado.get("complemento", ""),
                    "principal": 1
                }]

        if not self._enderecos_cliente:
            self._combo_endereco.configure(values=["Nenhum endereço cadastrado"])
            self._combo_endereco.set("Nenhum endereço cadastrado")
            self._endereco_selecionado = None
            return

        opcoes = []
        for i, end in enumerate(self._enderecos_cliente):
            apelido = end.get("apelido", "")
            logradouro = end.get("logradouro", "")
            numero = end.get("numero", "")
            bairro = end.get("bairro", "")
            rotulo = f"{apelido} - {logradouro}, {numero} - {bairro}" if apelido else f"{logradouro}, {numero} - {bairro}"
            opcoes.append(rotulo)

        self._combo_endereco.configure(values=opcoes)
        self._combo_endereco.set(opcoes[0])
        self._endereco_selecionado = self._enderecos_cliente[0]

    def _selecionar_endereco(self, valor):
        for i, end in enumerate(self._enderecos_cliente):
            apelido = end.get("apelido", "")
            logradouro = end.get("logradouro", "")
            numero = end.get("numero", "")
            bairro = end.get("bairro", "")
            rotulo = f"{apelido} - {logradouro}, {numero} - {bairro}" if apelido else f"{logradouro}, {numero} - {bairro}"
            if rotulo == valor:
                self._endereco_selecionado = end
                self._buscar_taxa_bairro(bairro)
                break

    def _buscar_taxa_bairro(self, bairro):
        from app.controller.taxa_entrega_controller import buscar_taxa_por_bairro
        taxa = buscar_taxa_por_bairro(bairro)
        if taxa:
            valor = taxa.get("valor", 0.0)
            self._taxa_entrega = float(valor)
            self._entry_taxa.delete(0, "end")
            self._entry_taxa.insert(0, f"{valor:.2f}".replace(".", ","))
        else:
            self._taxa_entrega = 0.0
            self._entry_taxa.delete(0, "end")
            self._entry_taxa.insert(0, "0,00")

    def _abrir_novo_cliente(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Novo Cliente")
        popup.geometry("600x700")
        popup.grab_set()

    def _abrir_novo_endereco(self):
        if not self._cliente_selecionado:
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Novo Endereço")
        popup.geometry("450x580")
        popup.grab_set()

        frame = ctk.CTkScrollableFrame(
            popup, fg_color=self.cores.fundo.branco,
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.fundo.cinza_claro,
            scrollbar_button_hover_color=self.cores.fundo.cinza_claro,
        )
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            frame, text="Novo Endereço de Entrega",
            font=self.fontes.titulo, text_color=self.cores.texto.principal
        ).pack(anchor="w", pady=(0, 12))

        labels = ["Apelido (opcional)", "CEP", "Logradouro", "Número", "Bairro", "Cidade", "Complemento"]
        entries = {}
        for label in labels:
            ctk.CTkLabel(frame, text=label, font=self.fontes.pequeno, text_color=self.cores.texto.principal).pack(anchor="w", padx=10, pady=(4, 0))
            entry = ctk.CTkEntry(frame, height=28, corner_radius=8, fg_color=self.cores.entry.formulario, border_color=self.cores.input.borda_entry, text_color=self.cores.texto.principal, font=self.fontes.pequeno)
            entry.pack(fill="x", padx=10, pady=(0, 4))
            entries[label] = entry

        def salvar():
            dados = {
                "id_cliente": (self._cliente_selecionado.get("id_cliente") or self._cliente_selecionado.get("id")),
                "apelido": entries["Apelido (opcional)"].get().strip(),
                "cep": entries["CEP"].get().strip(),
                "logradouro": entries["Logradouro"].get().strip(),
                "numero": entries["Número"].get().strip(),
                "bairro": entries["Bairro"].get().strip(),
                "cidade": entries["Cidade"].get().strip(),
                "complemento": entries["Complemento"].get().strip(),
                "principal": False
            }
            if not dados["logradouro"] or not dados["numero"] or not dados["bairro"]:
                from app.utils.componentes import DialogoConfirmacao
                DialogoConfirmacao(self, "Atenção", "Preencha Logradouro, Número e Bairro.")
                return
            from app.controller.endereco_controller import salvar_endereco
            salvar_endereco(dados)
            popup.destroy()
            self._carregar_enderecos_cliente((self._cliente_selecionado.get("id_cliente") or self._cliente_selecionado.get("id")))

        ctk.CTkButton(
            frame, text="Salvar", height=32, corner_radius=8,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco, font=self.fontes.texto_info,
            command=salvar
        ).pack(fill="x", padx=10, pady=(12, 0))

    def _editar_endereco(self):
        if not self._endereco_selecionado:
            from app.utils.componentes import DialogoConfirmacao
            DialogoConfirmacao(self, "Atenção", "Selecione um endereço para editar.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Editar Endereço")
        popup.geometry("450x580")
        popup.grab_set()

        frame = ctk.CTkScrollableFrame(
            popup, fg_color=self.cores.fundo.branco,
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.fundo.cinza_claro,
            scrollbar_button_hover_color=self.cores.fundo.cinza_claro,
        )
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            frame, text="Editar Endereço",
            font=self.fontes.titulo, text_color=self.cores.texto.principal
        ).pack(anchor="w", pady=(0, 12))

        labels = ["Apelido", "CEP", "Logradouro", "Número", "Bairro", "Cidade", "Complemento"]
        entries = {}
        valores = self._endereco_selecionado
        for label in labels:
            ctk.CTkLabel(frame, text=label, font=self.fontes.pequeno, text_color=self.cores.texto.principal).pack(anchor="w", padx=10, pady=(4, 0))
            entry = ctk.CTkEntry(frame, height=28, corner_radius=8, fg_color=self.cores.entry.formulario, border_color=self.cores.input.borda_entry, text_color=self.cores.texto.principal, font=self.fontes.pequeno)
            entry.pack(fill="x", padx=10, pady=(0, 4))
            valor = valores.get(label.lower().replace(" (opcional)", ""), "")
            if valor:
                entry.insert(0, str(valor))
            entries[label] = entry

        def salvar():
            dados = {
                "id_endereco": self._endereco_selecionado.get("id_endereco"),
                "id_cliente": (self._cliente_selecionado.get("id_cliente") or self._cliente_selecionado.get("id")),
                "apelido": entries["Apelido"].get().strip(),
                "cep": entries["CEP"].get().strip(),
                "logradouro": entries["Logradouro"].get().strip(),
                "numero": entries["Número"].get().strip(),
                "bairro": entries["Bairro"].get().strip(),
                "cidade": entries["Cidade"].get().strip(),
                "complemento": entries["Complemento"].get().strip(),
                "principal": self._endereco_selecionado.get("principal", False)
            }
            if not dados["logradouro"] or not dados["numero"] or not dados["bairro"]:
                from app.utils.componentes import DialogoConfirmacao
                DialogoConfirmacao(self, "Atenção", "Preencha Logradouro, Número e Bairro.")
                return
            from app.controller.endereco_controller import salvar_endereco
            salvar_endereco(dados)
            popup.destroy()
            self._carregar_enderecos_cliente((self._cliente_selecionado.get("id_cliente") or self._cliente_selecionado.get("id")))

        ctk.CTkButton(
            frame, text="Salvar", height=32, corner_radius=8,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco, font=self.fontes.texto_info,
            command=salvar
        ).pack(fill="x", padx=10, pady=(12, 0))
        popup = ctk.CTkToplevel(self)
        popup.title("Novo Cliente")
        popup.geometry("600x700")
        popup.grab_set()

    def _selecionar_tipo_entrega(self, valor):
        self._tipo_entrega = {"Delivery": "delivery", "Retirada": "retirada"}.get(valor)
        if self._tipo_entrega == "delivery":
            self._frame_entregador.pack(fill="x")
            self._frame_taxa.pack(fill="x")
            self._frame_endereco.pack(fill="x")
        else:
            self._frame_entregador.pack_forget()
            self._frame_taxa.pack_forget()
            self._frame_endereco.pack_forget()
            self._entregador_selecionado = None
            self._taxa_entrega = 0.0
            self._endereco_selecionado = None
        self._validar_etapa1()

    def _selecionar_entregador(self, nome):
        for e in self._entregadores:
            if e["nome"] == nome:
                self._entregador_selecionado = e
                break
        self._validar_etapa1()

    def _editar_entregador(self):
        if not self._entregador_selecionado:
            return
        id_func = self._entregador_selecionado.get("id_funcionario")
        if not id_func:
            return
        self.master._cancelar_timers()
        self.master.destroy()
        from app.view.funcionarios_view import FuncionariosView
        view = FuncionariosView(self.master)
        from app.controller.funcionario_controller import buscar_funcionario
        dados = buscar_funcionario(id_func)
        if dados:
            view._abrir_cadastro(dados)

    def _excluir_entregador(self):
        if not self._entregador_selecionado:
            return
        id_func = self._entregador_selecionado.get("id_funcionario")
        if not id_func:
            return
        from app.utils.componentes import DialogoConfirmacao
        DialogoConfirmacao(
            self, self.cores, self.fontes,
            titulo="Remover Entregador",
            mensagem="Tem certeza que deseja remover este entregador? Ele será desmarcado como entregador.",
            on_confirmar=lambda: self._confirmar_excluir_entregador(id_func)
        )

    def _confirmar_excluir_entregador(self, id_func):
        from app.controller.funcionario_controller import buscar_funcionario, salvar_funcionario
        dados = buscar_funcionario(id_func)
        if dados:
            dados["is_entregador"] = False
            dados["id"] = id_func
            if dados.get("senha") is None:
                dados.pop("senha", None)
            salvar_funcionario(dados)
        self._entregadores = self.pedido_controller.listar_entregadores()
        nomes = [e["nome"] for e in self._entregadores] if self._entregadores else ["Nenhum disponível"]
        self._combo_entregador.configure(values=nomes)
        self._entregador_selecionado = None
        self._combo_entregador.set(nomes[0] if nomes else "Nenhum disponível")

    def _validar_etapa1(self):
        tem_cliente = self._cliente_selecionado is not None
        tem_tipo = self._tipo_entrega is not None
        tem_cobranca = self._momento_cobranca is not None
        tem_entregador = (
            self._tipo_entrega == "retirada" or
            self._entregador_selecionado is not None
        )
        tem_endereco = (
            self._tipo_entrega == "retirada" or
            self._endereco_selecionado is not None
        )
        if tem_cliente and tem_tipo and tem_cobranca and tem_entregador and tem_endereco:
            self._btn_confirmar_etapa1.configure(
                fg_color=self.cores.botao.novo,
                hover_color=self.cores.botao.novo_hover,
                text_color=self.cores.texto.branco,
                state="normal"
            )
        else:
            self._btn_confirmar_etapa1.configure(
                fg_color=self.cores.fundo.cinza_claro,
                text_color=self.cores.texto.passivo,
                state="disabled"
            )

    def _recarregar_produtos_etapa2(self):
        produtos = self._obter_produtos()
        categorias_atual = tuple(sorted(set(p["categoria"] for p in produtos if p.get("ativo"))))
        if categorias_atual != self._categorias_hash:
            self._inicializar_categorias(produtos)
            self._inicializar_cards(produtos)
        else:
            self._aplicar_filtro_cards()
            
    def _criar_etapa_itens(self, parent):
        parent.grid_columnconfigure(0, weight=3)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        frame_produtos = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.branco,
            border_width=2, border_color=self.cores.card.borda_card,
            corner_radius=12
        )
        frame_produtos.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._criar_area_produtos(frame_produtos)

        frame_resumo = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.branco,
            border_width=2, border_color=self.cores.card.borda_card,
            corner_radius=12
        )
        frame_resumo.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._criar_area_resumo(frame_resumo)        

    def _selecionar_cobranca(self, valor):
        self._momento_cobranca = {"Antecipado": "antecipado", "Na Entrega": "na_entrega"}.get(valor)
        self._validar_etapa1()

    def _criar_etapa_pagamento(self, parent):
        from app.view.caixa_view import TelaCaixaPagamento
        self._tela_pagamento = TelaCaixaPagamento(
            parent, self.cores, self.fontes, self.icones,
            on_voltar=lambda: self._mostrar_etapa(2),
            on_home=self.on_home,
            menu_callbacks=self.menu_callbacks,
            on_click_titulo=self.on_click_titulo,
        )
        self._tela_pagamento.pack(fill="both", expand=True)

    def _abrir_pagamento(self):
        dados = self._pedido_criado_dados
        subtotal = sum(i["preco"] * i["qtd"] for i in self._itens_pedido)
        dados["subtotal"] = subtotal
        dados["origem"] = "delivery"
        dados["num_mesa"] = None
        dados["obs"] = self.txt_obs.get("1.0", "end").strip() if hasattr(self, "txt_obs") else ""
        self._tela_pagamento.carregar_pedido(dados)
        self._tela_pagamento.on_voltar = lambda: self._mostrar_etapa(2)

    def _criar_etapa_status(self, parent):
        from app.view.caixa_view import TelaCaixaStatus
        self._tela_status = TelaCaixaStatus(
            parent, self.cores, self.fontes, self.icones,
            on_voltar=lambda: self._mostrar_etapa(1),
            on_home=self.on_home,
            pedido_controller=self.pedido_controller,
            menu_callbacks=self.menu_callbacks,
            on_click_titulo=self.on_click_titulo,
        )
        self._tela_status.pack(fill="both", expand=True)

    def _abrir_status(self):
        dados = self._pedido_criado_dados
        self._tela_status.carregar_pedido(dados)
        self._tela_status.on_voltar = lambda: self._mostrar_etapa(1)

    def _criar_area_produtos(self, parent):
        cabecalho = ctk.CTkFrame(parent, fg_color="transparent")
        cabecalho.pack(fill="x", padx=12, pady=(10, 5))

        ctk.CTkButton(
            cabecalho, text="", image=self.icones.voltar_pequeno,
            width=30, height=30,
            fg_color="transparent", hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.secundario, font=ctk.CTkFont(size=12),
            command=self.on_voltar
        ).pack(side="left")

        ctk.CTkLabel(
            cabecalho, text="Produtos",
            font=self.fontes.subtitulo, text_color=self.cores.texto.principal
        ).pack(side="left", padx=10)

        frame_topo = ctk.CTkFrame(parent, fg_color="transparent")
        frame_topo.pack(fill="x", padx=12, pady=(0, 6))

        self._entry_busca = Barras.HeaderBusca(
            frame_topo, self.cores, self.fontes, self.icones,
            placeholder="produtos", search_callback=self._ao_digitar_busca,
            altura=20
        )
        self._entry_busca.pack(side="left", fill="x", padx=(0, 8))

        self._frame_filtros = ctk.CTkFrame(frame_topo, fg_color="transparent")
        self._frame_filtros.pack(side="left")

        self._frame_grid = ctk.CTkScrollableFrame(
            parent, fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.botao.scroll,
            scrollbar_button_hover_color=self.cores.botao.scroll_hover
        )
        self._frame_grid.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        for col in range(4):
            self._frame_grid.grid_columnconfigure(col, weight=1)

        produtos = self._obter_produtos()
        self._inicializar_categorias(produtos)
        self._inicializar_cards(produtos)

    def _obter_produtos(self):
        return self.controller.listar_produtos()

    def _inicializar_categorias(self, produtos):
        categorias = sorted(set(p["categoria"] for p in produtos if p.get("ativo")))
        self._categorias_hash = tuple(categorias)

        for w in self._frame_filtros.winfo_children():
            w.destroy()
        self._botoes_categorias.clear()

        btn_todos = ctk.CTkButton(
            self._frame_filtros, text="Todos", height=26, corner_radius=13,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.branco, font=self.fontes.pequeno, width=0,
            command=lambda: self._filtrar_categoria("Todos")
        )
        btn_todos.pack(side="left", padx=(0, 3))
        self._botoes_categorias["Todos"] = btn_todos

        for cat in categorias:
            btn = ctk.CTkButton(
                self._frame_filtros, text=cat, height=26, corner_radius=13,
                fg_color=self.cores.fundo.secundario, hover_color=self.cores.botao.hover,
                text_color=self.cores.texto.principal, font=self.fontes.pequeno, width=0,
                command=lambda c=cat: self._filtrar_categoria(c)
            )
            btn.pack(side="left", padx=(0, 3))
            self._botoes_categorias[cat] = btn

    def _inicializar_cards(self, produtos):
        for w in self._frame_grid.winfo_children():
            w.destroy()
        self._cards_produtos.clear()

        produtos_ativos = [p for p in produtos if p.get("ativo")]
        for i, prod in enumerate(produtos_ativos):
            card = CardProduto(
                self._frame_grid, self.cores, self.fontes, self.icones, prod,
                on_adicionar=self._adicionar_item
            )
            row = i // 4
            col = i % 4
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            self._cards_produtos[prod["id_produto"]] = card

    def _filtrar_categoria(self, categoria):
        self._categoria_filtro = categoria
        for nome, btn in self._botoes_categorias.items():
            selecionada = (self._categoria_filtro == nome)
            btn.configure(
                fg_color=self.cores.botao.novo if selecionada else self.cores.fundo.secundario,
                text_color=self.cores.texto.branco if selecionada else self.cores.texto.principal,
            )
        self._aplicar_filtro_cards()

    def _ao_digitar_busca(self, termo):
        if self._id_timer_busca:
            self.after_cancel(self._id_timer_busca)
        self._id_timer_busca = self.after(300, lambda: self._executar_busca(termo))

    def _executar_busca(self, termo):
        self._id_timer_busca = None
        self._texto_busca = termo.strip().lower()
        self._aplicar_filtro_cards()

    def _aplicar_filtro_cards(self):
        visiveis = 0
        for id_produto, card in self._cards_produtos.items():
            prod = card.produto
            if not prod.get("ativo"):
                card.grid_forget()
                continue
            if self._categoria_filtro != "Todos" and prod["categoria"] != self._categoria_filtro:
                card.grid_forget()
                continue
            if self._texto_busca:
                texto = self._texto_busca
                if texto not in prod["nome"].lower() and texto not in (prod.get("descricao") or "").lower():
                    card.grid_forget()
                    continue
            row = visiveis // 4
            col = visiveis % 4
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            visiveis += 1

    def _adicionar_item(self, produto):
        for item in self._itens_pedido:
            if item["id_produto"] == produto["id_produto"]:
                item["qtd"] += 1
                self._atualizar_resumo()
                self._validar_avancar()
                return
        self._itens_pedido.append({
            "id_produto": produto["id_produto"],
            "nome": produto["nome"],
            "preco": float(produto["preco"]),
            "foto": produto.get("foto", ""),
            "qtd": 1
        })
        self._atualizar_resumo()
        self._validar_avancar()

    def _criar_area_resumo(self, parent):
        frame_bottom = ctk.CTkFrame(parent, fg_color="transparent")
        frame_bottom.pack(side="bottom", fill="x", padx=8, pady=(0, 8))

        frame_valores = ctk.CTkFrame(
            frame_bottom, fg_color=self.cores.fundo.secundario, corner_radius=8
        )
        frame_valores.pack(fill="x", pady=(0, 6))

        f1 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f1.pack(fill="x", padx=10, pady=(6, 1))
        ctk.CTkLabel(f1, text="Subtotal:", font=self.fontes.pequeno, text_color=self.cores.texto.passivo).pack(side="left")
        self._lbl_subtotal = ctk.CTkLabel(f1, text="R$ 0,00", font=self.fontes.pequeno, text_color=self.cores.texto.principal)
        self._lbl_subtotal.pack(side="right")

        ctk.CTkFrame(frame_valores, height=1, fg_color=self.cores.card.borda_card).pack(fill="x", padx=10, pady=(4, 4))

        f3 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f3.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(f3, text="Total:", font=self.fontes.texto_info, text_color=self.cores.texto.principal).pack(side="left")
        self._lbl_total = ctk.CTkLabel(f3, text="R$ 0,00", font=self.fontes.texto_info, text_color=self.cores.texto.verde_escuro)
        self._lbl_total.pack(side="right")

        self._btn_avancar = ctk.CTkButton(
            frame_bottom, text="Avancar  →", height=34, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.passivo,
            font=self.fontes.texto_info,
            state="disabled",
            command=self._avancar
        )
        self._btn_avancar.pack(fill="x")

        frame_obs = ctk.CTkFrame(parent, fg_color="transparent")
        frame_obs.pack(side="bottom", fill="x", padx=8, pady=(0, 4))

        ctk.CTkLabel(
            frame_obs, text="Observacoes (opcional):",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w", padx=4, pady=(0, 2))

        self.txt_obs = ctk.CTkTextbox(
            frame_obs, corner_radius=6, border_width=1,
            border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal,
            font=self.fontes.texto_entry, height=60
        )
        self.txt_obs.pack(fill="x", padx=4)

        ctk.CTkLabel(
            parent, text="Resumo do Pedido",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=12, pady=(6, 2))

        self._frame_lista_itens = ctk.CTkScrollableFrame(
            parent, fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.fundo.cinza_claro,
            scrollbar_button_hover_color=self.cores.fundo.cinza_claro
        )
        self._frame_lista_itens.pack(fill="both", expand=True, padx=4, pady=(0, 2))

    def _atualizar_resumo(self):
        ids_atuais = {item["id_produto"] for item in self._itens_pedido}
        ids_widget = set(self._resumo_widgets.keys())

        for id_produto in ids_widget - ids_atuais:
            widgets = self._resumo_widgets.pop(id_produto)
            widgets["frame"].destroy()

        for item in self._itens_pedido:
            id_produto = item["id_produto"]
            if id_produto in self._resumo_widgets:
                self._atualizar_item_resumo(id_produto, item)
            else:
                self._criar_item_resumo(self._frame_lista_itens, item)

        subtotal = sum(i["preco"] * i["qtd"] for i in self._itens_pedido)
        texto_sub = f"R$ {subtotal:.2f}".replace(".", ",")
        self._lbl_subtotal.configure(text=texto_sub)
        self._lbl_total.configure(text=texto_sub)

    def _atualizar_item_resumo(self, id_produto, item):
        w = self._resumo_widgets[id_produto]
        qtd = item.get("qtd", 1)
        preco_unit = item.get("preco", 0)
        texto_preco = f"R$ {preco_unit * qtd:.2f}".replace(".", ",")
        w["lbl_preco"].configure(text=texto_preco)
        w["lbl_qtd"].configure(text=str(qtd))

    def _criar_item_resumo(self, parent, item):
        id_produto = item["id_produto"]
        qtd = item.get("qtd", 1)
        preco_unit = item.get("preco", 0)

        frame_item = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.secundario,
            corner_radius=6, border_width=1,
            border_color=self.cores.card.borda_card,
            height=40
        )
        frame_item.pack(fill="x", pady=1)
        frame_item.pack_propagate(False)

        foto = item.get("foto", "")
        caminho = os.path.join(PASTA_PRODUTOS, foto) if foto else ""
        if caminho and os.path.exists(caminho):
            try:
                img = get_foto_ctk(caminho, (35, 30))
                ctk.CTkLabel(
                    frame_item, text="", image=img, width=24, height=24,
                    fg_color=self.cores.fundo.cinza_clarinho, corner_radius=4
                ).pack(side="left", padx=(4, 4), pady=1)
            except Exception:
                pass

        frame_info = ctk.CTkFrame(frame_item, fg_color="transparent")
        frame_info.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            frame_info, text=item["nome"],
            font=self.fontes.pequeno, text_color=self.cores.texto.principal
        ).pack(anchor="nw", pady=2, padx=(4, 0))

        frame_preco = ctk.CTkFrame(frame_info, fg_color="transparent")
        frame_preco.pack(anchor="sw", pady=0, padx=(4, 0))

        texto_preco = f"R$ {preco_unit * qtd:.2f}".replace(".", ",")
        lbl_preco = ctk.CTkLabel(
            frame_preco, text=texto_preco,
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        )
        lbl_preco.pack(side="left")

        frame_qtd = ctk.CTkFrame(frame_item, fg_color=self.cores.fundo.cinza_claro, corner_radius=10)
        frame_qtd.pack(side="right", padx=4, pady=1)

        ctk.CTkButton(
            frame_qtd, text="-", width=20, height=20,
            corner_radius=0, fg_color="transparent",
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno, hover_color=self.cores.botao.hover,
            command=lambda id=id_produto: self._alterar_qtd(id, -1)
        ).pack(side="left", padx=(1, 0), pady=1)

        lbl_qtd = ctk.CTkLabel(
            frame_qtd, text=str(qtd), width=16,
            font=self.fontes.pequeno, text_color=self.cores.texto.principal
        )
        lbl_qtd.pack(side="left", padx=2, pady=1)

        ctk.CTkButton(
            frame_qtd, text="+", width=20, height=20,
            corner_radius=0, fg_color="transparent",
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno, hover_color=self.cores.botao.hover,
            command=lambda id=id_produto: self._alterar_qtd(id, 1)
        ).pack(side="left", padx=(0, 1), pady=1)

        self._resumo_widgets[id_produto] = {
            "frame": frame_item,
            "lbl_preco": lbl_preco,
            "lbl_qtd": lbl_qtd,
        }

    def _alterar_qtd(self, id_produto, delta):
        for item in self._itens_pedido:
            if item["id_produto"] == id_produto:
                item["qtd"] += delta
                if item["qtd"] <= 0:
                    self._itens_pedido.remove(item)
                break
        self._atualizar_resumo()
        self._validar_avancar()

    def _validar_avancar(self):
        tem_itens = len(self._itens_pedido) > 0
        tem_cliente = self._cliente_selecionado is not None
        tem_tipo = self._tipo_entrega is not None
        tem_cobranca = self._momento_cobranca is not None

        if tem_itens and tem_cliente and tem_tipo and tem_cobranca:
            self._btn_avancar.configure(
                fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
                text_color=self.cores.texto.branco, state="normal"
            )
        else:
            self._btn_avancar.configure(
                fg_color=self.cores.fundo.cinza_claro,
                text_color=self.cores.texto.passivo, state="disabled"
            )

    def _avancar(self):
        tipo_pedido = self._tipo_entrega
        origem = "delivery"
        id_cliente = (
            self._cliente_selecionado.get("id_cliente") or
            (self._cliente_selecionado.get("id_cliente") or self._cliente_selecionado.get("id"))
        ) if self._cliente_selecionado else None
        obs = self.txt_obs.get("1.0", "end").strip()
        subtotal = sum(i["preco"] * i["qtd"] for i in self._itens_pedido)

        try:
            taxa_str = self._entry_taxa.get().strip().replace(",", ".")
            self._taxa_entrega = float(taxa_str) if taxa_str else 0.0
        except ValueError:
            self._taxa_entrega = 0.0

        id_entregador = (
            self._entregador_selecionado.get("id_funcionario")
            if self._entregador_selecionado else None
        )

        id_endereco = (
            self._endereco_selecionado.get("id_endereco")
            if self._endereco_selecionado else None
        )

        id_pedido = self.pedido_controller.criar_pedido(
            tipo_pedido=tipo_pedido,
            origem=origem,
            observacoes=obs if obs else None,
            valor_total=subtotal + self._taxa_entrega,
            taxa_entrega=self._taxa_entrega,
            id_cliente=id_cliente,
            momento_cobranca=self._momento_cobranca,
            id_entregador=id_entregador,
            id_endereco=id_endereco,
        )

        if id_pedido:
            self.id_pedido = id_pedido
            itens_db = [
                {
                    "id_produto": item.get("id_produto"),
                    "quantidade": item.get("qtd", 1),
                    "preco_unitario": item.get("preco", 0),
                    "observacoes": item.get("obs"),
                }
                for item in self._itens_pedido
            ]
            self.pedido_controller.adicionar_itens_pedido(id_pedido, itens_db)
            self.pedido_controller.atualizar_valor_total(id_pedido, subtotal + self._taxa_entrega)

        dados = {
            "id_pedido": id_pedido,
            "itens": list(self._itens_pedido),
            "tipo_entrega": tipo_pedido,
            "id_cliente": id_cliente,
            "cliente_nome": self._cliente_selecionado.get("nome", "") if self._cliente_selecionado else "",
            "obs": obs,
            "subtotal": subtotal,
            "taxa_entrega": self._taxa_entrega,
            "entregador_nome": self._entregador_selecionado.get("nome", "") if self._entregador_selecionado else "",
            "momento_cobranca": self._momento_cobranca,
        }

        if self._momento_cobranca == "na_entrega":
            self._pedido_criado_dados = dados
            self._mostrar_etapa(4)
        else:
            self._pedido_criado_dados = dados
            self._mostrar_etapa(3)


class TelaDeliveryStatus(Frames.FrameLayoutPadrao):
    """Placeholder — será implementado no Módulo 6."""
    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_home=None, menu_callbacks=None,
                 pedido_controller=None, on_click_titulo=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Delivery", icone=icones.delivery,
                         on_novo=None, on_home=on_home,
                         menu_callbacks=menu_callbacks,
                         on_click_titulo=on_click_titulo)
        self.cores, self.fontes, self.icones = cores, fontes, icones
        self.on_voltar = on_voltar
        self.pedido_controller = pedido_controller
        self._dados_pedido = {}

        ctk.CTkLabel(
            self.area_tela, text="Tela de status — em desenvolvimento",
            font=self.fontes.subtitulo, text_color=self.cores.texto.passivo
        ).pack(expand=True)

    def carregar_pedido(self, dados_pedido, pagamentos=None):
        self._dados_pedido = dados_pedido or {}
