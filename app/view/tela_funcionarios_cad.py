"""
tela_funcionarios_cad.py - Cadastro e edição de funcionários.

Recebe callbacks do Controller (salvar, excluir, voltar, home) e usa componentes reutilizáveis.
"""
import re
import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import (
    Frames, Botoes, Titulos, DialogoConfirmacao
)
from app.utils.validacoes import validar_celular, formatar_celular

# Conexão com o Controller (callbacks)
from app.controller.funcionario_controller import salvar_funcionario

def main():
    """Ponto de entrada para testar a tela isolada (sem o sistema completo)."""
    root = ctk.CTk()
    root.title("Sabores do Pará - Funcionários")
    root.geometry("1100x700")

    fontes = Fontes()
    icones = Icones()
    cores  = get_cores()

    tela = TelaFuncionarios(
        root, cores, fontes, icones,
        on_salvar=salvar_funcionario,
        on_voltar=root.destroy,
    )
    root.mainloop()


# ── TELA PRINCIPAL ─────────────────────────────────────────────────────────────
class TelaFuncionarios(Frames.FrameLayoutPadrao):
    """
    Tela de cadastro/edição. Recebe callbacks do Controller e usa componentes reutilizáveis.
    API: .preencher_dados(dict), .limpar_formulario(), .definir_modo('novo'/'editar')
    """
    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_salvar=None, on_excluir=None,
                 on_home=None, menu_callbacks=None, on_click_titulo=None,
                 show_password_button=True, mostrar_senha_no_editar=False):
        super().__init__(master, cores, fontes, icones,
                        titulo="Funcionários", icone=icones.funcionarios,
                        on_novo=None, on_home=on_home,
                        menu_callbacks=menu_callbacks,
                        on_click_titulo=on_click_titulo)
        self.cores, self.fontes, self.icones = cores, fontes, icones
        self.on_voltar = on_voltar
        self.on_salvar, self.on_excluir = on_salvar, on_excluir
        self.show_password_button = show_password_button
        self.mostrar_senha_no_editar = mostrar_senha_no_editar

        self.id_funcionario = None  # None = novo cadastro
        self._modo = "novo"
        self._criar_formulario()

    # ── Modo (novo/editar) ───────────────────────────────────────────────────
    def definir_modo(self, modo: str):
        """'novo' oculta senha/excluir; 'editar' mostra se permitido."""
        self._modo = modo
        self.frame_cadastro.definir_modo(modo)
        self.frame_comandos.mostrar_excluir(modo == "editar")
        if modo == "novo" or (modo == "editar" and self.mostrar_senha_no_editar):
            self._mostrar_senha_frame()
        else:
            self._ocultar_senha_frame()

    def _mostrar_senha_frame(self):
        self.frame_senha.grid()
        self.frame_cadastro.visivel_senha = True

    def _ocultar_senha_frame(self):
        self.frame_senha.ocultar_campos()
        self.frame_cadastro.visivel_senha = False
        self.frame_senha.limpar()

    # ── Dados ──────────────────────────────────────────────────────────────────
    def obter_dados(self) -> dict:
        """Coleta campos da tela. Retorna dict para o Controller."""
        tel = self.frame_cadastro.telefone.get() if hasattr(self.frame_cadastro, "telefone") else ""
        # Normaliza para o formato esperado: (DD) D DDDD-DDDD
        tel_numeros = re.sub(r"\D", "", tel)[:11]
        tel_norm = ""
        if len(tel_numeros) >= 1:
            tel_norm += "(" + tel_numeros[:2]
        if len(tel_numeros) >= 3:
            tel_norm += ") " + tel_numeros[2:3]
        if len(tel_numeros) >= 4:
            tel_norm += " " + tel_numeros[3:7]
        if len(tel_numeros) >= 8:
            tel_norm += "-" + tel_numeros[7:11]
        tel = tel_norm







        return {
            "id":        self.id_funcionario,
            "nome":      self.frame_cadastro.nome.get(),
            "email":     self.frame_cadastro.email.get(),
            "telefone":  tel,
            "cargo":     self.frame_cadastro.cargo.get(),
            "ativo":     self.frame_cadastro.get_ativo(),
            "is_entregador": self.frame_cadastro.get_entregador(),
            "senha":     self.frame_senha.senha.get() if self.frame_cadastro.visivel_senha else None,
        }



    def preencher_dados(self, dados: dict):
        """Preenche formulário e muda para modo 'editar'."""
        self.id_funcionario = dados.get("id")
        self.frame_cadastro.preencher_dados(dados)
        self.definir_modo("editar")
        # Garantia extra: manter o painel de senha oculto até o botão ser apertado.
        if not self.mostrar_senha_no_editar:
            self._ocultar_senha_frame()

    # ── Ações dos botões ───────────────────────────────────────────────────────
    def acao_salvar(self):
        """Valida campos e chama on_salvar(dados) do Controller."""
        dados = self.obter_dados()
        erros = self._validar_dados(dados)
        if erros:
            self.frame_cadastro.mostrar_feedback(erros, tipo="erro")
            return
        try:
            self.on_salvar(dados)
            self.frame_cadastro.mostrar_feedback("Salvo com sucesso!", tipo="sucesso")
            if self.on_voltar:
                self.after(300, self.on_voltar)
        except Exception as e:
            self.frame_cadastro.mostrar_feedback(str(e), tipo="erro")

    def acao_cancelar(self):
        self.limpar_formulario()
        if self.on_voltar:
            self.on_voltar()

    def acao_voltar(self):
        self.limpar_formulario()
        if self.on_voltar:
            self.on_voltar()

    def acao_excluir(self):
        """Abre diálogo de confirmação antes de excluir."""
        if not self.on_excluir or self.id_funcionario is None:
            return
        DialogoConfirmacao(
            self.winfo_toplevel(), self.cores, self.fontes,
            titulo="Excluir Funcionário",
            mensagem="Tem certeza que deseja excluir este funcionário? Esta ação não pode ser desfeita.",
            on_confirmar=self._confirmar_exclusao,
        )

    def _confirmar_exclusao(self):
        try:
            self.on_excluir(self.id_funcionario)
            self.limpar_formulario()
            if self.on_voltar:
                self.on_voltar()
        except Exception as e:
            self.frame_cadastro.mostrar_feedback(str(e), tipo="erro")

    def limpar_formulario(self):
        """Reseta campos e volta para modo 'novo'."""
        self.id_funcionario = None
        self.frame_cadastro.nome.set("")
        self.frame_cadastro.email.set("")
        self.frame_cadastro.telefone.set("")
        self.frame_cadastro.cargo.set("Funcionário")
        self.frame_cadastro.set_ativo(True)
        self.frame_cadastro.set_entregador(False)
        self.frame_cadastro.mostrar_feedback("")

        self._ocultar_senha_frame()
        self.definir_modo("novo")

    # ── Validação ──────────────────────────────────────────────────────────────
    def _validar_dados(self, dados) -> str | None:
        """Valida campos. Retorna string de erros ou None."""
        erros = []
        if not dados["nome"].strip():
            erros.append("• Nome é obrigatório")
        if not dados["email"].strip():
            erros.append("• Email é obrigatório")
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", dados["email"].strip()):
            erros.append("• Email inválido (deve conter @)")

        # Telefone é obrigatório
        if not dados.get("telefone", "").strip():
            erros.append("• Telefone é obrigatório")
        else:
            tel = dados["telefone"].strip()
            # Normaliza para o formato esperado: (DD) D  DDDD-DDDD
            tel_numeros = re.sub(r"\D", "", tel)[:11]
            tel_norm = ""
            if len(tel_numeros) >= 1:
                tel_norm += "(" + tel_numeros[:2]
            if len(tel_numeros) >= 3:
                tel_norm += ") " + tel_numeros[2:3]
            if len(tel_numeros) >= 4:
                tel_norm += " " + tel_numeros[3:7]
            if len(tel_numeros) >= 8:
                tel_norm += "-" + tel_numeros[7:11]

            if not validar_celular(tel_norm):
                erros.append("• Telefone inválido")


        # Senha: obrigatória apenas no cadastro; em edição é opcional
        if self.frame_cadastro.visivel_senha:
            senha = (self.frame_senha.senha.get() or "").strip()
            confirmar = (self.frame_senha.confirmar_senha.get() or "").strip()
            if self._modo == "novo":
                if not senha:
                    erros.append("• Senha é obrigatória")
                if senha and senha != confirmar:
                    erros.append("• As senhas não coincidem")
            else:
                # modo editar: se preencher um dos campos, exige ambos e que coincidam
                if senha or confirmar:
                    if not senha:
                        erros.append("• Senha é obrigatória")
                    if not confirmar:
                        erros.append("• Confirme a senha")
                    if senha and confirmar and senha != confirmar:
                        erros.append("• As senhas não coincidem")
        return "\n".join(erros) if erros else None

    # ── Layout ─────────────────────────────────────────────────────────────────
    def _criar_formulario(self):
        conteudo = ctk.CTkFrame(self, fg_color="transparent")
        conteudo.place(relx=0.08, rely=0.10, relwidth=0.85, relheight=0.80)

        conteudo.grid_columnconfigure(0, weight=2)  # formulário principal
        conteudo.grid_columnconfigure(1, weight=1)  # painel de senha
        conteudo.grid_rowconfigure(0, weight=1)      # formulário
        conteudo.grid_rowconfigure(1, weight=0)      # botões salvar/cancelar

        # Formulário principal (nome, cargo, email, ativo)
        self.frame_cadastro = Frames.FrameCadastro(
            conteudo, self.cores, self.fontes, self.icones,
            modo=self._modo,
            show_password_button=self.show_password_button,
            show_password_button_edit_mode=not self.mostrar_senha_no_editar,
        )
        self.frame_cadastro.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_cadastro.voltar_bttn.configure(command=self.acao_voltar)

        # Painel de senha (lado direito, visível apenas no modo novo)
        self.frame_senha = Frames.FrameSenha(conteudo, self.cores, self.fontes, self.icones,
                                             on_toggle=self.frame_cadastro.toggle_senha)
        self.frame_senha.grid(row=0, column=1, sticky="nsew", padx=10, pady=(150, 10))
        self.frame_cadastro.senha_frame = self.frame_senha  # liga ao formulário

        # Botões Salvar/Cancelar/Excluir
        self.frame_comandos = Frames.FrameComandos(
            conteudo, self.cores, self.fontes, self.icones, modo=self._modo
        )
        self.frame_comandos.grid(row=1, column=0, columnspan=2, sticky="ew", pady=20)
        self.frame_comandos.set_callbacks(
            salvar=self.acao_salvar,
            cancelar=self.acao_cancelar,
            excluir=self.acao_excluir,
        )

        self._mostrar_senha_frame()  # modo novo: senha obrigatória


if __name__ == "__main__":
    main()
