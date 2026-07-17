import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones


class MenuLateral:

    def __init__(self, root, callbacks=None):
        self.root = root
        self.cores = get_cores()
        self.fontes = Fontes()
        self.icones = Icones()
        self.menu_aberto = False
        self.callbacks = callbacks or {}
        self.criar_menu()

    def criar_menu(self):
        self.menu_lateral = ctk.CTkFrame(
            self.root, width=70, corner_radius=0,
            fg_color=self.cores.fundo.sidebar
        )
        self.menu_lateral.pack_propagate(False)
        self.menu_lateral.pack(side="left", fill="y")

        self.btn_menu = ctk.CTkButton(
            self.menu_lateral, image=self.icones.tela_lateral, text="",
            width=40, height=40, fg_color="transparent",
            text_color=self.cores.texto.principal,
            hover_color=self.cores.botao.hover,
            command=self.toggle_menu
        )
        self.btn_menu.pack(pady=20)

        self.frame_botoes = ctk.CTkFrame(self.menu_lateral, fg_color="transparent")
        self.frame_botoes.pack(fill="both", expand=True, padx=10, pady=10)

        self.criar_botao("Caixa",       self.icones.caixa,       lambda: self.callbacks.get("caixa",       lambda: None)())
        self.criar_botao("Delivery",     self.icones.delivery,     lambda: self.callbacks.get("delivery",     lambda: None)())
        self.criar_botao("Produtos",     self.icones.produtos,     lambda: self.callbacks.get("produtos",     lambda: None)())
        self.criar_botao("Clientes",     self.icones.clientes,     lambda: self.callbacks.get("clientes",     lambda: None)())
        self.criar_botao("Estoque",      self.icones.estoque,      lambda: self.callbacks.get("estoque",      lambda: None)())
        self.criar_botao("Relatórios",   self.icones.relatorios,   lambda: self.callbacks.get("relatorios",   lambda: None)())
        self.criar_botao("Funcionários", self.icones.funcionarios, lambda: self.callbacks.get("funcionarios", lambda: None)())

        self.frame_botoes.pack_forget()

    def criar_botao(self, texto, icone, comando):
        botao = ctk.CTkButton(
            self.frame_botoes, text=texto, image=icone,
            compound="left", anchor="w", height=45, corner_radius=10,
            fg_color=self.cores.botao.primario,
            hover_color=self.cores.botao.primario_hover,
            border_width=1, border_color=self.cores.botao.borda,
            text_color=self.cores.texto.branco,
            font=self.fontes.texto_info,
            command=comando
        )
        botao.pack(fill="x", pady=5)

    def toggle_menu(self):
        if self.menu_aberto:
            self.menu_lateral.configure(width=70)
            self.frame_botoes.pack_forget()
            self.menu_aberto = False
        else:
            self.menu_lateral.configure(width=230)
            self.frame_botoes.pack(fill="both", expand=True, padx=10, pady=10)
            self.menu_aberto = True
