from datetime import datetime, timedelta
import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import Frames
from app.utils.usuario_atual import usuario_atual
from app.controller.pedido_controller import PedidoController
from app.controller.relatorio_controller import carregar_estoque_minimo
from app.utils.graficos import criar_grafico_vendas, renderizar_grafico



class PainelControleView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Sabores do Pará")
        self.minsize(1100, 700)
        self.after(0, lambda: self.state('zoomed'))
        self.lift()
        self.focus_force()

        self.cores  = get_cores()
        self.fontes = Fontes()
        self.icones = Icones()
        self.controller = PedidoController()

        self.configure(fg_color=self.cores.fundo.principal)
        self._build_ui()

        self._destaque = "ambos"
        self._dados_hoje = []
        self._dados_ontem = []
        self._fig_grafico = None
        self._canvas_grafico = None
        self._linha_hoje = None
        self._linha_ontem = None

        self.after_idle(self._carregar_tudo)

        self.protocol("WM_DELETE_WINDOW", self._fechar_app)

    def destroy(self):
        self._limpar_grafico()
        super().destroy()

    def _limpar_grafico(self):
        if hasattr(self, '_redim_after') and self._redim_after:
            self.after_cancel(self._redim_after)
            self._redim_after = None
        if self._fig_grafico is not None:
            import matplotlib.pyplot as plt
            plt.close(self._fig_grafico)
            self._fig_grafico = None
            self._canvas_grafico = None

    def _fechar_app(self):
        self._limpar_grafico()
        self.destroy()
        self.master.destroy()

    def _carregar_tudo(self):
        self._atualizar_dados()
        self.after(10, self._etapa_grafico)

    def _etapa_grafico(self):
        self._carregar_dados_grafico()
        self.after(10, self._etapa_renderizar)

    def _etapa_renderizar(self):
        self._renderizar_grafico()
        self.after(10, self._carregar_alertas_estoque)

    def _build_ui(self):
        cores  = self.cores
        fontes = self.fontes
        icones = self.icones

        def abrir_caixa():
            self.destroy()
            from app.view.caixa_view import CaixaView
            CaixaView(self.master)

        def abrir_produtos():
            self.destroy()
            from app.view.produto_view_novo import ProdutosView
            ProdutosView(self.master)

        def abrir_clientes():
            self.destroy()
            from app.view.clientes_view import ClientesView
            ClientesView(self.master)

        def abrir_estoque():
            from app.utils.permissoes import bloquear_se_sem_acesso
            if bloquear_se_sem_acesso("estoque", self, None):
                return
            self.destroy()
            from app.view.estoque_view import EstoqueView
            EstoqueView(self.master)

        def abrir_funcionarios():
            from app.utils.permissoes import bloquear_se_sem_acesso
            if bloquear_se_sem_acesso("funcionarios", self, None):
                return
            self.destroy()
            from app.view.funcionarios_view import FuncionariosView
            FuncionariosView(self.master)

        def abrir_relatorios():
            from app.utils.permissoes import bloquear_se_sem_acesso
            if bloquear_se_sem_acesso("relatorios", self, None):
                return
            self.destroy()
            from app.view.relatorio_view import RelatoriosView
            RelatoriosView(self.master)

        def abrir_delivery():
            self.destroy()
            from app.view.delivery_list_view import DeliveryListView
            DeliveryListView(self.master)

        menu_callbacks = {
            "caixa":        abrir_caixa,
            "delivery":     abrir_delivery,
            "clientes":     abrir_clientes,
            "estoque":      abrir_estoque,
            "funcionarios": abrir_funcionarios,
            "produtos":     abrir_produtos,
            "relatorios":   abrir_relatorios,
        }

        self.layout = Frames.FrameLayoutPadrao(
            self, cores, fontes, icones,
            titulo="Painel de Controle",
            usuario=usuario_atual["nome"],
            menu_callbacks=menu_callbacks
        )
        
        self.layout.pack(expand=True, fill="both")
        layout = self.layout

        frame_cards = ctk.CTkFrame(layout.area_tela, fg_color="transparent")
        frame_cards.pack(fill="x", padx=150, pady=(30, 10))
        frame_cards.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

        self.cards = {}

        self.cards["vendas"] = Frames.MetricCard(
            frame_cards, cores, fontes,
            icone=icones.crescente, titulo="Vendas do dia", valor="R$ 0,00",
            destaque=True,
        )
        self.cards["vendas"].grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        self.cards["andamento"] = Frames.MetricCard(
            frame_cards, cores, fontes,
            icone=icones.relogio, titulo="Em andamento", valor="0",
            cor_valor=cores.texto.laranja,
        )
        self.cards["andamento"].grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        self.cards["ticket"] = Frames.MetricCard(
            frame_cards, cores, fontes,
            icone=icones.carteira, titulo="Consumo médio por pedido", valor="R$ 0,00",
            cor_valor=cores.texto.verde_jambu,
        )
        self.cards["ticket"].grid(row=0, column=2, sticky="nsew", padx=10, pady=5)

        self.cards["atrasos"] = Frames.MetricCard(
            frame_cards, cores, fontes,
            icone=icones.fechar_preto, titulo="Atrasos críticos", valor="0",
            cor_valor=cores.texto.vermelho,
        )
        self.cards["atrasos"].grid(row=0, column=3, sticky="nsew", padx=10, pady=5)

        frame_meio = ctk.CTkFrame(layout.area_tela, fg_color="transparent")
        frame_meio.pack(fill="both", expand=True, padx=(150, 150), pady=(10, 10))
        frame_meio.grid_rowconfigure(0, weight=1)
        frame_meio.grid_columnconfigure(0, weight=1)
        frame_meio.grid_columnconfigure(1, weight=0, minsize=250)

        # --- Left: chart ---
        frame_grafico_cartao = ctk.CTkFrame(
            frame_meio, fg_color=cores.fundo.branco,
            border_color=cores.card.borda_card, border_width=1, corner_radius=15,
        )
        frame_grafico_cartao.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        frame_grafico = ctk.CTkFrame(frame_grafico_cartao, fg_color="transparent")
        frame_grafico.pack(fill="both", expand=True, padx=15, pady=15)

        cabecalho = ctk.CTkFrame(frame_grafico, fg_color="transparent")
        cabecalho.pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            cabecalho, image=icones.crescente, text=""
        ).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            cabecalho, text="Vendas por hora",
            font=fontes.subtitulo, text_color=cores.texto.principal,
        ).pack(side="left")

        toggle_frame = ctk.CTkFrame(frame_grafico, fg_color="transparent")
        toggle_frame.pack(anchor="w")

        self._btn_hoje = ctk.CTkButton(
            toggle_frame, text="Hoje  ●",
            font=fontes.pequeno,
            fg_color=cores.fundo.cinza_claro, text_color=cores.texto.laranja,
            hover_color=cores.botao.passivo, width=80, height=28,
            corner_radius=6,
            command=lambda: self._toggle_destaque("hoje"),
        )
        self._btn_hoje.pack(side="left", padx=(0, 8))

        self._btn_ontem = ctk.CTkButton(
            toggle_frame, text="Ontem  ─",
            font=fontes.pequeno,
            fg_color=cores.fundo.cinza_claro, text_color=cores.texto.passivo,
            hover_color=cores.botao.passivo, width=80, height=28,
            corner_radius=6,
            command=lambda: self._toggle_destaque("ontem"),
        )
        self._btn_ontem.pack(side="left")

        self._area_grafico = ctk.CTkFrame(frame_grafico, fg_color="transparent")
        self._area_grafico.pack(fill="both", expand=True)
        self._area_grafico.bind("<Configure>", self._redimensionar_grafico)
        self._lbl_loading = ctk.CTkLabel(
            self._area_grafico, text="Carregando gráfico...",
            font=fontes.subtitulo, text_color=cores.texto.passivo,
        )
        self._lbl_loading.pack(expand=True)

        # --- Right: Alertas de Estoque ---
        frame_alertas_cartao = ctk.CTkFrame(
            frame_meio, fg_color=cores.fundo.branco,
            border_color=cores.card.borda_card, border_width=1, corner_radius=15,
        )
        frame_alertas_cartao.grid(row=0, column=1, sticky="nsew")
        frame_alertas_cartao.grid_propagate(False)

        self._frame_alertas = ctk.CTkFrame(frame_alertas_cartao, fg_color="transparent")
        self._frame_alertas.pack(fill="both", expand=True, padx=15, pady=15)

        cabecalho_alerta = ctk.CTkFrame(self._frame_alertas, fg_color="transparent")
        cabecalho_alerta.pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(
            cabecalho_alerta, image=icones.estoque, text=""
        ).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            cabecalho_alerta, text="Alertas de Estoque",
            font=fontes.subtitulo, text_color=cores.texto.principal,
        ).pack(side="left")

        separador = ctk.CTkFrame(self._frame_alertas, fg_color=cores.botao.borda, height=1)
        separador.pack(fill="x", pady=(0, 8))

        self._frame_alertas_lista = ctk.CTkScrollableFrame(
            self._frame_alertas, fg_color="transparent",
            scrollbar_button_color=cores.botao.passivo,
            scrollbar_button_hover_color=cores.botao.passivo,
        )
        self._frame_alertas_lista.pack(fill="both", expand=True)

        btn_inventario = ctk.CTkButton(
            self._frame_alertas,
            text="Ver inventário completo  →",
            font=fontes.texto_info,
            fg_color=cores.botao.ativo, text_color=cores.texto.branco,
            hover_color=cores.botao.passivo,
            corner_radius=8, height=36,
            command=self._abrir_estoque,
        )
        btn_inventario.pack(fill="x", pady=(10, 0))

        frame_fluxo = ctk.CTkFrame(layout.area_tela, fg_color="transparent")
        frame_fluxo.pack(fill="x", padx=150, pady=(0, 30))
        frame_fluxo.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="fluxo")

        self.fluxo = {}
        fluxo_config = [
            ("em_preparo", "Em preparo", cores.texto.laranja),
            ("prontos",    "Pronto",     cores.texto.verde),
            ("entregues",  "Entregue",   cores.texto.verde_jambu),
            ("cancelados", "Cancelado",  cores.texto.vermelho),
        ]
        for i, (chave, titulo, cor) in enumerate(fluxo_config):
            self.fluxo[chave] = Frames.MetricCard(
                frame_fluxo, cores, fontes,
                titulo=titulo, valor="0",
                cor_valor=cor,
            )
            self.fluxo[chave].grid(row=0, column=i, sticky="nsew", padx=8, pady=5)

    def _toggle_destaque(self, lado):
        if self._destaque == lado:
            self._destaque = "ambos"
        else:
            self._destaque = lado

        alpha_hoje = 0.3 if self._destaque == "ontem" else 1.0
        alpha_ontem = 0.3 if self._destaque == "hoje" else 1.0
        self._linha_hoje.set_alpha(alpha_hoje)
        self._linha_ontem.set_alpha(alpha_ontem)
        self._canvas_grafico.draw_idle()

    def _carregar_dados_grafico(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        ontem = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        dados = self.controller.vendas_por_datas([hoje, ontem])
        self._dados_hoje = dados.get(hoje, [])
        self._dados_ontem = dados.get(ontem, [])

    def _renderizar_grafico(self):
        if not self.winfo_exists():
            return
        if self._fig_grafico is not None:
            import matplotlib.pyplot as plt
            plt.close(self._fig_grafico)
        fig, self._linha_hoje, self._linha_ontem = criar_grafico_vendas(
            self.cores,
            dados_hoje=self._dados_hoje,
            dados_ontem=self._dados_ontem,
            destaque=self._destaque,
        )
        self._fig_grafico = fig
        self._canvas_grafico = renderizar_grafico(self._area_grafico, fig)

    def _redimensionar_grafico(self, event=None):
        if not self.winfo_exists():
            return
        if hasattr(self, '_redim_after') and self._redim_after:
            self.after_cancel(self._redim_after)
        self._redim_after = self.after(200, self._renderizar_grafico)

    def _atualizar_dados(self):
        resumo = self.controller.carregar_resumo_cards()
        atrasados = self.controller.carregar_atrasados_por_origem()

        hoje = resumo["vendas_dia"]
        ontem = resumo["vendas_ontem"]

        self.cards["vendas"].set_valor(f"R$ {hoje:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if ontem > 0:
            pct = ((hoje - ontem) / ontem) * 100
            sub = f"{pct:+.1f}% vs ontem"
        elif hoje > 0:
            sub = "+100% vs ontem"
        else:
            sub = ""
        self.cards["vendas"].set_subtexto(sub)

        total_andamento = resumo["pedidos_ativos"]
        delivery_andamento = resumo["delivery_andamento"]
        presencial_andamento = resumo["presencial_andamento"]
        self.cards["andamento"].set_valor(str(total_andamento))
        self.cards["andamento"].set_subtexto(
            f"🚚{delivery_andamento} delivery · 🍽{presencial_andamento} presencial"
        )

        ticket = resumo["ticket_medio"]
        self.cards["ticket"].set_valor(
            f"R$ {ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        total_atrasos = atrasados["delivery"] + atrasados["presencial"]
        self.cards["atrasos"].set_valor(str(total_atrasos))
        self.cards["atrasos"].set_subtexto(
            f"🚚{atrasados['delivery']} delivery · 🍽{atrasados['presencial']} presencial"
        )

        total = max(resumo["total_pedidos"], 1)
        for chave in ("em_preparo", "prontos", "entregues", "cancelados"):
            valor = resumo[chave]
            delivery = resumo[f"{chave}_delivery"]
            presencial = resumo[f"{chave}_presencial"]
            pct = (valor / total) * 100
            self.fluxo[chave].set_valor(str(valor))
            if valor > 0:
                self.fluxo[chave].set_subtexto(
                    f"{pct:.0f}% · 🚚{delivery} delivery 🍽{presencial} presencial"
                )
            else:
                self.fluxo[chave].set_subtexto("0%")

    def _abrir_estoque(self):
        self.destroy()
        from app.view.estoque_view import EstoqueView
        EstoqueView(self.master)

    def _carregar_alertas_estoque(self):
        itens = carregar_estoque_minimo()
        cores = self.cores
        fontes = self.fontes

        for w in self._frame_alertas_lista.winfo_children():
            w.destroy()

        exibir = itens[:6]
        mostrar_mais = len(itens) > 6

        for item in exibir:
            qtd = item["quantidade"] or 0
            nome = item["nome"]
            unidade = item["unidade"]

            if qtd == 0:
                status = "Crítico"
                cor_status = cores.texto.vermelho
            else:
                status = "Baixo"
                cor_status = cores.texto.laranja

            row = ctk.CTkFrame(self._frame_alertas_lista, fg_color=cores.fundo.cinza_claro, corner_radius=6)
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row, text=nome,
                font=fontes.sub_info, text_color=cores.texto.principal,
                anchor="w",
            ).pack(side="left", padx=(10, 5), pady=8, fill="x", expand=True)

            ctk.CTkLabel(
                row, text=f"{qtd} {unidade}",
                font=fontes.sub_info, text_color=cores.texto.passivo,
                anchor="e",
            ).pack(side="left", padx=5)

            badge = ctk.CTkLabel(
                row, text=status,
                font=fontes.pequeno,
                text_color=cores.texto.branco,
                fg_color=cor_status,
                corner_radius=4,
                padx=8, pady=2,
            )
            badge.pack(side="right", padx=(5, 10))

        if mostrar_mais:
            mais = len(itens) - 6
            ctk.CTkLabel(
                self._frame_alertas_lista,
                text=f"e mais {mais} item(ns) em alerta",
                font=fontes.pequeno,
                text_color=cores.texto.passivo,
            ).pack(pady=(5, 0))

    def _recarregar_tema(self):
        from app.utils.estilos import get_cores
        self.cores = get_cores()
        self.configure(fg_color=self.cores.fundo.principal)
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
        self.after(10, self._carregar_tudo)

    def atualizar_usuario(self):
        if hasattr(self, "layout"):
            self.layout.atualizar_usuario(usuario_atual["nome"])


def abrir_painel(master=None):
    return PainelControleView(master)


def main(master=None):
    return abrir_painel(master)


