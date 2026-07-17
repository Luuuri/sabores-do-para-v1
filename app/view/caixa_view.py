import customtkinter as ctk
from PIL import Image
import os
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import tkinter.messagebox as tk_msgbox
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import Frames, Barras, TabelaGenerica, Celulas, CardProduto, PASTA_PRODUTOS, Botoes, DialogoConfirmacao
from app.utils.cache import get_foto_ctk, get_qr_pix
from app.controller.produto_controller import ProdutoController
from app.controller.pedido_controller import PedidoController
from app.utils.pdf_generator import gerar_pdf_comprovante, gerar_comanda


class CaixaView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Caixa")
        self.minsize(1100, 700)
        self.after(0, lambda: self.state('zoomed'))
        self.lift()
        self.focus_force()

        self.cores = get_cores()
        self.fontes = Fontes()
        self.icones = Icones()
        self.controller = ProdutoController()
        self.pedido_controller = PedidoController()

        self.configure(fg_color=self.cores.fundo.principal)

        self._telas = {"lista": None, "cad": None, "pagamento": None, "status": None}
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

    def _abrir_clientes(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.clientes_view import ClientesView
        ClientesView(self.master)

    def _abrir_estoque(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("estoque", self, None):
            return
        self._cancelar_timers()
        self.destroy()
        from app.view.estoque_view import EstoqueView
        EstoqueView(self.master)

    def _abrir_funcionarios(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("funcionarios", self, None):
            return
        self._cancelar_timers()
        self.destroy()
        from app.view.funcionarios_view import FuncionariosView
        FuncionariosView(self.master)
        
    def _recarregar_tema(self):
        self._cancelar_timers()
        from app.utils.estilos import get_cores
        self.cores = get_cores()
        self.configure(fg_color=self.cores.fundo.principal)
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass
        self._telas = {"lista": None, "cad": None, "pagamento": None, "status": None}
        self._mostrar_lista()    

    def _abrir_produtos(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.produto_view_novo import ProdutosView
        ProdutosView(self.master)

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
        """Timer centralizado que roda a cada 1s e atualiza todos os timers ativos"""
        if self._id_timer_central:
            return
        self._tick_timer_central()

    def _garantir_timer_central(self):
        """Liga o timer central se nao estiver rodando"""
        if not self._id_timer_central:
            self._iniciar_timer_central()

    def _tick_timer_central(self):
        """Atualiza _timers_ativos com cálculo local (sem consulta ao banco)"""
        if not self.winfo_exists():
            self._id_timer_central = None
            return

        if not self._timers_ativos:
            self._id_timer_central = None
            return

        agora = datetime.now()
        vermelho = self.cores.texto.vermelho
        cor_normal = None

        # Calcular tempo decorrido localmente para todos os timers ativos
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

            # Atualizar célula na lista
            if self._telas["lista"] and self._telas["lista"].winfo_exists():
                try:
                    cor = vermelho if restante <= 0 else cor_normal
                    self._telas["lista"].tabela.atualizar_celula(id_pedido, "tempo", tempo_fmt, cor=cor)
                except Exception:
                    pass

            # Atualizar label na tela de status
            if self._telas["status"] and self._telas["status"].winfo_exists():
                try:
                    id_atual = self._telas["status"]._dados_pedido.get("id_pedido")
                    if id_atual == id_pedido:
                        status_tela = self._telas["status"]
                        if hasattr(status_tela, "_lbl_tempo_decorrido") and status_tela._lbl_tempo_decorrido:
                            cor = vermelho if restante <= 0 else status_tela.cores.texto.principal
                            status_tela._lbl_tempo_decorrido.configure(text=tempo_fmt, text_color=cor)
                        if hasattr(status_tela, "_lbl_aviso_atraso") and status_tela._lbl_aviso_atraso:
                            if restante <= 0:
                                if not status_tela._lbl_aviso_atraso.winfo_ismapped():
                                    status_tela._lbl_aviso_atraso.pack(anchor="w", padx=12, pady=(0, 12))
                            else:
                                if status_tela._lbl_aviso_atraso.winfo_ismapped():
                                    status_tela._lbl_aviso_atraso.pack_forget()
                except Exception:
                    pass

        self._id_timer_central = self.after(1000, self._tick_timer_central)

    def _abrir_relatorios(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("relatorios", self, None):
            return
        if self._id_tick_lista:
            self.after_cancel(self._id_tick_lista)
            self._id_tick_lista = None
        for timer_id in list(self._timers_ativos.keys()):
            self._timers_ativos.pop(timer_id, None)
        self.destroy()
        from app.view.relatorio_view import RelatoriosView
        RelatoriosView(self.master)

    def _abrir_delivery(self):
        self._cancelar_timers()
        self.destroy()
        from app.view.delivery_list_view import DeliveryListView
        DeliveryListView(self.master)

    def _mostrar_lista(self):
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()
        if self._telas["pagamento"]:
            self._telas["pagamento"].pack_forget()
        if self._telas["status"]:
            self._telas["status"].pack_forget()
        if not self._telas["lista"]:
            self._telas["lista"] = TelaCaixaLista(
                self, self.cores, self.fontes, self.icones,
                on_novo=self._abrir_cadastro,
                on_editar=self._abrir_cadastro,
                on_excluir=self._excluir_pedido,
                on_home=self._voltar_painel,
                menu_callbacks={
                    "caixa": self._mostrar_lista,
                    "delivery": self._abrir_delivery,
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
        if self._telas["pagamento"]:
            self._telas["pagamento"].pack_forget()
        if self._telas["status"]:
            self._telas["status"].pack_forget()
        if not self._telas["cad"]:
            self._telas["cad"] = TelaCaixaCad(
                self, self.cores, self.fontes, self.icones,
                on_voltar=self._mostrar_lista,
                on_salvar=self._salvar_pedido,
                on_excluir=self._excluir_pedido,
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._mostrar_lista,
                    "delivery": self._abrir_delivery,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                },
                controller=self.controller,
                pedido_controller=self.pedido_controller,
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
            self._telas["pagamento"] = TelaCaixaPagamento(
                self, self.cores, self.fontes, self.icones,
                on_voltar=lambda: self._abrir_cadastro(limpar=False),
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._mostrar_lista,
                    "delivery": self._abrir_delivery,
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

    def _abrir_status(self, dados_pedido, pagamentos=None):
        if self._telas["lista"]:
            self._telas["lista"].pack_forget()
        if self._id_tick_lista:
            self.after_cancel(self._id_tick_lista)
            self._id_tick_lista = None
        if self._telas["pagamento"]:
            self._telas["pagamento"].pack_forget()
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()
        if not self._telas["status"]:
            self._telas["status"] = TelaCaixaStatus(
                self, self.cores, self.fontes, self.icones,
                on_voltar=lambda: self._abrir_pagamento(dados_pedido),
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._mostrar_lista,
                    "delivery": self._abrir_delivery,
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
        self._telas["status"].carregar_pedido(dados_pedido, pagamentos)
        self._telas["status"].pack(fill="both", expand=True)
        self.update()

    def _salvar_pedido(self, id_pedido, dados):
        if id_pedido:
            pass
        else:
            pass
        self._mostrar_lista()

    def _excluir_pedido(self, id_pedido):
        DialogoConfirmacao(
            self, self.cores, self.fontes,
            titulo="Excluir Pedido",
            mensagem="Tem certeza que deseja excluir este pedido?",
            on_confirmar=lambda: (
                self.pedido_controller.excluir_pedido(id_pedido),
                self._mostrar_lista()
            )
        )


class TelaCaixaLista(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_novo=None, on_editar=None, on_excluir=None, on_home=None,
                 menu_callbacks=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Caixa", icone=icones.caixa,
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
            total = self.pedido_controller.contar_pedidos()
            self._total_pedidos = total
            self._total_paginas = max(1, (total + 11) // 12)
            self._atualizar_botoes_pagina()
            pedidos = self.pedido_controller.listar_pedidos(pagina=self._pagina_atual, itens_por_pagina=12)
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
                origem = p.get("origem", "")
                if origem == "mesa":
                    origem = f"Mesa {p.get('num_mesa', '')}"
                elif origem == "balcao":
                    origem = "Balcão"
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
                    "origem": origem,
                    "origem_filtro": p.get("origem", "").lower(),
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
            self.cores.texto.verde_jambu, "R$ 0,00"
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

        # ── Botão atualizar manual
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
            placeholder_busca="Pedidos, Origem, Data",
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
                    "titulo": "Origem",
                    "campo": "origem",
                    "peso": 1,
                    "min": 100,
                    "limite": 15,
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
                    "campo": "origem_filtro",
                    "titulo": "Origem",
                    "opcoes": [
                        {"label": "Balcão", "valor": "balcao"},
                        {"label": "Mesa", "valor": "mesa"},
                    ]
                },
            ]
        )
        self.tabela.pack(expand=True, fill="both", padx=5, pady=(10, 0))

        # ── Paginação ──
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
            self.cards["pedidos_ativos"].valor_label.configure(text=str(resumo['pedidos_ativos']))
            self.cards["pendentes"].valor_label.configure(text=str(resumo['pendentes']))
        atrasados = sum(1 for d in dados if d.get("atrasado"))
        self.cards["atrasados"].valor_label.configure(text=str(atrasados))

    def _acao_excluir(self, id_pedido):
        if self.on_excluir:
            self.on_excluir(id_pedido)

    def _status_em_andamento(self, status):
        return status in ["Em Preparo", "Pronto", "Entregue"]

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


class TelaCaixaCad(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_salvar=None, on_excluir=None, on_home=None,
                 menu_callbacks=None, controller=None, pedido_controller=None,
                 on_click_titulo=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Caixa", icone=icones.caixa,
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
        self.controller = controller
        self.pedido_controller = pedido_controller or PedidoController()

        self.id_pedido = None
        self._modo = "novo"
        self.origem_selecionada = None
        self.etapa_atual = 1

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
        self._validar_pagamento()

    def definir_modo(self, modo: str):
        self._modo = modo
        if modo == "novo":
            self.atualizar_info("Novo Pedido")
            self._itens_pedido = []
            self._produto_selecionado_idx = None
            self.origem_selecionada = None
            if hasattr(self, "_seg_origem"):
                self._seg_origem.set(None)
            self.frame_numero.pack_forget()
            self._atualizar_resumo()
            self._validar_pagamento()
        elif self.id_pedido:
            self.atualizar_info(f"Pedido #{self.id_pedido}")

    def limpar_formulario(self):
        self.id_pedido = None
        self._modo = "novo"
        self.atualizar_info("Novo Pedido")
        self._itens_pedido = []
        self._resumo_widgets.clear()

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

    # ═════════════════════════════════════════════════════════════
    # CONTEÚDO PRINCIPAL
    # ═════════════════════════════════════════════════════════════
    def _criar_conteudo(self):
        principal = ctk.CTkFrame(self.area_tela, fg_color="transparent")
        principal.pack(fill="both", expand=True, padx=50, pady=20)

        # ── Stepper ──────────────────────────────────────────────
        frame_stepper = ctk.CTkFrame(
            principal,
            fg_color=self.cores.fundo.branco,
            corner_radius=12,
            height=46
        )
        frame_stepper.pack(fill="x", pady=(0, 20))
        frame_stepper.pack_propagate(False)

        self.stepper = Frames.StepperPassos(
            frame_stepper, self.cores, self.fontes,
            etapas=[
                {"num": "1", "label": "Itens"},
                {"num": "2", "label": "Pagamento"},
                {"num": "3", "label": "Status"},
            ],
            etapa_atual=self.etapa_atual,
            padx_circle=(100, 6), padx_label=(0, 200)
        )
        self.stepper.pack(expand=True)

        # ── Corpo ────────────────────────────────────────────────
        corpo = ctk.CTkFrame(principal, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.grid_columnconfigure(0, weight=3)
        corpo.grid_columnconfigure(1, weight=1)
        corpo.grid_rowconfigure(0, weight=1)

        # Coluna esquerda: Produtos
        frame_produtos = ctk.CTkFrame(
            corpo,
            fg_color=self.cores.fundo.branco,
            border_width=2,
            border_color=self.cores.card.borda_card,
            corner_radius=12
        )
        frame_produtos.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        self._criar_area_produtos(frame_produtos)

        # Coluna direita
        frame_direita = ctk.CTkFrame(corpo, fg_color="transparent")
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        frame_direita.grid_rowconfigure(1, weight=1)
        frame_direita.grid_columnconfigure(0, weight=1)

        # Origem
        frame_origem = ctk.CTkFrame(
            frame_direita,
            fg_color=self.cores.fundo.branco,
            border_width=2,
            border_color=self.cores.card.borda_card,
            corner_radius=12,
            height=110
        )
        frame_origem.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        frame_origem.grid_propagate(False)
        self._criar_area_origem(frame_origem)

        # Resumo
        frame_resumo = ctk.CTkFrame(
            frame_direita,
            fg_color=self.cores.fundo.branco,
            border_width=2,
            border_color=self.cores.card.borda_card,
            corner_radius=12
        )
        frame_resumo.grid(row=1, column=0, sticky="nsew")
        self._criar_area_resumo(frame_resumo)

    # ═════════════════════════════════════════════════════════════
    # ÁREA DE PRODUTOS
    # ═════════════════════════════════════════════════════════════
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
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(side="left", padx=10)

        frame_topo = ctk.CTkFrame(parent, fg_color="transparent")
        frame_topo.pack(fill="x", padx=12, pady=(0, 6))

        self._entry_busca = Barras.HeaderBusca(
            frame_topo, self.cores, self.fontes, self.icones,
            placeholder="produtos",
            search_callback=self._ao_digitar_busca,
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
            fg_color=self.cores.botao.novo,
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.branco,
            font=self.fontes.pequeno, width=0,
            command=lambda: self._filtrar_categoria("Todos")
        )
        btn_todos.pack(side="left", padx=(0, 3))
        self._botoes_categorias["Todos"] = btn_todos

        for cat in categorias:
            btn = ctk.CTkButton(
                self._frame_filtros, text=cat, height=26, corner_radius=13,
                fg_color=self.cores.fundo.secundario,
                hover_color=self.cores.botao.hover,
                text_color=self.cores.texto.principal,
                font=self.fontes.pequeno, width=0,
                command=lambda c=cat: self._filtrar_categoria(c)
            )
            btn.pack(side="left", padx=(0, 3))
            self._botoes_categorias[cat] = btn

    def _atualizar_selecao_categorias(self):
        for nome, btn in self._botoes_categorias.items():
            selecionada = (self._categoria_filtro == nome)
            btn.configure(
                fg_color=self.cores.botao.novo if selecionada else self.cores.fundo.secundario,
                text_color=self.cores.texto.branco if selecionada else self.cores.texto.principal,
            )

    def _verificar_categorias(self, produtos):
        categorias = sorted(set(p["categoria"] for p in produtos if p.get("ativo")))
        if tuple(categorias) != self._categorias_hash:
            self._inicializar_categorias(produtos)

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
        self._atualizar_selecao_categorias()
        self._aplicar_filtro_cards()

    def _ao_digitar_busca(self, termo):
        if self._id_timer_busca:
            self.after_cancel(self._id_timer_busca)
        self._id_timer_busca = self.after(300, lambda: self._executar_busca(termo))

    def _executar_busca(self, termo):
        self._id_timer_busca = None
        self._texto_busca = termo.strip().lower()
        self._aplicar_filtro_cards()

    def _renderizar_produtos(self, produtos=None):
        if produtos is not None:
            self._verificar_categorias(produtos)
            self._inicializar_cards(produtos)
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
                self._validar_pagamento()
                return
        self._itens_pedido.append({
            "id_produto": produto["id_produto"],
            "nome": produto["nome"],
            "preco": float(produto["preco"]),
            "foto": produto.get("foto", ""),
            "qtd": 1
        })
        self._atualizar_resumo()
        self._validar_pagamento()

    # ═════════════════════════════════════════════════════════════
    # ÁREA DE ORIGEM
    # ═════════════════════════════════════════════════════════════
    def _criar_area_origem(self, parent):
        ctk.CTkLabel(
            parent, text="Origem do Pedido",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(10, 8))

        self._seg_origem = ctk.CTkSegmentedButton(
            parent, values=["Mesa", "Balcão"],
            height=30, corner_radius=8,
            selected_color=self.cores.botao.novo,
            selected_hover_color=self.cores.botao.novo_hover,
            unselected_color=self.cores.fundo.cinza_claro,
            unselected_hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            command=self._selecionar_origem
        )
        self._seg_origem.pack(fill="x", padx=15, pady=(0, 8))

        self.frame_numero = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(
            self.frame_numero, text="Nº Mesa:",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(side="left", padx=(15, 8))
        self.entry_mesa = ctk.CTkEntry(
            self.frame_numero, placeholder_text="0", width=60, height=28,
            corner_radius=6, border_width=1,
            border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal,
            font=self.fontes.texto_entry, justify="center"
        )
        self.entry_mesa.pack(side="left")
        self.entry_mesa.bind("<KeyRelease>", lambda e: self._validar_pagamento())

    def _selecionar_origem(self, origem):
        self.origem_selecionada = origem
        if origem == "Mesa":
            self.frame_numero.pack(fill="x", pady=(0, 8), padx=5)
        else:
            self.frame_numero.pack_forget()
        self._validar_pagamento()

    # ═════════════════════════════════════════════════════════════
    # ÁREA DE RESUMO
    # ═════════════════════════════════════════════════════════════
    def _criar_area_resumo(self, parent):
        # Bottom (valores + botão) — sempre embaixo
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

        f2 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f2.pack(fill="x", padx=10, pady=1)
        ctk.CTkLabel(f2, text="Taxa serviço (0%):", font=self.fontes.pequeno, text_color=self.cores.texto.passivo).pack(side="left")
        self._lbl_taxa = ctk.CTkLabel(f2, text="R$ 0,00", font=self.fontes.pequeno, text_color=self.cores.texto.principal)
        self._lbl_taxa.pack(side="right")

        ctk.CTkFrame(frame_valores, height=1, fg_color=self.cores.card.borda_card).pack(fill="x", padx=10, pady=(4, 4))

        f3 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f3.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(f3, text="Total:", font=self.fontes.texto_info, text_color=self.cores.texto.principal).pack(side="left")
        self._lbl_total = ctk.CTkLabel(f3, text="R$ 0,00", font=self.fontes.texto_info, text_color=self.cores.texto.verde_escuro)
        self._lbl_total.pack(side="right")

        self._btn_ir_pagamentos = ctk.CTkButton(
            frame_bottom, text="Ir para Pagamentos  →",
            height=34, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.passivo,
            font=self.fontes.texto_info,
            state="disabled",
            command=self._avancar_pagamento
        )
        self._btn_ir_pagamentos.pack(fill="x")

        # Observações — fixo acima do bottom
        frame_obs = ctk.CTkFrame(parent, fg_color="transparent")
        frame_obs.pack(side="bottom", fill="x", padx=8, pady=(0, 4))

        ctk.CTkLabel(
            frame_obs, text="Observações (opcional):",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w", padx=4, pady=(0, 2))

        self.txt_obs = ctk.CTkTextbox(
            frame_obs, corner_radius=6, border_width=1,
            border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal,
            font=self.fontes.texto_entry, height=80
        )
        self.txt_obs.pack(fill="x", padx=4)

        # Lista de itens — scrollável, ocupa espaço restante
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
        self._lbl_taxa.configure(text="R$ 0,00")
        self._lbl_total.configure(text=texto_sub)

    def _atualizar_item_resumo(self, id_produto, item):
        w = self._resumo_widgets[id_produto]
        qtd = item.get("qtd", 1)
        preco_unit = item.get("preco", 0)
        texto_preco = f"R$ {preco_unit * qtd:.2f}".replace(".", ",")
        w["lbl_preco"].configure(text=texto_preco)
        w["lbl_qtd"].configure(text=str(qtd))
        if w["lbl_unit"]:
            if qtd > 1:
                texto_unit = f"{qtd}x R$ {preco_unit:.2f}".replace(".", ",")
                w["lbl_unit"].configure(text=texto_unit)
                if not w["lbl_unit"].winfo_ismapped():
                    w["lbl_unit"].pack(side="left", padx=(4, 0))
            else:
                if w["lbl_unit"].winfo_ismapped():
                    w["lbl_unit"].pack_forget()

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
        caminho_completo = os.path.join(PASTA_PRODUTOS, foto) if foto else ""
        if caminho_completo and os.path.exists(caminho_completo):
            try:
                img = get_foto_ctk(caminho_completo, (35, 30))
                ctk.CTkLabel(
                    frame_item, text="", image=img, width=24, height=24,
                    fg_color=self.cores.fundo.cinza_clarinho, corner_radius=4
                ).pack(side="left", padx=(4, 4), pady=1)
            except Exception:
                ctk.CTkLabel(
                    frame_item, text="📷", font=("Arial", 12),
                    width=24, height=24,
                    fg_color=self.cores.fundo.cinza_clarinho, corner_radius=4
                ).pack(side="left", padx=(4, 4), pady=3)
        else:
            ctk.CTkLabel(
                frame_item, text="📷", font=("Arial", 12),
                width=24, height=24,
                fg_color=self.cores.fundo.cinza_clarinho, corner_radius=4
            ).pack(side="left", padx=(4, 4), pady=3)

        frame_info = ctk.CTkFrame(frame_item, fg_color="transparent")
        frame_info.pack(side="left", fill="both", expand=True)

        frame_textos = ctk.CTkFrame(frame_info, fg_color="transparent")
        frame_textos.pack(side="left", fill="both", expand=True, padx=(0, 4), pady=2)

        ctk.CTkLabel(
            frame_textos, text=item["nome"],
            font=self.fontes.pequeno, text_color=self.cores.texto.principal
        ).pack(anchor="nw", pady=0)

        frame_preco_linha = ctk.CTkFrame(frame_textos, fg_color="transparent")
        frame_preco_linha.pack(anchor="sw", pady=0)

        texto_preco = f"R$ {preco_unit * qtd:.2f}".replace(".", ",")
        lbl_preco = ctk.CTkLabel(
            frame_preco_linha, text=texto_preco,
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        )
        lbl_preco.pack(side="left", padx=0)

        lbl_unit = None
        if qtd > 1:
            texto_unit = f"{qtd}x R$ {preco_unit:.2f}".replace(".", ",")
            lbl_unit = ctk.CTkLabel(
                frame_preco_linha, text=texto_unit,
                font=self.fontes.pequeno, text_color=self.cores.texto.passivo
            )
            lbl_unit.pack(side="left", padx=(4, 0))

        frame_qtd = ctk.CTkFrame(frame_item, fg_color=self.cores.fundo.cinza_claro, corner_radius=10)
        frame_qtd.pack(side="right", padx=4, pady=1)

        ctk.CTkButton(
            frame_qtd, text="−", width=20, height=20,
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
            "lbl_unit": lbl_unit,
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
        self._validar_pagamento()

    def _validar_pagamento(self):
        tem_itens = len(self._itens_pedido) > 0
        tem_origem = self.origem_selecionada in ("Mesa", "Balcão")
        mesa_ok = self.origem_selecionada != "Mesa" or bool(self.entry_mesa.get().strip())

        if tem_itens and tem_origem and mesa_ok:
            self._btn_ir_pagamentos.configure(
                fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
                text_color=self.cores.texto.branco, state="normal"
            )
        else:
            self._btn_ir_pagamentos.configure(
                fg_color=self.cores.fundo.cinza_claro,
                text_color=self.cores.texto.passivo, state="disabled"
            )

    def _avancar_pagamento(self):
        origem = "mesa" if self.origem_selecionada == "Mesa" else "balcao"
        num_mesa = self.entry_mesa.get() if self.origem_selecionada == "Mesa" else None
        obs = self.txt_obs.get("1.0", "end").strip()
        subtotal = sum(i["preco"] * i["qtd"] for i in self._itens_pedido)

        id_pedido = self.pedido_controller.criar_pedido(
            tipo_pedido="presencial",
            origem=origem,
            num_mesa=num_mesa,
            observacoes=obs if obs else None,
            valor_total=subtotal,
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
            self.pedido_controller.atualizar_valor_total(id_pedido, subtotal)

        dados = {
            "id_pedido": id_pedido,
            "itens": list(self._itens_pedido),
            "origem": origem,
            "num_mesa": num_mesa,
            "obs": obs,
            "subtotal": subtotal,
        }
        self.master._abrir_pagamento(dados)

    def _excluir(self):
        if self.id_pedido and self.on_excluir:
            self.on_excluir(self.id_pedido)

    def _salvar(self):
        if self.on_salvar:
            self.on_salvar(self.id_pedido, {})


class TelaCaixaPagamento(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_home=None,
                 menu_callbacks=None, on_click_titulo=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Caixa", icone=icones.caixa,
                         on_novo=None, on_home=on_home,
                         menu_callbacks=menu_callbacks,
                         texto_info="Pagamento",
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

        self._dados_pedido = {}
        self._pagamentos = []
        self._metodo_selecionado = None
        self._ultimo_metodo = None
        self._status_pagamento = "aguardando"
        self._pagamento_widgets = {}
        self._pagamentos_header_criado = False

        self._criar_conteudo()

    def carregar_pedido(self, dados):
        self._dados_pedido = dados
        self._pagamentos = []
        self._metodo_selecionado = None
        self._ultimo_metodo = None
        self._status_pagamento = "aguardando"

        origem = dados.get("origem", "").lower()
        num_mesa = dados.get("num_mesa")
        id_pedido = dados.get("id_pedido", 1)
        if origem == "mesa" and num_mesa:
            self.atualizar_info(f"Mesa {num_mesa} · Pedido #{id_pedido:03d}")
        elif origem == "balcao":
            self.atualizar_info(f"Balcão · Pedido #{id_pedido:03d}")
        else:
            self.atualizar_info(f"Pedido #{id_pedido:03d}")

        self._reabilitar_botoes_metodo()
        self._atualizar_resumo()
        self._atualizar_pagamentos()
        self._atualizar_status()
        self._atualizar_rodape()
        self._atualizar_botao_adicionar()
        self._mostrar_selecao_metodo()

    # ═════════════════════════════════════════════════════════════
    # CONTEÚDO PRINCIPAL
    # ═════════════════════════════════════════════════════════════
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
                {"num": "1", "label": "Itens"},
                {"num": "2", "label": "Pagamento"},
                {"num": "3", "label": "Status"},
            ],
            etapa_atual=2,
            padx_circle=(100, 6), padx_label=(0, 200)
        )
        self.stepper.pack(expand=True)

        corpo = ctk.CTkFrame(principal, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.grid_columnconfigure(0, weight=2)
        corpo.grid_columnconfigure(1, weight=5)
        corpo.grid_rowconfigure(0, weight=1)

        frame_esquerda = ctk.CTkFrame(
            corpo, fg_color=self.cores.fundo.branco,
            corner_radius=12
        )
        frame_esquerda.grid(row=0, column=0, sticky="new", padx=(0, 8))
        self._criar_resumo_pedido(frame_esquerda)

        frame_direita = ctk.CTkFrame(
            corpo, fg_color=self.cores.fundo.branco,
            corner_radius=12
        )
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._criar_area_pagamento(frame_direita)

    # ═════════════════════════════════════════════════════════════
    # LADO ESQUERDO — RESUMO DO PEDIDO
    # ═════════════════════════════════════════════════════════════
    def _criar_resumo_pedido(self, parent):
        cabecalho = ctk.CTkFrame(parent, fg_color="transparent")
        cabecalho.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkButton(
            cabecalho, text="", image=self.icones.voltar_pequeno,
            width=30, height=30,
            fg_color="transparent", hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.secundario, font=ctk.CTkFont(size=12),
            command=self.on_voltar
        ).pack(side="left")

        ctk.CTkLabel(
            cabecalho, text="Pagamento",
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(side="left", padx=10)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 8))

        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left")

        self._lbl_pedido_num = ctk.CTkLabel(
            left_header, text="Pedido #000",
            font=self.fontes.subtitulo, text_color=self.cores.botao.id_badge_txt,
            fg_color=self.cores.botao.id_badge, corner_radius=50, padx=10, pady=4
        )
        self._lbl_pedido_num.pack(anchor="w")

        self._badge_origem = ctk.CTkLabel(
            left_header, text="Mesa 00",
            font=self.fontes.pequeno, text_color=self.cores.texto.branco,
            fg_color=self.cores.botao.novo, corner_radius=6,
            padx=8, pady=2
        )

        right_header = ctk.CTkFrame(header, fg_color="transparent")
        right_header.pack(side="right")

        ctk.CTkLabel(
            right_header, text="Atendente",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="e")

        self._lbl_atendente = ctk.CTkLabel(
            right_header, text="—",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        )
        self._lbl_atendente.pack(anchor="e")

        ctk.CTkFrame(parent, height=1, fg_color=self.cores.card.borda_card).pack(fill="x", padx=12, pady=4)

        self._frame_conteudo_itens = ctk.CTkFrame(parent, fg_color="transparent")
        self._frame_conteudo_itens.pack(fill="both", expand=True)

        self._frame_lista_itens = ctk.CTkScrollableFrame(
            self._frame_conteudo_itens, fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.fundo.cinza_claro,
            scrollbar_button_hover_color=self.cores.fundo.cinza_claro
        )
        self._frame_lista_itens.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        self._frame_obs = ctk.CTkFrame(
            self._frame_conteudo_itens, fg_color=self.cores.fundo.secundario, corner_radius=8
        )

        self._lbl_obs = ctk.CTkLabel(
            self._frame_obs, text="",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo,
            anchor="w", justify="left", wraplength=280
        )
        self._lbl_obs.pack(anchor="w", padx=10, pady=8)

        frame_valores = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.secundario, corner_radius=8
        )
        frame_valores.pack(fill="x", padx=12, pady=(0, 12))

        f1 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f1.pack(fill="x", padx=10, pady=(6, 1))
        ctk.CTkLabel(f1, text="Subtotal:", font=self.fontes.pequeno, text_color=self.cores.texto.passivo).pack(side="left")
        self._lbl_subtotal = ctk.CTkLabel(f1, text="R$ 0,00", font=self.fontes.pequeno, text_color=self.cores.texto.principal)
        self._lbl_subtotal.pack(side="right")

        f2 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f2.pack(fill="x", padx=10, pady=1)
        ctk.CTkLabel(f2, text="Taxa serviço (0%):", font=self.fontes.pequeno, text_color=self.cores.texto.passivo).pack(side="left")
        self._lbl_taxa = ctk.CTkLabel(f2, text="R$ 0,00", font=self.fontes.pequeno, text_color=self.cores.texto.principal)
        self._lbl_taxa.pack(side="right")

        ctk.CTkFrame(frame_valores, height=1, fg_color=self.cores.card.borda_card).pack(fill="x", padx=10, pady=(4, 4))

        f3 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f3.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(f3, text="Total:", font=self.fontes.texto_info, text_color=self.cores.texto.principal).pack(side="left")
        self._lbl_total = ctk.CTkLabel(f3, text="R$ 0,00", font=self.fontes.texto_info, text_color=self.cores.texto.verde_escuro)
        self._lbl_total.pack(side="right")

    def _atualizar_resumo(self):
        dados = self._dados_pedido
        id_pedido = dados.get("id_pedido", 1)
        self._lbl_pedido_num.configure(text=f"Pedido #{id_pedido:03d}")

        from app.utils.usuario_atual import usuario_atual

        origem = (dados.get("origem") or "").lower()
        num_mesa = dados.get("num_mesa")
        if origem == "mesa" and num_mesa:
            self._badge_origem.configure(text=f"Mesa {num_mesa}", fg_color=self.cores.fundo.verde, text_color=self.cores.texto.verde_escuro)
            self._badge_origem.pack(anchor="w", pady=(2, 0))
        elif origem == "balcao":
            self._badge_origem.configure(text="Balcão", fg_color=self.cores.fundo.laranja, text_color=self.cores.texto.branco)
            self._badge_origem.pack(anchor="w", pady=(2, 0))
        else:
            self._badge_origem.pack_forget()

        self._lbl_atendente.configure(text=usuario_atual.get("nome", "Operador"))

        for w in self._frame_lista_itens.winfo_children():
            w.destroy()

        itens = dados.get("itens", [])
        for item in itens:
            qtd = item.get("quantidade", item.get("qtd", 1))
            nome = item.get("nome", "")
            preco_unit = item.get("preco", item.get("preco_unitario", 0))
            texto = f"{qtd}x {nome}"
            preco = f"R$ {preco_unit * qtd:.2f}".replace(".", ",")

            frame_item = ctk.CTkFrame(self._frame_lista_itens, fg_color="transparent")
            frame_item.pack(fill="x", pady=1)

            ctk.CTkLabel(
                frame_item, text=texto,
                font=self.fontes.pequeno, text_color=self.cores.texto.principal
            ).pack(side="left")

            ctk.CTkLabel(
                frame_item, text=preco,
                font=self.fontes.pequeno, text_color=self.cores.texto.passivo
            ).pack(side="right")

        obs = dados.get("obs", "")
        if obs:
            self._lbl_obs.configure(text=f"Obs: {obs}")
            if not self._frame_obs.winfo_ismapped():
                self._frame_obs.pack(fill="x", padx=12, pady=(0, 4))
        else:
            self._frame_obs.pack_forget()

        subtotal = dados.get("subtotal", 0)
        texto_sub = f"R$ {subtotal:.2f}".replace(".", ",")
        self._lbl_subtotal.configure(text=texto_sub)
        self._lbl_taxa.configure(text="R$ 0,00")
        self._lbl_total.configure(text=texto_sub)

    # ═════════════════════════════════════════════════════════════
    # LADO DIREITO — PAGAMENTO
    # ═════════════════════════════════════════════════════════════
    def _criar_area_pagamento(self, parent):
        self._frame_rodape = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.branco,
            corner_radius=8
        )
        self._frame_rodape.pack(side="bottom", fill="x", padx=12, pady=(0, 12))
        self._criar_rodape()

        self._frame_pagamentos = ctk.CTkFrame(
            parent, fg_color=self.cores.fundo.secundario, corner_radius=8
        )
        self._frame_pagamentos.pack(side="bottom", fill="x", padx=8, pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.fundo.cinza_claro,
            scrollbar_button_hover_color=self.cores.fundo.cinza_claro
        )
        scroll.pack(fill="both", expand=True, padx=4, pady=4)
        scroll.grid_columnconfigure(0, weight=1)

        self._frame_status = ctk.CTkFrame(
            scroll, fg_color=self.cores.fundo.amarelo, corner_radius=8
        )
        self._frame_status.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 8))

        self._lbl_status_icone = ctk.CTkLabel(
            self._frame_status, text="🟡",
            font=ctk.CTkFont(size=16)
        )
        self._lbl_status_icone.pack(side="left", padx=(8, 4), pady=8)

        frame_status_texto = ctk.CTkFrame(self._frame_status, fg_color="transparent")
        frame_status_texto.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=8)

        self._lbl_status_titulo = ctk.CTkLabel(
            frame_status_texto, text="Aguardando Pagamento",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        )
        self._lbl_status_titulo.pack(anchor="w")

        self._lbl_status_desc = ctk.CTkLabel(
            frame_status_texto,
            text="Selecione uma forma de pagamento para lançar um valor parcial ou total.",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        )
        self._lbl_status_desc.pack(anchor="w")

        frame_metodos = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_metodos.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self._frame_adicionar = ctk.CTkFrame(scroll, fg_color="transparent")
        self._frame_adicionar.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._frame_adicionar.grid_forget()

        ctk.CTkButton(
            self._frame_adicionar, text="ADICIONAR OUTRO PAGAMENTO",
            height=28, corner_radius=6,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._adicionar_outro_pagamento
        ).pack(fill="x")

        frame_botoes = ctk.CTkFrame(frame_metodos, fg_color="transparent")
        frame_botoes.pack(fill="x")
        frame_botoes.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_dinheiro = ctk.CTkButton(
            frame_botoes, text="💵 Dinheiro", height=44, corner_radius=10,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            border_width=1, border_color=self.cores.card.borda_card,
            command=lambda: self._selecionar_metodo("dinheiro")
        )
        self.btn_dinheiro.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_cartao = ctk.CTkButton(
            frame_botoes, text="💳 Cartão", height=44, corner_radius=10,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            border_width=1, border_color=self.cores.card.borda_card,
            command=lambda: self._selecionar_metodo("cartao")
        )
        self.btn_cartao.grid(row=0, column=1, sticky="ew", padx=2)

        self.btn_pix = ctk.CTkButton(
            frame_botoes, text="📱 PIX", height=44, corner_radius=10,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            border_width=1, border_color=self.cores.card.borda_card,
            command=lambda: self._selecionar_metodo("pix")
        )
        self.btn_pix.grid(row=0, column=2, sticky="ew", padx=(4, 0))

        self._frame_metodo_conteudo = ctk.CTkFrame(
            scroll, fg_color=self.cores.fundo.secundario, corner_radius=8
        )
        self._frame_metodo_conteudo.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))

        self._mostrar_selecao_metodo()

    # ═════════════════════════════════════════════════════════════
    # STATUS
    # ═════════════════════════════════════════════════════════════
    def _atualizar_status(self):
        total = self._dados_pedido.get("subtotal", 0)
        pago = sum(p["valor"] for p in self._pagamentos)
        restante = total - pago

        if not self._pagamentos:
            cor = self.cores.fundo.amarelo
            icone = "🟡"
            titulo = "Aguardando Pagamento"
            desc = "Selecione uma forma de pagamento para lançar um valor parcial ou total."
        elif restante > 0:
            cor = self.cores.fundo.amarelo
            icone = "🟡"
            titulo = "Pagamento Parcial"
            desc = f"Restante: R$ {restante:.2f}".replace(".", ",")
        elif restante <= 0:
            cor = self.cores.fundo.verde
            icone = "🟢"
            titulo = "Pagamento Aprovado"
            desc = "Valor total pago. Clique em Finalizar Pedido."

        self._frame_status.configure(fg_color=cor)
        self._lbl_status_icone.configure(text=icone)
        self._lbl_status_titulo.configure(text=titulo)
        self._lbl_status_desc.configure(text=desc)

    def _restante(self):
        total = self._dados_pedido.get("subtotal", 0)
        pago = sum(p["valor"] for p in self._pagamentos)
        return total - pago

    def _atualizar_botao_adicionar(self):
        if self._pagamentos and self._restante() > 0:
            self._frame_adicionar.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        else:
            self._frame_adicionar.grid_forget()

    # ═════════════════════════════════════════════════════════════
    # MÉTODO DE PAGAMENTO
    # ═════════════════════════════════════════════════════════════
    def _selecionar_metodo(self, metodo):
        self._metodo_selecionado = metodo

        for btn in [self.btn_dinheiro, self.btn_cartao, self.btn_pix]:
            btn.configure(fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal, border_width=1)

        if metodo == "dinheiro":
            self.btn_dinheiro.configure(fg_color=self.cores.botao.novo, text_color=self.cores.texto.branco, border_width=0, state="normal")
            self._mostrar_dinheiro()
        elif metodo == "cartao":
            self.btn_cartao.configure(fg_color=self.cores.botao.novo, text_color=self.cores.texto.branco, border_width=0, state="normal")
            self._mostrar_cartao()
        elif metodo == "pix":
            self.btn_pix.configure(fg_color=self.cores.botao.novo, text_color=self.cores.texto.branco, border_width=0, state="normal")
            self._mostrar_pix()

    def _reabilitar_botoes_metodo(self):
        for btn in [self.btn_dinheiro, self.btn_cartao, self.btn_pix]:
            btn.configure(fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal, border_width=1, state="normal")

    def _desabilitar_botoes_metodo(self):
        for btn in [self.btn_dinheiro, self.btn_cartao, self.btn_pix]:
            btn.configure(state="disabled")

    def _adicionar_outro_pagamento(self):
        self._metodo_selecionado = None
        mapping = [("dinheiro", self.btn_dinheiro), ("cartao", self.btn_cartao), ("pix", self.btn_pix)]
        for metodo_key, btn in mapping:
            if metodo_key == self._ultimo_metodo:
                btn.configure(state="disabled")
            else:
                btn.configure(fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal, border_width=1, state="normal")
        self._mostrar_selecao_metodo()

    def _mostrar_selecao_metodo(self):
        for w in self._frame_metodo_conteudo.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._frame_metodo_conteudo, text="Selecione um método de pagamento",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(pady=20)

    def _mostrar_dinheiro(self):
        for w in self._frame_metodo_conteudo.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self._frame_metodo_conteudo, fg_color="transparent")
        frame.pack(fill="x", padx=12, pady=12)

        frame_valor_troco = ctk.CTkFrame(frame, fg_color="transparent")
        frame_valor_troco.pack(fill="x")
        frame_valor_troco.grid_columnconfigure(0, weight=3)
        frame_valor_troco.grid_columnconfigure(1, weight=1)

        col_valor = ctk.CTkFrame(frame_valor_troco, fg_color="transparent")
        col_valor.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkLabel(
            col_valor, text="Valor Recebido",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w")

        restante = self._restante()
        self._entry_valor_recebido = ctk.CTkEntry(
            col_valor, placeholder_text="R$ 0,00",
            height=32, corner_radius=8,
            border_width=1, border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal
        )
        self._entry_valor_recebido.pack(fill="x", pady=(2, 0))
        if restante > 0:
            self._entry_valor_recebido.insert(0, f"{restante:.2f}".replace(".", ","))

        self._col_troco = ctk.CTkFrame(frame_valor_troco, fg_color="transparent")
        self._col_troco.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            self._col_troco, text="Troco",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w")

        self._lbl_troco = ctk.CTkLabel(
            self._col_troco, text="R$ 0,00",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        )
        self._lbl_troco.pack(anchor="w", pady=(2, 0))

        self._col_troco.grid_remove()

        ctk.CTkButton(
            frame, text="Lançar Pagamento", height=32, corner_radius=8,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco, font=self.fontes.texto_info,
            command=self._lancar_dinheiro
        ).pack(fill="x", pady=(8, 0))

    def _lancar_dinheiro(self):
        try:
            valor_texto = self._entry_valor_recebido.get().replace("R$", "").replace(",", ".").strip()
            valor = float(valor_texto) if valor_texto else 0
        except ValueError:
            valor = 0
        if valor <= 0:
            return

        restante = self._restante()
        troco = valor - restante

        if troco > 0:
            self._lbl_troco.configure(text=f"R$ {troco:.2f}".replace(".", ","))
            self._col_troco.grid()
        else:
            self._col_troco.grid_remove()

        self._pagamentos.append({
            "metodo": "Dinheiro",
            "valor": valor,
            "horario": datetime.now().strftime("%H:%M"),
            "status": "pendente",
        })
        self._atualizar_pagamentos()
        self._atualizar_rodape()
        self._atualizar_botao_adicionar()
        self._ultimo_metodo = "dinheiro"
        self._desabilitar_botoes_metodo()

        novo_restante = self._restante()
        self._entry_valor_recebido.delete(0, "end")
        if novo_restante > 0:
            self._entry_valor_recebido.insert(0, f"{novo_restante:.2f}".replace(".", ","))
        self._col_troco.grid_remove()

    def _mostrar_cartao(self):
        for w in self._frame_metodo_conteudo.winfo_children():
            w.destroy()

        self._frame_cartao = ctk.CTkFrame(self._frame_metodo_conteudo, fg_color="transparent")
        self._frame_cartao.pack(fill="x", padx=12, pady=12)

        frame_tipo = ctk.CTkFrame(self._frame_cartao, fg_color="transparent")
        frame_tipo.pack(fill="x", pady=(0, 8))
        frame_tipo.grid_columnconfigure((0, 1), weight=1)

        self.btn_credito = ctk.CTkButton(
            frame_tipo, text="Crédito", height=30, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            command=lambda: self._tipo_cartao("credito")
        )
        self.btn_credito.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        self.btn_debito = ctk.CTkButton(
            frame_tipo, text="Débito", height=30, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            command=lambda: self._tipo_cartao("debito")
        )
        self.btn_debito.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        self._tipo_cartao_selecionado = None
        self._frame_parcelas = None
        self._combo_parcelas = None

        restante = self._restante()

        ctk.CTkLabel(
            self._frame_cartao, text="Valor a pagar",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w", pady=(0, 2))

        self._entry_valor_cartao = ctk.CTkEntry(
            self._frame_cartao, placeholder_text="R$ 0,00",
            height=32, corner_radius=8,
            border_width=1, border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal
        )
        self._entry_valor_cartao.pack(fill="x", pady=(0, 8))
        if restante > 0:
            self._entry_valor_cartao.insert(0, f"{restante:.2f}".replace(".", ","))

        ctk.CTkButton(
            self._frame_cartao, text="Confirmar Pagamento", height=32, corner_radius=8,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco, font=self.fontes.texto_info,
            command=self._lancar_cartao
        ).pack(fill="x")

    def _tipo_cartao(self, tipo):
        self._tipo_cartao_selecionado = tipo
        if tipo == "credito":
            self.btn_credito.configure(fg_color=self.cores.botao.novo, text_color=self.cores.texto.branco)
            self.btn_debito.configure(fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal)
            if not self._frame_parcelas:
                self._criar_frame_parcelas()
            self._frame_parcelas.pack(fill="x", after=self.btn_credito.master, pady=(0, 8))
        else:
            self.btn_debito.configure(fg_color=self.cores.botao.novo, text_color=self.cores.texto.branco)
            self.btn_credito.configure(fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal)
            if self._frame_parcelas:
                self._frame_parcelas.pack_forget()

    def _criar_frame_parcelas(self):
        self._frame_parcelas = ctk.CTkFrame(self._frame_cartao, fg_color="transparent")

        ctk.CTkLabel(
            self._frame_parcelas, text="Parcelas",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w", pady=(0, 2))

        restante = self._restante()
        opcoes = ["1x (sem juros)"]
        if restante > 0:
            for i in range(2, min(7, int(restante / 10) + 1)):
                opcoes.append(f"{i}x (sem juros)")

        self._combo_parcelas = ctk.CTkOptionMenu(
            self._frame_parcelas, values=opcoes, height=30,
            corner_radius=6, fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=self._ao_mudar_parcela
        )
        self._combo_parcelas.pack(fill="x")
        self._combo_parcelas.set(opcoes[0])

        self._lbl_valor_parcela = ctk.CTkLabel(
            self._frame_parcelas, text="",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        )
        self._lbl_valor_parcela.pack(anchor="w", pady=(2, 0))

    def _ao_mudar_parcela(self, escolha):
        restante = self._restante()
        num = int(escolha.split("x")[0])
        if num > 1:
            valor_dividido = restante / num
            self._lbl_valor_parcela.configure(
                text=f"{num}x de R$ {valor_dividido:.2f}".replace(".", ",")
            )
        else:
            self._lbl_valor_parcela.configure(text="")

    def _lancar_cartao(self):
        if not self._tipo_cartao_selecionado:
            return
        try:
            valor_texto = self._entry_valor_cartao.get().replace("R$", "").replace(",", ".").strip()
            valor = float(valor_texto) if valor_texto else 0
        except ValueError:
            valor = 0
        if valor <= 0:
            return

        restante = self._restante()

        pagamento = {
            "metodo": f"Cartão ({self._tipo_cartao_selecionado.title()})",
            "valor": valor,
            "horario": datetime.now().strftime("%H:%M"),
            "status": "pendente",
        }
        if self._tipo_cartao_selecionado == "credito":
            pagamento["detalhes"] = self._combo_parcelas.get()
        self._pagamentos.append(pagamento)
        self._atualizar_pagamentos()
        self._atualizar_rodape()
        self._atualizar_botao_adicionar()
        self._ultimo_metodo = "cartao"
        self._desabilitar_botoes_metodo()

        novo_restante = self._restante()
        self._entry_valor_cartao.delete(0, "end")
        if novo_restante > 0:
            self._entry_valor_cartao.insert(0, f"{novo_restante:.2f}".replace(".", ","))

    def _mostrar_pix(self):
        for w in self._frame_metodo_conteudo.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self._frame_metodo_conteudo, fg_color="transparent")
        frame.pack(fill="x", padx=12, pady=12)

        frame_qr = ctk.CTkFrame(frame, fg_color="transparent")
        frame_qr.pack(fill="x", pady=(0, 8))

        qr_frame = ctk.CTkFrame(frame_qr, width=120, height=120, fg_color="white", corner_radius=8)
        qr_frame.pack(side="left", padx=(0, 12))
        qr_frame.pack_propagate(False)

        qr = get_qr_pix()
        qr = qr.resize((100, 100))
        qr_img = ctk.CTkImage(light_image=qr, size=(100, 100))
        ctk.CTkLabel(qr_frame, text="", image=qr_img).pack(expand=True)

        frame_info_pix = ctk.CTkFrame(frame_qr, fg_color="transparent")
        frame_info_pix.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            frame_info_pix, text="Pagamento via PIX",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame_info_pix,
            text="Aponte a câmera do celular para o QR Code ou copie a chave.",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo,
            wraplength=200, justify="left"
        ).pack(anchor="w", pady=(2, 0))

        frame_chave = ctk.CTkFrame(frame, fg_color="transparent")
        frame_chave.pack(fill="x", pady=(0, 8))

        self._lbl_chave_pix = ctk.CTkLabel(
            frame_chave, text="chave-pix-exemplo@dominio.com",
            font=self.fontes.pequeno, text_color=self.cores.texto.principal
        )
        self._lbl_chave_pix.pack(side="left")

        ctk.CTkButton(
            frame_chave, text="Copiar", width=60, height=24, corner_radius=6,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal, font=self.fontes.pequeno,
            command=self._copiar_chave_pix
        ).pack(side="right")

        restante = self._restante()

        ctk.CTkLabel(
            frame, text="Valor a pagar",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w", pady=(0, 2))

        self._entry_valor_pix = ctk.CTkEntry(
            frame, placeholder_text="R$ 0,00",
            height=32, corner_radius=8,
            border_width=1, border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal
        )
        self._entry_valor_pix.pack(fill="x", pady=(0, 8))
        if restante > 0:
            self._entry_valor_pix.insert(0, f"{restante:.2f}".replace(".", ","))

        ctk.CTkButton(
            frame, text="Confirmar Pagamento",
            height=32, corner_radius=8,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco, font=self.fontes.texto_info,
            command=self._lancar_pix
        ).pack(fill="x", pady=(8, 0))

    def _copiar_chave_pix(self):
        self.clipboard_clear()
        self.clipboard_append(self._lbl_chave_pix.cget("text"))

    def _lancar_pix(self):
        try:
            valor_texto = self._entry_valor_pix.get().replace("R$", "").replace(",", ".").strip()
            valor = float(valor_texto) if valor_texto else 0
        except ValueError:
            valor = 0
        if valor <= 0:
            return

        self._pagamentos.append({
            "metodo": "PIX",
            "valor": valor,
            "horario": datetime.now().strftime("%H:%M"),
            "status": "pendente",
        })
        self._atualizar_pagamentos()
        self._atualizar_rodape()
        self._atualizar_botao_adicionar()
        self._ultimo_metodo = "pix"
        self._desabilitar_botoes_metodo()

        novo_restante = self._restante()
        self._entry_valor_pix.delete(0, "end")
        if novo_restante > 0:
            self._entry_valor_pix.insert(0, f"{novo_restante:.2f}".replace(".", ","))

    # ═════════════════════════════════════════════════════════════
    # PAGAMENTOS APLICADOS
    # ═════════════════════════════════════════════════════════════
    def _atualizar_pagamentos(self):
        for w in self._frame_pagamentos.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self._frame_pagamentos, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(
            header, text="Pagamentos Aplicados",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(side="left")

        qtd = len(self._pagamentos)
        texto_qtd = "lançamento realizado" if qtd == 1 else "lançamentos realizados"
        ctk.CTkLabel(
            header, text=f"{qtd} {texto_qtd}",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(side="right")

        if not self._pagamentos:
            ctk.CTkLabel(
                self._frame_pagamentos, text="Nenhum pagamento lançado",
                font=self.fontes.pequeno, text_color=self.cores.texto.passivo
            ).pack(pady=10)
        else:
            for i, pag in enumerate(self._pagamentos):
                frame = ctk.CTkFrame(
                    self._frame_pagamentos, fg_color=self.cores.fundo.branco,
                    corner_radius=6
                )
                frame.pack(fill="x", padx=8, pady=2)

                frame_info = ctk.CTkFrame(frame, fg_color="transparent")
                frame_info.pack(fill="x", padx=8, pady=6)

                frame_left = ctk.CTkFrame(frame_info, fg_color="transparent")
                frame_left.pack(side="left")

                icones_map = {"Dinheiro": "💵", "Cartão": "💳", "PIX": "📱"}
                icone = "💵"
                for chave, ic in icones_map.items():
                    if chave in pag["metodo"]:
                        icone = ic
                        break

                ctk.CTkLabel(
                    frame_left, text=f"{icone} {pag['metodo']}",
                    font=self.fontes.texto_info, text_color=self.cores.texto.principal
                ).pack(anchor="w")

                detalhes = pag.get("detalhes", "")
                texto_detalhes = f"{pag['horario']}"
                if detalhes:
                    texto_detalhes += f" · {detalhes}"
                ctk.CTkLabel(
                    frame_left, text=texto_detalhes,
                    font=self.fontes.pequeno, text_color=self.cores.texto.passivo
                ).pack(anchor="w")

                frame_right = ctk.CTkFrame(frame_info, fg_color="transparent")
                frame_right.pack(side="right")

                texto_valor = f"R$ {pag['valor']:.2f}".replace(".", ",")
                ctk.CTkLabel(
                    frame_right, text=texto_valor,
                    font=self.fontes.texto_info, text_color=self.cores.texto.principal
                ).pack(anchor="e")

                ctk.CTkButton(
                    frame_right, text="🗑", width=24, height=24,
                    corner_radius=4, fg_color="transparent",
                    text_color=self.cores.texto.passivo,
                    hover_color=self.cores.card.atrasado_card,
                    font=ctk.CTkFont(size=14),
                    command=lambda idx=i: self._remover_pagamento(idx)
                ).pack(anchor="e", pady=(2, 0))

    def _remover_pagamento(self, idx):
        if 0 <= idx < len(self._pagamentos):
            self._pagamentos.pop(idx)
            self._atualizar_pagamentos()
            self._atualizar_status()
            self._atualizar_rodape()
            self._atualizar_botao_adicionar()
            if not self._pagamentos:
                self._ultimo_metodo = None
                self._reabilitar_botoes_metodo()
            else:
                self._reabilitar_botoes_metodo()

            novo_restante = self._restante()
            if self._metodo_selecionado == "dinheiro" and hasattr(self, '_entry_valor_recebido'):
                self._entry_valor_recebido.delete(0, "end")
                if novo_restante > 0:
                    self._entry_valor_recebido.insert(0, f"{novo_restante:.2f}".replace(".", ","))
            elif self._metodo_selecionado == "cartao" and hasattr(self, '_entry_valor_cartao'):
                self._entry_valor_cartao.delete(0, "end")
                if novo_restante > 0:
                    self._entry_valor_cartao.insert(0, f"{novo_restante:.2f}".replace(".", ","))
            elif self._metodo_selecionado == "pix" and hasattr(self, '_entry_valor_pix'):
                self._entry_valor_pix.delete(0, "end")
                if novo_restante > 0:
                    self._entry_valor_pix.insert(0, f"{novo_restante:.2f}".replace(".", ","))

    # ═════════════════════════════════════════════════════════════
    # RODAPÉ
    # ═════════════════════════════════════════════════════════════
    def _criar_rodape(self):
        frame_valores = ctk.CTkFrame(self._frame_rodape, fg_color="transparent")
        frame_valores.pack(fill="x", padx=12, pady=(8, 4))

        for texto_label, attr_name in [("Total", "_lbl_rodape_total"),
                                        ("Pago", "_lbl_rodape_pago")]:
            col = ctk.CTkFrame(frame_valores, fg_color="transparent")
            col.pack(side="left", expand=True)

            ctk.CTkLabel(
                col, text=texto_label,
                font=self.fontes.pequeno, text_color=self.cores.texto.passivo
            ).pack(anchor="w")

            lbl = ctk.CTkLabel(
                col, text="R$ 0,00",
                font=self.fontes.texto_info, text_color=self.cores.texto.principal
            )
            lbl.pack(anchor="w")
            setattr(self, attr_name, lbl)

        self._frame_rodape_dinheiro = ctk.CTkFrame(frame_valores, fg_color="transparent")
        self._frame_rodape_dinheiro.pack(side="left", expand=True)

        self._lbl_rodape_dinheiro_label = ctk.CTkLabel(
            self._frame_rodape_dinheiro, text="Restante",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        )
        self._lbl_rodape_dinheiro_label.pack(anchor="w")

        self._lbl_rodape_dinheiro_valor = ctk.CTkLabel(
            self._frame_rodape_dinheiro, text="R$ 0,00",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        )
        self._lbl_rodape_dinheiro_valor.pack(anchor="w")

        frame_botoes = ctk.CTkFrame(self._frame_rodape, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=12, pady=(0, 8))

        self._btn_comprovante = ctk.CTkButton(
            frame_botoes, text="🖨 Comprovante", height=34, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.passivo,
            font=self.fontes.texto_info,
            state="disabled",
            command=self._gerar_comprovante
        )
        self._btn_comprovante.pack(side="left", padx=(0, 4))

        self._btn_ir_status = ctk.CTkButton(
            frame_botoes, text="Ir para Status →", height=34, corner_radius=8,
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco,
            font=self.fontes.texto_info,
            command=self._ir_para_status
        )
        self._btn_ir_status.pack(side="right")

        self._btn_confirmar_pagamento = ctk.CTkButton(
            frame_botoes, text="Confirmar Pagamento", height=34, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.passivo,
            font=self.fontes.texto_info,
            state="disabled",
            command=self._confirmar_pagamento
        )
        self._btn_confirmar_pagamento.pack(side="right", padx=(0, 4))

    def _atualizar_rodape(self):
        total = self._dados_pedido.get("subtotal", 0)
        pago = sum(p["valor"] for p in self._pagamentos)
        restante = total - pago

        self._lbl_rodape_total.configure(text=f"R$ {total:.2f}".replace(".", ","))
        self._lbl_rodape_pago.configure(text=f"R$ {pago:.2f}".replace(".", ","))

        if restante > 0:
            self._lbl_rodape_dinheiro_label.configure(text="Restante")
            self._lbl_rodape_dinheiro_valor.configure(
                text=f"R$ {restante:.2f}".replace(".", ","),
                text_color=self.cores.texto.principal
            )
            self._frame_rodape_dinheiro.pack(side="left", expand=True)
        elif restante < 0:
            self._lbl_rodape_dinheiro_label.configure(text="Troco")
            self._lbl_rodape_dinheiro_valor.configure(
                text=f"R$ {abs(restante):.2f}".replace(".", ","),
                text_color=self.cores.texto.verde_escuro
            )
            self._frame_rodape_dinheiro.pack(side="left", expand=True)
        else:
            self._frame_rodape_dinheiro.pack_forget()

        if restante <= 0 and self._pagamentos:
            self._btn_confirmar_pagamento.configure(
                fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
                text_color=self.cores.texto.branco, state="normal"
            )
        else:
            self._btn_confirmar_pagamento.configure(
                fg_color=self.cores.fundo.cinza_claro,
                text_color=self.cores.texto.passivo, state="disabled"
            )

        if self._status_pagamento == "finalizado":
            self._btn_comprovante.configure(
                fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
                text_color=self.cores.texto.branco, state="normal"
            )

    def _confirmar_pagamento(self):
        id_pedido = self._dados_pedido.get("id_pedido")
        if not id_pedido:
            return

        for pag in self._pagamentos:
            pag["status"] = "pago"

        self.master.pedido_controller.confirmar_pagamento(id_pedido, self._pagamentos)

        self._status_pagamento = "finalizado"

        cor = self.cores.fundo.verde
        icone = "🟢"
        titulo = "Pagamento Confirmado"
        desc = "Pagamento registrado com sucesso."
        self._frame_status.configure(fg_color=cor)
        self._lbl_status_icone.configure(text=icone)
        self._lbl_status_titulo.configure(text=titulo)
        self._lbl_status_desc.configure(text=desc)

        self._btn_confirmar_pagamento.configure(
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.passivo, state="disabled"
        )

        self._btn_comprovante.configure(
            fg_color=self.cores.botao.novo, hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco, state="normal"
        )

    def _gerar_comprovante(self):
        logo_path = os.path.join(
            os.path.dirname(__file__), "..", "utils", "assets", "logo.png"
        )
        if not os.path.exists(logo_path):
            logo_path = None

        dados = dict(self._dados_pedido)
        dados["itens"] = list(dados.get("itens", []))

        gerar_pdf_comprovante(dados, self._pagamentos, logo_path=logo_path)

    def _ir_para_status(self):
        self.master._abrir_status(self._dados_pedido, self._pagamentos)


# ═══════════════════════════════════════════════════════════════════
# TELA DE STATUS
# ═══════════════════════════════════════════════════════════════════
class TelaCaixaStatus(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_home=None,
                 menu_callbacks=None, pedido_controller=None,
                 on_click_titulo=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Caixa", icone=icones.caixa,
                         on_novo=None, on_home=on_home,
                         menu_callbacks=menu_callbacks,
                         texto_info="Status",
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
        self.pedido_controller = pedido_controller or PedidoController()

        self._dados_pedido = {}
        self._pagamentos = []
        self._status_pedido = "recebido"
        self._tempo_estimado = 30
        self._tempo_decorrido = 0
        self._timer_rodando = False
        self._status_atual_index = 0
        self._lbl_tempo_decorrido = None
        self._lbl_aviso_atraso = None
        self._lbl_tempo_label = None
        self._btn_iniciar_timer = None

        self._criar_conteudo()

    def carregar_pedido(self, dados, pagamentos=None):
        self._dados_pedido = dados
        self._pagamentos = pagamentos or dados.get("pagamentos", [])
        self._status_pedido = dados.get("status_pedido", "criado")

        status_map = {
            "criado": 0, "confirmado": 1, "em_preparo": 2,
            "pronto": 3, "entregue": 4, "recebido": 0, "cancelado": -1
        }
        self._status_atual_index = status_map.get(self._status_pedido, 0)

        self._tempo_estimado = dados.get("tempo_estimado", 30) or 30
        id_pedido = dados.get("id_pedido")
        timer_iniciado_em = dados.get("timer_iniciado_em")
        timer_concluido_em = dados.get("timer_concluido_em")
        self._timer_iniciado_em_original = timer_iniciado_em
        timer_info = self.master._timers_ativos.get(id_pedido) if id_pedido else None
        if timer_info:
            self._tempo_decorrido = timer_info.get("tempo_decorrido_atual", 0)
        elif timer_iniciado_em and timer_concluido_em:
            self._tempo_decorrido = int((timer_concluido_em - timer_iniciado_em).total_seconds())
        elif timer_iniciado_em and hasattr(timer_iniciado_em, 'strftime'):
            self._tempo_decorrido = int((datetime.now() - timer_iniciado_em).total_seconds())
        else:
            self._tempo_decorrido = 0

        # Garante timer nos _timers_ativos se estiver rodando (em_preparo ou pronto)
        if self._status_atual_index in (2, 3) and id_pedido and timer_iniciado_em and hasattr(timer_iniciado_em, 'strftime') and not timer_concluido_em:
            if id_pedido not in self.master._timers_ativos:
                self.master._timers_ativos[id_pedido] = {
                    "timer_iniciado_em": timer_iniciado_em,
                    "tempo_estimado": self._tempo_estimado,
                }
                self.master._garantir_timer_central()

        origem = dados.get("origem", "mesa")
        num_mesa = dados.get("num_mesa")
        id_pedido = dados.get("id_pedido", 1)
        if origem == "mesa" and num_mesa:
            self.atualizar_info(f"Mesa {num_mesa} · Pedido #{id_pedido:03d}")
        elif origem == "balcao":
            self.atualizar_info(f"Balcão · Pedido #{id_pedido:03d}")
        else:
            self.atualizar_info(f"Pedido #{id_pedido:03d}")

        self._montar_status_producao()
        self._montar_detalhes_pedido()
        self._montar_controle()
        self._atualizar_botoes()

    # ═════════════════════════════════════════════════════════════
    # CONTEÚDO PRINCIPAL
    # ═════════════════════════════════════════════════════════════
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
                {"num": "1", "label": "Itens"},
                {"num": "2", "label": "Pagamento"},
                {"num": "3", "label": "Status"},
            ],
            etapa_atual=3,
            padx_circle=(100, 6), padx_label=(0, 200)
        )
        self.stepper.pack(expand=True)

        corpo = ctk.CTkFrame(principal, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.grid_columnconfigure(0, weight=2)
        corpo.grid_columnconfigure(1, weight=4)
        corpo.grid_columnconfigure(2, weight=2)
        corpo.grid_rowconfigure(0, weight=1)

        self._frame_status = ctk.CTkFrame(
            corpo, fg_color=self.cores.fundo.branco,
            corner_radius=12
        )
        self._frame_status.grid(row=0, column=0, sticky="new", padx=(0, 8))

        self._frame_detalhes = ctk.CTkFrame(
            corpo, fg_color=self.cores.fundo.branco,
            corner_radius=12
        )
        self._frame_detalhes.grid(row=0, column=1, sticky="nsew", padx=8)

        self._frame_controle = ctk.CTkFrame(
            corpo, fg_color=self.cores.fundo.branco,
            corner_radius=12
        )
        self._frame_controle.grid(row=0, column=2, sticky="new", padx=(8, 0))

        self._montar_status_producao()
        self._montar_detalhes_pedido()
        self._montar_controle()

    # ═════════════════════════════════════════════════════════════
    # STATUS DA PRODUÇÃO (esquerda)
    # ═════════════════════════════════════════════════════════════
    def _montar_status_producao(self):
        for w in self._frame_status.winfo_children():
            w.destroy()

        cabecalho = ctk.CTkFrame(self._frame_status, fg_color="transparent")
        cabecalho.pack(fill="x", padx=12, pady=(12, 0))

        ctk.CTkButton(
            cabecalho, text="", image=self.icones.voltar_pequeno,
            width=30, height=30,
            fg_color="transparent", hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.secundario, font=ctk.CTkFont(size=12),
            command=lambda: self.master._abrir_pagamento(self._dados_pedido)
        ).pack(side="left")

        if self._status_pedido == "cancelado":
            ctk.CTkLabel(
                self._frame_status, text="PEDIDO CANCELADO",
                font=self.fontes.titulo, text_color=self.cores.texto.vermelho
            ).pack(anchor="w", padx=16, pady=(16, 12))
            return

        ctk.CTkLabel(
            self._frame_status, text="STATUS DA PRODUÇÃO",
            font=self.fontes.titulo, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=16, pady=(12, 12))

        etapas = [
            ("Criado", "criado"),
            ("Confirmado", "confirmado"),
            ("Em Preparo", "em_preparo"),
            ("Pronto", "pronto"),
            ("Entregue", "entregue"),
        ]

        historico = self._dados_pedido.get("historico", [])
        hist_map = {}
        desfazer_map = {}
        for h in historico:
            status = h["status"]
            if status not in hist_map:
                hist_map[status] = h
            else:
                desfazer_map.setdefault(status, []).append(h)

        verde_jambu = self.cores.texto.verde_jambu
        laranja = self.cores.botao.novo

        frame_timeline = ctk.CTkFrame(self._frame_status, fg_color="transparent")
        frame_timeline.pack(fill="x", padx=16, pady=(0, 16))
        frame_timeline.columnconfigure(1, weight=1)

        for i, (nome, status_key) in enumerate(etapas):
            row = i * 2
            concluido = i < self._status_atual_index
            eh_atual = i == self._status_atual_index

            if concluido:
                cor_circle = verde_jambu
                icone = "✓"
                cor_texto = self.cores.texto.principal
            elif eh_atual:
                cor_circle = laranja
                icone = str(i + 1)
                cor_texto = self.cores.texto.principal
            else:
                cor_circle = self.cores.fundo.cinza_claro
                icone = str(i + 1)
                cor_texto = self.cores.texto.passivo

            circle = ctk.CTkLabel(
                frame_timeline, text=icone, width=26, height=26,
                corner_radius=13, fg_color=cor_circle,
                text_color=self.cores.texto.branco,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            circle.grid(row=row, column=0, sticky="w", padx=(0, 10))

            frame_texto = ctk.CTkFrame(frame_timeline, fg_color="transparent")
            frame_texto.grid(row=row, column=1, sticky="w", pady=(2, 0))

            ctk.CTkLabel(
                frame_texto, text=nome,
                font=self.fontes.texto_info, text_color=cor_texto
            ).pack(anchor="w")

            entry = hist_map.get(status_key)
            if entry:
                func_nome = entry.get("funcionario", "")
                data_hora = entry.get("data_hora", "")
                if hasattr(data_hora, 'strftime'):
                    data_hora = data_hora.strftime("%d/%m/%Y %H:%M")
                else:
                    data_hora = str(data_hora)[:16] if data_hora else ""
                subtexto = f"{func_nome} — {data_hora}" if func_nome else data_hora
                ctk.CTkLabel(
                    frame_texto, text=subtexto,
                    font=self.fontes.pequeno, text_color=self.cores.texto.passivo
                ).pack(anchor="w")
                desfazer = desfazer_map.get(status_key, [])
                for rev in desfazer:
                    rev_nome = rev.get("funcionario", "")
                    rev_hora = rev.get("data_hora", "")
                    if hasattr(rev_hora, 'strftime'):
                        rev_hora = rev_hora.strftime("%d/%m/%Y %H:%M")
                    else:
                        rev_hora = str(rev_hora)[:16] if rev_hora else ""
                    rev_texto = f"Desfeito por {rev_nome} — {rev_hora}" if rev_nome else f"Desfeito — {rev_hora}"
                    ctk.CTkLabel(
                        frame_texto, text=rev_texto,
                        font=self.fontes.pequeno, text_color=self.cores.texto.vermelho
                    ).pack(anchor="w")
            elif eh_atual and self._status_pedido == "em_preparo":
                tempo_fmt = self._formatar_tempo(self._tempo_decorrido)
                ctk.CTkLabel(
                    frame_texto, text=f"Em andamento • {tempo_fmt}",
                    font=self.fontes.pequeno, text_color=self.cores.texto.passivo
                ).pack(anchor="w")

            if i < len(etapas) - 1:
                cor_linha = verde_jambu if concluido else self.cores.fundo.cinza_claro
                barra = ctk.CTkLabel(
                    frame_timeline, text="", fg_color=cor_linha,
                    width=2, height=12
                )
                barra.grid(row=row + 1, column=0, sticky="w", padx=(13, 10), pady=0)

    # ═════════════════════════════════════════════════════════════
    # DETALHES DO PEDIDO (centro)
    # ═════════════════════════════════════════════════════════════
    def _montar_detalhes_pedido(self):
        for w in self._frame_detalhes.winfo_children():
            w.destroy()

        id_pedido = self._dados_pedido.get("id_pedido", 1)
        origem = self._dados_pedido.get("origem", "mesa")
        num_mesa = self._dados_pedido.get("num_mesa")
        texto_origem = f"Mesa {num_mesa}" if origem == "mesa" and num_mesa else "Balcão"
        cliente = self._dados_pedido.get("cliente", "")
        itens = self._dados_pedido.get("itens", [])
        qtd_itens = sum(i.get("quantidade", 1) for i in itens)
        subtotal = self._dados_pedido.get("subtotal", 0)

        # ── Header fixo (não rola)
        header = ctk.CTkFrame(self._frame_detalhes, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 0))

        frame_esq = ctk.CTkFrame(header, fg_color="transparent")
        frame_esq.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            frame_esq, text=f"Pedido #{id_pedido:03d}",
            font=self.fontes.subtitulo, text_color=self.cores.botao.id_badge_txt,
            fg_color=self.cores.botao.id_badge, corner_radius=50, padx=10, pady=4
        ).pack(anchor="w")

        frame_badges = ctk.CTkFrame(frame_esq, fg_color="transparent")
        frame_badges.pack(anchor="w", pady=(4, 0))

        cor_origem_bg = self.cores.fundo.verde if "Mesa" in texto_origem else self.cores.fundo.laranja
        cor_origem_txt = self.cores.texto.verde_escuro if "Mesa" in texto_origem else self.cores.texto.branco
        ctk.CTkLabel(
            frame_badges, text=texto_origem,
            font=self.fontes.pequeno, text_color=cor_origem_txt,
            fg_color=cor_origem_bg, corner_radius=10,
            padx=8, pady=2
        ).pack(side="left", padx=(0, 6))

        if cliente:
            ctk.CTkLabel(
                frame_badges, text=cliente,
                font=self.fontes.pequeno, text_color=self.cores.texto.passivo
            ).pack(side="left")

        frame_dir = ctk.CTkFrame(header, fg_color="transparent")
        frame_dir.pack(side="right")

        data_pedido = self._dados_pedido.get("data_pedido")
        if data_pedido:
            if isinstance(data_pedido, str):
                try:
                    data_fmt = datetime.strptime(str(data_pedido), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    data_fmt = str(data_pedido)
            else:
                data_fmt = str(data_pedido)
        else:
            data_fmt = "—"
        ctk.CTkLabel(
            frame_dir, text=data_fmt,
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="e")

        pagamentos = self._pagamentos
        total_pago = sum(p.get("valor", 0) for p in pagamentos if p.get("status") == "pago")
        subtotal = self._dados_pedido.get("subtotal", 0)
        if total_pago >= subtotal and subtotal > 0:
            texto_pagamento = "Pago"
            cor_pagamento = self.cores.texto.verde
        elif total_pago > 0:
            texto_pagamento = "Parcial"
            cor_pagamento = self.cores.botao.novo
        else:
            texto_pagamento = "Pendente"
            cor_pagamento = self.cores.texto.passivo

        ctk.CTkLabel(
            frame_dir, text=texto_pagamento,
            font=self.fontes.texto_info, text_color=cor_pagamento
        ).pack(anchor="e")

        ctk.CTkFrame(self._frame_detalhes, height=1, fg_color=self.cores.card.borda_card).pack(fill="x", padx=12, pady=8)

        # ── Observações (se houver)
        observacoes = self._dados_pedido.get("observacoes", "")
        if observacoes:
            frame_obs = ctk.CTkFrame(
                self._frame_detalhes, fg_color=self.cores.fundo.secundario, corner_radius=8
            )
            frame_obs.pack(fill="x", padx=12, pady=(0, 8))

            ctk.CTkLabel(
                frame_obs, text="Observações:",
                font=self.fontes.pequeno, text_color=self.cores.texto.passivo
            ).pack(anchor="w", padx=10, pady=(8, 2))

            ctk.CTkLabel(
                frame_obs, text=observacoes,
                font=self.fontes.pequeno, text_color=self.cores.texto.principal,
                anchor="w", justify="left", wraplength=350
            ).pack(anchor="w", padx=10, pady=(0, 8))

        # ── Título + subtotal + botão editar
        frame_titulo_row = ctk.CTkFrame(self._frame_detalhes, fg_color="transparent")
        frame_titulo_row.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(
            frame_titulo_row,
            text=f"Itens do Pedido ({qtd_itens})",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(side="left")

        ctk.CTkLabel(
            frame_titulo_row,
            text=f"Subtotal: R$ {subtotal:.2f}".replace(".", ","),
            font=self.fontes.texto_info, text_color=self.cores.texto.passivo
        ).pack(side="right")

        # ── Lista de itens (com scroll) + botão editar fixo no rodapé
        frame_scroll_wrapper = ctk.CTkFrame(
            self._frame_detalhes, fg_color=self.cores.fundo.secundario, corner_radius=8
        )
        frame_scroll_wrapper.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        frame_scroll_itens = ctk.CTkScrollableFrame(
            frame_scroll_wrapper, fg_color=self.cores.fundo.secundario, corner_radius=0,
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.fundo.cinza_claro,
            scrollbar_button_hover_color=self.cores.fundo.cinza_claro
        )
        frame_scroll_itens.pack(fill="both", expand=True)

        for item in itens:
            frame_item = ctk.CTkFrame(frame_scroll_itens, fg_color="transparent")
            frame_item.pack(fill="x", padx=8, pady=4)

            foto = item.get("foto", "")
            foto_carregada = False
            if foto:
                caminho = os.path.join(PASTA_PRODUTOS, foto)
                if os.path.exists(caminho):
                    try:
                        img = get_foto_ctk(caminho, (36, 36))
                        ctk.CTkLabel(frame_item, text="", image=img).pack(side="left", padx=(0, 8))
                        foto_carregada = True
                    except Exception:
                        pass

            if not foto_carregada:
                nome_produto = item.get("nome", "?")
                inicial = nome_produto[0].upper() if nome_produto else "?"
                ctk.CTkLabel(
                    frame_item, text=inicial, width=36, height=36,
                    corner_radius=18, fg_color=self.cores.fundo.cinza_claro,
                    text_color=self.cores.texto.principal,
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(side="left", padx=(0, 8))

            frame_info_item = ctk.CTkFrame(frame_item, fg_color="transparent")
            frame_info_item.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                frame_info_item, text=item.get("nome", ""),
                font=self.fontes.pequeno, text_color=self.cores.texto.principal
            ).pack(anchor="w")

            qtd = item.get("quantidade", 1)
            preco = item.get("preco", 0)
            ctk.CTkLabel(
                frame_info_item,
                text=f"{qtd}x R$ {preco:.2f}".replace(".", ","),
                font=ctk.CTkFont(size=9), text_color=self.cores.texto.passivo
            ).pack(anchor="w")

            total_item = preco * qtd
            ctk.CTkLabel(
                frame_item,
                text=f"R$ {total_item:.2f}".replace(".", ","),
                font=self.fontes.pequeno, text_color=self.cores.texto.principal
            ).pack(side="right")

        # Botão editar fixo no canto inferior direito
        frame_editar_row = ctk.CTkFrame(frame_scroll_wrapper, fg_color="transparent")
        frame_editar_row.pack(fill="x", padx=8, pady=(4, 8))
        self._btn_editar = Botoes.BotaoCircular(
            frame_editar_row, self.cores, self.icones.editar,
            tamanho=30, cor_fundo=self.cores.fundo.cinza_claro,
            comando=lambda: self.master._abrir_cadastro(dados=self._dados_pedido, limpar=False)
        )
        self._btn_editar.pack(side="right")
        frame_editar_row.pack_forget()  # mostrado apenas se status = criado/confirmado

        # ── Total fixo
        frame_total = ctk.CTkFrame(self._frame_detalhes, fg_color="transparent")
        frame_total.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(
            frame_total, text="TOTAL",
            font=self.fontes.titulo, text_color=self.cores.texto.principal
        ).pack(side="left")

        ctk.CTkLabel(
            frame_total,
            text=f"R$ {subtotal:.2f}".replace(".", ","),
            font=self.fontes.titulo, text_color=self.cores.texto.principal
        ).pack(side="right")

        # ── Botões de status (fixos no fundo)
        frame_acoes = ctk.CTkFrame(self._frame_detalhes, fg_color="transparent")
        frame_acoes.pack(fill="x", padx=12, pady=(6, 12))

        frame_botoes_dir = ctk.CTkFrame(frame_acoes, fg_color="transparent")
        frame_botoes_dir.pack(side="right")

        self._btn_reverter = Botoes.BotaoReverter(
            frame_botoes_dir, self.cores, self.fontes
        )
        self._btn_reverter.configure(command=self._reverter_status)
        self._btn_reverter.pack(side="left", padx=(0, 6))

        self._btn_status = self._criar_btn_avancar_status(frame_botoes_dir)
        self._btn_status.pack(side="left")

        self._lbl_aviso_pagamento = ctk.CTkLabel(
            frame_acoes, text="",
            font=self.fontes.pequeno, text_color=self.cores.texto.vermelho
        )
        self._lbl_aviso_pagamento.pack(side="left", padx=(0, 10))

    # ═════════════════════════════════════════════════════════════
    # CONTROLE (direita)
    # ═════════════════════════════════════════════════════════════
    def _montar_controle(self):
        for w in self._frame_controle.winfo_children():
            w.destroy()

        # ── Controle de Tempo
        frame_tempo = ctk.CTkFrame(
            self._frame_controle, fg_color=self.cores.fundo.secundario,
            corner_radius=8
        )
        frame_tempo.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(
            frame_tempo, text="CONTROLE DE TEMPO",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=12, pady=(12, 8))

        # Tempo estimado
        ctk.CTkLabel(
            frame_tempo, text="Tempo Estimado",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(anchor="w", padx=12)

        frame_estimado = ctk.CTkFrame(frame_tempo, fg_color="transparent")
        frame_estimado.pack(fill="x", padx=12, pady=(4, 8))

        ja_em_preparo = self._status_atual_index >= 2

        frame_capsula = ctk.CTkFrame(frame_estimado, fg_color=self.cores.fundo.cinza_claro, corner_radius=10)
        frame_capsula.pack()

        self._btn_menos = ctk.CTkButton(
            frame_capsula, text="−", width=26, height=26,
            corner_radius=0, fg_color="transparent",
            text_color=self.cores.texto.principal, font=self.fontes.texto_info,
            state="disabled" if ja_em_preparo else "normal",
            command=self._diminuir_estimado
        )
        self._btn_menos.pack(side="left", padx=(2, 0))

        self._lbl_tempo_estimado = ctk.CTkLabel(
            frame_capsula, text=f"{self._tempo_estimado} min",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal,
            width=50
        )
        self._lbl_tempo_estimado.pack(side="left", padx=4)

        self._btn_mais = ctk.CTkButton(
            frame_capsula, text="+", width=26, height=26,
            corner_radius=0, fg_color="transparent",
            text_color=self.cores.texto.principal, font=self.fontes.texto_info,
            state="disabled" if ja_em_preparo else "normal",
            command=self._aumentar_estimado
        )
        self._btn_mais.pack(side="left", padx=(0, 2))

        # ── Timer: centralizado pelo _tick_timer_central
        self._timer_rodando = ja_em_preparo

        self._lbl_tempo_label = ctk.CTkLabel(
            frame_tempo, text="Restante" if ja_em_preparo else "",
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        )
        self._lbl_tempo_label.pack(anchor="w", padx=12, pady=(4, 0))

        if ja_em_preparo:
            restante = self._tempo_estimado * 60 - self._tempo_decorrido
            tempo_texto = self._formatar_tempo(restante)
            self._lbl_tempo_decorrido = ctk.CTkLabel(
                frame_tempo, text=tempo_texto,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=self.cores.texto.principal
            )
            self._lbl_tempo_decorrido.pack(anchor="w", padx=12, pady=(2, 4))

            self._lbl_aviso_atraso = ctk.CTkLabel(
                frame_tempo, text="⚠️ ATRASADO",
                font=self.fontes.pequeno, text_color=self.cores.texto.vermelho
            )
        else:
            self._lbl_tempo_decorrido = None
            self._lbl_aviso_atraso = None

            ctk.CTkLabel(
                frame_tempo, text="Timer será iniciado ao preparar pedido",
                font=self.fontes.pequeno, text_color=self.cores.texto.passivo
            ).pack(anchor="w", padx=12, pady=(2, 12))

        # ── Frame ações
        frame_acoes_controle = ctk.CTkFrame(
            self._frame_controle, fg_color=self.cores.fundo.secundario,
            corner_radius=8
        )
        frame_acoes_controle.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(
            frame_acoes_controle, text="AÇÕES",
            font=self.fontes.texto_info, text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=12, pady=(12, 8))

        self._btn_cancelar_pedido = Botoes.BotaoCancelarPedido(
            frame_acoes_controle, self.cores, self.fontes
        )
        self._btn_cancelar_pedido.configure(command=self._confirmar_cancelar)
        self._btn_cancelar_pedido.pack(fill="x", padx=12, pady=(0, 6))

        self._btn_excluir = Botoes.BotaoExcluirPedido(
            frame_acoes_controle, self.cores, self.fontes
        )
        self._btn_excluir.configure(command=self._confirmar_excluir)
        self._btn_excluir.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkButton(
            frame_acoes_controle, text="🖨 Imprimir Comanda",
            height=34, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal, font=self.fontes.texto_info,
            command=self._imprimir_comanda
        ).pack(fill="x", padx=12, pady=(0, 12))

    # ══════════════════════════════════════════════════════════════
    # AÇÕES DE STATUS
    # ══════════════════════════════════════════════════════════════
    def _criar_btn_avancar_status(self, parent):
        """Cria o BotaoAvancarStatus com callback que executa a ação correta."""
        btn = Botoes.BotaoAvancarStatus(parent, self.cores, self.fontes)

        def avancar():
            id_pedido = self._dados_pedido.get("id_pedido")
            if not id_pedido:
                return
            status = self._status_pedido

            if status == "criado":
                self.pedido_controller.atualizar_status(id_pedido, "confirmado")
                self._status_pedido = "confirmado"
                self._status_atual_index = 1
            elif status == "confirmado":
                self.pedido_controller.iniciar_timer(id_pedido, self._tempo_estimado)
                self._status_pedido = "em_preparo"
                self._status_atual_index = 2
                self._tempo_decorrido = 0
                # Timer local
                self.master._timers_ativos[id_pedido] = {
                    "timer_iniciado_em": datetime.now(),
                    "tempo_estimado": self._tempo_estimado,
                }
                self.master._garantir_timer_central()
            elif status == "em_preparo":
                timer_info = self.master._timers_ativos.get(id_pedido, {})
                self._tempo_decorrido = timer_info.get("tempo_decorrido_atual", 0)
                self.pedido_controller.atualizar_status(id_pedido, "pronto")
                self._status_pedido = "pronto"
                self._status_atual_index = 3
            elif status == "pronto":
                timer_info = self.master._timers_ativos.get(id_pedido, {})
                self._tempo_decorrido = timer_info.get("tempo_decorrido_atual", 0)
                restante = self._tempo_estimado * 60 - self._tempo_decorrido
                timer_status = "atrasado" if restante <= 0 else "normal"
                self.pedido_controller.parar_timer(id_pedido, timer_status)
                if id_pedido in self.master._timers_ativos:
                    del self.master._timers_ativos[id_pedido]
                self.pedido_controller.atualizar_status(id_pedido, "entregue")
                self._status_pedido = "entregue"
                self._status_atual_index = 4
            elif status == "entregue":
                total_pago = sum(p.get("valor", 0) for p in self._pagamentos if p.get("status") == "pago")
                restante = self._dados_pedido.get("subtotal", 0) - total_pago
                if restante > 0 or total_pago <= 0:
                    tk_msgbox.showwarning(
                        "Pagamento Pendente",
                        "Confirme o pagamento antes de concluir o pedido."
                    )
                    return
                if not tk_msgbox.askyesno("Concluir Pedido", "Deseja concluir este pedido?"):
                    return
                self.pedido_controller.atualizar_status(id_pedido, "concluido")
                self._status_pedido = "concluido"
                self._status_atual_index = 5
                self._recarregar_tela()
                self.master._mostrar_lista()
                return

            self._atualizar_dados_pedido()
            self._recarregar_tela()

        btn.configure(command=avancar)
        return btn

    def _atualizar_botoes(self):
        status = self._status_pedido
        id_pedido = self._dados_pedido.get("id_pedido")

        # Cálculo de pagamento (usado por Avançar e Editar)
        total_pago = sum(p.get("valor", 0) for p in self._pagamentos if p.get("status") == "pago")
        restante = self._dados_pedido.get("subtotal", 0) - total_pago
        pedido_pago = restante <= 0 and total_pago > 0

        # Botão Avançar Status
        if hasattr(self, "_btn_status") and self._btn_status:
            self._btn_status.atualizar(status)

        # Label de aviso de pagamento pendente
        if hasattr(self, "_lbl_aviso_pagamento") and self._lbl_aviso_pagamento:
            if status == "entregue" and not pedido_pago:
                self._lbl_aviso_pagamento.configure(text="⚠️ Confirme o pagamento para concluir")
                self._lbl_aviso_pagamento.pack(side="left", padx=(0, 10))
            else:
                self._lbl_aviso_pagamento.pack_forget()

        # Botão Editar - bloqueado se pago, senão visível em Criado e Confirmado
        if hasattr(self, "_btn_editar") and self._btn_editar:
            if not pedido_pago and status in ("criado", "confirmado"):
                self._btn_editar.master.pack(fill="x", padx=8, pady=(4, 8))
                self._btn_editar.configure(state="normal")
            else:
                self._btn_editar.master.pack_forget()

        # Botão Cancelar Pedido - exceto Concluído e Cancelado
        if hasattr(self, "_btn_cancelar_pedido") and self._btn_cancelar_pedido:
            if status in ("concluido", "cancelado"):
                self._btn_cancelar_pedido.pack_forget()
            else:
                self._btn_cancelar_pedido.pack(fill="x", padx=12, pady=(0, 6))
                self._btn_cancelar_pedido.configure(state="normal")

        # Botão Excluir - só visível se cancelado
        if hasattr(self, "_btn_excluir") and self._btn_excluir:
            if status == "cancelado":
                self._btn_excluir.pack(fill="x", padx=12, pady=(0, 6))
            else:
                self._btn_excluir.pack_forget()

        # Botão Reverter
        if hasattr(self, "_btn_reverter") and self._btn_reverter:
            from app.utils.permissoes import nivel
            pode_revert = self.pedido_controller.pode_reverter(
                id_pedido, nivel()
            ) if id_pedido else False
            habilitado = status not in ("criado", "cancelado", "concluido") and pode_revert
            self._btn_reverter.atualizar(habilitado)

    def _confirmar_cancelar(self):
        id_pedido = self._dados_pedido.get("id_pedido")
        if not id_pedido:
            return
        from app.utils.permissoes import tem_acao, pedir_senha_admin

        if tem_acao("caixa", "cancelar"):
            self._executar_cancelamento(id_pedido)
        else:
            pedir_senha_admin(
                master=self,
                callback=lambda: self._executar_cancelamento(id_pedido)
            )
            
    def _executar_cancelamento(self, id_pedido):
        if not tk_msgbox.askyesno("Cancelar Pedido", "Deseja cancelar este pedido?"):
            return
        if self._status_pedido in ("em_preparo", "pronto"):
            timer_info = self.master._timers_ativos.get(id_pedido, {})
            self._tempo_decorrido = timer_info.get("tempo_decorrido_atual", 0)
            restante = self._tempo_estimado * 60 - self._tempo_decorrido
            timer_status = "atrasado" if restante <= 0 else "normal"
            self.pedido_controller.parar_timer(id_pedido, timer_status)
            if id_pedido in self.master._timers_ativos:
                del self.master._timers_ativos[id_pedido]
        self.pedido_controller.cancelar_pedido(id_pedido)
        self._status_pedido = "cancelado"
        self._status_atual_index = -1
        self._recarregar_tela()
        self.master._mostrar_lista() 

    def _confirmar_excluir(self):
        id_pedido = self._dados_pedido.get("id_pedido")
        if not id_pedido:
            return
        if not tk_msgbox.askyesno("Excluir Pedido",
                                   "Tem certeza que deseja excluir este pedido? Esta ação não pode ser desfeita."):
            return
        self.pedido_controller.excluir_pedido(id_pedido)
        if id_pedido in self.master._timers_ativos:
            del self.master._timers_ativos[id_pedido]
        self.master._mostrar_lista()

    def _atualizar_dados_pedido(self, completo=False):
        id_pedido = self._dados_pedido.get("id_pedido")
        if not id_pedido:
            return
        if completo:
            pedido_db = self.pedido_controller.buscar_pedido(id_pedido)
            if pedido_db:
                self._dados_pedido = pedido_db
        else:
            historico = self.pedido_controller.buscar_historico(id_pedido)
            if historico:
                self._dados_pedido["historico"] = historico
            self._dados_pedido["status_pedido"] = self._status_pedido

    def _reverter_status(self):
        id_pedido = self._dados_pedido.get("id_pedido")
        if not id_pedido:
            return
        if not tk_msgbox.askyesno("Reverter Status", "Tem certeza? Esta ação será computada."):
            return

        status_map = {
            "confirmado": "criado",
            "em_preparo": "confirmado",
            "pronto": "em_preparo",
            "entregue": "pronto",
            "concluido": "entregue",
        }
        status_anterior = status_map.get(self._status_pedido)
        if not status_anterior:
            return
        if self._status_pedido == "em_preparo":
            timer_info = self.master._timers_ativos.get(id_pedido, {})
            self._tempo_decorrido = timer_info.get("tempo_decorrido_atual", 0)
            restante = self._tempo_estimado * 60 - self._tempo_decorrido
            timer_status = "atrasado" if restante <= 0 else "normal"
            self.pedido_controller.parar_timer(id_pedido, timer_status)
            if id_pedido in self.master._timers_ativos:
                del self.master._timers_ativos[id_pedido]
        self.pedido_controller.reverter_status(id_pedido, status_anterior)
        self._status_pedido = status_anterior
        self._status_atual_index = {"criado": 0, "confirmado": 1, "em_preparo": 2, "pronto": 3}.get(status_anterior, 0)

        self._atualizar_dados_pedido(completo=True)

        if status_anterior in ("em_preparo", "pronto"):
            ti = self._dados_pedido.get("timer_iniciado_em")
            self._tempo_decorrido = int((datetime.now() - ti).total_seconds()) if ti and hasattr(ti, 'strftime') else 0

        self._recarregar_tela()

        if status_anterior in ("em_preparo", "pronto"):
            timer_iniciado_em = self._dados_pedido.get("timer_iniciado_em")
            if timer_iniciado_em and hasattr(timer_iniciado_em, 'strftime'):
                self.master._timers_ativos[id_pedido] = {
                    "timer_iniciado_em": timer_iniciado_em,
                    "tempo_estimado": self._tempo_estimado,
                }
                self.master._garantir_timer_central()

    def _recarregar_tela(self):
        self._montar_status_producao()
        self._montar_detalhes_pedido()
        self._montar_controle()
        self._atualizar_botoes()

    def _imprimir_comanda(self):
        id_pedido = self._dados_pedido.get("id_pedido")
        if not id_pedido:
            return
        logo = os.path.join(os.path.dirname(__file__), "..", "utils", "assets", "logo.png")
        caminho = gerar_comanda(self._dados_pedido, logo_path=logo)
        if caminho:
            import subprocess
            subprocess.Popen([caminho], shell=True)

    # ═════════════════════════════════════════════════════════════
    # TIMER
    # ═════════════════════════════════════════════════════════════
    def _diminuir_estimado(self):
        if self._tempo_estimado > 5:
            self._tempo_estimado -= 5
            self._lbl_tempo_estimado.configure(text=f"{self._tempo_estimado} min")

    def _aumentar_estimado(self):
        self._tempo_estimado += 5
        self._lbl_tempo_estimado.configure(text=f"{self._tempo_estimado} min")

    def _formatar_tempo(self, segundos):
        sinal = "-" if segundos < 0 else ""
        segundos = abs(segundos)
        h = segundos // 3600
        m = (segundos % 3600) // 60
        s = segundos % 60
        return f"{sinal}{h:02d}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()

    CaixaView(root)

    root.mainloop()

