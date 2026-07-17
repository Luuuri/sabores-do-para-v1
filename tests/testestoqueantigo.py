import customtkinter as ctk
from app.utils.estilos import Cores, Fontes, Icones
from app.utils.componentes import Frames, Barras, Botoes
from app.controller.estoque_controller import (
    carregar_itens,
    salvar_novo_item,
    salvar_edicao,
    salvar_quantidade,
    excluir_item,
)


class EstoqueView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        # Configurações básicas da janela
        self.title("Sabores do Pará")
        self.minsize(600, 600)
        self.after(0, lambda: self.state('zoomed'))  # maximiza após a janela estar pronta
        self.lift()
        self.focus_force()

        # Instancia utilitários de estilo
        cores  = Cores()
        fontes = Fontes()
        icones = Icones()

        self.configure(fg_color=cores.fundo.principal)

        def voltar_painel():
            # Fecha o estoque e reabre o painel, mantendo o mesmo root invisível
            self.destroy()
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)

        # Monta o conteúdo da tela dentro desta janela
        TelaEstoque(self, cores, fontes, icones, on_home=voltar_painel)

        # Garante que fechar pelo X também volta ao painel (não encerra o app)
        self.protocol("WM_DELETE_WINDOW", voltar_painel)


# ── Helpers 

def status_da_quantidade(quantidade: int) -> str:
    # Classifica o nível de estoque de um item baseado na quantidade
    if quantidade == 0:
        return "Zerado"
    elif quantidade <= 5:
        return "Baixo"
    return "OK"


# ── Componentes visuais reutilizáveis 

class BadgeStatus(ctk.CTkFrame):
    def __init__(self, master, status: str, cores, **kwargs):
        # Mapeamento de status para cores de fundo e borda
        CORES_STATUS = {
            "OK":     (cores.texto.ok,     "#27ae60"),
            "Baixo":  (cores.texto.baixo,  "#e67e22"),
            "Zerado": (cores.texto.zerado, "#c0392b"),
        }
        cor = CORES_STATUS.get(status, ("#95a5a6", "#7f8c8d"))
        super().__init__(master, fg_color=cor[0], corner_radius=12,
                         width=70, height=26, **kwargs)
        self.grid_propagate(False)  # impede o frame de encolher para o conteúdo
        ctk.CTkLabel(self, text=status, text_color="white",
                     font=ctk.CTkFont(size=12, weight="bold")).place(
            relx=0.5, rely=0.5, anchor="center")


class ControleQuantidade(ctk.CTkFrame):
    def __init__(self, master, valor_inicial: int, ao_alterar=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.valor      = valor_inicial
        self.ao_alterar = ao_alterar  # callback chamado ao mudar o valor

        # Botão de decremento (vermelho)
        ctk.CTkButton(self, text="−", width=26, height=26, corner_radius=13,
                      fg_color="#e74c3c", hover_color="#c0392b",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.decrementar).grid(row=0, column=0, padx=(0, 4))

        # Rótulo central que exibe o valor atual
        self.rotulo = ctk.CTkLabel(self, text=str(self.valor),
                                   font=ctk.CTkFont(size=13, weight="bold"),
                                   width=30, anchor="center")
        self.rotulo.grid(row=0, column=1)

        # Botão de incremento (verde)
        ctk.CTkButton(self, text="+", width=26, height=26, corner_radius=13,
                      fg_color="#2ecc71", hover_color="#27ae60",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.incrementar).grid(row=0, column=2, padx=(4, 0))

    def incrementar(self):
        self.valor += 1
        self.rotulo.configure(text=str(self.valor))
        if self.ao_alterar:
            self.ao_alterar(self.valor)  # notifica quem criou o controle

    def decrementar(self):
        if self.valor > 0:  # não permite valor negativo
            self.valor -= 1
            self.rotulo.configure(text=str(self.valor))
            if self.ao_alterar:
                self.ao_alterar(self.valor)  # notifica quem criou o controle


# ── Tela de Estoque ───────────────────────────────────────────────────────────

class TelaEstoque:

    CATEGORIAS = ["Ingredientes", "Bebidas", "Descartáveis", "Limpeza", "Outros"]
    UNIDADES   = ["KG", "UN", "L", "G", "CX", "PCT"]

    def __init__(self, root, cores, fontes, icones, on_home=None):
        self.root    = root
        self.cores   = cores
        self.fontes  = fontes
        self.icones  = icones
        self.on_home = on_home             # callback para voltar ao painel
        self._itens  = carregar_itens()    # carrega itens do banco ao iniciar
        self.filtros_ativos = {}           # dicionário de filtros aplicados no momento

        # Layout padrão com cabeçalho, botão home e botão novo
        self.layout = Frames.FrameLayoutPadrao(
            root,
            cores,
            fontes,
            icones,

            titulo="Estoque",
            icone=icones.estoque,

            on_novo=self.abrir_novo_item,
            on_home=on_home,

            menu_callbacks={
                "clientes": self.abrir_clientes,
                "estoque": self.abrir_estoque,
                "funcionarios": self.abrir_funcionarios,
                "produtos": self.abrir_produtos,
                "relatorios": self.abrir_relatorios,
            }
        )
        self.layout.pack(expand=True, fill="both")

        self.frame_atual = None  # referência ao frame de conteúdo ativo (lista ou formulário)
        self.construir_lista()   # começa exibindo a lista

    def aplicar_filtro(self, tipo, valor):
        # Limpa todos os filtros se tipo for None, senão aplica o filtro recebido
        if tipo is None:
            self.filtros_ativos.clear()
        else:
            self.filtros_ativos[tipo] = valor
        self.renderizar_linhas()

    def trocar_frame(self, funcao_novo_frame):
        # Destrói o frame atual (lista ou formulário) antes de construir o próximo
        if self.frame_atual and self.frame_atual.winfo_exists():
            self.frame_atual.destroy()
        funcao_novo_frame()

    def abrir_novo_item(self):
        self.trocar_frame(lambda: self.construir_formulario())

    def abrir_editar_item(self, item: dict):
        # Passa os dados do item para preencher o formulário em modo edição
        self.trocar_frame(lambda: self.construir_formulario(item=item))

    def voltar_lista(self):
        self.trocar_frame(self.construir_lista)

    def abrir_clientes(self):
        from app.view.clientes_view import ClientesView
        self.root.destroy()
        ClientesView(self.root.master)

    def abrir_estoque(self):
        self._itens = carregar_itens()
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

    def construir_lista(self):
        # Recarrega os itens do banco antes de exibir (garante dados atualizados)
        self._itens = carregar_itens()

        conteudo = Frames.FrameConteudo(self.layout.area_tela, self.cores)
        conteudo.pack(expand=True, fill="both", padx=20, pady=20)
        self.frame_atual = conteudo

        # Topo da lista: barra de busca + botão de filtro
        topo = ctk.CTkFrame(conteudo, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 8))

        self.header_busca = Barras.HeaderBusca(
            topo, self.cores, self.fontes, self.icones,
            placeholder="Itens",
            search_callback=lambda termo: self.renderizar_linhas()
        )
        self.header_busca.pack(side="left", fill="x", expand=True)

        # Coleta categorias únicas dos itens para popular o menu de filtro
        categorias_existentes = sorted({
            item.get("categoria", "")
            for item in self._itens
            if item.get("categoria")
        })

        self.botao_filtro = Botoes.BotaoFunil(
            topo, self.icones, self.cores, self.fontes,
            filtros=[
                *[(f"Categoria: {c}", "categoria", c) for c in categorias_existentes],
                ("Status: OK",     "status", "OK"),
                ("Status: Baixo",  "status", "Baixo"),
                ("Status: Zerado", "status", "Zerado"),
            ],
            on_filtrar=self.aplicar_filtro
        )
        self.botao_filtro.pack(side="left", padx=(5, 1000))

        # Tabela com scroll — cada coluna tem peso proporcional
        self.frame_tabela = ctk.CTkScrollableFrame(conteudo, fg_color="white", corner_radius=12)
        self.frame_tabela.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        for coluna, peso in enumerate([3, 2, 2, 1, 2, 1]):
            self.frame_tabela.columnconfigure(coluna, weight=peso)

        self.construir_cabecalho_tabela()
        self.renderizar_linhas()

    def construir_cabecalho_tabela(self):
        f = self.frame_tabela
        opcoes = dict(font=ctk.CTkFont(size=12, weight="bold"), text_color="#888", anchor="w")
        colunas = ["Item ▾", "Categoria ▾", "Quantidade ▾", "Unidade ▾", "Status ▾", "Ações"]

        # Cria os rótulos do cabeçalho na linha 0
        for col, texto in enumerate(colunas):
            ctk.CTkLabel(f, text=texto, **opcoes).grid(
                row=0, column=col, sticky="w",
                padx=(16, 8) if col == 0 else 8, pady=(12, 4))

        # Linha separadora abaixo do cabeçalho
        ctk.CTkFrame(f, fg_color="#e8e8e8", height=1).grid(
            row=1, column=0, columnspan=6, sticky="ew", padx=8)

    def renderizar_linhas(self):
        f = self.frame_tabela

        # Remove apenas as linhas de dados (row >= 2), preservando o cabeçalho
        for widget in f.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) >= 2:
                widget.destroy()

        # Aplica filtro de busca por texto (nome ou categoria)
        busca = self.header_busca.busca.get().lower().strip()
        filtrados = [
            item for item in self._itens
            if busca in item["nome"].lower() or busca in item.get("categoria", "").lower()
        ] if busca else list(self._itens)

        # Aplica filtros de categoria e status selecionados no funil
        for tipo, valor in self.filtros_ativos.items():
            if tipo == "categoria":
                filtrados = [i for i in filtrados if i.get("categoria") == valor]
            elif tipo == "status":
                filtrados = [i for i in filtrados if status_da_quantidade(i["quantidade"]) == valor]

        # Renderiza cada item em uma linha da tabela (linha par = dados, linha ímpar = separador)
        for indice, item in enumerate(filtrados):
            linha = indice * 2 + 2  # começa na row 2, pulando o cabeçalho

            # Coluna 0: nome + descrição empilhados verticalmente
            frame_nome = ctk.CTkFrame(f, fg_color="transparent")
            ctk.CTkLabel(frame_nome, text=item["nome"],
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#1a1a1a", anchor="w").pack(anchor="w")
            if item.get("descricao"):
                ctk.CTkLabel(frame_nome, text=item["descricao"],
                             font=ctk.CTkFont(size=11), text_color="#999",
                             anchor="w").pack(anchor="w")
            frame_nome.grid(row=linha, column=0, sticky="w", padx=(16, 8), pady=10)

            # Coluna 1: categoria
            ctk.CTkLabel(f, text=item.get("categoria", ""),
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#1a1a1a").grid(row=linha, column=1, sticky="w", padx=8, pady=10)

            # Coluna 2: controle de quantidade com botões + e −
            ControleQuantidade(f, item["quantidade"],
                ao_alterar=lambda v, i=item: self.ao_alterar_quantidade(i, v)
            ).grid(row=linha, column=2, sticky="w", padx=8, pady=10)

            # Coluna 3: unidade de medida
            ctk.CTkLabel(f, text=item["unidade"],
                         font=ctk.CTkFont(size=13), text_color="#555").grid(
                row=linha, column=3, sticky="w", padx=8, pady=10)

            # Coluna 4: badge colorido com o status calculado
            BadgeStatus(f, status_da_quantidade(item["quantidade"]), self.cores).grid(
                row=linha, column=4, sticky="w", padx=8, pady=10)

            # Coluna 5: botões de editar e apagar
            frame_acoes = ctk.CTkFrame(f, fg_color="transparent")
            Botoes.BotaoEditar(frame_acoes, self.cores, self.icones,
                               command=lambda i=item: self.abrir_editar_item(i)).pack(side="left")
            Botoes.BotaoApagar(frame_acoes, self.cores, self.icones,
                               command=lambda i=item: self.ao_excluir(i)).pack(side="left")
            frame_acoes.grid(row=linha, column=5, sticky="w", padx=8, pady=10)

            # Linha separadora fina entre os itens
            ctk.CTkFrame(f, fg_color="#eeeeee", height=1).grid(
                row=linha + 1, column=0, columnspan=6, sticky="ew", padx=8)

    def construir_formulario(self, item: dict = None):
        conteudo = Frames.FrameConteudo(self.layout.area_tela, self.cores)
        conteudo.pack(expand=True, fill="both", padx=20, pady=20)
        self.frame_atual = conteudo

        cabecalho = ctk.CTkFrame(conteudo, fg_color="transparent")
        cabecalho.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkButton(cabecalho, text="← Voltar", width=90, height=30,
                    fg_color="transparent", hover_color="#e0e0e0",
                    text_color="#555", font=ctk.CTkFont(size=12),
                    command=self.voltar_lista).pack(side="left")

        ctk.CTkLabel(cabecalho,
                    text="Novo Item" if item is None else "Editar Item",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color="#1a1a1a").pack(side="left", padx=12)

        body_frame = ctk.CTkFrame(conteudo,
                                fg_color=self.cores.fundo.branco,
                                border_width=2,
                                border_color=self.cores.card.borda_card,
                                corner_radius=20)
        body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        frame_campos = ctk.CTkFrame(body_frame, fg_color="transparent")
        frame_campos.pack(anchor="center", pady=20, padx=40, fill="x")

        esp = {"pady": 6}

        def campo_label(texto):
            ctk.CTkLabel(frame_campos, text=texto,
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=self.cores.texto.principal).pack(anchor="w", pady=(8, 2))

        def campo_entry(placeholder):
            e = ctk.CTkEntry(frame_campos, placeholder_text=placeholder,
                            height=60, corner_radius=8,
                            fg_color=self.cores.entry.formulario,
                            border_width=0,
                            text_color=self.cores.texto.principal,
                            placeholder_text_color=self.cores.texto.passivo)
            e.pack(fill="x", **esp)
            return e

        def campo_opcao(valores):
            o = ctk.CTkOptionMenu(frame_campos, values=valores,
                                height=60, corner_radius=8,
                                fg_color=self.cores.entry.formulario,
                                button_color=self.cores.entry.formulario,
                                button_hover_color=self.cores.entry.formulario,
                                text_color=self.cores.texto.passivo,
                                dropdown_fg_color=self.cores.fundo.branco,
                                dropdown_hover_color=self.cores.fundo.cinza_muito_claro)
            o.pack(fill="x", **esp)
            return o

        campo_label("Nome")
        entrada_nome = campo_entry("Nome do item")

        campo_label("Descrição")
        entrada_descricao = campo_entry("Ex: Lata, 350ml...")

        # Quantidade e Quantidade Mínima lado a lado
        frame_qtd = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_qtd.pack(fill="x", pady=6)
        frame_qtd.grid_columnconfigure(0, weight=1)
        frame_qtd.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_qtd, text="Quantidade",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.cores.texto.principal).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ctk.CTkLabel(frame_qtd, text="Quantidade Mínima",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.cores.texto.principal).grid(row=0, column=1, sticky="w")

        entrada_quantidade = ctk.CTkEntry(frame_qtd, placeholder_text="0",
                                        height=60, corner_radius=8,
                                        fg_color=self.cores.entry.formulario,
                                        border_width=0,
                                        text_color=self.cores.texto.principal,
                                        placeholder_text_color=self.cores.texto.passivo)
        entrada_quantidade.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)

        entrada_qtd_minima = ctk.CTkEntry(frame_qtd, placeholder_text="0",
                                        height=60, corner_radius=8,
                                        fg_color=self.cores.entry.formulario,
                                        border_width=0,
                                        text_color=self.cores.texto.principal,
                                        placeholder_text_color=self.cores.texto.passivo)
        entrada_qtd_minima.grid(row=1, column=1, sticky="ew", pady=5)

        # Unidade e Categoria lado a lado
        frame_un_cat = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_un_cat.pack(fill="x", pady=6)
        frame_un_cat.grid_columnconfigure(0, weight=1)
        frame_un_cat.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_un_cat, text="Unidade",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.cores.texto.principal).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ctk.CTkLabel(frame_un_cat, text="Categoria",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.cores.texto.principal).grid(row=0, column=1, sticky="w")

        var_unidade = ctk.StringVar(value=self.UNIDADES[0])
        op_unidade = ctk.CTkOptionMenu(frame_un_cat, variable=var_unidade, values=self.UNIDADES,
                                        height=60, corner_radius=8,
                                        fg_color=self.cores.entry.formulario,
                                        button_color=self.cores.entry.formulario,
                                        button_hover_color=self.cores.entry.formulario,
                                        text_color=self.cores.texto.passivo,
                                        dropdown_fg_color=self.cores.fundo.branco)
        op_unidade.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)

        var_categoria = ctk.StringVar(value=self.CATEGORIAS[0])
        op_categoria = ctk.CTkOptionMenu(frame_un_cat, variable=var_categoria, values=self.CATEGORIAS,
                                        height=60, corner_radius=8,
                                        fg_color=self.cores.entry.formulario,
                                        button_color=self.cores.entry.formulario,
                                        button_hover_color=self.cores.entry.formulario,
                                        text_color=self.cores.texto.passivo,
                                        dropdown_fg_color=self.cores.fundo.branco)
        op_categoria.grid(row=1, column=1, sticky="ew", pady=5)

        if item:
            entrada_nome.insert(0, item.get("nome", ""))
            entrada_descricao.insert(0, item.get("descricao", ""))
            entrada_quantidade.insert(0, str(item.get("quantidade", 0)))
            entrada_qtd_minima.insert(0, str(item.get("quantidade_minima", 0)))
            var_unidade.set(item.get("unidade", self.UNIDADES[0]))
            var_categoria.set(item.get("categoria", self.CATEGORIAS[0]))

        frame_botoes = ctk.CTkFrame(frame_campos, fg_color="transparent")
        frame_botoes.pack(anchor="w", pady=(20, 0))

        def ao_salvar():
            if item is None:
                novo = salvar_novo_item(entrada_nome.get(), entrada_descricao.get(),
                                        entrada_quantidade.get(), var_unidade.get(),
                                        var_categoria.get(), entrada_qtd_minima.get())
                if novo:
                    self.voltar_lista()
            else:
                atualizado = salvar_edicao(item["id_estoque"], entrada_nome.get(),
                                        entrada_descricao.get(), entrada_quantidade.get(),
                                        var_unidade.get(), var_categoria.get(),
                                        entrada_qtd_minima.get())
                if atualizado:
                    self.voltar_lista()

        ctk.CTkButton(frame_botoes, text="Salvar", width=120, height=38,
                    fg_color="#1a1a1a", hover_color="#333",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    command=ao_salvar).pack(side="left", padx=(0, 12))

        ctk.CTkButton(frame_botoes, text="Cancelar", width=120, height=38,
                    fg_color="#e74c3c", hover_color="#c0392b", text_color="white",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    command=self.voltar_lista).pack(side="left")

    def ao_alterar_quantidade(self, item: dict, valor: int):
        # Atualiza o valor no dicionário local e persiste no banco imediatamente
        item["quantidade"] = valor
        salvar_quantidade(item["id_estoque"], valor)
        self.renderizar_linhas()  # re-renderiza para atualizar o badge de status

    def ao_excluir(self, item: dict):
        # Remove o item do banco; se bem-sucedido, remove da lista local e re-renderiza
        if excluir_item(item["id_estoque"], item["nome"]):
            self._itens = [i for i in self._itens if i["id_estoque"] != item["id_estoque"]]
            self.renderizar_linhas()