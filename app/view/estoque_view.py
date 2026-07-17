import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import Frames, TabelaGenerica, Celulas
from app.controller.estoque_controller import (
    carregar_itens,
    salvar_novo_item,
    salvar_edicao,
    salvar_quantidade,
    excluir_item,
)

class EstoqueView(ctk.CTkToplevel):
    """
    Janela (Toplevel) do módulo de Estoque.
    Responsável apenas por criar a janela e montar a TelaEstoque dentro dela.
    """
    def __init__(self, master):
        super().__init__(master)
        
        def _voltar():
            self.destroy()
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)

        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("estoque", self, _voltar):
            return
        
        self.title("Sabores do Pará")
        self.minsize(600, 600)
        self.after(0, lambda: self.state('zoomed'))
        self.lift()
        self.focus_force()

        self.cores = get_cores()
        fontes = Fontes()
        icones = Icones()

        self.configure(fg_color=self.cores.fundo.principal)

        def voltar_painel():
            self.destroy()
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)  
            
        TelaEstoque(self, self.cores, fontes, icones, on_home=voltar_painel)

        self.protocol("WM_DELETE_WINDOW", voltar_painel)

    def _recarregar_tema(self):
        self.cores = get_cores()
        self.configure(fg_color=self.cores.fundo.principal)
        for widget in self.winfo_children():
            widget.destroy()
        from app.utils.estilos import Fontes, Icones
        fontes = Fontes()
        icones = Icones()

        def voltar_painel():
            self.destroy()
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)

        TelaEstoque(self, self.cores, fontes, icones, on_home=voltar_painel)
        self.protocol("WM_DELETE_WINDOW", voltar_painel)


class TelaEstoque:
    """
    Controla a tela de Estoque: lista de itens (com busca/filtro/ações)
    e o formulário de cadastro/edição de item.
    """

    CATEGORIAS = ["Ingredientes", "Bebidas", "Descartáveis", "Limpeza", "Outros"]
    UNIDADES = ["KG", "UN", "L", "G", "CX", "PCT"]

    def __init__(self, root, cores, fontes, icones, on_home=None):
        self.root = root
        self.cores = cores
        self.fontes = fontes
        self.icones = icones
        self.on_home = on_home
        self._itens = carregar_itens()

        self.layout = Frames.FrameLayoutPadrao(
            root,
            cores,
            fontes,
            icones,
            titulo="Estoque",
            icone=icones.estoque,
            on_novo=self.abrir_novo_item,
            on_home=on_home,
            on_click_titulo=self.voltar_lista,
            menu_callbacks={
                "caixa": self.abrir_caixa,
                "delivery": self.abrir_delivery,
                "clientes": self.abrir_clientes,
                "estoque": self.abrir_estoque,
                "funcionarios": self.abrir_funcionarios,
                "produtos": self.abrir_produtos,
                "relatorios": self.abrir_relatorios,
            }
        )

        self.layout.pack(expand=True, fill="both")

        self.frame_atual = None
        self.construir_lista()

    def trocar_frame(self, funcao_novo_frame):
        if self.frame_atual and self.frame_atual.winfo_exists():
            self.frame_atual.destroy()

        funcao_novo_frame()

    def abrir_novo_item(self):
        self.trocar_frame(lambda: self.construir_formulario())

    def abrir_editar_item(self, item: dict):
        self.trocar_frame(lambda: self.construir_formulario(item=item))

    def voltar_lista(self):
        self.trocar_frame(self.construir_lista)

    # ---------------------------------------------------------
    # Navegação entre módulos do sistema (menu lateral)
    # ---------------------------------------------------------

    def abrir_caixa(self):
        from app.view.caixa_view import CaixaView
        self.root.destroy()
        CaixaView(self.root.master)

    def abrir_clientes(self):
        from app.view.clientes_view import ClientesView
        self.root.destroy()
        ClientesView(self.root.master)

    def abrir_estoque(self):
        self.trocar_frame(self.construir_lista)

    def abrir_funcionarios(self):
        from app.view.funcionarios_view import FuncionariosView
        self.root.destroy()
        FuncionariosView(self.root.master)

    def abrir_produtos(self):
        from app.view.produto_view_novo import ProdutosView
        self.root.destroy()
        ProdutosView(self.root.master)

    def abrir_relatorios(self):
        from app.view.relatorio_view import RelatoriosView
        self.root.destroy()
        RelatoriosView(self.root.master)

    def abrir_delivery(self):
        from app.view.delivery_list_view import DeliveryListView
        self.root.destroy()
        DeliveryListView(self.root.master)

    # ---------------------------------------------------------
    # Tela de listagem (usa TabelaGenerica, igual ao módulo Produtos)
    # ---------------------------------------------------------

    def construir_lista(self):
        self._itens = carregar_itens()

        for item in self._itens:
            qtd = item.get("quantidade", 0) or 0
            qtd_min = item.get("quantidade_minima", 0) or 0
            if qtd == 0:
                item["status"] = "Zerado"
            elif qtd <= qtd_min:
                item["status"] = "Baixo"
            else:
                item["status"] = "OK"

        frame_conteudo = Frames.FrameConteudoTabela(self.layout.area_tela, self.cores)
        frame_conteudo.pack(expand=True, fill="both", padx=30, pady=20)

        self.frame_atual = frame_conteudo

        categorias_existentes = sorted({
            item.get("categoria", "")
            for item in self._itens
            if item.get("categoria")
        })
        unidades_existentes = sorted({
            item.get("unidade", "")
            for item in self._itens
            if item.get("unidade")
        })
        status_existentes = sorted(set(
            item.get("status", "")
            for item in self._itens
        ), reverse=True)

        self.tabela = TabelaGenerica(
            frame_conteudo,
            self.cores,
            self.fontes,
            self.icones,
            placeholder_busca="Itens",
            # Define as colunas da tabela e qual "célula" usar para renderizar cada uma
            colunas=[
                {
                    "titulo": "Item",
                    "campo": "nome",
                    "peso": 3,
                    "min": 200,
                    "limite": 30,
                    "render": Celulas.CelulaNomeDescricao
                },
                {
                    "titulo": "Categoria",
                    "campo": "categoria",
                    "peso": 2,
                    "min": 140,
                    "limite": 18,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Quantidade",
                    "campo": "quantidade",
                    "peso": 2,
                    "min": 140,
                    "render": Celulas.CelulaControleQuantidade
                },
                {
                    "titulo": "Unidade",
                    "campo": "unidade",
                    "peso": 1,
                    "min": 80,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Status",
                    "campo": "quantidade",
                    "limite": 10,
                    "render": Celulas.CelulaStatusEstoque
                },
                {
                    "titulo": "Ações",
                    "campo": "acoes",
                    "limite": 5,
                    "align": "nw",
                    "render": Celulas.CelulaAcoes
                },
            ],
            on_editar=lambda d: self.abrir_editar_item(d),
            on_excluir=lambda id_estoque: self.ao_excluir_id(id_estoque),
            on_alterar_quantidade=self.ao_alterar_quantidade,
            mostrar_busca=True,
            filtros_inline=[
                {
                    "campo": "categoria",
                    "titulo": "Categoria",
                    "opcoes": [{"label": c, "valor": c} for c in categorias_existentes],
                },
                {
                    "campo": "unidade",
                    "titulo": "Unidade",
                    "opcoes": [{"label": u, "valor": u} for u in unidades_existentes],
                },
                {
                    "campo": "status",
                    "titulo": "Status",
                    "opcoes": [{"label": s, "valor": s} for s in status_existentes],
                },
            ],
        )
        self.tabela.pack(expand=True, fill="both", padx=5, pady=10)
        self.tabela.carregar(self._itens)

    # ---------------------------------------------------------
    # Formulário de novo item / edição de item
    # ---------------------------------------------------------

    def construir_formulario(self, item: dict = None):
        conteudo = Frames.FrameConteudo(self.layout.area_tela, self.cores)
        conteudo.pack(expand=True, fill="both", padx=20, pady=20)

        self.frame_atual = conteudo

        cabecalho = ctk.CTkFrame(conteudo, fg_color="transparent")
        cabecalho.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkButton(
            cabecalho,
            text="← Voltar",
            width=90,
            height=30,
            fg_color="transparent",
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.secundario,
            font=ctk.CTkFont(size=12),
            command=self.voltar_lista
        ).pack(side="left")

        ctk.CTkLabel(
            cabecalho,
            text="Novo Item" if item is None else "Editar Item",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.cores.texto.principal
        ).pack(side="left", padx=12)

        body_frame = ctk.CTkFrame(
            conteudo,
            fg_color=self.cores.fundo.branco,
            border_width=2,
            border_color=self.cores.card.borda_card,
            corner_radius=20
        )
        body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        frame_campos = ctk.CTkFrame(body_frame, fg_color="transparent")
        frame_campos.pack(anchor="center", pady=20, padx=40, fill="x")

        esp = {"pady": 6}

        def campo_label(texto):
            ctk.CTkLabel(
                frame_campos,
                text=texto,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.cores.texto.principal
            ).pack(anchor="w", pady=(8, 2))

        def campo_entry(placeholder):
            entrada = ctk.CTkEntry(
                frame_campos,
                placeholder_text=placeholder,
                height=60,
                corner_radius=8,
                fg_color=self.cores.entry.formulario,
                border_width=0,
                text_color=self.cores.texto.principal,
                placeholder_text_color=self.cores.texto.passivo
            )
            entrada.pack(fill="x", **esp)
            return entrada

        campo_label("Nome")
        entrada_nome = campo_entry("Nome do item")

        campo_label("Descrição")
        entrada_descricao = campo_entry("Ex: Lata, 350ml...")

        frame_qtd = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_qtd.pack(fill="x", pady=6)

        frame_qtd.grid_columnconfigure(0, weight=1)
        frame_qtd.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_qtd,
            text="Quantidade",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores.texto.principal
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            frame_qtd,
            text="Quantidade Mínima",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores.texto.principal
        ).grid(row=0, column=1, sticky="w")

        entrada_quantidade = ctk.CTkEntry(
            frame_qtd,
            placeholder_text="0",
            height=60,
            corner_radius=8,
            fg_color=self.cores.entry.formulario,
            border_width=0,
            text_color=self.cores.texto.principal,
            placeholder_text_color=self.cores.texto.passivo
        )
        entrada_quantidade.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)

        entrada_qtd_minima = ctk.CTkEntry(
            frame_qtd,
            placeholder_text="0",
            height=60,
            corner_radius=8,
            fg_color=self.cores.entry.formulario,
            border_width=0,
            text_color=self.cores.texto.principal,
            placeholder_text_color=self.cores.texto.passivo
        )
        entrada_qtd_minima.grid(row=1, column=1, sticky="ew", pady=5)

        frame_un_cat = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_un_cat.pack(fill="x", pady=6)

        frame_un_cat.grid_columnconfigure(0, weight=1)
        frame_un_cat.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_un_cat,
            text="Unidade",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores.texto.principal
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            frame_un_cat,
            text="Categoria",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores.texto.principal
        ).grid(row=0, column=1, sticky="w")

        var_unidade = ctk.StringVar(value=self.UNIDADES[0])

        op_unidade = ctk.CTkOptionMenu(
            frame_un_cat,
            variable=var_unidade,
            values=self.UNIDADES,
            height=60,
            corner_radius=8,
            fg_color=self.cores.entry.formulario,
            button_color=self.cores.entry.formulario,
            button_hover_color=self.cores.entry.formulario,
            text_color=self.cores.texto.passivo,
            dropdown_fg_color=self.cores.fundo.branco
        )
        op_unidade.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)

        var_categoria = ctk.StringVar(value=self.CATEGORIAS[0])

        op_categoria = ctk.CTkOptionMenu(
            frame_un_cat,
            variable=var_categoria,
            values=self.CATEGORIAS,
            height=60,
            corner_radius=8,
            fg_color=self.cores.entry.formulario,
            button_color=self.cores.entry.formulario,
            button_hover_color=self.cores.entry.formulario,
            text_color=self.cores.texto.passivo,
            dropdown_fg_color=self.cores.fundo.branco
        )
        op_categoria.grid(row=1, column=1, sticky="ew", pady=5)

        # =====================================================
        # ALTERAÇÃO FEITA AQUI
        # CAMPO NOVO: CUSTO DO PRODUTO
        # Fica abaixo de Unidade e Categoria
        # =====================================================

        campo_label("Preço Unitário (Custo Produto)")
        entrada_custo_produto = campo_entry("Ex: 25.90")

        if item:
            entrada_nome.insert(0, item.get("nome", ""))
            entrada_descricao.insert(0, item.get("descricao", ""))
            entrada_quantidade.insert(0, str(item.get("quantidade", 0)))
            entrada_qtd_minima.insert(0, str(item.get("quantidade_minima", 0)))
            var_unidade.set(item.get("unidade", self.UNIDADES[0]))
            var_categoria.set(item.get("categoria", self.CATEGORIAS[0]))
            entrada_custo_produto.insert(0, str(item.get("preco_unitario", "")))

        frame_botoes = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_botoes.pack(anchor="w", pady=(20, 0))

        def ao_salvar():
            if item is None:
                novo = salvar_novo_item(
                    entrada_nome.get(),
                    entrada_descricao.get(),
                    entrada_quantidade.get(),
                    var_unidade.get(),
                    var_categoria.get(),
                    entrada_qtd_minima.get(),
                    entrada_custo_produto.get()
                )

                if novo:
                    self.voltar_lista()

            else:
                atualizado = salvar_edicao(
                    item["id_estoque"],
                    entrada_nome.get(),
                    entrada_descricao.get(),
                    entrada_quantidade.get(),
                    var_unidade.get(),
                    var_categoria.get(),
                    entrada_qtd_minima.get(),
                    entrada_custo_produto.get()
                )

                if atualizado:
                    self.voltar_lista()

        ctk.CTkButton(
            frame_botoes,
            text="Salvar",
            width=120,
            height=38,
            fg_color=self.cores.botao.primario,
            hover_color=self.cores.botao.primario_hover,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=ao_salvar
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            width=120,
            height=38,
            fg_color=self.cores.botao.excluir,
            hover_color=self.cores.botao.excluir,
            text_color=self.cores.texto.branco,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.voltar_lista
        ).pack(side="left")

    # ---------------------------------------------------------
    # Ações chamadas pela TabelaGenerica (callbacks)
    # ---------------------------------------------------------

    def ao_alterar_quantidade(self, item: dict, valor: int):
        salvar_quantidade(item["id_estoque"], valor)

    def ao_excluir_id(self, id_estoque):
        item = next((i for i in self._itens if i["id_estoque"] == id_estoque), None)
        if item and excluir_item(item["id_estoque"], item["nome"]):
            self._itens = [i for i in self._itens if i["id_estoque"] != id_estoque]
            self.tabela.carregar(self._itens)

