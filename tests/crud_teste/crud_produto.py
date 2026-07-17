# IMPORTAÇÕES

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar(): #fazendo a coxecao com o banco
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
        )
print("conector!")
# CONFIGURAÇÃO INICIAL DO CUSTOMTKINTER

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# CLASSE DE CORES DO SISTEMA

class Cores:
    def __init__(self):
        self.fundo_principal = "#f4f4f4"
        self.barra_topo = "#d9d9d9"
        self.cinza_claro = "#dbdbdb"
        self.cinza_escuro = "#b4b4b4"
        self.branco = "#ffffff"
        self.preto = "#1e1e1e"
        self.vermelho = "#ff9b9b"
        self.azul_escuro = "#062733"
        self.texto_principal = "#1e1e1e"
        self.texto_branco = "#ffffff"


# CLASSE MODELO DO PRODUTO
class Produto:
    def __init__(self, id_produto, nome, preco, categoria, descricao, status):
        self.id = id_produto
        self.nome = nome
        self.preco = preco
        self.categoria = categoria
        self.descricao = descricao 
        self.status = status


# CLASSE PRINCIPAL DA TELA DE PRODUTOS
class TelaProdutos:
    def __init__(self, root):
        self.root = root
        self.root.title("Point dos Sabores - Produtos")
        self.root.geometry("1100x700")

        self.cores = Cores()

        self.produtos = []

        self.criar_frame_principal()
        self.criar_topo()
        self.criar_lateral()
        self.criar_conteudo()
        self.criar_tabela()
        self.carregar_do_banco()

    # FRAME PRINCIPAL
    def criar_frame_principal(self):
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.cores.fundo_principal
        )
        self.main_frame.pack(fill="both", expand=True)

    # TOPO
    def criar_topo(self):
        self.topo_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.cores.barra_topo,
            height=60,
            corner_radius=0
        )
        self.topo_frame.pack(fill="x", side="top")

        self.btn_home = ctk.CTkButton(
            self.topo_frame,
            text="🏠",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=self.cores.cinza_claro,
            text_color=self.cores.texto_principal
        )
        self.btn_home.pack(side="left", padx=15, pady=10)

        self.lbl_titulo = ctk.CTkLabel(
            self.topo_frame,
            text="🍔 Produtos",
            font=("Arial", 18, "bold"),
            text_color=self.cores.texto_principal
        )
        self.lbl_titulo.pack(side="left", padx=5)

        self.btn_config = ctk.CTkButton(
            self.topo_frame,
            text="⚙",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=self.cores.cinza_claro,
            text_color=self.cores.texto_principal
        )
        self.btn_config.pack(side="right", padx=15, pady=10)

        self.btn_novo_produto = ctk.CTkButton(
            self.topo_frame,
            text="+ Novo Produto",
            fg_color=self.cores.preto,
            text_color=self.cores.texto_branco,
            corner_radius=20,
            cursor="hand2",
            command=self.abrir_formulario_novo
        )
        self.btn_novo_produto.pack(side="right", padx=10, pady=10)

    # MENU LATERAL
    def criar_lateral(self):
        self.lateral_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            width=60,
            corner_radius=0
        )
        self.lateral_frame.pack(fill="y", side="left")

        self.btn_menu = ctk.CTkButton(
            self.lateral_frame,
            text="☰",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=self.cores.cinza_claro,
            text_color=self.cores.texto_principal
        )
        self.btn_menu.pack(side="top", padx=10, pady=10)

        self.btn_sair = ctk.CTkButton(
            self.lateral_frame,
            text="⏻",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=self.cores.cinza_claro,
            text_color=self.cores.texto_principal
        )
        self.btn_sair.pack(side="bottom", padx=10, pady=10)

    # ÁREA DE CONTEÚDO
    def criar_conteudo(self):
        self.conteudo_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.cores.cinza_claro,
            corner_radius=10
        )
        self.conteudo_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=30,
            pady=40
        )

        self.busca_entry = ctk.CTkEntry(
            self.conteudo_frame,
            placeholder_text="🔍 Buscar produto...",
            width=230,
            height=30,
            fg_color=self.cores.branco,
            border_width=0,
            corner_radius=10
        )
        self.busca_entry.pack(anchor="nw", padx=25, pady=(20, 10))
        self.busca_entry.bind("<KeyRelease>", self.filtrar_produtos)

    # TABELA DE PRODUTOS

    def criar_tabela(self):
        self.tabela_frame = ctk.CTkFrame(
            self.conteudo_frame,
            fg_color=self.cores.branco,
            corner_radius=10
        )
        self.tabela_frame.pack(fill="both", expand=True, padx=25, pady=15)

        self.cabecalho = ctk.CTkFrame(
            self.tabela_frame,
            fg_color=self.cores.branco
        )
        self.cabecalho.pack(fill="x", padx=10, pady=10)

        colunas = ["Nome", "Categoria", "Preço", "Status", "Ações"]

        for i, coluna in enumerate(colunas):
            label = ctk.CTkLabel(
                self.cabecalho,
                text=coluna,
                font=("Arial", 12, "bold"),
                text_color=self.cores.texto_principal
            )
            label.grid(row=0, column=i, sticky="nsew", padx=5)
            
        for i in range(len(colunas)):
            self.cabecalho.grid_columnconfigure(i, weight=1)

        self.lista_frame = ctk.CTkFrame(
            self.tabela_frame,
            fg_color=self.cores.branco
        )
        
           
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # FORMULÁRIO DE NOVO PRODUTO

    def abrir_formulario_novo(self):
        self.janela_formulario = ctk.CTkToplevel(self.root)
        self.janela_formulario.title("Novo Produto")
        self.janela_formulario.geometry("750x500")
        self.janela_formulario.configure(fg_color=self.cores.fundo_principal)
        
        self.janela_formulario.transient(self.root) #vincula ao pai
        self.janela_formulario.grab_set()           #bloqueia a janela principal
        self.janela_formulario.lift()               #traz para frete
        self.janela_formulario.focus_force()        #força o foco

        self.lbl_form_titulo = ctk.CTkLabel(
            self.janela_formulario,
            text="Novo Produto",
            font=("Arial", 22, "bold"),
            text_color=self.cores.texto_principal
        )
        self.lbl_form_titulo.pack(anchor="nw", padx=40, pady=(30, 20))

        self.nome_entry = ctk.CTkEntry(
            self.janela_formulario,
            placeholder_text="Nome",
            width=250,
            height=40,
            fg_color=self.cores.cinza_escuro,
            border_width=0,
            corner_radius=8
        )
        self.nome_entry.pack(anchor="nw", padx=40, pady=8)

        self.descricao_entry = ctk.CTkEntry(
            self.janela_formulario,
            placeholder_text="Descrição",
            width=250,
            height=40,
            fg_color=self.cores.cinza_escuro,
            border_width=0,
            corner_radius=8
        )
        self.descricao_entry.pack(anchor="nw", padx=40, pady=8)

        self.categoria_menu = ctk.CTkOptionMenu(
            self.janela_formulario,
            values=["Comidas Típicas", "Sobremesas", "Bebidas"],
            width=250,
            height=40,
            fg_color=self.cores.cinza_escuro,
            button_color=self.cores.cinza_claro,
            text_color=self.cores.texto_principal
        )
        self.categoria_menu.pack(anchor="nw", padx=40, pady=8)

        self.preco_entry = ctk.CTkEntry(
            self.janela_formulario,
            placeholder_text="Preço",
            width=250,
            height=40,
            fg_color=self.cores.cinza_escuro,
            border_width=0,
            corner_radius=8
        )
        self.preco_entry.pack(anchor="nw", padx=40, pady=8)

        self.status_var = ctk.StringVar(value="Ativo")

        self.btn_status = ctk.CTkButton(
            self.janela_formulario,
            text="Ativo",
            width=90,
            height=35,
            fg_color=self.cores.azul_escuro,
            text_color=self.cores.texto_branco,
            corner_radius=20,
            command=self.alternar_status
        )
        self.btn_status.pack(anchor="nw", padx=115, pady=15)

        self.botoes_frame = ctk.CTkFrame(
            self.janela_formulario,
            fg_color="transparent"
        )
        self.botoes_frame.pack(anchor="nw", padx=40, pady=20)

        self.btn_salvar = ctk.CTkButton(
            self.botoes_frame,
            text="Salvar",
            width=100,
            height=38,
            fg_color=self.cores.preto,
            text_color=self.cores.texto_branco,
            corner_radius=20,
            command=self.salvar_produto
        )
        self.btn_salvar.pack(side="left", padx=(0, 15))

        self.btn_cancelar = ctk.CTkButton(
            self.botoes_frame,
            text="Cancelar",
            width=100,
            height=38,
            fg_color=self.cores.vermelho,
            text_color=self.cores.texto_branco,
            corner_radius=20,
            command=self.janela_formulario.destroy
        )
        self.btn_cancelar.pack(side="left")


    # ALTERAR STATUS

    def alternar_status(self):
        if self.status_var.get() == "Ativo":
            self.status_var.set("Inativo")
            self.btn_status.configure(
                text="Inativo",
                fg_color=self.cores.cinza_escuro
            )
        else:
            self.status_var.set("Ativo")
            self.btn_status.configure(
                text="Ativo",
                fg_color=self.cores.azul_escuro
            )

    # SALVAR PRODUTO

    def salvar_produto(self): #modificado para salvar do banco
        try:
            nome = self.nome_entry.get()
            descricao= self.descricao_entry.get()
            categoria = self.categoria_menu.get()
            preco = self.preco_entry.get().replace(",",".")
            status = self.status_var.get()

            conn = conectar()
            cursor = conn.cursor()
    
            if hasattr(self, "produto_editando"):
                cursor.execute("""
                    UPDATE produto
                    SET nome=%s, preco=%s, categoria=%s, descricao=%s, status=%s
                    WHERE id_produto=%s                           
                """, (nome, preco, categoria, descricao, status, self.produto_editando))

                del self.produto_editando
            else:
                print(nome, preco, categoria, descricao, status)
                cursor.execute("""
                    INSERT INTO produto (nome, preco, categoria, descricao, status)
                    VALUES (%s, %s, %s, %s, %s)           
                """, (nome, preco, categoria, descricao, status))    
    
            conn.commit()    
            
            messagebox.showinfo("Sucesso","Produto salvo!")
            self.carregar_do_banco()
            self.janela_formulario.destroy()

        except Exception as e: 
            messagebox.showerror("Erro", str(e))  
        finally:
            if conn:
                conn.close()     
         
            
            
    def carregar_do_banco(self): #criei a funcao buscar do banco
        self.produtos = []
        try:

            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_produto, nome, preco, categoria, descricao, status 
                FROM produto
            """)
            dados = cursor.fetchall()
            conn.close()
       
            for item in dados:
                produto = Produto(*item)
                self.produtos.append(produto)

        except Exception as e:
            print("erro ao carregar banco:", e)
            messagebox.showerror("Erro de conexão", str(e))        

        self.atualizar_tabela() 
        
    def filtrar_produtos(self, event=None):
        termo = self.busca_entry.get().lower()

        if termo == "":
            self.atualizar_tabela()
            return

        filtrados = []

        for produto in self.produtos:
            if (
                termo in produto.nome.lower()
                or termo in produto.categoria.lower()
                or termo in produto.status.lower()
        ):
                filtrados.append(produto)

        self.mostrar_produtos(filtrados) 
        
        
    def mostrar_produtos(self, lista):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        for i in range(5):
            self.lista_frame.grid_columnconfigure(i, weight=1)

        for row, produto in enumerate(lista):
            dados = [
                produto.nome,
                produto.categoria,
                f"R$ {produto.preco}",
                produto.status
            ]

        for col, dado in enumerate(dados):
            label = ctk.CTkLabel(self.lista_frame, text=dado,font=("Ariel", 12))

            if col == 2:
                label.grid(row=row, column=col, sticky="e", padx=5)
            else:
                label.grid(row=row, column=col, sticky="w", padx=5)

        frame_acoes = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
        frame_acoes.grid(row=row, column=4, padx=5)

        ctk.CTkButton(
            frame_acoes,
            text="✏",
            width=30,
            command=lambda p=produto: self.editar_produto(p)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            frame_acoes,
            text="🗑",
            width=30,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="white",
            command=lambda id=produto.id: self.deletar_produto(id)
        ).pack(side="left", padx=2)            

    
    # ATUALIZAR TABELA
    # =====================================================

    def atualizar_tabela(self):
       
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
            
        for i in range(5):
            self.lista_frame.grid_columnconfigure(i, weight=1)

        for row, produto in enumerate(self.produtos):
            dados =[
                produto.nome,
                produto.categoria,
                f"R$ {produto.preco}",
                produto.status
            ]

            for col, dado in enumerate(dados):
                label = ctk.CTkLabel(
                    self.lista_frame,
                    text=dado,
                    font=("Arial", 12),
                    text_color=self.cores.texto_principal
                )
                if col == 2: #coluna do preco
                    label.grid(row=row, column=col, padx=5, sticky="e")
                    
                else:
                    label.grid(row=row, column=col, sticky="w", padx=5)  
                    
               # criar um "container" para os botões
            frame_acoes = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            frame_acoes.grid(row=row, column=4, padx=5)
                  
              #botão editar
            btn_edit = ctk.CTkButton(
                frame_acoes,
                text="✏",
                width=30,
                command=lambda p=produto: self.editar_produto(p)
                )
            btn_edit.pack(side="left", padx=2)          
            
            #botao deletar
            btn_delete = ctk.CTkButton(
                frame_acoes,
                text="🗑",
                width=30,
                fg_color="#e74c3c",      # vermelho
                hover_color="#c0392b",   # vermelho mais escuro
                text_color="white",
                command=lambda id=produto.id: self.confirmar_exclusao(id) #mudou aqui
            )
            btn_delete.pack(side="left", padx=2)
            
    def confirmar_exclusao(self, id):
        # Cria janela de confirmação
        janela_confirm = ctk.CTkToplevel(self.root)
        janela_confirm.title("Confirmar Exclusão")
        janela_confirm.geometry("350x180")
        janela_confirm.resizable(False, False)
        janela_confirm.transient(self.root)
        janela_confirm.grab_set()
        janela_confirm.lift()
        janela_confirm.focus_force()
        
        
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (350 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (180 // 2)
        janela_confirm.geometry(f"350x180+{x}+{y}")
        
        # Mensagem
        ctk.CTkLabel(
            janela_confirm,
            text="⚠️ Deseja realmente excluir\neste produto?",
            font=("Arial", 16, "bold"),
        ).pack(pady=(30, 20))
        
        #Frame dos botoes
        frame_btns = ctk.CTkFrame(janela_confirm, fg_color="transparent")
        frame_btns.pack()
        
        #botao confirmar
        ctk.CTkButton(
            frame_btns,
            text="Sim, excluir",
            width=120,
            height=38,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="white",
            corner_radius=20,
            command=lambda: [self.deletar_produto(id), janela_confirm.destroy()]
        ).pack(side="left", padx=10)
        
        #botao cancelar
        ctk.CTkButton(
            frame_btns,
            text="Cancelar",
            width=120,
            height=38,
            fg_color="#555555",
            hover_color= "#333333",
            text_color="white",
            corner_radius=20,
            command=janela_confirm.destroy
        ).pack(side="left", padx=10)
         
            
        for i in range(5):
                self.lista_frame.grid_columnconfigure(i, weight=1)


    def deletar_produto(self, id):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM produto WHERE id_produto = %s", (id,))

        conn.commit()
        conn.close()

        self.carregar_do_banco()
    # =====================================================
    # PRODUTOS DE EXEMPLO
    # =====================================================

    def editar_produto(self, produto):
        self.abrir_formulario_novo()

        self.nome_entry.insert(0, produto.nome)
        self.descricao_entry.insert(0, produto.descricao)
        self.preco_entry.insert(0, produto.preco)

        self.produto_editando = produto.id


    """def carregar_produtos_exemplo(self):
        self.produtos.append(
            Produto(None, "Vatapá",10.00, "Comidas Típicas", "Arroz branco", "Inativo")
        )

        self.produtos.append(
            Produto("Mega Maluca", "", "Sobremesas", "15,00", "Ativo")
        )

        self.produtos.append(
            Produto("Coca-Cola", "Lata", "Bebidas", "6,50", "Ativo")
        )

        self.atualizar_tabela()"""

# EXECUÇÃO DO SISTEMA
# =========================================================

if __name__ == "__main__":
    root = ctk.CTk()
    print("CRIANDO APP...")
    app = TelaProdutos(root)
    print("RODANDO LOOP...")
    root.mainloop()