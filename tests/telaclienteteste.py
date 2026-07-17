import customtkinter as ctk

from app.utils.componentes import Frames, TabelaGenerica, Campos, Botoes
from app.utils.estilos import Cores, Fontes, Icones

from app.utils.validacoes import (
    validar_email,
    validar_celular,
    formatar_celular,
    formatar_cpf,
    cpf_valido
)


class TelaClientes:

    def __init__(self, root):
        self.root = root

        self.cores = Cores()
        self.fontes = Fontes()
        self.icones = Icones()

        self.configurar_janela()
        self.criar_layout()
        self.criar_formulario()
        self.criar_tabela()

    def configurar_janela(self):
        self.root.title("Clientes")
        self.root.geometry("1100x700")
        self.root.minsize(1100, 650)

    def criar_layout(self):
        self.layout = Frames.FrameLayoutPadrao(
            self.root,
            self.cores,
            self.fontes,
            self.icones,
            titulo="Clientes",
            icone=self.icones.clientes
        )

        self.layout.pack(fill="both", expand=True)

        self.frame_conteudo = Frames.FrameConteudoTabela(
            self.layout,
            self.cores,
            padx=80,
            pady=50
        )

    def criar_formulario(self):
        self.frame_formulario = ctk.CTkFrame(
            self.frame_conteudo,
            fg_color="transparent"
        )

        self.frame_formulario.pack(
            side="left",
            fill="y",
            padx=20,
            pady=20
        )

        self.campo_nome = Campos.CampoTexto(
            self.frame_formulario,
            "Nome Completo",
            "Digite o nome completo do cliente",
            self.cores,
            self.fontes
        )
        self.campo_nome.pack(fill="x", pady=5)

        self.campo_telefone = Campos.CampoTexto(
            self.frame_formulario,
            "Telefone",
            "Digite o telefone do cliente",
            self.cores,
            self.fontes
        )
        self.campo_telefone.pack(fill="x", pady=5)

        self.campo_telefone.entry.bind(
            "<KeyRelease>",
            lambda event: formatar_celular(event, self.campo_telefone.entry)
        )

        self.campo_cpf = Campos.CampoTexto(
            self.frame_formulario,
            "CPF",
            "Digite o CPF do cliente",
            self.cores,
            self.fontes
        )
        self.campo_cpf.pack(fill="x", pady=5)

        self.campo_cpf.entry.bind(
            "<KeyRelease>",
            lambda event: formatar_cpf(event, self.campo_cpf.entry)
        )

        self.campo_email = Campos.CampoTexto(
            self.frame_formulario,
            "Email",
            "Digite o email do cliente",
            self.cores,
            self.fontes
        )
        self.campo_email.pack(fill="x", pady=5)

        self.botao_salvar = Botoes.BotaoSalvar(
            self.frame_formulario,
            self.cores,
            self.fontes
        )

        self.botao_salvar.pack(
            pady=20,
            fill="x"
        )

        self.botao_salvar.configure(
            command=self.salvar_cliente
        )

    def criar_tabela(self):
        self.tabela = TabelaGenerica(
            self.frame_conteudo,
            self.cores,
            self.fontes,
            self.icones,
            colunas=[
                ("Nome", "nome"),
                ("Telefone", "telefone"),
                ("CPF", "cpf"),
                ("Email", "email"),
            ],
            mostrar_busca=True,
            mostrar_filtros=True
        )

        self.tabela.pack(
            side="left",
            expand=True,
            fill="both",
            padx=20,
            pady=20
        )

    def salvar_cliente(self):
        nome = self.campo_nome.get().strip()
        telefone = self.campo_telefone.get().strip()
        cpf = self.campo_cpf.get().strip()
        email = self.campo_email.get().strip()

        if not nome:
            print("Digite o nome do cliente")
            return

        if not telefone:
            print("Digite o telefone do cliente")
            return

        if not validar_celular(telefone):
            print("Digite o telefone no formato (93)99999-9999")
            return

        if not cpf:
            print("Digite o CPF do cliente")
            return

        if not cpf_valido(cpf):
            print("CPF inválido")
            return

        if email and not validar_email(email):
            print("Email inválido")
            return

        cliente = {
            "nome": nome,
            "telefone": telefone,
            "cpf": cpf,
            "email": email
        }

        print(cliente)

        self.limpar_campos()

    def limpar_campos(self):
        self.campo_nome.set("")
        self.campo_telefone.set("")
        self.campo_cpf.set("")
        self.campo_email.set("")


if __name__ == "__main__":
    root = ctk.CTk()
    app = TelaClientes(root)
    root.mainloop()