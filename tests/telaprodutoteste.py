# =========================================================
# TELA PRODUTOS - CUSTOMTKINTER
# VERSÃO CORRIGIDA E DEBUGADA
# =========================================================

import customtkinter as ctk

from tkinter import filedialog as fd
from tkinter import messagebox

from PIL import Image

from dataclasses import dataclass

# =========================================================
# IMPORTAÇÕES DO PROJETO
# =========================================================

from app.utils.estilos import Cores, Fontes, Icones

from app.utils.componentes import (
    Botoes,
    DialogoConfirmacao
)

# =========================================================
# CAMPO TEXTO
# =========================================================

class CampoTexto(ctk.CTkFrame):

    def __init__(self, master, label, placeholder, cores, fontes):
        super().__init__(master, fg_color="transparent")

        self.cores = cores
        self.fontes = fontes

        ctk.CTkLabel(
            self,
            text=label,
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(anchor="w")

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            fg_color=self.cores.fundo.cinza_escuro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_entry,
            border_width=0,
            corner_radius=8,
            height=40
        )

        self.entry.pack(fill="x", pady=5)

    def get(self):
        return self.entry.get()

    def set(self, valor):
        self.entry.delete(0, "end")
        self.entry.insert(0, valor)

class CampoOpcao(ctk.CTkFrame):
     def __init__(self, master, label, valores, cores, fontes):
        super().__init__(master, fg_color="transparent")
        
        self.cores = cores
        self.fontes = fontes

        ctk.CTkLabel(
            self, 
            text= label,
            font = self.fontes.subtitulo,
            text_color= self.cores.texto.principal
        ).pack(anchor="w")

        self.menu = ctk. CTkOptionMenu(
            self,
            values = valores,
            fg_color= self.cores.fundo.cinza_claro,
            button_color=self.cores.fundo.cinza_claro,
            button_hover_color=self.cores.fundo.cinza_escuro,
            font=self.fontes.texto_info,
            text_color=self.cores.texto.principal,
            dropdown_fg_color=self.cores.fundo.cinza_escuro,
            dropdown_text_color=self.cores.texto.passivo,
            dropdown_hover_color=self.cores.botao.passivo,
            corner_radius=8
        )
        self.menu.pack(fill="x", pady=5)
        
     def get (self):
        return self.menu.get()

     def set (self, valor):
        self.menu.set(valor)

# =========================================================
# CAMPO MULTILINHA
# =========================================================

class CampoTextoMultilinha(ctk.CTkFrame):

    def __init__(self, master, label, cores, fontes, altura=100):
        super().__init__(master, fg_color="transparent")

        self.cores = cores
        self.fontes = fontes

        ctk.CTkLabel(
            self,
            text=label,
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(anchor="w")

        self.entry = ctk.CTkTextbox(
            self,
            fg_color=self.cores.fundo.cinza_escuro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_entry,
            border_width=0,
            corner_radius=8,
            height=altura
        )

        self.entry.pack(fill="both", expand=True, pady=5)

    def get(self):
        return self.entry.get("1.0", "end").strip()

    def set(self, valor):
        self.entry.delete("1.0", "end")
        self.entry.insert("1.0", valor)


# =========================================================
# CAMPO OPÇÃO
# =========================================================

class CampoOpcao(ctk.CTkFrame):

    def __init__(self, master, label, valores, cores, fontes):
        super().__init__(master, fg_color="transparent")

        self.cores = cores
        self.fontes = fontes

        ctk.CTkLabel(
            self,
            text=label,
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(anchor="w")

        self.combo = ctk.CTkComboBox(
            self,
            values=valores,
            fg_color=self.cores.fundo.cinza_escuro,
            border_width=0,
            corner_radius=8,
            button_color=self.cores.botao.ativo_secundario,
            button_hover_color=self.cores.botao.confirmar,
            dropdown_fg_color=self.cores.fundo.branco,
            dropdown_text_color=self.cores.texto.principal,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_entry
        )

        self.combo.pack(fill="x", pady=5)

    def get(self):
        return self.combo.get()

    def set(self, valor):
        self.combo.set(valor)


# =========================================================
# CAMPO FOTO PRODUTO
# =========================================================

class CampoFotoProduto(ctk.CTkFrame):

    def __init__(self, master, cores, fontes):
        super().__init__(master, fg_color="transparent")

        self.cores = cores
        self.fontes = fontes

        # Guarda o caminho da foto escolhida

        self.caminho_foto = ""
        self.imagem_preview = None

        ctk.CTkLabel(
            self,
            text="Foto do produto",
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(anchor="w")

        self.preview = ctk.CTkLabel(
            self,
            text="Sem foto",
            width=160,
            height=120,
            fg_color=self.cores.fundo.cinza_escuro,
            text_color=self.cores.texto.passivo,
            corner_radius=10
        )

        self.preview.pack(anchor="w", pady=8)

        self.botao_importar = ctk.CTkButton(
            self,
            text="Adicionar foto",
            command=self.selecionar_foto
        )

        self.botao_importar.pack(anchor="w")

    def selecionar_foto(self):

        filetypes = (
            ("Imagens", "*.png *.jpg *.jpeg *.webp"),
            ("Todos", "*.*")
        )

        filename = fd.askopenfilename(
            title="Escolher foto",
            filetypes=filetypes
        )

        if filename:
            self.set(filename)

    def set(self, caminho):

        self.caminho_foto = caminho

        if caminho == "":
            self.preview.configure(text="Sem foto", image=None)
            return

        try:

            imagem = Image.open(caminho)

            self.imagem_preview = ctk.CTkImage(
                light_image=imagem,
                size=(160, 120)
            )

            self.preview.configure(
                text="",
                image=self.imagem_preview
            )

        except Exception as erro:

            print("ERRO FOTO:", erro)

            self.preview.configure(
                text="Erro na imagem",
                image=None
            )

    def get(self):
        return self.caminho_foto


# =========================================================
# MODEL PRODUTO
# =========================================================

@dataclass
class Produto:

    nome: str
    descricao: str
    categoria: str
    preco: str
    ativo: bool = True
    foto: str = ""

    def status_texto(self):
        return "Ativo" if self.ativo else "Inativo"


# =========================================================
# TELA PRODUTOS
# =========================================================

class TelaProdutos:

    def __init__(self, root, cores, fontes, icones):

        self.root = root

        self.cores = cores
        self.fontes = fontes
        self.icones = icones

        self.produtos = []

        self.configurar_janela()
        self.criar_topo()
        self.criar_area()
        self.carregar_produtos_exemplo()

    # =====================================================
    # JANELA
    # =====================================================

    def configurar_janela(self):

        self.root.title("Produtos")

        self.root.geometry("1100x700")

        self.root.configure(
            fg_color=self.cores.fundo.principal
        )

    # =====================================================
    # TOPO
    # =====================================================

    def criar_topo(self):

        self.topo = ctk.CTkFrame(
            self.root,
            fg_color=self.cores.barra.topo,
            corner_radius=0,
            height=70
        )

        self.topo.pack(fill="x")

        self.titulo = ctk.CTkLabel(
            self.topo,
            text="Produtos",
            font=self.fontes.titulo,
            text_color=self.cores.texto.principal
        )

        self.titulo.pack(side="left", padx=20)

        self.btn_novo = ctk.CTkButton(
            self.topo,
            text="+ Novo Produto",
            command=self.abrir_formulario
        )

        self.btn_novo.pack(side="right", padx=20)

    # =====================================================
    # ÁREA
    # =====================================================

    def criar_area(self):

        self.area = ctk.CTkFrame(
            self.root,
            fg_color=self.cores.fundo.cinza_claro
        )

        self.area.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.frame_lista = ctk.CTkScrollableFrame(
            self.area
        )

        self.frame_lista.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

    # =====================================================
    # LISTA
    # =====================================================

    def atualizar_lista(self):

        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        for produto in self.produtos:

            frame = ctk.CTkFrame(
                self.frame_lista
            )

            frame.pack(
                fill="x",
                padx=10,
                pady=5
            )

            texto = f"""
Nome: {produto.nome}

Categoria: {produto.categoria}

Preço: R$ {produto.preco}

Status: {produto.status_texto()}
"""

            ctk.CTkLabel(
                frame,
                text=texto,
                justify="left"
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                frame,
                text="Editar",
                width=80,
                command=lambda p=produto: self.abrir_formulario(p)
            ).pack(side="right", padx=5)

            ctk.CTkButton(
                frame,
                text="Excluir",
                width=80,
                fg_color="red",
                command=lambda p=produto: self.excluir_produto(p)
            ).pack(side="right")

    # =====================================================
    # FORMULÁRIO
    # =====================================================

    def abrir_formulario(self, produto=None):

        janela = ctk.CTkToplevel(self.root)

        janela.geometry("700x550")

        janela.title("Produto")

        campo_nome = CampoTexto(
            janela,
            "Nome",
            "Digite o nome",
            self.cores,
            self.fontes
        )

        campo_nome.pack(
            fill="x",
            padx=20,
            pady=10
        )

        campo_descricao = CampoTextoMultilinha(
            janela,
            "Descrição",
            self.cores,
            self.fontes
        )

        campo_descricao.pack(
            fill="x",
            padx=20,
            pady=10
        )

        campo_categoria = CampoOpcao(
            janela,
            "Categoria",
            ["Comidas", "Bebidas", "Sobremesas"],
            self.cores,
            self.fontes
        )

        campo_categoria.pack(
            fill="x",
            padx=20,
            pady=10
        )

        campo_preco = CampoTexto(
            janela,
            "Preço",
            "0,00",
            self.cores,
            self.fontes
        )

        campo_preco.pack(
            fill="x",
            padx=20,
            pady=10
        )

        campo_foto = CampoFotoProduto(
            janela,
            self.cores,
            self.fontes
        )

        campo_foto.pack(
            fill="x",
            padx=20,
            pady=10
        )

        if produto:

            campo_nome.set(produto.nome)
            campo_descricao.set(produto.descricao)
            campo_categoria.set(produto.categoria)
            campo_preco.set(produto.preco)

        def salvar():

            nome = campo_nome.get()

            descricao = campo_descricao.get()

            categoria = campo_categoria.get()

            preco = campo_preco.get()

            foto = campo_foto.get()

            if nome == "":
                messagebox.showwarning(
                    "Aviso",
                    "Digite o nome"
                )
                return

            if produto:

                produto.nome = nome
                produto.descricao = descricao
                produto.categoria = categoria
                produto.preco = preco
                produto.foto = foto

            else:

                novo = Produto(
                    nome,
                    descricao,
                    categoria,
                    preco,
                    True,
                    foto
                )

                self.produtos.append(novo)

            self.atualizar_lista()

            janela.destroy()

            messagebox.showinfo(
                "Sucesso",
                "Produto salvo"
            )

        btn_salvar = ctk.CTkButton(
            janela,
            text="Salvar",
            command=salvar
        )

        btn_salvar.pack(
            pady=20
        )

    # =====================================================
    # EXCLUIR
    # =====================================================

    def excluir_produto(self, produto):

        confirmar = messagebox.askyesno(
            "Excluir",
            f"Deseja excluir {produto.nome}?"
        )

        if confirmar:

            self.produtos.remove(produto)

            self.atualizar_lista()

    # =====================================================
    # PRODUTOS EXEMPLO
    # =====================================================

    def carregar_produtos_exemplo(self):

        self.produtos.append(
            Produto(
                "Vatapá",
                "Comida típica",
                "Comidas",
                "25,00"
            )
        )

        self.produtos.append(
            Produto(
                "Coca-Cola",
                "Lata 350ml",
                "Bebidas",
                "6,00"
            )
        )

        self.atualizar_lista()


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    ctk.set_appearance_mode("light")

    root = ctk.CTk()

    cores = Cores()
    fontes = Fontes()
    icones = Icones()

    app = TelaProdutos(
        root,
        cores,
        fontes,
        icones
    )

    root.mainloop()