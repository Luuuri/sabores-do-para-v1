# =========================================================
# IMPORTAÇÕES
# =========================================================

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk


# =========================================================
# CLASSE DE CORES DO SISTEMA
# =========================================================

class Cores:
    def __init__(self):
        self.fundo_principal = "#f4f4f4"
        self.barra_topo = "#d9d9d9"
        self.cinza_claro = "#dbdbdb"
        self.cinza_escuro = "#b4b4b4"
        self.branco = "#ffffff"
        self.preto = "#000000"
        self.vermelho = "#ff8f8f"
        self.azul_escuro = "#062733"
        self.texto = "#1e1e1e"


# =========================================================
# CLASSE JSON DO PRODUTO
# Responsável por salvar e carregar os produtos em um arquivo JSON
# =========================================================

def salvar_no_json(self):
    dados = []

    for produto in self.produtos:
        dados.append({
            "nome": produto.nome,
            "descricao": produto.descricao,
            "categoria": produto.categoria,
            "preco": produto.preco,
            "status": produto.status,
            "imagem": produto.imagem
        })

    with open(self.arquivo_json, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def carregar_do_json(self):
    try:
        with open(self.arquivo_json, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        for item in dados:
            produto = Produto(
                item["nome"],
                item["descricao"],
                item["categoria"],
                item["preco"],
                item["status"],
                item["imagem"]
            )

            self.produtos.append(produto)

    except FileNotFoundError:
        self.produtos = []

    self.atualizar_tabela()


# =========================================================
# CLASSE MODELO DO PRODUTO
# Representa os dados de um produto
# =========================================================

class Produto:
    def __init__(self, nome, descricao, categoria, preco, status="Ativo", imagem=""):
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.preco = preco
        self.status = status
        self.imagem = imagem


# =========================================================
# CLASSE PRINCIPAL DA TELA DE PRODUTOS
# =========================================================

class TelaProdutos:

    def __init__(self, root):
        self.root = root
        self.root.title("Produtos")
        self.root.geometry("1100x700")
        self.root.config(bg="#f4f4f4")
        self.root.minsize(1000, 650)

        self.cores = Cores()

        self.produtos = []

        self.criar_topo()
        self.criar_menu_lateral()
        self.criar_area_conteudo()
        self.criar_tabela_produtos()
        self.carregar_produtos_exemplo()

    # =====================================================
    # TOPO
    # =====================================================

    def criar_topo(self):
        self.topo = tk.Frame(self.root, bg=self.cores.barra_topo)
        self.topo.place(relx=0, rely=0, relwidth=1, relheight=0.08)

        self.lbl_home = tk.Label(
            self.topo,
            text="🏠",
            bg=self.cores.barra_topo,
            font=("Arial", 14)
        )
        self.lbl_home.pack(side="left", padx=20)

        self.lbl_titulo = tk.Label(
            self.topo,
            text="🍔 Produtos",
            bg=self.cores.barra_topo,
            fg=self.cores.texto,
            font=("Arial", 12, "bold")
        )
        self.lbl_titulo.pack(side="left")

        self.btn_novo = tk.Button(
            self.topo,
            text="+ Novo Produto",
            bg=self.cores.preto,
            fg=self.cores.branco,
            font=("Arial", 10, "bold"),
            bd=0,
            cursor="hand2",
            command=self.abrir_formulario_novo
        )
        self.btn_novo.pack(side="right", padx=20)

        self.lbl_config = tk.Label(
            self.topo,
            text="⚙",
            bg=self.cores.barra_topo,
            font=("Arial", 14)
        )
        self.lbl_config.pack(side="right", padx=10)

    # =====================================================
    # MENU LATERAL
    # =====================================================

    def criar_menu_lateral(self):
        self.menu_lateral = tk.Frame(self.root, bg=self.cores.fundo_principal)
        self.menu_lateral.place(relx=0, rely=0.08, relwidth=0.07, relheight=0.92)

        self.lbl_menu = tk.Label(
            self.menu_lateral,
            text="☰",
            bg=self.cores.fundo_principal,
            fg="#555555",
            font=("Arial", 18)
        )
        self.lbl_menu.place(relx=0.30, rely=0.03)

        self.lbl_sair = tk.Label(
            self.menu_lateral,
            text="⏻",
            bg=self.cores.fundo_principal,
            fg="#555555",
            font=("Arial", 18)
        )
        self.lbl_sair.place(relx=0.30, rely=0.92)

    # =====================================================
    # ÁREA PRINCIPAL
    # =====================================================

    def criar_area_conteudo(self):
        self.area = tk.Frame(self.root, bg=self.cores.cinza_claro)
        self.area.place(relx=0.12, rely=0.16, relwidth=0.78, relheight=0.68)

        self.entrada_busca = tk.Entry(
            self.area,
            font=("Arial", 10),
            bd=0
        )
        self.entrada_busca.insert(0, "🔍 Buscar produto...")
        self.entrada_busca.place(relx=0.03, rely=0.04, relwidth=0.20, relheight=0.04)

        self.lbl_filtro = tk.Label(
            self.area,
            text="⚱",
            bg=self.cores.cinza_claro,
            font=("Arial", 12)
        )
        self.lbl_filtro.place(relx=0.24, rely=0.04)

    # =====================================================
    # TABELA DE PRODUTOS
    # =====================================================

    def criar_tabela_produtos(self):
        colunas = ("nome", "categoria", "preco", "status", "acoes")

        self.tabela = ttk.Treeview(
            self.area,
            columns=colunas,
            show="headings"
        )

        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("categoria", text="Categoria")
        self.tabela.heading("preco", text="Preço")
        self.tabela.heading("status", text="Status")
        self.tabela.heading("acoes", text="Ações")

        self.tabela.column("nome", width=250)
        self.tabela.column("categoria", width=180)
        self.tabela.column("preco", width=100)
        self.tabela.column("status", width=100)
        self.tabela.column("acoes", width=100)

        self.tabela.place(relx=0.03, rely=0.12, relwidth=0.94, relheight=0.80)

        self.tabela.bind("<Double-1>", self.editar_produto_selecionado)

    # =====================================================
    # FORMULÁRIO DE NOVO PRODUTO
    # =====================================================

    def abrir_formulario_novo(self):
        janela = tk.Toplevel(self.root)
        janela.title("Novo Produto")
        janela.geometry("650x500")
        janela.config(bg=self.cores.fundo_principal)

        tk.Label(janela, text="Novo Produto", bg=self.cores.fundo_principal,
                 font=("Arial", 18, "bold")).place(x=40, y=30)

        tk.Label(janela, text="Nome", bg=self.cores.fundo_principal).place(x=40, y=90)
        entrada_nome = tk.Entry(janela)
        entrada_nome.place(x=40, y=115, width=230, height=35)

        tk.Label(janela, text="Descrição", bg=self.cores.fundo_principal).place(x=40, y=160)
        entrada_descricao = tk.Entry(janela)
        entrada_descricao.place(x=40, y=185, width=230, height=35)

        tk.Label(janela, text="Categoria", bg=self.cores.fundo_principal).place(x=40, y=230)
        combo_categoria = ttk.Combobox(
            janela,
            values=["Comidas Típicas", "Sobremesas", "Bebidas"]
        )
        combo_categoria.place(x=40, y=255, width=230, height=35)

        tk.Label(janela, text="Preço", bg=self.cores.fundo_principal).place(x=40, y=300)
        entrada_preco = tk.Entry(janela)
        entrada_preco.place(x=40, y=325, width=230, height=35)

        status = tk.StringVar(value="Ativo")

        btn_status = tk.Button(
            janela,
            text="Ativo",
            bg=self.cores.azul_escuro,
            fg=self.cores.branco,
            bd=0
        )
        btn_status.place(x=110, y=380, width=80, height=35)

        def salvar():
            nome = entrada_nome.get()
            descricao = entrada_descricao.get()
            categoria = combo_categoria.get()
            preco = entrada_preco.get()

            if nome == "" or categoria == "" or preco == "":
                messagebox.showwarning("Aviso", "Preencha nome, categoria e preço.")
                return

            produto = Produto(nome, descricao, categoria, preco, status.get())

            self.produtos.append(produto)
            self.atualizar_tabela()

            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            janela.destroy()

        btn_salvar = tk.Button(
            janela,
            text="Salvar",
            bg=self.cores.preto,
            fg=self.cores.branco,
            bd=0,
            command=salvar
        )
        btn_salvar.place(x=40, y=430, width=90, height=35)

        btn_cancelar = tk.Button(
            janela,
            text="Cancelar",
            bg=self.cores.vermelho,
            fg=self.cores.branco,
            bd=0,
            command=janela.destroy
        )
        btn_cancelar.place(x=150, y=430, width=90, height=35)

    # =====================================================
    # EDITAR PRODUTO
    # =====================================================

    def editar_produto_selecionado(self, event):
        item = self.tabela.selection()

        if not item:
            return

        valores = self.tabela.item(item, "values")

        messagebox.showinfo(
            "Editar Produto",
            f"Produto selecionado: {valores[0]}"
        )

    # =====================================================
    # ATUALIZAR TABELA
    # =====================================================

    def atualizar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for produto in self.produtos:
            self.tabela.insert(
                "",
                "end",
                values=(
                    produto.nome,
                    produto.categoria,
                    f"R$ {produto.preco}",
                    produto.status,
                    "✏ 🗑"
                )
            )

    # =====================================================
    # PRODUTOS DE EXEMPLO
    # =====================================================

    def carregar_produtos_exemplo(self):
        self.produtos.append(Produto("Vatapá", "Arroz branco", "Comidas Típicas", "10,00", "Inativo"))
        self.produtos.append(Produto("Mega Maluca", "", "Sobremesas", "15,00", "Ativo"))
        self.produtos.append(Produto("Coca-Cola", "Lata", "Bebidas", "6,50", "Ativo"))

        self.atualizar_tabela()


# =========================================================
# EXECUÇÃO DO SISTEMA
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = TelaProdutos(root)
    root.mainloop()