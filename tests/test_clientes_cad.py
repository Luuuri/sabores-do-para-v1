import tkinter as tk
from tkinter import ttk


class TelaClientesCad:
    """
    Tela de Cadastro / Edição de Cliente.
    Fiel ao protótipo do Canva:
      - Layout em duas colunas (dados à esq., pedidos/endereço à dir.)
      - Botão "⊕ Endereço" que expande campos à direita
      - Tabela de pedidos vinculados (modo edição)
      - Título dinâmico: "Novo Cliente" ou "Editar Cliente"

    Callbacks esperados (injetados de fora):
        self.on_salvar(dados: dict)  → recebe dicionário com os dados do form
        self.on_cancelar()           → volta para a lista
    """

    # ──────────────────────────────────────────────────────────
    # PALETA
    # ──────────────────────────────────────────────────────────
    COR_FUNDO      = "#f0f0f0"
    COR_TOPO       = "#d9d9d9"
    COR_CARD       = "#ffffff"
    COR_CAMPO      = "#d4d4d4"
    COR_BTN_SALVAR = "#1a2e2a"
    COR_BTN_CANCEL = "#f48c8c"
    COR_BTN_ENDER  = "#e0e0e0"
    COR_TEXTO      = "#222222"
    COR_LABEL      = "#444444"
    FONTE          = "Segoe UI"

    # largura mínima das duas janelas (normal / endereço expandido)
    GEO_NORMAL  = "1024x680"
    GEO_EXPANDA = "1280x780"

    def __init__(self, root, modo="novo"):
        """
        modo: "novo"  → Novo Cliente
              "editar" → Editar Cliente
        """
        self.root = root
        self.modo = modo
        self.root.title("Point dos Sabores – Clientes")
        self.root.geometry(self.GEO_NORMAL)
        self.root.minsize(900, 600)
        self.root.configure(bg=self.COR_FUNDO)

        self._endereco_visivel = False

        # callbacks – sobrescritos pela lógica
        self.on_salvar   = lambda dados: None
        self.on_cancelar = lambda: None
        self.on_voltar   = lambda: None

        self._construir_ui()

    # ══════════════════════════════════════════════════════════
    # CONSTRUÇÃO DA INTERFACE
    # ══════════════════════════════════════════════════════════

    def _construir_ui(self):
        self._criar_topo()
        self._criar_corpo()

    # ──────────────────────────────────────────────────────────
    # TOPO
    # ──────────────────────────────────────────────────────────
    def _criar_topo(self):
        topo = tk.Frame(self.root, bg=self.COR_TOPO, height=54)
        topo.pack(fill="x", side="top")
        topo.pack_propagate(False)

        tk.Label(topo, text="⌂", bg=self.COR_TOPO, fg="#444",
                 font=(self.FONTE, 18)).pack(side="left", padx=18, pady=10)

        tk.Label(topo, text="Clientes", bg=self.COR_TOPO, fg="#222",
                 font=(self.FONTE, 13, "bold")).pack(side="left")

        tk.Label(topo, text="⚙", bg=self.COR_TOPO, fg="#555",
                 font=(self.FONTE, 16)).pack(side="right", padx=20)

    # ──────────────────────────────────────────────────────────
    # CORPO
    # ──────────────────────────────────────────────────────────
    def _criar_corpo(self):
        corpo = tk.Frame(self.root, bg=self.COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=32, pady=20)

        # ── título da página (seta + texto) ──────────────────
        tit_row = tk.Frame(corpo, bg=self.COR_FUNDO)
        tit_row.pack(fill="x", pady=(0, 18))

        btn_voltar = tk.Label(tit_row, text="←", bg=self.COR_FUNDO, fg="#333",
                              font=(self.FONTE, 20, "bold"), cursor="hand2")
        btn_voltar.pack(side="left")
        btn_voltar.bind("<Button-1>", lambda e: self.on_voltar())

        titulo_texto = "Novo Cliente" if self.modo == "novo" else "Editar Cliente"
        self.lbl_titulo = tk.Label(tit_row, text=titulo_texto, bg=self.COR_FUNDO,
                                   fg=self.COR_TEXTO, font=(self.FONTE, 20, "bold"))
        self.lbl_titulo.pack(side="left", padx=10)

        # ── área em duas colunas ─────────────────────────────
        self.col_frame = tk.Frame(corpo, bg=self.COR_FUNDO)
        self.col_frame.pack(fill="both", expand=True)

        self._criar_coluna_esquerda(self.col_frame)
        self._criar_coluna_direita(self.col_frame)

    # ──────────────────────────────────────────────────────────
    # COLUNA ESQUERDA – campos do cliente
    # ──────────────────────────────────────────────────────────
    def _criar_coluna_esquerda(self, pai):
        esq = tk.Frame(pai, bg=self.COR_FUNDO)
        esq.pack(side="left", fill="y", padx=(0, 32))

        self.ent_nome     = self._campo(esq, "Nome *")
        self.ent_telefone = self._campo(esq, "Telefone *")
        self.ent_cpf      = self._campo(esq, "CPF")
        self.ent_email    = self._campo(esq, "Email")

        # botão Endereço
        self.btn_endereco = tk.Button(
            esq, text="⊕  Endereço",
            bg=self.COR_BTN_ENDER, fg="#1a2e2a",
            font=(self.FONTE, 11, "bold"),
            bd=0, cursor="hand2", relief="flat",
            activebackground="#d0d0d0",
            command=self._alternar_endereco,
            padx=14, pady=8
        )
        self.btn_endereco.pack(anchor="w", pady=(18, 24))

        # botões Salvar / Cancelar
        btn_row = tk.Frame(esq, bg=self.COR_FUNDO)
        btn_row.pack(anchor="w")

        self.btn_salvar = tk.Button(
            btn_row, text="Salvar",
            bg=self.COR_BTN_SALVAR, fg="#ffffff",
            font=(self.FONTE, 11, "bold"),
            bd=0, cursor="hand2", relief="flat",
            activebackground="#2d4a44", activeforeground="#ffffff",
            padx=20, pady=8,
            command=self._acao_salvar
        )
        self.btn_salvar.pack(side="left", padx=(0, 12))

        self.btn_cancelar = tk.Button(
            btn_row, text="Cancelar",
            bg=self.COR_BTN_CANCEL, fg="#ffffff",
            font=(self.FONTE, 11, "bold"),
            bd=0, cursor="hand2", relief="flat",
            activebackground="#d96060", activeforeground="#ffffff",
            padx=20, pady=8,
            command=self._acao_cancelar
        )
        self.btn_cancelar.pack(side="left")

    def _campo(self, pai, texto: str) -> tk.Entry:
        """Cria label + entry e retorna a entry."""
        tk.Label(pai, text=texto, bg=self.COR_FUNDO, fg=self.COR_LABEL,
                 font=(self.FONTE, 11, "bold")).pack(anchor="w", pady=(10, 2))
        ent = tk.Entry(pai, font=(self.FONTE, 12), bg=self.COR_CAMPO,
                       fg=self.COR_TEXTO, relief="flat", bd=0,
                       insertbackground=self.COR_TEXTO, width=32)
        ent.pack(anchor="w", ipady=6, ipadx=8, pady=(0, 2))
        return ent

    # ──────────────────────────────────────────────────────────
    # COLUNA DIREITA – tabela de pedidos  OU  endereço
    # ──────────────────────────────────────────────────────────
    def _criar_coluna_direita(self, pai):
        self.dir_frame = tk.Frame(pai, bg=self.COR_FUNDO)
        self.dir_frame.pack(side="left", fill="both", expand=True)

        self._criar_area_pedidos()

    def _criar_area_pedidos(self):
        """Card com busca + tabela de pedidos vinculados."""
        self.area_pedidos = tk.Frame(self.dir_frame, bg="#dcdcdc", bd=0)
        self.area_pedidos.pack(fill="both", expand=True)

        # barra de busca interna
        busca_row = tk.Frame(self.area_pedidos, bg="#dcdcdc")
        busca_row.pack(fill="x", padx=12, pady=(12, 4))

        tk.Label(busca_row, text="🔍", bg="#dcdcdc", fg="#aaa",
                 font=(self.FONTE, 11)).pack(side="left")
        ent = tk.Entry(busca_row, font=(self.FONTE, 10), bd=0, bg="#f5f5f5",
                       fg="#555", relief="flat", width=22)
        ent.insert(0, " Buscar Pedido...")
        ent.pack(side="left", ipady=4, padx=4)

        tk.Label(busca_row, text="Filtrar", bg="#dcdcdc", fg="#888",
                 font=(self.FONTE, 10)).pack(side="left", padx=8)

        # card branco da tabela
        card = tk.Frame(self.area_pedidos, bg=self.COR_CARD)
        card.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        cols = ("id", "origem", "data", "status", "pagamento")
        self.tabela_pedidos = ttk.Treeview(card, columns=cols, show="headings",
                                           height=8)
        for col, texto, larg in [
            ("id",         "ID",         70),
            ("origem",     "Origem",    110),
            ("data",       "Data",       90),
            ("status",     "Status",    110),
            ("pagamento",  "Pagamento", 110),
        ]:
            self.tabela_pedidos.heading(col, text=texto)
            self.tabela_pedidos.column(col, width=larg, anchor="center")

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview",
                         background=self.COR_CARD, foreground="#333",
                         rowheight=32, fieldbackground=self.COR_CARD,
                         borderwidth=0, font=(self.FONTE, 10))
        estilo.configure("Treeview.Heading",
                         background=self.COR_CARD, foreground="#555",
                         font=(self.FONTE, 10, "bold"), relief="flat")
        estilo.map("Treeview",
                   background=[("selected", "#d9edf7")],
                   foreground=[("selected", "#222")])

        self.tabela_pedidos.pack(fill="both", expand=True)

    def _criar_area_endereco(self):
        """Campos de endereço (expandidos à direita)."""
        self.area_endereco = tk.Frame(self.dir_frame, bg=self.COR_FUNDO)
        self.area_endereco.pack(fill="both", expand=True)

        # grade: Nome(linha inteira), CEP+Nº, Logradouro, Complemento, Bairro+Cidade
        campos_config = [
            # (texto, col, row, columnspan, sticky)
            ("Nome",                   0, 0, 2, "ew"),
            ("CEP",                    0, 1, 1, "ew"),
            ("Número",                 1, 1, 1, "ew"),
            ("Logradouro",             0, 2, 2, "ew"),
            ("Complemento/Referência", 0, 3, 2, "ew"),
            ("Bairro",                 0, 4, 1, "ew"),
            ("Cidade",                 1, 4, 1, "ew"),
        ]

        self.area_endereco.columnconfigure(0, weight=1, minsize=180)
        self.area_endereco.columnconfigure(1, weight=1, minsize=140)

        for texto, col, row, cs, sticky in campos_config:
            lbl = tk.Label(self.area_endereco, text=texto,
                           bg=self.COR_FUNDO, fg=self.COR_LABEL,
                           font=(self.FONTE, 11, "bold"))
            lbl.grid(row=row*2, column=col, columnspan=cs,
                     sticky="w", padx=(0 if col == 0 else 10, 0), pady=(10, 2))

            ent = tk.Entry(self.area_endereco, font=(self.FONTE, 12),
                           bg=self.COR_CAMPO, fg=self.COR_TEXTO,
                           relief="flat", bd=0, insertbackground=self.COR_TEXTO)
            ent.grid(row=row*2+1, column=col, columnspan=cs,
                     sticky="ew", padx=(0 if col == 0 else 10, 0), ipady=6, ipadx=8)

            # guarda referência pelo nome do campo
            attr = "ent_end_" + texto.lower().replace(" ", "_").replace("/", "_")
            setattr(self, attr, ent)

    # ══════════════════════════════════════════════════════════
    # ALTERNAR ENDEREÇO
    # ══════════════════════════════════════════════════════════

    def _alternar_endereco(self):
        if self._endereco_visivel:
            # esconde endereço, mostra pedidos
            self.area_endereco.pack_forget()
            self.area_pedidos.pack(fill="both", expand=True)
            self.root.geometry(self.GEO_NORMAL)
            self._endereco_visivel = False
            self.btn_endereco.config(text="⊕  Endereço")
        else:
            # esconde pedidos, mostra endereço
            self.area_pedidos.pack_forget()
            if not hasattr(self, "area_endereco"):
                self._criar_area_endereco()
            self.area_endereco.pack(fill="both", expand=True)
            self.root.geometry(self.GEO_EXPANDA)
            self._endereco_visivel = True
            self.btn_endereco.config(text="⊖  Endereço")

    # ══════════════════════════════════════════════════════════
    # API PÚBLICA
    # ══════════════════════════════════════════════════════════

    def preencher(self, dados: dict):
        """
        Preenche o formulário com dados existentes (modo edição).
        dados: {"nome", "telefone", "cpf", "email",
                "pedidos": [{"id","origem","data","status","pagamento"}]}
        """
        self.lbl_titulo.config(text="Editar Cliente")
        self.modo = "editar"

        def _set(entry, valor):
            entry.delete(0, tk.END)
            entry.insert(0, valor or "")

        _set(self.ent_nome,     dados.get("nome", ""))
        _set(self.ent_telefone, dados.get("telefone", ""))
        _set(self.ent_cpf,      dados.get("cpf", ""))
        _set(self.ent_email,    dados.get("email", ""))

        for pedido in dados.get("pedidos", []):
            self.tabela_pedidos.insert(
                "", "end",
                values=(pedido["id"], pedido["origem"], pedido["data"],
                        pedido["status"], pedido["pagamento"])
            )

    def obter_dados(self) -> dict:
        """Retorna dicionário com os valores atuais do formulário."""
        dados = {
            "nome":     self.ent_nome.get().strip(),
            "telefone": self.ent_telefone.get().strip(),
            "cpf":      self.ent_cpf.get().strip(),
            "email":    self.ent_email.get().strip(),
        }
        # endereço (se visível)
        if self._endereco_visivel:
            dados["endereco"] = {
                "nome":        getattr(self, "ent_end_nome",        tk.Entry()).get(),
                "cep":         getattr(self, "ent_end_cep",         tk.Entry()).get(),
                "numero":      getattr(self, "ent_end_número",       tk.Entry()).get(),
                "logradouro":  getattr(self, "ent_end_logradouro",  tk.Entry()).get(),
                "complemento": getattr(self, "ent_end_complemento_referência", tk.Entry()).get(),
                "bairro":      getattr(self, "ent_end_bairro",      tk.Entry()).get(),
                "cidade":      getattr(self, "ent_end_cidade",      tk.Entry()).get(),
            }
        return dados

    # ══════════════════════════════════════════════════════════
    # AÇÕES
    # ══════════════════════════════════════════════════════════

    def _acao_salvar(self):
        dados = self.obter_dados()
        if not dados["nome"]:
            import tkinter.messagebox as mb
            mb.showwarning("Aviso", "O campo Nome é obrigatório!")
            return
        self.on_salvar(dados)

    def _acao_cancelar(self):
        self.on_cancelar()


# ══════════════════════════════════════════════════════════════
# EXECUÇÃO STANDALONE (teste visual)
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = TelaClientesCad(root, modo="editar")

    # simula dados de um cliente existente
    app.preencher({
        "nome":     "Débora Diniz",
        "telefone": "(93) 9 9152-9220",
        "cpf":      "",
        "email":    "",
        "pedidos":  [
            {"id": "#004", "origem": "Mesa 2", "data": "04/04/26",
             "status": "Entregue", "pagamento": "Pago"}
        ]
    })

    root.mainloop()