"""
splash_panel.py — Painel animado "Sabores do Pará"
Folhas estilizadas pontudas (contorno + nervura) flutuando sobre gradiente.
Execute diretamente:  python splash_panel.py
Requer: Pillow + numpy  →  pip install Pillow numpy
"""

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import math
import random

# ── Paleta ─────────────────────────────────────────────────────────────────────
_TOP_L = (218, 85,  32)
_TOP_R = (210, 102, 38)
_BOT_L = (168, 148, 22)
_BOT_R = (108, 122, 30)


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _make_gradient(w, h):
    """
    Gera o gradiente como array numpy (H, W, 3) diretamente,
    sem loop pixel-a-pixel — muito mais rápido que putpixel.
    """
    tx = np.linspace(0, 1, w)   # (W,)
    ty = np.linspace(0, 1, h)   # (H,)

    top = np.array(_TOP_L) + np.outer(np.zeros(w), np.zeros(3))  # placeholder
    # interpolação vetorizada para cada canal
    top_row = np.array(_TOP_L)[None, :] + tx[:, None] * (np.array(_TOP_R) - np.array(_TOP_L))  # (W, 3)
    bot_row = np.array(_BOT_L)[None, :] + tx[:, None] * (np.array(_BOT_R) - np.array(_BOT_L))  # (W, 3)

    # combina linhas ao longo do eixo Y: (H, W, 3)
    arr = top_row[None, :, :] + ty[:, None, None] * (bot_row - top_row)[None, :, :]
    return np.clip(arr, 0, 255).astype(np.uint8)


def _rounded_mask(w, h, r):
    from PIL import ImageDraw
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return np.array(mask)  # retorna como array numpy para uso vetorizado


# ── Ícone de fruta (círculo com 3 segmentos) ───────────────────────────────────
def _draw_fruit_icon(canvas, cx, cy, r, color="white", stipple="gray50"):
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       outline=color, fill="", width=2, stipple=stipple)
    ir = r * 0.50
    canvas.create_oval(cx - ir, cy - ir, cx + ir, cy + ir,
                       outline=color, fill="", width=1, stipple=stipple)
    for i in range(3):
        a = math.radians(90 + i * 120)
        canvas.create_line(cx, cy,
                           cx + math.cos(a) * r, cy + math.sin(a) * r,
                           fill=color, width=1, stipple=stipple)


# ══════════════════════════════════════════════════════════════════════════════
class SplashPanel(tk.Canvas):
    """
    Canvas animado com gradiente laranja→verde-oliva e folhas pontudas
    flutuando. Embutível em qualquer janela.

    Parâmetros
    ----------
    parent   : widget pai
    width    : largura em pixels   (padrão 420)
    height   : altura em pixels    (padrão 560)
    radius   : raio dos cantos arredondados
    bg_outer : cor de fundo externo (blend dos cantos)
    """

    def __init__(self, parent, width=420, height=560, radius=28,
                 bg_outer="#ECEAE6", **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=bg_outer, **kwargs)
        self._W, self._H, self._R = width, height, radius
        self._bg_outer = bg_outer
        self._t = 0.0
        self._big_angle = 0.0

        # Gradiente pré-computado como array numpy (H, W, 3)
        self._gradient_base = _make_gradient(width, height)

        # Máscara de cantos arredondados como array numpy (H, W)
        self._mask_arr = _rounded_mask(width, height, radius)

        # Cor de fundo externo como array (H, W, 3) para composição
        bg_rgb = self._hex_to_rgb(bg_outer)
        self._bg_outer_arr = np.full((height, width, 3), bg_rgb, dtype=np.uint8)

        self._bg_ref = None

        # ── Folhas espalhadas ─────────────────────────────────────────────────
        rng = random.Random(7)   # semente fixa → layout sempre igual
        self._rng = rng          # guardamos para uso interno consistente
        self._leaves = []

        attempts = 0
        while len(self._leaves) < 8 and attempts < 200:
            attempts += 1
            bx = rng.uniform(0.14, 0.86) * width
            by = rng.uniform(0.62, 0.88) * height

            # verifica distância mínima entre folhas
            valid = all(
                math.hypot(bx - lf["bx"], by - lf["by"]) >= 60
                for lf in self._leaves
            )

            if valid:
                self._leaves.append({
                    "bx": bx, "by": by,
                    "len": rng.uniform(10, 28),
                    "wid": rng.uniform(6, 10),
                    "angle": rng.uniform(-60, 60),
                    "phase": rng.uniform(0, math.pi * 2),
                    "speed": rng.uniform(0.3, 0.8),
                })

        # ── Pontos luminosos ──────────────────────────────────────────────────
        self._dots = [
            (rng.uniform(0.06, 0.90) * width,
             rng.uniform(0.40, 0.92) * height,
             rng.uniform(0, math.pi * 2))
            for _ in range(6)
        ]

        # ── Bolhas subindo ────────────────────────────────────────────────────
        self._bubbles = [
            {
                "x": rng.uniform(0.08, 0.92) * width,
                "y": rng.uniform(0.80, 1.15) * height,
                "r": rng.uniform(1.5, 4),
                "speed": rng.uniform(0.6, 2.0),
                "phase": rng.uniform(0, math.pi * 2),
            }
            for _ in range(28)
        ]

        self._animate()

    # ── Loop de animação ───────────────────────────────────────────────────────
    def _animate(self):
        self._t += 0.018
        self._big_angle += 0.007
        self.delete("all")

        # 1 — Gradiente com brilho pulsante (operação vetorizada com numpy)
        brightness = 0.95 + 0.05 * math.sin(self._t * 0.6)
        bg_arr = np.clip(self._gradient_base * brightness, 0, 255).astype(np.uint8)

        # Aplica máscara de cantos arredondados por composição alfa vetorizada
        alpha = self._mask_arr[:, :, None] / 255.0          # (H, W, 1) float
        composed = (bg_arr * alpha + self._bg_outer_arr * (1 - alpha)).astype(np.uint8)

        self._bg_ref = ImageTk.PhotoImage(Image.fromarray(composed))
        self.create_image(0, 0, anchor="nw", image=self._bg_ref)

        # 2 — Folhas flutuando
        for lf in self._leaves:
            t  = self._t * lf["speed"] + lf["phase"]
            dx = 4 * math.sin(t * 0.6)
            dy = -4 * math.sin(t * 0.4)
            da = 5 * math.sin(t * 0.4)
            self._draw_leaf(
                lf["bx"] + dx, lf["by"] + dy,
                length=lf["len"], width=lf["wid"],
                angle_deg=lf["angle"] + da,
                stipple="gray75",
            )

        # 3 — Pontos luminosos pulsando
        for (dx, dy, phase) in self._dots:
            v = (math.sin(self._t * 1.1 + phase) + 1) / 2
            sp = "gray75" if v < 0.35 else ("gray50" if v < 0.70 else "")
            r = 2
            self.create_oval(dx - r, dy - r, dx + r, dy + r,
                             fill="white", outline="", stipple=sp)

        # 4 — Bolhas subindo
        self._draw_bubbles()

        # 5 — Textos fixos
        self._draw_texts()

        self.after(18, self._animate)

    # ── Desenha uma folha pontuda no canvas ────────────────────────────────────
    def _draw_leaf(self, cx, cy, length, width, angle_deg, stipple="gray75"):
        ang = math.radians(angle_deg)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)

        tip_x  = cx + cos_a * length
        tip_y  = cy + sin_a * length
        base_x = cx - cos_a * length
        base_y = cy - sin_a * length
        perp_x = -sin_a
        perp_y =  cos_a

        points = []

        # lado esquerdo (base → ponta)
        for i in range(20):
            t = i / 19
            curve = math.sin(t * math.pi) * 1.6
            points.extend([
                base_x + (tip_x - base_x) * t + perp_x * width * curve,
                base_y + (tip_y - base_y) * t + perp_y * width * curve,
            ])

        # lado direito (ponta → base)
        for i in range(20):
            t = 1 - (i / 19)
            curve = math.sin(t * math.pi) * 1.6
            points.extend([
                base_x + (tip_x - base_x) * t - perp_x * width * curve,
                base_y + (tip_y - base_y) * t - perp_y * width * curve,
            ])

        # contorno da folha
        self.create_polygon(points, smooth=True, splinesteps=64,
                            outline="#fff8ef", fill="", width=1, stipple=stipple)

        # nervura central
        self.create_line(base_x, base_y, tip_x, tip_y,
                         fill="#f7f1e8", width=1, stipple=stipple)

        # nervuras laterais
        for i in range(2):
            t = (i + 1) / 4
            mx = base_x + (tip_x - base_x) * t
            my = base_y + (tip_y - base_y) * t
            size = width * (0.7 - t * 0.15)

            self.create_line(mx, my, mx - perp_x * size, my - perp_y * size,
                             fill="#f7f1e8", width=1, stipple="gray75")
            self.create_line(mx, my, mx + perp_x * size, my + perp_y * size,
                             fill="#f7f1e8", width=1, stipple="gray75")

    # ── Bolhas subindo ────────────────────────────────────────────────────────
    def _draw_bubbles(self):
        for bubble in self._bubbles:
            bubble["y"] -= bubble["speed"]
            bubble["x"] += math.sin(self._t * 1.5 + bubble["phase"]) * 0.25

            # reset quando sair da tela — usa self._rng para reprodutibilidade
            if bubble["y"] < -10:
                bubble["y"] = self._H + self._rng.randint(10, 80)
                bubble["x"] = self._rng.uniform(0.08, 0.92) * self._W

            x, y, r = bubble["x"], bubble["y"], bubble["r"]
            stipple = "gray75" if r < 2 else "gray50"
            self.create_oval(x - r, y - r, x + r, y + r,
                             fill="white", outline="", stipple=stipple)

    # ── Textos ─────────────────────────────────────────────────────────────────
    def _draw_texts(self):
        px, py = 34, 44
        self.create_text(px, py, text="SISTEMA DE GESTÃO",
                         anchor="w", fill="white", font=("Arial", 9, "bold"))
        self.create_text(px, py + 44, text="Sabores",
                         anchor="w", fill="white", font=("Georgia", 34, "bold"))
        self.create_text(px, py + 88, text="do Pará",
                         anchor="w", fill="white", font=("Georgia", 34, "bold"))
        self.create_text(px, self._H - 40,
                         text='"Sabores que contam história"',
                         anchor="w", fill="white", font=("Georgia", 11, "italic"))

    # ── Utilitários ───────────────────────────────────────────────────────────
    @staticmethod
    def _hex_to_rgb(hex_color):
        h = hex_color.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    BG = "#ECEAE6"
    PW, PH = 420, 560

    root = tk.Tk()
    root.title("Sabores do Pará")
    root.geometry(f"{PW + 60}x{PH + 60}")
    root.resizable(False, False)
    root.configure(bg=BG)

    SplashPanel(root, width=PW, height=PH, radius=28, bg_outer=BG).place(x=30, y=30)
    root.mainloop()