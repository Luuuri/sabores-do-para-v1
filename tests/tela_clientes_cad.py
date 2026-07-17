# importa a biblioteca tkinter e dá o apelido de tk
import tkinter as tk
import customtkinter as ctk

# importa o ttk, usado aqui para criar a tabela de pedidos
from tkinter import ttk

# Controller
from app.controller.cliente_controller import salvar_cliente


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class JanelaClientes:
    def __init__(self, root, on_voltar=None):
        self.root = root
        self.on_voltar = on_voltar

        self.root.title("Clientes")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        self.root.minsize(1100, 650)

        self.endereco_visivel = False
        self.cliente_em_edicao = None

        self.criar_topo()
        self.criar_menu_lateral()
        self.criar_titulo()
        self.criar_formulario_cliente()
        self.criar_area_pedidos()
        self._linhas = {}

    # MÉTODO: CRIAR TOPO
    def criar_topo(self):
        self.barra_topo = tk.Frame(self.root, bg="#d9d9d9")
        self.barra_topo.place(relx=0, rely=0, relwidth=1, relheight=0.08)

        self.lbl_icone_casa = tk.Label(self.barra_topo, text="⌂", bg="#d9d9d9", fg="#444444", font=("Arial", 16, "bold"))
        self.lbl_icone_casa.place(relx=0.015, rely=0.25)

        self.lbl_titulo_topo = tk.Label(self.barra_topo, text="Clientes", bg="#d9d9d9", fg="#222222", font=("Arial", 14, "bold"))
        self.lbl_titulo_topo.place(relx=0.09, rely=0.28)

        self.lbl_icone_config = tk.Label(self.barra_topo, text="⚙", bg="#d9d9d9", fg="#444444", font=("Arial", 16))
        self.lbl_icone_config.place(relx=0.965, rely=0.25)

    # MÉTODO: CRIAR MENU LATERAL
    def criar_menu_lateral(self):
        self.menu_lateral = tk.Frame(self.root, bg="#f0f0f0")
        self.menu_lateral.place(relx=0, rely=0.08, relwidth=0.06, relheight=0.92)

        self.lbl_menu = tk.Label(self.menu_lateral, text="☰", bg="#f0f0f0", fg="#555555", font=("Arial", 18))
        self.lbl_menu.place(relx=0.30, rely=0.02)

        self.lbl_sair = tk.Label(self.menu_lateral, text="⏻", bg="#f0f0f0", fg="#555555", font=("Arial", 18))
        self.lbl_sair.place(relx=0.30, rely=0.94)

    # MÉTODO: CRIAR TÍTULO DA PÁGINA
    def criar_titulo(self):
        self.lbl_voltar = tk.Label(self.root, text="←", bg="#f5f5f5", fg="#333333", font=("Arial", 18, "bold"))
        self.lbl_voltar.place(relx=0.085, rely=0.12)

        self.lbl_titulo = tk.Label(self.root, text="Novo Cliente", bg="#f5f5f5", fg="#111111", font=("Arial", 22, "bold"))
        self.lbl_titulo.place(relx=0.115, rely=0.118)

    # MÉTODO: CRIAR FORMULÁRIO DO CLIENTE
    def criar_formulario_cliente(self):
        self.area_formulario = tk.Frame(self.root, bg="#f5f5f5")
        self.area_formulario.place(relx=0.08, rely=0.18, relwidth=0.30, relheight=0.70)

        self.criar_campo(self.area_formulario, "Nome *", 0.00, "ent_nome")
        self.criar_campo(self.area_formulario, "Telefone *", 0.14, "ent_telefone")
        self.criar_campo(self.area_formulario, "CPF", 0.28, "ent_cpf")
        self.criar_campo(self.area_formulario, "Email", 0.42, "ent_email")

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

        self.area_endereco = tk.Frame(self.root, bg="#f5f5f5")

    # MÉTODO: CRIAR UM CAMPO PADRÃO
    def criar_campo(self, janela, texto, pos_y, nome_atributo):
        lbl = tk.Label(janela, text=texto, bg="#f5f5f5", fg="#333333", font=("Arial", 11, "bold"))
        lbl.place(relx=0.00, rely=pos_y)

        ent = tk.Entry(janela, font=("Arial", 12), bg="#cfcfcf", fg="#222222", relief="flat")
        ent.place(relx=0.00, rely=pos_y + 0.05, relwidth=0.62, relheight=0.07)

        setattr(self, nome_atributo, ent)

    # MÉTODO: CRIAR ÁREA DE PEDIDOS
    def criar_area_pedidos(self):
        self.area_pedidos = tk.Frame(self.root, bg="#dcdcdc")
        self.area_pedidos.place(relx=0.40, rely=0.23, relwidth=0.49, relheight=0.32)

        self.ent_busca = tk.Entry(self.area_pedidos, font=("Arial", 11), relief="flat", bg="#ffffff", fg="#333333")
        self.ent_busca.insert(0, " Buscar Pedido...")
        self.ent_busca.place(relx=0.03, rely=0.05, relwidth=0.30, relheight=0.08)

        self.lbl_filtrar = tk.Label(self.area_pedidos, text="⌕ Filtrar", bg="#dcdcdc", fg="#777777", font=("Arial", 10, "bold"))
        self.lbl_filtrar.place(relx=0.36, rely=0.06)

        self.tabela_frame = tk.Frame(self.area_pedidos, bg="#ffffff")
        self.tabela_frame.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.78)

        colunas = ("id", "origem", "data", "status", "pagamento")
        self.tabela = ttk.Treeview(self.tabela_frame, columns=colunas, show="headings")

        self.tabela.heading("id", text="ID")
        self.tabela.heading("origem", text="Origem")
        self.tabela.heading("data", text="Data")
        self.tabela.heading("status", text="Status")
        self.tabela.heading("pagamento", text="Pagamento")

        self.tabela.column("id", width=70, anchor="center")
        self.tabela.column("origem", width=120, anchor="center")
        self.tabela.column("data", width=100, anchor="center")
        self.tabela.column("status", width=120, anchor="center")
        self.tabela.column("pagamento", width=120, anchor="center")

        self.tabela.place(relx=0, rely=0, relwidth=1, relheight=1)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#ffffff", foreground="#333333", rowheight=32, fieldbackground="#ffffff", borderwidth=0, font=("Arial", 10))
        estilo.configure("Treeview.Heading", background="#ffffff", foreground="#444444", font=("Arial", 10, "bold"), relief="flat")
        estilo.map("Treeview", background=[("selected", "#d9edf7")], foreground=[("selected", "#222222")])

    # MÉTODO: MOSTRAR OU ESCONDER ENDEREÇO
    def alternar_endereco(self):
        if self.endereco_visivel:
            self.area_endereco.place_forget()
            self.area_pedidos.place(relx=0.40, rely=0.23, relwidth=0.49, relheight=0.32)
            self.root.geometry("900x700")
            self.endereco_visivel = False
        else:
            self.mostrar_endereco()
            self.area_pedidos.place_forget()
            self.root.geometry("1366x860")
            self.endereco_visivel = True

    # MÉTODO: MOSTRAR ENDEREÇO
    def mostrar_endereco(self):
        self.area_endereco.place(relx=0.40, rely=0.18, relwidth=0.53, relheight=0.52)

        for widget in self.area_endereco.winfo_children():
            widget.destroy()

        self.criar_campo_endereco("Nome", 0.00, 0.00, 0.86)
        self.criar_campo_endereco("CEP", 0.00, 0.18, 0.38)
        self.criar_campo_endereco("Número", 0.50, 0.18, 0.36)
        self.criar_campo_endereco("Logradouro", 0.00, 0.36, 0.86)
        self.criar_campo_endereco("Complemento/Referência", 0.00, 0.54, 0.86)
        self.criar_campo_endereco("Bairro", 0.00, 0.72, 0.38)
        self.criar_campo_endereco("Cidade", 0.52, 0.72, 0.34)

    # MÉTODO: CRIAR CAMPO DE ENDEREÇO
    def criar_campo_endereco(self, texto, pos_x, pos_y, largura):
        lbl = tk.Label(self.area_endereco, text=texto, bg="#f5f5f5", fg="#333333", font=("Arial", 11, "bold"))
        lbl.place(relx=pos_x, rely=pos_y)

        ent = tk.Entry(self.area_endereco, font=("Arial", 12), bg="#cfcfcf", fg="#222222", relief="flat")
        ent.place(relx=pos_x, rely=pos_y + 0.06, relwidth=largura, relheight=0.08)

    # MÉTODO: SALVAR CLIENTE
    def salvar_cliente(self):
        nome = self.ent_nome.get().strip()
        telefone = self.ent_telefone.get().strip()
        cpf = self.ent_cpf.get().strip()
        email = self.ent_email.get().strip()

        if nome == "" or telefone == "":
            from tkinter import messagebox
            messagebox.showwarning("Aviso", "Preencha menos Nome e Telefone.")
            return

        cep = self.pegar_valor_campo("ent_cep") if hasattr(self, "ent_cep") else ""
        numero = self.pegar_valor_campo("ent_numero") if hasattr(self, "ent_numero") else ""
        cidade = self.pegar_valor_campo("ent_cidade") if hasattr(self, "ent_cidade") else ""
        bairro = self.pegar_valor_campo("ent_bairro") if hasattr(self, "ent_bairro") else ""
        logradouro = self.pegar_valor_campo("ent_logradouro") if hasattr(self, "ent_logradouro") else ""
        complemento = self.pegar_valor_campo("ent_complemento") if hasattr(self, "ent_complemento") else ""

        dados = {
            "id": self.cliente_em_edicao,
            "nome": nome,
            "telefone": telefone,
            "cpf": cpf,
            "email": email,
            "cep": cep,
            "numero": numero,
            "cidade": cidade,
            "bairro": bairro,
            "logradouro": logradouro,
            "complemento": complemento,
        }

        salvar_cliente(dados)

        from tkinter import messagebox
        messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")

        self.limpar_campos()
        if self.on_voltar:
            self.on_voltar()

    # MÉTODO: LIMPAR CAMPOS
    def limpar_campos(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_telefone.delete(0, tk.END)
        self.ent_cpf.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)

        self.limpar_campo_se_existir("ent_cep")
        self.limpar_campo_se_existir("ent_numero")
        self.limpar_campo_se_existir("ent_cidade")
        self.limpar_campo_se_existir("ent_bairro")
        self.limpar_campo_se_existir("ent_logradouro")
        self.limpar_campo_se_existir("ent_complemento")

        self.cliente_em_edicao = None
        self.lbl_titulo.config(text="Novo Cliente")

    # MÉTODO: PREENCHER EXEMPLO DE EDIÇÃO
    def preencher_exemplo_edicao(self):
        self.lbl_titulo.config(text="Editar Cliente")
        self.ent_nome.delete(0, tk.END)
        self.ent_nome.insert(0, "Débora Diniz")
        self.ent_telefone.delete(0, tk.END)
        self.ent_telefone.insert(0, "(93) 9 9152-9220")
        self.tabela.insert("", "end", values=("#004", "Mesa 2", "04/04/26", "Entregue", "Pago"))

    # MÉTODO: AUXILIARES
    def pegar_valor_campo(self, nome_campo):
        if hasattr(self, nome_campo):
            return getattr(self, nome_campo).get().strip()
        return ""

    def limpar_campo_se_existir(self, nome_campo):
        if hasattr(self, nome_campo):
            getattr(self, nome_campo).delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = JanelaClientes(root)
    root.mainloop()