# =========================================================
# IMPORTAÇÕES
# =========================================================

import os
import sys
import customtkinter as ctk
from tkinter import messagebox
from app.utils.usuario_atual import usuario_atual

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.utils.estilos import Cores, Icones, Fontes
from app.utils.componentes import DialogoConfirmacao


# =========================================================
# CLASSE MODELO PRODUTO
# =========================================================

class Produto:

    def __init__(self, nome, descricao, categoria, preco, status="Ativo"):

        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.preco = preco
        self.status = status


# =========================================================
# CLASSE PRINCIPAL
# =========================================================

class TelaProdutos:

    def __init__(self):

        ctk.set_appearance_mode("light")

        self.root = ctk.CTk()

        self.cores = Cores()
        self.fontes = Fontes()
        self.icones = Icones()

        # =================================================
        # CORES PADRÃO DA TELA RELATÓRIOS
        # =================================================

        self.cor_fundo = "#F5EFE6"
        self.cor_card = "#FDFAF6"
        self.cor_secundaria = "#E8DDD0"
        self.cor_vermelho = "#C0392B"
        self.cor_vermelho_hover = "#A93226"
        self.cor_texto = "#1C2526"
        self.cor_texto_suave = "#7A6A5A"
        self.cor_borda = "#D4A97A"

        self.root.title("Produtos")
        self.root.after(0, lambda: self.root.state('zoomed'))
        self.root.minsize(1100, 700)
        self.root.configure(fg_color=self.cor_fundo)

        self.produtos = []

        self.menu_aberto = False

        self.criar_topo()
        self.criar_menu_lateral()
        self.criar_area_conteudo()
        self.criar_tabela_visual()

        self.carregar_produtos_exemplo()

        self.root.mainloop()

    # =====================================================
    # TOPO
    # =====================================================

    def criar_topo(self):

        self.topo = ctk.CTkFrame(
            self.root,
            fg_color=self.cor_fundo,
            corner_radius=0
        )

        self.topo.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=0.08
        )

        self.lbl_home = ctk.CTkLabel(
            self.topo,
            text="",
            image=self.icones.home
        )

        self.lbl_home.pack(
            side="left",
            padx=20
        )

        self.lbl_titulo = ctk.CTkLabel(
            self.topo,
            text="Produtos",
            text_color=self.cor_texto,
            font=self.fontes.titulo
        )

        self.lbl_titulo.pack(side="left")

        self.btn_novo = ctk.CTkButton(
            self.topo,
            text="+ Novo Produto",
            fg_color=self.cor_vermelho,
            hover_color=self.cor_vermelho_hover,
            text_color="white",
            font=self.fontes.texto_info,
            corner_radius=8,
            command=self.abrir_formulario_novo
        )

        self.btn_novo.pack(
            side="right",
            padx=20
        )

        self.lbl_config = ctk.CTkLabel(
            self.topo,
            text="",
            image=self.icones.config
        )

        self.lbl_config.pack(
            side="right",
            padx=10
        )

    # =====================================================
    # MENU LATERAL
    # =====================================================

    def criar_menu_lateral(self):

        self.menu_lateral = ctk.CTkFrame(
            self.root,
            fg_color=self.cor_fundo,
            corner_radius=0,
            width=70
        )

        self.menu_lateral.place(
            relx=0,
            rely=0.08,
            relheight=0.92
        )

        self.btn_menu = ctk.CTkButton(
            self.menu_lateral,
            text="☰",
            width=40,
            height=40,
            font=("Arial", 22, "bold"),
            fg_color="transparent",
            text_color=self.cor_texto,
            hover_color=self.cor_secundaria,
            command=self.toggle_menu
        )

        self.btn_menu.pack(pady=20)

        self.frame_botoes_menu = ctk.CTkFrame(
            self.menu_lateral,
            fg_color="transparent"
        )

        self.frame_botoes_menu.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.criar_botao_menu("Caixa", self.abrir_tela_caixa)
        self.criar_botao_menu("On-line", self.abrir_tela_online)
        self.criar_botao_menu("Produtos", self.abrir_tela_produtos)
        self.criar_botao_menu("Clientes", self.abrir_tela_clientes)
        self.criar_botao_menu("Estoque", self.abrir_tela_estoque)
        self.criar_botao_menu("Relatórios", self.abrir_tela_relatorios)
        self.criar_botao_menu("Funcionários", self.abrir_tela_funcionarios)

        self.frame_botoes_menu.pack_forget()

    # =====================================================
    # BOTÃO MENU
    # =====================================================

    def criar_botao_menu(self, texto, comando):

        botao = ctk.CTkButton(
            self.frame_botoes_menu,
            text=texto,
            height=40,
            corner_radius=8,
            anchor="w",
            fg_color=self.cor_card,
            hover_color=self.cor_vermelho,
            text_color=self.cor_texto,
            command=comando
        )

        botao.pack(
            fill="x",
            pady=5
        )

    # =====================================================
    # ABRIR E FECHAR MENU
    # =====================================================

    def toggle_menu(self):

        if self.menu_aberto:

            self.menu_lateral.configure(width=70)
            self.frame_botoes_menu.pack_forget()
            self.menu_aberto = False

        else:

            self.menu_lateral.configure(width=220)

            self.frame_botoes_menu.pack(
                fill="both",
                expand=True,
                padx=10,
                pady=10
            )

            self.menu_aberto = True

    # =====================================================
    # NAVEGAÇÃO ENTRE TELAS
    # =====================================================

    def abrir_tela_caixa(self):

        self.root.destroy()

        from app.view.telacaixa import TelaCaixa

        TelaCaixa()

    def abrir_tela_online(self):

        self.root.destroy()

        from app.view.telaonline import TelaOnline

        TelaOnline()

    def abrir_tela_produtos(self):

        self.toggle_menu()

    def abrir_tela_clientes(self):

        self.root.destroy()

        from app.view.telaclienteteste import TelaClientes

        TelaClientes()

    def abrir_tela_estoque(self):

        self.root.destroy()

        from app.view.telaestoque import TelaEstoque

        TelaEstoque()

    def abrir_tela_relatorios(self):

        self.root.destroy()

        from app.view.telarelatorios import TelaRelatorios

        TelaRelatorios()

    def abrir_tela_funcionarios(self):
        # Só administradores podem acessar a tela completa de funcionários.
        nivel = usuario_atual.get("nivel_acesso", "")
        if nivel != "administrador":
            messagebox.showinfo("Acesso Negado",
                                "Acesso restrito: apenas administradores podem abrir a tela de funcionários.\nFuncionários devem editar seu perfil via 'Editar perfil' no menu de configurações.")
            return

        self.root.destroy()

        from app.view.telafuncionarios import TelaFuncionarios

        TelaFuncionarios()

    # =====================================================
    # ÁREA CONTEÚDO
    # =====================================================

    def criar_area_conteudo(self):

        self.area = ctk.CTkFrame(
            self.root,
            fg_color=self.cor_card,
            corner_radius=12
        )

        self.area.place(
            relx=0.12,
            rely=0.16,
            relwidth=0.78,
            relheight=0.68
        )

        self.entrada_busca = ctk.CTkEntry(
            self.area,
            placeholder_text="Buscar produto...",
            font=self.fontes.texto_entry,
            fg_color=self.cor_secundaria,
            text_color=self.cor_texto,
            placeholder_text_color=self.cor_texto_suave,
            border_color=self.cor_borda,
            border_width=1,
            corner_radius=8
        )

        self.entrada_busca.place(
            relx=0.03,
            rely=0.04,
            relwidth=0.25,
            relheight=0.06
        )

        self.lbl_lupa = ctk.CTkLabel(
            self.area,
            text="",
            image=self.icones.lupa
        )

        self.lbl_lupa.place(
            relx=0.30,
            rely=0.045
        )

        self.lbl_filtro = ctk.CTkLabel(
            self.area,
            text="",
            image=self.icones.funil
        )

        self.lbl_filtro.place(
            relx=0.34,
            rely=0.045
        )

    # =====================================================
    # TABELA
    # =====================================================

    def criar_tabela_visual(self):

        self.frame_tabela = ctk.CTkFrame(
            self.area,
            fg_color=self.cor_secundaria,
            corner_radius=10
        )

        self.frame_tabela.place(
            relx=0.03,
            rely=0.14,
            relwidth=0.94,
            relheight=0.80
        )

        self.criar_cabecalho_tabela()

    # =====================================================
    # CABEÇALHO
    # =====================================================

    def criar_cabecalho_tabela(self):

        cabecalhos = [
            "Nome",
            "Categoria",
            "Preço",
            "Status",
            "Ações"
        ]

        for coluna, texto in enumerate(cabecalhos):

            label = ctk.CTkLabel(
                self.frame_tabela,
                text=texto,
                text_color=self.cor_texto,
                font=self.fontes.texto_info
            )

            label.grid(
                row=0,
                column=coluna,
                padx=10,
                pady=10,
                sticky="w"
            )

        for coluna in range(5):

            self.frame_tabela.grid_columnconfigure(
                coluna,
                weight=1
            )

    # =====================================================
    # ATUALIZAR TABELA
    # =====================================================

    def atualizar_tabela(self):

        for widget in self.frame_tabela.winfo_children():
            widget.destroy()

        self.criar_cabecalho_tabela()

        for linha, produto in enumerate(self.produtos, start=1):

            frame_nome = ctk.CTkFrame(
                self.frame_tabela,
                fg_color="transparent"
            )

            frame_nome.grid(
                row=linha,
                column=0,
                padx=10,
                pady=8,
                sticky="w"
            )

            label_nome = ctk.CTkLabel(
                frame_nome,
                text=produto.nome,
                text_color=self.cor_texto,
                font=self.fontes.texto_info
            )

            label_nome.pack(anchor="w")

            label_descricao = ctk.CTkLabel(
                frame_nome,
                text=produto.descricao,
                text_color=self.cor_texto_suave,
                font=self.fontes.pequeno
            )

            label_descricao.pack(anchor="w")

            dados = [
                produto.categoria,
                f"R$ {produto.preco}"
            ]

            for coluna, valor in enumerate(dados, start=1):

                label = ctk.CTkLabel(
                    self.frame_tabela,
                    text=valor,
                    text_color=self.cor_texto_suave,
                    font=self.fontes.pequeno
                )

                label.grid(
                    row=linha,
                    column=coluna,
                    padx=10,
                    pady=8,
                    sticky="w"
                )

            if produto.status == "Ativo":
                cor_status = self.cor_vermelho
            else:
                cor_status = self.cor_texto_suave

            btn_status = ctk.CTkButton(
                self.frame_tabela,
                text=produto.status,
                fg_color=cor_status,
                hover_color=self.cor_vermelho_hover,
                text_color="white",
                width=70,
                height=28
            )

            btn_status.grid(
                row=linha,
                column=3,
                padx=10,
                pady=8,
                sticky="w"
            )

            frame_acoes = ctk.CTkFrame(
                self.frame_tabela,
                fg_color="transparent"
            )

            frame_acoes.grid(
                row=linha,
                column=4,
                padx=5,
                pady=8,
                sticky="w"
            )

            btn_editar = ctk.CTkButton(
                frame_acoes,
                text="Editar",
                fg_color=self.cor_card,
                hover_color=self.cor_vermelho,
                text_color=self.cor_texto,
                border_width=1,
                border_color=self.cor_borda,
                width=70,
                height=28,
                command=lambda p=produto: self.editar_produto(p)
            )

            btn_editar.pack(
                side="left",
                padx=(0, 5)
            )

            btn_apagar = ctk.CTkButton(
                frame_acoes,
                text="Apagar",
                fg_color=self.cor_vermelho,
                hover_color=self.cor_vermelho_hover,
                text_color="white",
                width=70,
                height=28,
                command=lambda p=produto: self.confirmar_exclusao(p)
            )

            btn_apagar.pack(side="left")

    # =====================================================
    # FORMULÁRIO NOVO PRODUTO
    # =====================================================

    def abrir_formulario_novo(self):

        janela = ctk.CTkToplevel(self.root)

        janela.title("Novo Produto")
        janela.geometry("650x500")

        janela.configure(
            fg_color=self.cor_fundo
        )

        titulo = ctk.CTkLabel(
            janela,
            text="Novo Produto",
            text_color=self.cor_texto,
            font=self.fontes.titulo_grande
        )

        titulo.place(x=40, y=30)

    # =====================================================
    # EDITAR
    # =====================================================

    def editar_produto(self, produto):

        messagebox.showinfo(
            "Editar Produto",
            f"Produto selecionado: {produto.nome}"
        )

    # =====================================================
    # CONFIRMAR EXCLUSÃO
    # =====================================================

    def confirmar_exclusao(self, produto):

        resposta = DialogoConfirmacao.abrir(
            self.root,
            self.cores,
            self.fontes,
            titulo="Confirmar Exclusão"
        )

        if resposta:
            self.apagar_produto(produto)

    # =====================================================
    # APAGAR PRODUTO
    # =====================================================

    def apagar_produto(self, produto):

        if produto in self.produtos:

            self.produtos.remove(produto)

            self.atualizar_tabela()

            messagebox.showinfo(
                "Sucesso",
                f"Produto '{produto.nome}' excluído com sucesso!"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Produto não encontrado."
            )

    # =====================================================
    # EXEMPLOS
    # =====================================================

    def carregar_produtos_exemplo(self):

        self.produtos.append(
            Produto(
                "Vatapá",
                "Arroz branco",
                "Comidas Típicas",
                "10,00",
                "Inativo"
            )
        )

        self.produtos.append(
            Produto(
                "Mega Maluca",
                "",
                "Sobremesas",
                "15,00",
                "Ativo"
            )
        )

        self.produtos.append(
            Produto(
                "Coca-Cola",
                "Lata",
                "Bebidas",
                "6,50",
                "Ativo"
            )
        )

        self.atualizar_tabela()


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    TelaProdutos()