# importa a biblioteca tkinter e dá o apelido de tk
import tkinter as tk

# importa o ttk para usar a tabela Treeview
from tkinter import ttk, messagebox


# cria a classe da janela de clientes
class JanelaClientes:

    # método construtor da classe
    def __init__(self, root):

        # guarda a janela principal
        self.root = root

        # define o título da janela
        self.root.title("Clientes")

        # define o tamanho inicial da janela
        self.root.geometry("1100x700")

        # define a cor de fundo
        self.root.configure(bg="#f5f5f5")

        # define o tamanho mínimo da janela
        self.root.minsize(1100, 650)

        # controla se a área de endereço está visível ou não
        self.endereco_visivel = False

        # =========================================================
        # VARIÁVEIS DO CRUD
        # =========================================================

        # lista que guarda todos os clientes cadastrados
        self.clientes = []

        # número usado para gerar ID automático
        self.proximo_id = 1

        # guarda o cliente que está sendo editado
        # começa vazio, porque ninguém está sendo editado ainda
        self.cliente_em_edicao = None

        # chama os métodos que montam a interface
        self.criar_topo()
        self.criar_menu_lateral()
        self.criar_titulo()
        self.criar_formulario_cliente()
        self.criar_area_clientes()

    # =========================================================
    # TOPO
    # =========================================================
    def criar_topo(self):

        # cria a barra superior
        self.barra_topo = tk.Frame(self.root, bg="#d9d9d9")
        self.barra_topo.place(relx=0, rely=0, relwidth=1, relheight=0.08)

        # ícone de casa
        self.lbl_icone_casa = tk.Label(
            self.barra_topo,
            text="⌂",
            bg="#d9d9d9",
            fg="#444444",
            font=("Arial", 16, "bold")
        )
        self.lbl_icone_casa.place(relx=0.015, rely=0.25)

        # texto do topo
        self.lbl_titulo_topo = tk.Label(
            self.barra_topo,
            text="Clientes",
            bg="#d9d9d9",
            fg="#222222",
            font=("Arial", 14, "bold")
        )
        self.lbl_titulo_topo.place(relx=0.09, rely=0.28)

        # ícone de configuração
        self.lbl_icone_config = tk.Label(
            self.barra_topo,
            text="⚙",
            bg="#d9d9d9",
            fg="#444444",
            font=("Arial", 16)
        )
        self.lbl_icone_config.place(relx=0.965, rely=0.25)

    # =========================================================
    # MENU LATERAL
    # =========================================================
    def criar_menu_lateral(self):

        # cria o menu lateral
        self.menu_lateral = tk.Frame(self.root, bg="#f0f0f0")
        self.menu_lateral.place(relx=0, rely=0.08, relwidth=0.06, relheight=0.92)

        # ícone de menu
        self.lbl_menu = tk.Label(
            self.menu_lateral,
            text="☰",
            bg="#f0f0f0",
            fg="#555555",
            font=("Arial", 18)
        )
        self.lbl_menu.place(relx=0.30, rely=0.02)

        # ícone de sair
        self.lbl_sair = tk.Label(
            self.menu_lateral,
            text="⏻",
            bg="#f0f0f0",
            fg="#555555",
            font=("Arial", 18)
        )
        self.lbl_sair.place(relx=0.30, rely=0.94)

    # =========================================================
    # TÍTULO PRINCIPAL
    # =========================================================
    def criar_titulo(self):

        # seta de voltar
        self.lbl_voltar = tk.Label(
            self.root,
            text="←",
            bg="#f5f5f5",
            fg="#333333",
            font=("Arial", 18, "bold")
        )
        self.lbl_voltar.place(relx=0.085, rely=0.12)

        # título principal
        self.lbl_titulo = tk.Label(
            self.root,
            text="Novo Cliente",
            bg="#f5f5f5",
            fg="#111111",
            font=("Arial", 22, "bold")
        )
        self.lbl_titulo.place(relx=0.115, rely=0.118)

    # =========================================================
    # FORMULÁRIO DO CLIENTE
    # =========================================================
    def criar_formulario_cliente(self):

        # área da esquerda onde ficam os campos
        self.area_formulario = tk.Frame(self.root, bg="#f5f5f5")
        self.area_formulario.place(relx=0.08, rely=0.18, relwidth=0.30, relheight=0.78)

        # cria os campos principais do cliente
        self.criar_campo(self.area_formulario, "Nome *", 0.00, "ent_nome")
        self.criar_campo(self.area_formulario, "Telefone *", 0.14, "ent_telefone")
        self.criar_campo(self.area_formulario, "CPF", 0.28, "ent_cpf")
        self.criar_campo(self.area_formulario, "Email", 0.42, "ent_email")

        # botão para mostrar ou esconder endereço
        self.btn_endereco = tk.Button(
            self.area_formulario,
            text="✚  Endereço",
            bg="#e9e9e9",
            fg="#0b1f2a",
            font=("Arial", 12, "bold"),
            bd=0,
            activebackground="#dcdcdc",
            cursor="hand2",
            command=self.alternar_endereco
        )
        self.btn_endereco.place(relx=0.00, rely=0.58, relwidth=0.35, relheight=0.07)

        # botão salvar
        self.btn_salvar = tk.Button(
            self.area_formulario,
            text="Salvar",
            bg="#000000",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            bd=0,
            activebackground="#222222",
            activeforeground="#ffffff",
            cursor="hand2",
            command=self.salvar_cliente
        )
        self.btn_salvar.place(relx=0.00, rely=0.71, relwidth=0.20, relheight=0.07)

        # botão cancelar
        self.btn_cancelar = tk.Button(
            self.area_formulario,
            text="Cancelar",
            bg="#f48c8c",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            bd=0,
            activebackground="#ea7777",
            activeforeground="#ffffff",
            cursor="hand2",
            command=self.limpar_campos
        )
        self.btn_cancelar.place(relx=0.25, rely=0.71, relwidth=0.25, relheight=0.07)

        # botão editar
        self.btn_editar = tk.Button(
            self.area_formulario,
            text="Editar",
            bg="#4a90e2",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            bd=0,
            cursor="hand2",
            command=self.carregar_cliente_selecionado
        )
        self.btn_editar.place(relx=0.00, rely=0.81, relwidth=0.20, relheight=0.07)

        # botão excluir
        self.btn_excluir = tk.Button(
            self.area_formulario,
            text="Excluir",
            bg="#cc4444",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            bd=0,
            cursor="hand2",
            command=self.excluir_cliente
        )
        self.btn_excluir.place(relx=0.25, rely=0.81, relwidth=0.25, relheight=0.07)

        # cria a área de endereço, mas deixa escondida no começo
        self.area_endereco = tk.Frame(self.root, bg="#f5f5f5")

    # =========================================================
    # CAMPO PADRÃO
    # =========================================================
    def criar_campo(self, janela, texto, pos_y, nome_atributo):

        # label do campo
        lbl = tk.Label(
            janela,
            text=texto,
            bg="#f5f5f5",
            fg="#333333",
            font=("Arial", 11, "bold")
        )
        lbl.place(relx=0.00, rely=pos_y)

        # caixa de entrada
        ent = tk.Entry(
            janela,
            font=("Arial", 12),
            bg="#cfcfcf",
            fg="#222222",
            relief="flat"
        )
        ent.place(relx=0.00, rely=pos_y + 0.05, relwidth=0.62, relheight=0.07)

        # salva o campo dentro da classe
        setattr(self, nome_atributo, ent)

    # =========================================================
    # ÁREA DA TABELA DE CLIENTES
    # =========================================================
    def criar_area_clientes(self):

        # frame principal da tabela
        self.area_clientes = tk.Frame(self.root, bg="#dcdcdc")
        self.area_clientes.place(relx=0.40, rely=0.23, relwidth=0.55, relheight=0.50)

        # campo de busca
        self.ent_busca = tk.Entry(
            self.area_clientes,
            font=("Arial", 11),
            relief="flat",
            bg="#ffffff",
            fg="#333333"
        )
        self.ent_busca.place(relx=0.03, rely=0.05, relwidth=0.35, relheight=0.08)

        # botão buscar
        self.btn_buscar = tk.Button(
            self.area_clientes,
            text="Buscar",
            bg="#444444",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            bd=0,
            cursor="hand2",
            command=self.buscar_cliente
        )
        self.btn_buscar.place(relx=0.40, rely=0.05, relwidth=0.12, relheight=0.08)

        # frame da tabela
        self.tabela_frame = tk.Frame(self.area_clientes, bg="#ffffff")
        self.tabela_frame.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.80)

        # colunas da tabela de clientes
        colunas = ("id", "nome", "telefone", "cpf", "email")

        # cria a tabela
        self.tabela = ttk.Treeview(
            self.tabela_frame,
            columns=colunas,
            show="headings"
        )

        # nomes do cabeçalho
        self.tabela.heading("id", text="ID")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("telefone", text="Telefone")
        self.tabela.heading("cpf", text="CPF")
        self.tabela.heading("email", text="Email")

        # largura e alinhamento das colunas
        self.tabela.column("id", width=50, anchor="center")
        self.tabela.column("nome", width=180, anchor="w")
        self.tabela.column("telefone", width=120, anchor="center")
        self.tabela.column("cpf", width=130, anchor="center")
        self.tabela.column("email", width=220, anchor="w")

        # coloca a tabela no frame
        self.tabela.place(relx=0, rely=0, relwidth=1, relheight=1)

        # evento de clique duplo para carregar cliente
        self.tabela.bind("<Double-1>", self.evento_duplo_clique)

        # estilo visual da tabela
        estilo = ttk.Style()
        estilo.theme_use("default")

        estilo.configure(
            "Treeview",
            background="#ffffff",
            foreground="#333333",
            rowheight=32,
            fieldbackground="#ffffff",
            borderwidth=0,
            font=("Arial", 10)
        )

        estilo.configure(
            "Treeview.Heading",
            background="#ffffff",
            foreground="#444444",
            font=("Arial", 10, "bold"),
            relief="flat"
        )

        estilo.map(
            "Treeview",
            background=[("selected", "#d9edf7")],
            foreground=[("selected", "#222222")]
        )

    # =========================================================
    # MOSTRAR / ESCONDER ENDEREÇO
    # =========================================================
    def alternar_endereco(self):

        # se já estiver visível, esconde
        if self.endereco_visivel:
            self.area_endereco.place_forget()
            self.endereco_visivel = False

        # se não estiver visível, mostra
        else:
            self.mostrar_endereco()
            self.endereco_visivel = True

    # =========================================================
    # MOSTRAR CAMPOS DE ENDEREÇO
    # =========================================================
    def mostrar_endereco(self):

        # posiciona a área de endereço
        self.area_endereco.place(relx=0.40, rely=0.75, relwidth=0.55, relheight=0.20)

        # apaga os widgets antigos para não duplicar
        for widget in self.area_endereco.winfo_children():
            widget.destroy()

        # cria os campos de endereço
        self.criar_campo_endereco("CEP", 0.00, 0.00, 0.18, "ent_cep")
        self.criar_campo_endereco("Número", 0.22, 0.00, 0.15, "ent_numero")
        self.criar_campo_endereco("Cidade", 0.41, 0.00, 0.25, "ent_cidade")
        self.criar_campo_endereco("Bairro", 0.70, 0.00, 0.25, "ent_bairro")

        self.criar_campo_endereco("Logradouro", 0.00, 0.45, 0.45, "ent_logradouro")
        self.criar_campo_endereco("Complemento", 0.49, 0.45, 0.46, "ent_complemento")

    # =========================================================
    # CRIAR CAMPO DE ENDEREÇO
    # =========================================================
    def criar_campo_endereco(self, texto, pos_x, pos_y, largura, nome_atributo):

        # cria o texto do campo
        lbl = tk.Label(
            self.area_endereco,
            text=texto,
            bg="#f5f5f5",
            fg="#333333",
            font=("Arial", 11, "bold")
        )
        lbl.place(relx=pos_x, rely=pos_y)

        # cria a entrada do campo
        ent = tk.Entry(
            self.area_endereco,
            font=("Arial", 12),
            bg="#cfcfcf",
            fg="#222222",
            relief="flat"
        )
        ent.place(relx=pos_x, rely=pos_y + 0.20, relwidth=largura, relheight=0.22)

        # salva esse campo na classe
        setattr(self, nome_atributo, ent)

    # =========================================================
    # SALVAR CLIENTE
    # =========================================================
    def salvar_cliente(self):

        # pega os dados digitados
        nome = self.ent_nome.get().strip()
        telefone = self.ent_telefone.get().strip()
        cpf = self.ent_cpf.get().strip()
        email = self.ent_email.get().strip()

        # se os campos obrigatórios estiverem vazios, avisa
        if nome == "" or telefone == "":
            messagebox.showwarning("Aviso", "Preencha pelo menos Nome e Telefone.")
            return

        # tenta pegar os dados do endereço, se os campos existirem
        cep = self.pegar_valor_campo("ent_cep")
        numero = self.pegar_valor_campo("ent_numero")
        cidade = self.pegar_valor_campo("ent_cidade")
        bairro = self.pegar_valor_campo("ent_bairro")
        logradouro = self.pegar_valor_campo("ent_logradouro")
        complemento = self.pegar_valor_campo("ent_complemento")

        # =====================================================
        # SE NÃO ESTÁ EDITANDO, CADASTRA UM NOVO CLIENTE
        # =====================================================
        if self.cliente_em_edicao is None:

            cliente = {
                "id": self.proximo_id,
                "nome": nome,
                "telefone": telefone,
                "cpf": cpf,
                "email": email,
                "cep": cep,
                "numero": numero,
                "cidade": cidade,
                "bairro": bairro,
                "logradouro": logradouro,
                "complemento": complemento
            }

            # adiciona o cliente na lista
            self.clientes.append(cliente)

            # aumenta o próximo id
            self.proximo_id += 1

            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso.")

        # =====================================================
        # SE ESTÁ EDITANDO, ATUALIZA O CLIENTE EXISTENTE
        # =====================================================
        else:
            self.cliente_em_edicao["nome"] = nome
            self.cliente_em_edicao["telefone"] = telefone
            self.cliente_em_edicao["cpf"] = cpf
            self.cliente_em_edicao["email"] = email
            self.cliente_em_edicao["cep"] = cep
            self.cliente_em_edicao["numero"] = numero
            self.cliente_em_edicao["cidade"] = cidade
            self.cliente_em_edicao["bairro"] = bairro
            self.cliente_em_edicao["logradouro"] = logradouro
            self.cliente_em_edicao["complemento"] = complemento

            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso.")

            # sai do modo de edição
            self.cliente_em_edicao = None
            self.lbl_titulo.config(text="Novo Cliente")

        # atualiza a tabela
        self.atualizar_tabela()

        # limpa os campos
        self.limpar_campos()

    # =========================================================
    # ATUALIZAR TABELA
    # =========================================================
    def atualizar_tabela(self):

        # apaga tudo que já está na tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        # percorre a lista de clientes e insere cada um
        for cliente in self.clientes:
            self.tabela.insert(
                "",
                "end",
                values=(
                    cliente["id"],
                    cliente["nome"],
                    cliente["telefone"],
                    cliente["cpf"],
                    cliente["email"]
                )
            )

    # =========================================================
    # CARREGAR CLIENTE SELECIONADO PARA EDIÇÃO
    # =========================================================
    def carregar_cliente_selecionado(self):

        # pega o item selecionado
        item_selecionado = self.tabela.selection()

        # se não tiver nada selecionado, avisa
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente na tabela.")
            return

        # pega os valores da linha selecionada
        valores = self.tabela.item(item_selecionado[0], "values")

        # primeiro valor da tabela é o ID
        id_cliente = int(valores[0])

        # procura o cliente na lista
        for cliente in self.clientes:
            if cliente["id"] == id_cliente:
                self.cliente_em_edicao = cliente
                break

        # se encontrou o cliente, joga os dados nos campos
        if self.cliente_em_edicao:

            self.lbl_titulo.config(text="Editar Cliente")

            self.ent_nome.delete(0, tk.END)
            self.ent_nome.insert(0, self.cliente_em_edicao["nome"])

            self.ent_telefone.delete(0, tk.END)
            self.ent_telefone.insert(0, self.cliente_em_edicao["telefone"])

            self.ent_cpf.delete(0, tk.END)
            self.ent_cpf.insert(0, self.cliente_em_edicao["cpf"])

            self.ent_email.delete(0, tk.END)
            self.ent_email.insert(0, self.cliente_em_edicao["email"])

            # mostra a área de endereço automaticamente
            if not self.endereco_visivel:
                self.alternar_endereco()

            self.preencher_campo_se_existir("ent_cep", self.cliente_em_edicao.get("cep", ""))
            self.preencher_campo_se_existir("ent_numero", self.cliente_em_edicao.get("numero", ""))
            self.preencher_campo_se_existir("ent_cidade", self.cliente_em_edicao.get("cidade", ""))
            self.preencher_campo_se_existir("ent_bairro", self.cliente_em_edicao.get("bairro", ""))
            self.preencher_campo_se_existir("ent_logradouro", self.cliente_em_edicao.get("logradouro", ""))
            self.preencher_campo_se_existir("ent_complemento", self.cliente_em_edicao.get("complemento", ""))

    # =========================================================
    # EXCLUIR CLIENTE
    # =========================================================
    def excluir_cliente(self):

        # pega o item selecionado
        item_selecionado = self.tabela.selection()

        # se não tiver selecionado, avisa
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return

        # pega os valores da linha
        valores = self.tabela.item(item_selecionado[0], "values")
        id_cliente = int(valores[0])

        # pergunta se o usuário confirma
        resposta = messagebox.askyesno("Confirmação", "Deseja realmente excluir este cliente?")

        if not resposta:
            return

        # recria a lista sem o cliente escolhido
        self.clientes = [cliente for cliente in self.clientes if cliente["id"] != id_cliente]

        # limpa edição
        self.cliente_em_edicao = None
        self.lbl_titulo.config(text="Novo Cliente")

        # atualiza tabela
        self.atualizar_tabela()

        # limpa campos
        self.limpar_campos()

        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")

    # =========================================================
    # LIMPAR CAMPOS
    # =========================================================
    def limpar_campos(self):

        # limpa os campos principais
        self.ent_nome.delete(0, tk.END)
        self.ent_telefone.delete(0, tk.END)
        self.ent_cpf.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)

        # limpa os campos de endereço se existirem
        self.limpar_campo_se_existir("ent_cep")
        self.limpar_campo_se_existir("ent_numero")
        self.limpar_campo_se_existir("ent_cidade")
        self.limpar_campo_se_existir("ent_bairro")
        self.limpar_campo_se_existir("ent_logradouro")
        self.limpar_campo_se_existir("ent_complemento")

        # sai do modo edição
        self.cliente_em_edicao = None

        # volta o título para novo cliente
        self.lbl_titulo.config(text="Novo Cliente")

    # =========================================================
    # BUSCAR CLIENTE
    # =========================================================
    def buscar_cliente(self):

        # pega o texto digitado
        texto_busca = self.ent_busca.get().strip().lower()

        # limpa a tabela antes de mostrar o resultado
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        # se a busca estiver vazia, mostra todos
        if texto_busca == "":
            self.atualizar_tabela()
            return

        # filtra os clientes pelo nome, telefone, cpf ou email
        for cliente in self.clientes:
            if (
                texto_busca in cliente["nome"].lower()
                or texto_busca in cliente["telefone"].lower()
                or texto_busca in cliente["cpf"].lower()
                or texto_busca in cliente["email"].lower()
            ):
                self.tabela.insert(
                    "",
                    "end",
                    values=(
                        cliente["id"],
                        cliente["nome"],
                        cliente["telefone"],
                        cliente["cpf"],
                        cliente["email"]
                    )
                )

    # =========================================================
    # EVENTO DE DUPLO CLIQUE NA TABELA
    # =========================================================
    def evento_duplo_clique(self, event):

        # chama a função de carregar cliente
        self.carregar_cliente_selecionado()

    # =========================================================
    # FUNÇÃO AUXILIAR PARA PEGAR VALOR DE CAMPO
    # =========================================================
    def pegar_valor_campo(self, nome_campo):

        # verifica se o atributo existe na classe
        if hasattr(self, nome_campo):
            return getattr(self, nome_campo).get().strip()

        return ""

    # =========================================================
    # FUNÇÃO AUXILIAR PARA LIMPAR CAMPO
    # =========================================================
    def limpar_campo_se_existir(self, nome_campo):

        # verifica se o campo existe
        if hasattr(self, nome_campo):
            getattr(self, nome_campo).delete(0, tk.END)

    # =========================================================
    # FUNÇÃO AUXILIAR PARA PREENCHER CAMPO
    # =========================================================
    def preencher_campo_se_existir(self, nome_campo, valor):

        # verifica se o campo existe
        if hasattr(self, nome_campo):
            campo = getattr(self, nome_campo)
            campo.delete(0, tk.END)
            campo.insert(0, valor)


# =========================================================
# PARTE PRINCIPAL
# =========================================================
if __name__ == "__main__":

    # cria a janela principal
    root = tk.Tk()

    # cria a aplicação
    app = JanelaClientes(root)

    # mantém a janela aberta
    root.mainloop()