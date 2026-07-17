#!/usr/bin/env python3
"""
login_window.py
Tela de login "Sabores do Pará" com painel botânico animado.

Pré-requisito:
    1. Execute generate_login_animation.py UMA VEZ para gerar login_panel.webp
    2. Então execute este arquivo normalmente

Dependências:
    pip install customtkinter pillow
"""

import customtkinter as ctk
from PIL import Image
import os
import sys

# ═══════════════════════════════════════════════════════════════
#  CONFIGURAÇÕES VISUAIS
# ═══════════════════════════════════════════════════════════════

WIN_W, WIN_H = 960, 600     # largura x altura da janela
PANEL_W      = 440          # largura do painel animado esquerdo
PANEL_H      = 560          # altura do painel animado

# Paleta
CORAL   = "#C94E1A"         # botões de ação
AMBER   = "#E8961E"         # destaques
BG      = "#FAF6F0"         # fundo geral
SURFACE = "#FFFFFF"         # cartões/painéis
TEXT    = "#2C2015"         # texto principal
MUTED   = "#7A6A58"         # texto secundário
BORDER  = "#E0D5C8"         # bordas

# Caminho do WebP gerado
WEBP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login_panel.webp") # <---------


# ═══════════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class LoginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sabores do Pará — Sistema de Gestão")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        # Centraliza na tela
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{WIN_W}x{WIN_H}+{(sw - WIN_W)//2}+{(sh - WIN_H)//2}")

        # Ícone opcional (descomente se tiver um .ico)
        # self.iconbitmap("icon.ico")

        self._frames      = []
        self._frame_delays = []
        self._frame_idx   = 0

        self._build_ui()
        self._load_animation()
        self._next_frame()

    # ── Interface ──────────────────────────────────────────────

    def _build_ui(self):
        # Card externo (sombra simulada com frame branco arredondado)
        card = ctk.CTkFrame(
            self,
            corner_radius=24,
            fg_color=SURFACE,
            border_width=0,
        )
        card.pack(fill="both", expand=True, padx=20, pady=20)
        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # ── Painel esquerdo (animação + texto) ─────────────────
        self.left = ctk.CTkFrame(
            card,
            corner_radius=20,
            fg_color=CORAL,        # fundo coral visível nos cantos transparentes do WebP
            width=PANEL_W,
            height=PANEL_H,
        )
        self.left.grid(row=0, column=0, sticky="ns", padx=(12, 6), pady=16)
        self.left.grid_propagate(False)

        # Label que recebe os frames animados (preenche o painel inteiro)
        self.anim_label = ctk.CTkLabel(
            self.left,
            text="",
            fg_color="transparent",
        )
        self.anim_label.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        # Texto sobre a animação (fica acima do label de imagem via z-order)
        self._add_panel_text()

        # ── Painel direito (formulário de login) ───────────────
        right = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=16)
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self._add_form(right)

    def _add_panel_text(self):
        """Texto sobreposto ao painel animado."""

        # Rótulo superior
        ctk.CTkLabel(
            self.left,
            text="SISTEMA DE GESTÃO",
            font=ctk.CTkFont("Segoe UI", 10, weight="normal"),
            text_color="#FFFFFF99",
            fg_color="transparent",
        ).place(relx=0.10, rely=0.09)

        # Título grande
        ctk.CTkLabel(
            self.left,
            text="Sabores\ndo Pará",
            font=ctk.CTkFont("Georgia", 34, weight="bold"),
            text_color="#FFFFFF",
            justify="left",
            fg_color="transparent",
        ).place(relx=0.10, rely=0.14)

        # Slogan no rodapé
        ctk.CTkLabel(
            self.left,
            text='"Sabores que contam história"',
            font=ctk.CTkFont("Georgia", 13),
            text_color="#FFFFFFCC",
            justify="left",
            fg_color="transparent",
        ).place(relx=0.10, rely=0.85)

    def _add_form(self, parent):
        """Formulário de login centralizado no painel direito."""

        # Centraliza verticalmente com um frame interno
        form = ctk.CTkFrame(parent, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")

        # Ícone de folha (placeholder — substitua por CTkImage com logo real)
        icon_bg = ctk.CTkFrame(form, width=52, height=52, corner_radius=14, fg_color="#F5E6DC")
        icon_bg.grid(row=0, column=0, sticky="w", pady=(0, 6))
        icon_bg.grid_propagate(False)
        ctk.CTkLabel(
            icon_bg, text="🍃",
            font=ctk.CTkFont("Segoe UI Emoji", 26),
            fg_color="transparent",
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Subtítulo e nome do restaurante
        ctk.CTkLabel(
            form,
            text="Restaurante",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=MUTED,
        ).grid(row=1, column=0, sticky="w")

        ctk.CTkLabel(
            form,
            text="Sabores do Pará",
            font=ctk.CTkFont("Georgia", 18, weight="bold"),
            text_color=CORAL,
        ).grid(row=2, column=0, sticky="w", pady=(0, 16))

        # Saudação
        ctk.CTkLabel(
            form,
            text="Bem-vindo(a)",
            font=ctk.CTkFont("Georgia", 28, weight="bold"),
            text_color=TEXT,
        ).grid(row=3, column=0, sticky="w")

        ctk.CTkLabel(
            form,
            text="Acesse o sistema para gerenciar\nseu restaurante.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=MUTED,
            justify="left",
        ).grid(row=4, column=0, sticky="w", pady=(2, 20))

        # Campo E-mail
        ctk.CTkLabel(
            form,
            text="E-mail",
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            text_color=TEXT,
        ).grid(row=5, column=0, sticky="w")

        self.email_var = ctk.StringVar(value="admin@saboresdopara.com.br")
        email_entry = ctk.CTkEntry(
            form,
            textvariable=self.email_var,
            width=300, height=44,
            corner_radius=10,
            border_color=BORDER,
            border_width=1,
            fg_color=SURFACE,
            text_color=TEXT,
            font=ctk.CTkFont("Segoe UI", 13),
            placeholder_text="Seu e-mail…",
        )
        email_entry.grid(row=6, column=0, pady=(4, 12))
        email_entry.bind("<FocusIn>",  lambda e: email_entry.configure(border_color=AMBER))
        email_entry.bind("<FocusOut>", lambda e: email_entry.configure(border_color=BORDER))

        # Campo Senha
        ctk.CTkLabel(
            form,
            text="Senha",
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            text_color=TEXT,
        ).grid(row=7, column=0, sticky="w")

        self.pass_var = ctk.StringVar(value="senha123")
        pwd_entry = ctk.CTkEntry(
            form,
            textvariable=self.pass_var,
            show="•",
            width=300, height=44,
            corner_radius=10,
            border_color=BORDER,
            border_width=1,
            fg_color=SURFACE,
            text_color=TEXT,
            font=ctk.CTkFont("Segoe UI", 13),
            placeholder_text="Sua senha…",
        )
        pwd_entry.grid(row=8, column=0, pady=(4, 20))
        pwd_entry.bind("<FocusIn>",  lambda e: pwd_entry.configure(border_color=AMBER))
        pwd_entry.bind("<FocusOut>", lambda e: pwd_entry.configure(border_color=BORDER))

        # Botão Entrar
        btn = ctk.CTkButton(
            form,
            text="ENTRAR",
            width=300, height=46,
            corner_radius=10,
            fg_color=CORAL,
            hover_color="#D86A18",
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            text_color=SURFACE,
            command=self._on_login,
        )
        btn.grid(row=9, column=0, pady=(0, 14))

        # Rodapé
        ctk.CTkLabel(
            form,
            text="Problemas de acesso? Fale com o Administrador",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=MUTED,
        ).grid(row=10, column=0)

        ctk.CTkLabel(
            form,
            text="© 2026 Sabores do Pará · Sistema de Gestão",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=BORDER,
        ).grid(row=11, column=0, pady=(4, 0))

    # ── Animação ───────────────────────────────────────────────

    def _load_animation(self):                                                
        """Carrega os frames do WebP animado em memória."""
        if not os.path.exists(WEBP_PATH):
            print(f"\n[AVISO] login_panel.webp não encontrado.")                # <---------------------
            print(f"  Caminho esperado: {WEBP_PATH}")
            print("  Execute generate_login_animation.py primeiro.\n")
            return

        try:
            anim = Image.open(WEBP_PATH)
        except Exception as e:
            print(f"[ERRO] Não foi possível abrir login_panel.webp: {e}")
            return

        frame_n = 0
        while True:
            try:
                # Converte e redimensiona para caber no painel esquerdo
                frame_rgba = anim.copy().convert("RGBA")
                frame_rgba = frame_rgba.resize((PANEL_W, PANEL_H), Image.LANCZOS)

                ctk_img = ctk.CTkImage(
                    light_image=frame_rgba,
                    dark_image=frame_rgba,
                    size=(PANEL_W, PANEL_H),
                )
                self._frames.append(ctk_img)

                delay = anim.info.get("duration", 50)
                self._frame_delays.append(max(int(delay), 16))

                frame_n += 1
                anim.seek(anim.tell() + 1)

            except EOFError:
                break
            except Exception as e:
                print(f"[AVISO] Erro no frame {frame_n}: {e}")
                break

        print(f"[OK] {len(self._frames)} frames carregados de login_panel.webp")

    def _next_frame(self):
        """Avança para o próximo frame da animação."""
        if not self._frames:
            return

        img   = self._frames[self._frame_idx]
        delay = self._frame_delays[self._frame_idx]
        self._frame_idx = (self._frame_idx + 1) % len(self._frames)

        self.anim_label.configure(image=img)
        self.after(delay, self._next_frame)

    # ── Ações ──────────────────────────────────────────────────

    def _on_login(self):
        """Substituir pela lógica real de autenticação (SQL, etc.)."""
        email = self.email_var.get().strip()
        senha = self.pass_var.get().strip()

        # Validação básica de exemplo
        if not email or not senha:
            self._show_error("Preencha e-mail e senha.")
            return

        # TODO: conectar ao banco de dados aqui
        # Ex: usuario = db.verificar_login(email, senha)
        print(f"[LOGIN] Tentativa: {email}")

        # Simulação de acesso — remova em produção
        if email and senha:
            self._open_dashboard()

    def _open_dashboard(self):
        """Abre a tela principal do sistema após login."""
        # TODO: destruir janela de login e abrir a janela principal
        print("[OK] Login bem-sucedido — abrir tela principal aqui.")
        # Exemplo: self.destroy(); DashboardWindow().mainloop()

    def _show_error(self, msg):
        """Exibe uma mensagem de erro simples."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Atenção")
        dialog.geometry("320x120")
        dialog.resizable(False, False)
        dialog.configure(fg_color=SURFACE)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=msg, font=ctk.CTkFont("Segoe UI", 13), text_color=TEXT).pack(pady=30)
        ctk.CTkButton(dialog, text="OK", width=100, fg_color=CORAL,
                      hover_color="#D86A18", command=dialog.destroy).pack()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Verifica dependências
    try:
        import customtkinter  # noqa
    except ImportError:
        print("[ERRO] customtkinter não instalado.  Execute: pip install customtkinter")
        sys.exit(1)
    try:
        from PIL import Image  # noqa
    except ImportError:
        print("[ERRO] Pillow não instalado.  Execute: pip install pillow")
        sys.exit(1)

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")  # cores sobrescritas manualmente acima

    app = LoginWindow()
    app.mainloop()
