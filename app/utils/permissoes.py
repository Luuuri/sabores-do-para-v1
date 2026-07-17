from app.utils.usuario_atual import usuario_atual
import customtkinter as ctk

TELAS = {
    "administrador": ["caixa", "clientes", "estoque", "funcionarios", "produtos", "relatorios"],
    "funcionario":   ["caixa", "clientes", "produtos"],
}

ACOES = {
    "administrador": {
        "clientes": ["ver", "adicionar", "editar", "excluir"],
        "produtos": ["ver", "adicionar", "editar", "excluir"],
        "caixa":    ["ver", "adicionar", "editar", "excluir", "cancelar", "desfazer_status"],
    },
    "funcionario": {
        "clientes": ["ver", "adicionar", "editar"],
        "produtos": ["ver"],
        "caixa":    ["ver", "adicionar", "editar", "desfazer_status"],
    },
}

def nivel() -> str:
    return usuario_atual.get("nivel_acesso") or "funcionario"

def eh_admin() -> bool:
    return nivel() == "administrador"

def tem_tela(tela: str) -> bool:
    return tela in TELAS.get(nivel(), [])

def tem_acao(modulo: str, acao: str) -> bool:
    return acao in ACOES.get(nivel(), {}).get(modulo, [])

def bloquear_se_sem_acesso(tela: str, master, callback_voltar) -> bool:
    """
    Chama no início de cada view restrita.
    Retorna True se bloqueou, False se pode continuar.
    """
    if tem_tela(tela):
        return False

    from app.utils.estilos import get_cores, Fontes
    cores  = get_cores()
    fontes = Fontes()

    popup = ctk.CTkToplevel(master)
    popup.title("Acesso restrito")
    popup.geometry("360x180")
    popup.grab_set()
    popup.resizable(False, False)
    popup.configure(fg_color=cores.fundo.principal)

    ctk.CTkLabel(
        popup, text="Acesso restrito",
        font=fontes.subtitulo,
        text_color=cores.texto.vermelho
    ).pack(pady=(28, 6))

    ctk.CTkLabel(
        popup,
        text="Você não tem permissão para acessar esta área.\nFale com o administrador.",
        font=fontes.sub_info,
        text_color=cores.texto.passivo,
        justify="center"
    ).pack(pady=(0, 20))

    def fechar():
        popup.destroy()
        if callback_voltar:
            callback_voltar()

    ctk.CTkButton(
        popup, text="Voltar",
        fg_color=cores.botao.primario,
        hover_color=cores.botao.primario_hover,
        text_color=cores.texto.branco,
        font=fontes.texto_info,
        width=200,
        command=fechar
    ).pack()

    popup.protocol("WM_DELETE_WINDOW", fechar)
    return True

def pedir_senha_admin(master, callback):
    """Popup pedindo senha do admin antes de executar ação restrita."""
    from app.utils.estilos import get_cores, Fontes
    from app.model.login_model import autenticar_admin_por_senha

    cores  = get_cores()
    fontes = Fontes()

    popup = ctk.CTkToplevel(master)
    popup.title("Confirmação")
    popup.geometry("360x220")
    popup.grab_set()
    popup.resizable(False, False)
    popup.configure(fg_color=cores.fundo.principal)

    ctk.CTkLabel(
        popup, text="Ação restrita",
        font=fontes.subtitulo,
        text_color=cores.texto.vermelho
    ).pack(pady=(24, 4))

    ctk.CTkLabel(
        popup,
        text="Digite a senha do administrador para continuar.",
        font=fontes.sub_info,
        text_color=cores.texto.passivo,
        justify="center"
    ).pack(pady=(0, 12))

    entrada = ctk.CTkEntry(
        popup,
        placeholder_text="Senha do administrador",
        show="*", width=280,
        fg_color=cores.entry.formulario,
        border_color=cores.input.borda_entry
    )
    entrada.pack(pady=(0, 6))
    entrada.focus()

    lbl_erro = ctk.CTkLabel(
        popup, text="",
        font=fontes.sub_info,
        text_color=cores.texto.vermelho
    )
    lbl_erro.pack()

    def confirmar():
        senha = entrada.get().strip()
        if not senha:
            lbl_erro.configure(text="Digite a senha.")
            return
        if autenticar_admin_por_senha(senha):
            popup.destroy()
            callback()
        else:
            lbl_erro.configure(text="Senha incorreta.")
            entrada.delete(0, "end")
            entrada.focus()

    ctk.CTkButton(
        popup, text="Confirmar",
        fg_color=cores.botao.primario,
        hover_color=cores.botao.primario_hover,
        text_color=cores.texto.branco,
        font=fontes.texto_info,
        width=280,
        command=confirmar
    ).pack(pady=(8, 0))

    entrada.bind("<Return>", lambda e: confirmar())
    popup.protocol("WM_DELETE_WINDOW", popup.destroy)