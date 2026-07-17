"""
integracao_login.py
═══════════════════════════════════════════════════════════════════
INSTRUÇÕES DE INTEGRAÇÃO — cole as seções abaixo no seu login.py

RESUMO DO QUE MUDA:
  1. Remover o import de gradiente1
  2. Adicionar ImageTk e os ao import do PIL
  3. Carregar os frames WebP UMA VEZ (após tela.update())
  4. Mover a criação do logo para fora do animar()
  5. Substituir a chamada gradiente() por canvas.create_image()
  6. Adicionar canvas.delete("all") no início de animar()

NADA MAIS MUDA — o resto do seu código permanece igual.
═══════════════════════════════════════════════════════════════════
"""

# ───────────────────────────────────────────────────────────────
# [1] IMPORTS — substitua / adicione no topo do seu login.py
# ───────────────────────────────────────────────────────────────

# REMOVA esta linha:
#   from app.utils.gradiente1 import gradiente

# MANTENHA:
import tkinter as tk
import customtkinter as ctk
import os
from PIL import Image, ImageTk          # ← adicione ImageTk aqui
from app.utils.estilos import Cores, Fontes, Icones
from tkinter import messagebox
from app.controller.login_controller import login


# ───────────────────────────────────────────────────────────────
# [2] SETUP DA JANELA — igual ao seu código atual
# ───────────────────────────────────────────────────────────────

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

tela = ctk.CTk()
tela.after(0, lambda: tela.state("zoomed"))

cores   = Cores()
fontes  = Fontes()
icones  = Icones()

tela.title("Sabores do Pará")
tela.configure(fg_color=cores.texto.cinza_muito_claro)

tela.grid_rowconfigure(0, weight=1)
tela.grid_columnconfigure(0, weight=1)
tela.grid_columnconfigure(1, weight=1)

# Painel esquerdo (canvas) — igual ao seu código
canvas = tk.Canvas(tela, highlightthickness=0, bd=0, relief="flat", bg=cores.fundo.verde)
canvas.place(relx=0.015, rely=0.02, relwidth=0.43, relheight=0.95)

tela.update()
largura_canvas = int(tela.winfo_width()  * 0.43)
altura_canvas  = int(tela.winfo_height() * 0.95)


# ───────────────────────────────────────────────────────────────
# [3] CARREGA ANIMAÇÃO — adicione este bloco após tela.update()
#     Executa UMA VEZ só. Todos os frames ficam em memória.
# ───────────────────────────────────────────────────────────────

_WEBP_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login_panel.webp")
_frames_tk     = []    # frames prontos para o canvas (tkinter PhotoImage)
_frame_idx     = 0     # índice do frame exibido agora
_frame_counter = 0     # conta chamadas internas de animar()
_SKIP          = 3     # avança 1 frame WebP a cada 3 chamadas ≈ 48ms ≈ 20fps

try:
    _anim = Image.open(_WEBP_PATH)
    while True:
        frame_pil = _anim.copy().convert("RGB")
        frame_pil = frame_pil.resize((largura_canvas, altura_canvas), Image.LANCZOS)
        _frames_tk.append(ImageTk.PhotoImage(frame_pil))
        try:
            _anim.seek(_anim.tell() + 1)
        except EOFError:
            break
    print(f"[OK] Animação carregada — {len(_frames_tk)} frames.")

except FileNotFoundError:
    print("[AVISO] login_panel.webp não encontrado.")
    print("        Execute generate_login_animation.py primeiro.")
except Exception as e:
    print(f"[AVISO] Erro ao carregar animação: {e}")


# ───────────────────────────────────────────────────────────────
# [4] LOGO — mova para FORA de animar() para criar apenas UMA VEZ
#     No seu código original estava dentro de animar(), o que
#     recriava um novo CTkLabel a cada 16ms (vazamento de memória).
# ───────────────────────────────────────────────────────────────

logo_widget = ctk.CTkLabel(tela, image=icones.logotipo, text="")
logo_widget.place(relx=0.20, rely=0.50)

tempo = 0


# ───────────────────────────────────────────────────────────────
# [5] FUNÇÃO animar() — substitua a sua por esta versão
#     Apenas 3 linhas mudaram: delete("all"), create_image(), e
#     o avanço de frame. O resto é idêntico ao seu código.
# ───────────────────────────────────────────────────────────────

def animar():
    global tempo, _frame_idx, _frame_counter

    # Limpa o canvas antes de redesenhar
    canvas.delete("all")

    # ── NOVO: exibe o frame da animação WebP ──────────────────
    if _frames_tk:
        canvas.create_image(0, 0, anchor="nw", image=_frames_tk[_frame_idx])
        _frame_counter += 1
        if _frame_counter >= _SKIP:
            _frame_counter = 0
            _frame_idx = (_frame_idx + 1) % len(_frames_tk)
    # ── FIM da mudança ─────────────────────────────────────────

    tempo += 2
    tela.after(16, animar)

    # Textos sobre a animação — idênticos ao seu código original
    canvas.create_text(
        largura_canvas * 0.50, altura_canvas * 0.25,
        text="Sistema do Restaurante",
        anchor="center",
        font=fontes.titulo_esquerdo,
        fill=cores.texto.verde_jambu,
    )
    canvas.create_text(
        largura_canvas * 0.35, altura_canvas * 0.90,
        text="\u201cSabores que contam hist\u00f3ria\u201d",
        anchor="w",
        font=fontes.titulo,
        fill=cores.texto.branco,
    )

    # REMOVIDO daqui: logo = ctk.CTkLabel(...)  → está na linha [4] acima


# ───────────────────────────────────────────────────────────────
# O resto do seu login.py NÃO MUDA:
# frame, campos de e-mail, senha, botão, rodapé — tudo igual.
# ───────────────────────────────────────────────────────────────

# ... (seu código do frame direito permanece aqui sem alteração) ...

animar()
tela.mainloop()
