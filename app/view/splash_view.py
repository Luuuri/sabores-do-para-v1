import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import threading


class SplashView(tk.Toplevel):
    """
    Tela de splash simples e leve — aparece instantaneamente enquanto
    o LoginView carrega por trás. Sem animação pesada, sem numpy.
    """

    def __init__(self, master, largura=480, altura=280):
        super().__init__(master)

        self._concluido = False
        self._on_done = None

        # ── Configurações da janela ──────────────────────────────────────
        self.overrideredirect(True)          # sem borda/título
        self.attributes("-topmost", True)    # sempre na frente
        self.configure(bg="#2E5D2E")         # verde escuro (mesma paleta do sistema)

        # Centraliza na tela
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - largura) // 2
        y  = (sh - altura)  // 2
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        self._largura = largura
        self._altura  = altura

        self._build_ui()

    # ── Interface ────────────────────────────────────────────────────────
    def _build_ui(self):
        w, h = self._largura, self._altura

        canvas = tk.Canvas(self, width=w, height=h,
                           bg="#2E5D2E", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Fundo degradê simples (sem numpy — apenas 2 retângulos)
        canvas.create_rectangle(0, 0, w, h // 2,
                                 fill="#3A6B3A", outline="")
        canvas.create_rectangle(0, h // 2, w, h,
                                 fill="#2E5D2E", outline="")

        # Borda sutil
        canvas.create_rectangle(2, 2, w - 2, h - 2,
                                 outline="#C8853A", width=2)

        # Nome do sistema
        canvas.create_text(w // 2, h * 0.30,
                            text="Sabores do Pará",
                            fill="white",
                            font=("Georgia", 28, "bold"),
                            anchor="center")

        canvas.create_text(w // 2, h * 0.48,
                            text="SISTEMA DE GESTÃO",
                            fill="#f0d9b5",
                            font=("Georgia", 12, "italic"),
                            anchor="center")

        # Barra de progresso (simulada com Canvas)
        barra_bg = canvas.create_rectangle(
            w * 0.12, h * 0.68,
            w * 0.88, h * 0.76,
            fill="#1e3e1e", outline="#C8853A", width=1
        )

        self._canvas    = canvas
        self._barra_x1  = w * 0.12
        self._barra_y1  = h * 0.68
        self._barra_x2  = w * 0.88
        self._barra_y2  = h * 0.76
        self._progresso = 0.0

        self._barra_fill = canvas.create_rectangle(
            self._barra_x1, self._barra_y1,
            self._barra_x1, self._barra_y2,   # começa vazia
            fill="#C8853A", outline=""
        )

        # Texto de status
        self._label_status = canvas.create_text(
            w // 2, h * 0.86,
            text="Carregando...",
            fill="#c8c8c8",
            font=("Arial", 10),
            anchor="center"
        )

        # Rodapé
        canvas.create_text(w // 2, h * 0.95,
                            text="© 2026 Sabores do Pará",
                            fill="#7a9e7a",
                            font=("Arial", 8),
                            anchor="center")

        # Inicia animação da barra
        self._animar_barra()

    # ── Animação da barra ────────────────────────────────────────────────
    def _animar_barra(self):
        """Avança a barra até 85% enquanto o login carrega."""
        if self._concluido:
            return

        if self._progresso < 0.85:
            self._progresso += 0.012
            self._atualizar_barra()

        self.after(30, self._animar_barra)

    def _atualizar_barra(self):
        x2 = self._barra_x1 + (self._barra_x2 - self._barra_x1) * self._progresso
        self._canvas.coords(
            self._barra_fill,
            self._barra_x1, self._barra_y1,
            x2,             self._barra_y2
        )

    def set_status(self, texto: str):
        """Atualiza o texto de status (pode ser chamado de outra thread via after)."""
        self._canvas.itemconfig(self._label_status, text=texto)

    # ── Conclusão ────────────────────────────────────────────────────────
    def concluir(self, on_done=None):
        """
        Chamado quando o LoginView terminou de carregar.
        Completa a barra rapidamente e fecha o splash.
        """
        self._on_done = on_done
        self._concluido = True
        self._completar_barra()

    def _completar_barra(self):
        if self._progresso < 1.0:
            self._progresso += 0.05
            self._atualizar_barra()
            self.after(20, self._completar_barra)
        else:
            self.after(150, self._finalizar)   # pequena pausa antes de fechar

    def _finalizar(self):
        on_done = self._on_done
        self.destroy()
        if on_done:
            self.master.after(0, on_done)
