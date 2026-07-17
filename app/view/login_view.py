import tkinter as tk
import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones
from tkinter import messagebox
from app.utils.validacoes import validar_email


class LoginView(ctk.CTkToplevel):
    def __init__(self, master, on_ready=None):
        super().__init__(master)
        self._on_ready = on_ready
        self.withdraw()
        self.title("Sabores do Pará")
        self.resizable(True, True)
        self.minsize(1530, 950)
        self.cores = get_cores()
        self.fontes = Fontes()
        self.configure(fg_color=self.cores.texto.cinza_muito_claro)
        self.protocol("WM_DELETE_WINDOW", self._fechar_app)
        self.after_idle(self._inicializar_ui)

    def _inicializar_ui(self):
        largura_tela = self.winfo_screenwidth()
        altura_tela  = self.winfo_screenheight()
        self.geometry(f"{largura_tela}x{altura_tela}+0+0")
        logo_w = int(largura_tela * 0.10)
        logo_h = int(altura_tela  * 0.12)
        self.icones = Icones(logo_size=(logo_w, logo_h))
        self._build_ui(largura_tela, altura_tela)
        self.after_idle(self._notificar_pronto)

    def _notificar_pronto(self):
        if self._on_ready:
            self.after(10, lambda: self._on_ready(self))
        else:
            self.after(10, self.mostrar)

    def mostrar(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.after(0, lambda: self.state('zoomed'))
        if hasattr(self, "_painel_gradiente"):
            self.after(80, self._painel_gradiente.iniciar)

    def _recarregar_tema(self):
        self.cores = get_cores()
        self.configure(fg_color=self.cores.texto.cinza_muito_claro)
        if hasattr(self, "_painel_gradiente"):
            self._painel_gradiente.parar()
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass
        self._inicializar_ui()

    def _fechar_app(self):
        self.master.quit()
        self.destroy()

    def _build_ui(self, largura_tela, altura_tela):
        cores  = self.cores
        fontes = self.fontes
        icones = self.icones

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        largura_painel = int(largura_tela * 0.50)
        altura_painel  = int(altura_tela  * 1.0)

        from app.utils.gradiente_panel import GradientePainel
        self._painel_gradiente = GradientePainel(
            self, width=largura_painel, height=altura_painel,
            bg_outer=cores.texto.cinza_muito_claro, icones=self.icones, auto_start=False
        )
        self._painel_gradiente.place(relx=0.00, rely=0.00, relwidth=0.50, relheight=1.0)

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.place(relx=0.55, rely=0.12, relwidth=0.36, relheight=0.72)

        logo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        logo_frame.place(relx=0.00, rely=0.00, relwidth=0.77, relheight=0.16)
        ctk.CTkLabel(logo_frame, image=icones.logotipo, text="").place(relx=0.5, rely=0.00, anchor="n")

        ctk.CTkLabel(frame, text="Bem-vindo(a)", font=fontes.titulo_login,
                     text_color=cores.texto.verde_jambu).place(relx=0.00, rely=0.16)
        ctk.CTkLabel(frame, text="Acesse o sistema para gerenciar o restaurante.",
                     font=fontes.subtitulo_login,
                     text_color=cores.texto.verde_jambu).place(relx=0.00, rely=0.23)

        # ── Campo EMAIL
        ctk.CTkLabel(frame, text="Email", font=fontes.senha_login,
                     text_color=cores.texto.verde_jambu).place(relx=0.00, rely=0.36)

        frame_email = ctk.CTkFrame(frame, fg_color="transparent",
                                   border_color=cores.fundo.bege_rosado, border_width=1, corner_radius=6)
        frame_email.place(relx=0.00, rely=0.40, relwidth=0.80, relheight=0.08)

        ctk.CTkLabel(frame_email, text="✉", font=("Segoe UI Emoji", 20),
                     text_color=cores.fundo.cinza_médio).place(relx=0.93, rely=0.50, anchor="center")

        self.entrada_email = ctk.CTkEntry(
            frame_email, border_width=0, fg_color="transparent",
            placeholder_text="Seu e-mail...",
            placeholder_text_color=cores.fundo.cinza_médio,
            font=fontes.email_senha
        )
        self.entrada_email.place(relx=0.03, rely=0.10, relwidth=0.82, relheight=0.80)

        # ── Campo SENHA
        ctk.CTkLabel(frame, text="Senha", font=fontes.senha_login,
                     text_color=cores.texto.verde_jambu).place(relx=0.00, rely=0.54)

        frame_senha = ctk.CTkFrame(frame, fg_color="transparent",
                                   border_color=cores.fundo.bege_rosado, border_width=1, corner_radius=6)
        frame_senha.place(relx=0.00, rely=0.58, relwidth=0.80, relheight=0.08)

        self.entrada_senha = ctk.CTkEntry(
            frame_senha, border_width=0, fg_color="transparent",
            placeholder_text="Sua senha...",
            placeholder_text_color=cores.fundo.cinza_médio,
            text_color=cores.texto.verde_jambu,
            font=fontes.email_senha,
            show="*"
        )
        self.entrada_senha.place(relx=0.03, rely=0.10, relwidth=0.75, relheight=0.80)

        # ── Botão olho
        self._mostrar_senha = False

        def alterar_senha():
            self._mostrar_senha = not self._mostrar_senha
            if self._mostrar_senha:
                self.entrada_senha.configure(show="")
                botao_olho.configure(text="🙈")
            else:
                self.entrada_senha.configure(show="*")
                botao_olho.configure(text="👁")

        botao_olho = ctk.CTkButton(
            frame_senha, text="👁", width=30, fg_color="transparent",
            hover=False, text_color=cores.fundo.cinza_médio,
            font=("Segoe UI Emoji", 20), command=alterar_senha
        )
        botao_olho.place(relx=0.92, rely=0.50, anchor="center")

        # ── Checkbox lembrar senha
        self.variavel_lembrar = tk.IntVar()
        tk.Checkbutton(
            frame, text="Lembrar senha", font=fontes.email_senha,
            bg=cores.texto.cinza_muito_claro, fg=cores.texto.verde_jambu,
            activebackground=cores.texto.cinza_muito_claro, selectcolor=cores.fundo.cinza_médio,
            variable=self.variavel_lembrar, borderwidth=0
        ).place(relx=0.01, rely=0.68)

        # ── Botão ENTRAR
        ctk.CTkButton(
            frame, text="ENTRAR", corner_radius=8,
            fg_color=cores.fundo.laranja, hover_color=cores.texto.laranja_HOVER,
            text_color=cores.texto.branco, font=fontes.entrar,
            command=self._clicar_entrar
        ).place(relx=0.00, rely=0.76, relwidth=0.80, relheight=0.09)

        # ── Textos de rodapé
        ctk.CTkLabel(frame, text="Problemas de acesso? Fale com o Administrador",
                     font=fontes.esqueci_senha,
                     text_color=cores.texto.verde_jambu).place(relx=0.20, rely=0.96)

        ctk.CTkLabel(self, text="2026 Sabores do Pará · Sistema de Gestão",
                     font=fontes.email_senha,
                     text_color=cores.fundo.cinza_médio).place(relx=0.63, rely=0.93)

        # ── Bindings — definidos aqui, ativados com delay para evitar eventos residuais
        def ir_para_senha(event):
            email = self.entrada_email.get().strip()
            if not validar_email(email):
                messagebox.showerror("Erro", "Digite um e-mail válido")
                return
            self.entrada_senha.focus()

        self.entrada_email.unbind("<Return>")
        self.entrada_senha.unbind("<Return>")
        self.entrada_email.bind("<Return>", ir_para_senha)
        self.entrada_senha.bind("<Return>", lambda e: self._clicar_entrar() if self.entrada_senha.get().strip() else None)
    def _clicar_entrar(self):
        email = self.entrada_email.get().strip()
        senha = self.entrada_senha.get().strip()

        # Não faz nada se campos estiverem vazios (evita disparos automáticos)
        if not email or not senha:
            return

        if not validar_email(email):
            messagebox.showerror("Erro", "Digite um e-mail válido")
            return

        from app.controller.login_controller import login
        usuario = login(email, senha)

        if usuario:
            self._painel_gradiente.parar()
            self.destroy()
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)

