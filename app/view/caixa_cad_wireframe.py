import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones


class WireframePedido(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Wireframe - Tela de Pedido")
        self.minsize(1100, 700)
        self.after(0, lambda: self.state('zoomed'))

        self.cores = get_cores()
        self.fontes = Fontes()
        self.icones = Icones()

        self.configure(fg_color=self.cores.fundo.principal)

        self.origem_selecionada = "Mesa"
        self.etapa_atual = 1  # 1=Itens, 2=Pagamento, 3=Status

        self._criar_layout()

    def _recarregar_tema(self):
        self.cores = get_cores()
        self.configure(fg_color=self.cores.fundo.principal)
        for widget in self.winfo_children():
            widget.destroy()
        self._criar_layout()

    def _criar_layout(self):
        principal = ctk.CTkFrame(self, fg_color=self.cores.fundo.principal)
        principal.pack(fill="both", expand=True, padx=12, pady=12)

        # ═══════════════════════════════════════════════════════════
        # TOPO: STEPPER
        # ═══════════════════════════════════════════════════════════
        frame_stepper = ctk.CTkFrame(
            principal,
            fg_color=self.cores.fundo.branco,
            border_width=2,
            border_color=self.cores.card.borda_card,
            corner_radius=12,
            height=50
        )
        frame_stepper.pack(fill="x", pady=(0, 8))
        frame_stepper.pack_propagate(False)

        self._criar_stepper(frame_stepper)

        # ═══════════════════════════════════════════════════════════
        # CORPO
        # ═══════════════════════════════════════════════════════════
        corpo = ctk.CTkFrame(principal, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.grid_columnconfigure(0, weight=3)
        corpo.grid_columnconfigure(1, weight=2)
        corpo.grid_rowconfigure(0, weight=1)

        # ── COLUNA ESQUERDA: Produtos ────────────────────────────
        frame_produtos = ctk.CTkFrame(
            corpo,
            fg_color=self.cores.fundo.branco,
            border_width=2,
            border_color=self.cores.card.borda_card,
            corner_radius=12
        )
        frame_produtos.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self._criar_area_produtos(frame_produtos)

        # ── COLUNA DIREITA ──────────────────────────────────────
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
        frame_origem.grid(row=0, column=0, sticky="ew", pady=(0, 8))
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
        frame_resumo.grid_rowconfigure(3, weight=1)
        frame_resumo.grid_columnconfigure(0, weight=1)

        self._criar_area_resumo(frame_resumo)

    # ═════════════════════════════════════════════════════════════
    # STEPPER
    # ═════════════════════════════════════════════════════════════
    def _criar_stepper(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(expand=True)

        etapas = [
            {"num": "1", "label": "Itens"},
            {"num": "2", "label": "Pagamento"},
            {"num": "3", "label": "Status"},
        ]

        for i, etapa in enumerate(etapas):
            num_etapa = i + 1

            # Só mostra ✓ se a etapa já foi concluída (etapa < atual)
            if num_etapa < self.etapa_atual:
                texto = "✓"
                cor_circle = self.cores.texto.verde_escuro
                cor_texto = self.cores.texto.branco
            elif num_etapa == self.etapa_atual:
                texto = str(num_etapa)
                cor_circle = self.cores.botao.novo
                cor_texto = self.cores.texto.branco
            else:
                texto = str(num_etapa)
                cor_circle = self.cores.fundo.cinza_claro
                cor_texto = self.cores.texto.passivo

            circle = ctk.CTkLabel(
                container,
                text=texto,
                width=28, height=28,
                corner_radius=14,
                fg_color=cor_circle,
                text_color=cor_texto,
                font=self.fontes.texto_info
            )
            circle.pack(side="left", padx=(0, 4))

            lbl = ctk.CTkLabel(
                container,
                text=etapa["label"],
                font=self.fontes.pequeno,
                text_color=self.cores.texto.principal if num_etapa <= self.etapa_atual else self.cores.texto.passivo
            )
            lbl.pack(side="left", padx=(0, 10))

            if i < len(etapas) - 1:
                ctk.CTkFrame(
                    container,
                    width=50, height=2,
                    fg_color=self.cores.fundo.cinza_claro
                ).pack(side="left", padx=(0, 10))

    # ═════════════════════════════════════════════════════════════
    # ÁREA DE PRODUTOS
    # ═════════════════════════════════════════════════════════════
    def _criar_area_produtos(self, parent):
        ctk.CTkLabel(
            parent,
            text="Produtos",
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=12, pady=(10, 5))

        # ── Busca + Filtros ────────────────────────────────────
        frame_topo = ctk.CTkFrame(parent, fg_color="transparent")
        frame_topo.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkEntry(
            frame_topo,
            placeholder_text="Buscar produtos...",
            height=32,
            corner_radius=8,
            border_width=1,
            border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Filtros de categoria
        frame_filtros = ctk.CTkFrame(frame_topo, fg_color="transparent")
        frame_filtros.pack(side="left")

        categorias = ["Todos", "Comidas Típicas", "Sobremesas", "Bebidas"]
        for cat in categorias:
            cor = self.cores.botao.novo if cat == "Todos" else self.cores.fundo.secundario
            txt_cor = self.cores.texto.branco if cat == "Todos" else self.cores.texto.principal
            ctk.CTkButton(
                frame_filtros,
                text=cat,
                height=26,
                corner_radius=13,
                fg_color=cor,
                hover_color=self.cores.botao.hover,
                text_color=txt_cor,
                font=self.fontes.pequeno,
                width=0
            ).pack(side="left", padx=(0, 3))

        # ── Grid de produtos ────────────────────────────────────
        frame_grid = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.botao.scroll,
            scrollbar_button_hover_color=self.cores.botao.scroll_hover
        )
        frame_grid.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        for col in range(3):
            frame_grid.grid_columnconfigure(col, weight=1)

        for i in range(9):
            row = i % 3
            col = i // 3
            self._criar_card_produto_mock(frame_grid, row, col, i + 1)

    def _criar_card_produto_mock(self, parent, row, col, num):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.cores.fundo.secundario,
            border_width=1,
            border_color=self.cores.card.borda_card,
            corner_radius=10
        )
        card.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

        # Imagem (preenche largura do card)
        ctk.CTkLabel(
            card,
            text="📷",
            font=("Arial", 18),
            fg_color=self.cores.fundo.cinza_clarinho,
            corner_radius=6,
            height=55
        ).pack(fill="x", padx=6, pady=(6, 2))

        # Nome
        ctk.CTkLabel(
            card,
            text=f"Produto {num}",
            font=self.fontes.texto_info,
            text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=6, pady=(0, 0))

        # Descrição (colada no nome)
        ctk.CTkLabel(
            card,
            text="Descrição...",
            font=self.fontes.pequeno,
            text_color=self.cores.texto.passivo
        ).pack(anchor="w", padx=6, pady=(0, 2))

        # Preço + Botão
        frame_preco = ctk.CTkFrame(card, fg_color="transparent")
        frame_preco.pack(fill="x", padx=6, pady=(2, 6))

        ctk.CTkLabel(
            frame_preco,
            text=f"R$ {20 + num},90",
            font=self.fontes.pequeno,
            text_color=self.cores.texto.verde_escuro
        ).pack(side="left")

        ctk.CTkButton(
            frame_preco,
            text="+",
            height=20, width=20,
            corner_radius=5,
            fg_color=self.cores.botao.novo,
            hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco,
            font=self.fontes.pequeno
        ).pack(side="right")

    # ═════════════════════════════════════════════════════════════
    # ÁREA DE ORIGEM
    # ═════════════════════════════════════════════════════════════
    def _criar_area_origem(self, parent):
        ctk.CTkLabel(
            parent,
            text="Origem do Pedido",
            font=self.fontes.texto_info,
            text_color=self.cores.texto.principal
        ).pack(anchor="w", padx=15, pady=(10, 8))

        # Botão segmentado
        frame_segmentado = ctk.CTkFrame(parent, fg_color="transparent")
        frame_segmentado.pack(fill="x", padx=15, pady=(0, 8))

        self.btn_mesa_ref = ctk.CTkButton(
            frame_segmentado,
            text="Mesa",
            height=30,
            corner_radius=8,
            fg_color=self.cores.botao.novo,
            text_color=self.cores.texto.branco,
            font=self.fontes.texto_info,
            command=lambda: self._selecionar_origem("Mesa")
        )
        self.btn_mesa_ref.pack(side="left", fill="x", expand=True, padx=(0, 2))

        self.btn_balcao_ref = ctk.CTkButton(
            frame_segmentado,
            text="Balcão",
            height=30,
            corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            command=lambda: self._selecionar_origem("Balcão")
        )
        self.btn_balcao_ref.pack(side="left", fill="x", expand=True, padx=(2, 0))

        # Nº mesa (escondido por padrão)
        self.frame_numero = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(
            self.frame_numero,
            text="Nº Mesa:",
            font=self.fontes.texto_info,
            text_color=self.cores.texto.principal
        ).pack(side="left", padx=(15, 8))

        self.entry_mesa = ctk.CTkEntry(
            self.frame_numero,
            placeholder_text="0",
            width=60,
            height=28,
            corner_radius=6,
            border_width=1,
            border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal,
            font=self.fontes.texto_entry,
            justify="center"
        )
        self.entry_mesa.pack(side="left")

    def _selecionar_origem(self, origem):
        self.origem_selecionada = origem
        if origem == "Mesa":
            self.btn_mesa_ref.configure(fg_color=self.cores.botao.novo, text_color=self.cores.texto.branco)
            self.btn_balcao_ref.configure(fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal)
            self.frame_numero.pack(fill="x", pady=(0, 8))
        else:
            self.btn_mesa_ref.configure(fg_color=self.cores.fundo.cinza_claro, text_color=self.cores.texto.principal)
            self.btn_balcao_ref.configure(fg_color=self.cores.botao.novo, text_color=self.cores.texto.branco)
            self.frame_numero.pack_forget()

    # ═════════════════════════════════════════════════════════════
    # ÁREA DE RESUMO
    # ═════════════════════════════════════════════════════════════
    def _criar_area_resumo(self, parent):
        parent.grid_rowconfigure(3, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            parent,
            text="Resumo do Pedido",
            font=self.fontes.texto_info,
            text_color=self.cores.texto.principal
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        # Lista de itens (menor)
        frame_lista = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            height=70,
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.botao.scroll,
            scrollbar_button_hover_color=self.cores.botao.scroll_hover
        )
        frame_lista.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 2))

        itens_mock = [
            {"nome": "Tacacá", "preco": 18.00, "qtd": 2},
            {"nome": "Açaí", "preco": 22.50, "qtd": 1},
            {"nome": "Caldinho", "preco": 12.00, "qtd": 3},
        ]
        for item in itens_mock:
            self._criar_item_resumo(frame_lista, item)

        # ── Observações (colada no label) ───────────────────────
        ctk.CTkLabel(
            parent,
            text="Observações (opcional):",
            font=self.fontes.pequeno,
            text_color=self.cores.texto.passivo
        ).grid(row=2, column=0, sticky="w", padx=12, pady=(2, 0))

        self.txt_obs = ctk.CTkTextbox(
            parent,
            corner_radius=6,
            border_width=1,
            border_color=self.cores.card.borda_card,
            fg_color=self.cores.fundo.principal,
            font=self.fontes.texto_entry
        )
        self.txt_obs.grid(row=3, column=0, sticky="nsew", padx=12, pady=(2, 4))

        # ── Bloco de valores + botão (sempre embaixo) ───────────
        frame_bottom = ctk.CTkFrame(parent, fg_color="transparent")
        frame_bottom.grid(row=4, column=0, sticky="sew", padx=8, pady=(0, 8))

        # Valores
        frame_valores = ctk.CTkFrame(
            frame_bottom,
            fg_color=self.cores.fundo.secundario,
            corner_radius=8
        )
        frame_valores.pack(fill="x", pady=(0, 6))

        f1 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f1.pack(fill="x", padx=10, pady=(6, 1))
        ctk.CTkLabel(f1, text="Subtotal:", font=self.fontes.pequeno, text_color=self.cores.texto.passivo).pack(side="left")
        ctk.CTkLabel(f1, text="R$ 80,00", font=self.fontes.pequeno, text_color=self.cores.texto.principal).pack(side="right")

        f2 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f2.pack(fill="x", padx=10, pady=1)
        ctk.CTkLabel(f2, text="Taxa serviço (0%):", font=self.fontes.pequeno, text_color=self.cores.texto.passivo).pack(side="left")
        ctk.CTkLabel(f2, text="R$ 0,00", font=self.fontes.pequeno, text_color=self.cores.texto.principal).pack(side="right")

        ctk.CTkFrame(frame_valores, height=1, fg_color=self.cores.card.borda_card).pack(fill="x", padx=10, pady=(4, 4))

        f3 = ctk.CTkFrame(frame_valores, fg_color="transparent")
        f3.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(f3, text="Total:", font=self.fontes.texto_info, text_color=self.cores.texto.principal).pack(side="left")
        ctk.CTkLabel(f3, text="R$ 80,00", font=self.fontes.texto_info, text_color=self.cores.texto.verde_escuro).pack(side="right")

        # Botão
        ctk.CTkButton(
            frame_bottom,
            text="Ir para Pagamentos  →",
            height=34,
            corner_radius=8,
            fg_color=self.cores.botao.novo,
            hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco,
            font=self.fontes.texto_info
        ).pack(fill="x")

    def _criar_item_resumo(self, parent, item):
        frame_item = ctk.CTkFrame(
            parent,
            fg_color=self.cores.fundo.secundario,
            corner_radius=6,
            border_width=1,
            border_color=self.cores.card.borda_card
        )
        frame_item.pack(fill="x", pady=1)

        # Imagem
        ctk.CTkLabel(
            frame_item, text="📷", font=("Arial", 12),
            width=24, height=24,
            fg_color=self.cores.fundo.cinza_clarinho,
            corner_radius=4
        ).pack(side="left", padx=(4, 4), pady=3)

        # Info
        frame_info = ctk.CTkFrame(frame_item, fg_color="transparent")
        frame_info.pack(side="left", fill="x", expand=True, pady=2)

        # Linha 1: Nome
        ctk.CTkLabel(
            frame_info, text=item["nome"],
            font=self.fontes.pequeno, text_color=self.cores.texto.principal
        ).pack(anchor="w")

        # Linha 2: Preço + anotação juntos
        frame_preco_linha = ctk.CTkFrame(frame_info, fg_color="transparent")
        frame_preco_linha.pack(anchor="w")

        texto_preco = f"R$ {item['preco']:.2f}".replace(".", ",")
        ctk.CTkLabel(
            frame_preco_linha, text=texto_preco,
            font=self.fontes.pequeno, text_color=self.cores.texto.passivo
        ).pack(side="left")

        if item["qtd"] > 1:
            texto_qtd = f"  ({item['qtd']} un)"
            ctk.CTkLabel(
                frame_preco_linha, text=texto_qtd,
                font=("Open Sans", 9), text_color=self.cores.texto.passivo
            ).pack(side="left")

        # Controle quantidade
        frame_qtd = ctk.CTkFrame(frame_item, fg_color=self.cores.fundo.cinza_clarinho, corner_radius=4)
        frame_qtd.pack(side="right", padx=4, pady=3)

        ctk.CTkButton(
            frame_qtd, text="−", width=18, height=18,
            corner_radius=3, fg_color=self.cores.fundo.branco,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno, hover_color=self.cores.botao.hover
        ).pack(side="left", padx=(2, 1), pady=1)

        ctk.CTkLabel(
            frame_qtd, text=str(item["qtd"]), width=14,
            font=self.fontes.pequeno, text_color=self.cores.texto.principal
        ).pack(side="left", padx=1, pady=1)

        ctk.CTkButton(
            frame_qtd, text="+", width=18, height=18,
            corner_radius=3, fg_color=self.cores.fundo.branco,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno, hover_color=self.cores.botao.hover
        ).pack(side="left", padx=(1, 2), pady=1)


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()

    WireframePedido(root)

    root.mainloop()
