"""
Requer: Pillow, numpy
    pip install Pillow numpy
"""

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import math
import random
from app.utils.estilos import Icones

#Paleta
_TOP_L = (218, 85,  32)
_TOP_R = (210, 102, 38)
_BOT_L = (168, 148, 22)
_BOT_R = (108, 122, 30)


def _make_gradient(w, h):
    """Gradiente bilinear vetorizado (numpy) — sem loop pixel-a-pixel."""
    tx = np.linspace(0, 1, w)
    ty = np.linspace(0, 1, h)

    top_row = np.array(_TOP_L) + tx[:, None] * (np.array(_TOP_R) - np.array(_TOP_L))
    bot_row = np.array(_BOT_L) + tx[:, None] * (np.array(_BOT_R) - np.array(_BOT_L))

    arr = top_row[None, :, :] + ty[:, None, None] * (bot_row - top_row)[None, :, :]
    return np.clip(arr, 0, 255).astype(np.uint8)


def _rounded_mask(w, h, r):
    """Máscara de cantos arredondados como array numpy (H, W)."""
    from PIL import ImageDraw
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return np.array(mask)


def _hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class GradientePainel(tk.Canvas):
    """
    Canvas animado com gradiente laranja→verde-oliva e folhas pontudas
    flutuando. Embutível em qualquer janela tkinter/customtkinter.

    Parâmetros
    ----------
    parent   : widget pai
    width    : largura em pixels   (padrão 420)
    height   : altura em pixels    (padrão 560)
    radius   : raio dos cantos arredondados
    bg_outer : cor de fundo externo (blend dos cantos)
    """

    def __init__(self, parent, width=420, height=560, radius=28,
                 bg_outer="#ECEAE6", icones=None, auto_start=True, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=bg_outer, **kwargs)

        self._icones = icones or Icones() # usa o passado ou cria um novo
        logo_pil = self._icones.logo._light_image  # pega a imagem PIL interna
        self._logo_tk = ImageTk.PhotoImage(logo_pil)
        
        self._W, self._H, self._R = width, height, radius
        self._bg_outer = bg_outer
        self._t = 0.0
        self._rodando = False # ← começa PAUSADO

        # Gradiente e máscara pré-computados
        self._gradient_base = _make_gradient(width, height)
        self._mask_arr      = _rounded_mask(width, height, radius)
        self._bg_outer_arr  = np.full((height, width, 3), _hex_to_rgb(bg_outer), dtype=np.uint8)
        self._bg_ref        = None

        # Folhas (semente fixa → layout sempre igual) 
        rng = random.Random(7)
        self._rng    = rng
        self._leaves = []

        attempts = 0
        
        while len(self._leaves) < 20 and attempts < 600:
            
            attempts += 1
            # espalhamento melhor
            bx = rng.uniform(0.08, 0.92) * width
            by = rng.uniform(0.42, 0.88) * height

            if all(math.hypot(bx - lf["bx"], by - lf["by"]) >= 85
                for lf in self._leaves):
                # profundidade visual
                escala = by / height

                tamanho = rng.uniform(10, 22) * escala
                
                self._leaves.append({
                    "bx":    bx,
                    "by":    by,
                    "len":   tamanho,
                    "wid":   tamanho * 0.35,
                    "angle": rng.uniform(-60, 60),
                    "phase": rng.uniform(0, math.pi * 2),
                    "speed": rng.uniform(0.3, 0.8),
                })

        #Pontos luminosos
        self._dots = [
            (rng.uniform(0.06, 0.90) * width,
             rng.uniform(0.40, 0.92) * height,
             rng.uniform(0, math.pi * 2))
            for _ in range(6)
        ]

        #Bolhas subindo
        self._bubbles = [
            {
                "x":     rng.uniform(0.08, 0.92) * width,
                "y":     rng.uniform(0.80, 1.15) * height,
                "r":     rng.uniform(1.5, 4),
                "speed": rng.uniform(0.6, 2.0),
                "phase": rng.uniform(0, math.pi * 2),
            }
            for _ in range(28)
        ]

        if auto_start:
            self.after(100, self.iniciar)
        
    def iniciar(self):
        if self._rodando:
            return
        self._rodando = True
        self._animate()

    #Loop de animação
    def _animate(self):
        if not self._rodando:
            return
        self._t += 0.018
        self.delete("all")

        # Gradiente com brilho pulsante (vetorizado)
        brightness = 0.95 + 0.05 * math.sin(self._t * 0.6)
        bg_arr = np.clip(self._gradient_base * brightness, 0, 255).astype(np.uint8)

        # Composição com máscara de cantos
        alpha    = self._mask_arr[:, :, None] / 255.0
        composed = (bg_arr * alpha + self._bg_outer_arr * (1 - alpha)).astype(np.uint8)

        self._bg_ref = ImageTk.PhotoImage(Image.fromarray(composed))
        self.create_image(0, 0, anchor="nw", image=self._bg_ref)

        # Folhas flutuando
        for lf in self._leaves:
            t = self._t * lf["speed"] + lf["phase"]
            self._draw_leaf(
                lf["bx"] + 4 * math.sin(t * 0.6),
                lf["by"] - 4 * math.sin(t * 0.4),
                length=lf["len"],
                width=lf["wid"],
                angle_deg=lf["angle"] + 5 * math.sin(t * 0.4),
            )

        # Pontos luminosos pulsando
        for (dx, dy, phase) in self._dots:
            
            # movimento suave
            mov_x = math.sin(self._t * 0.8 + phase) * 14
            mov_y = math.cos(self._t * 0.6 + phase) * 10

            # brilho
            v = (math.sin(self._t * 1.1 + phase) + 1) / 2

            sp = "gray75" if v < 0.35 else (
                "gray50" if v < 0.70 else ""
            )

            tamanho = 2 + math.sin(self._t + phase) * 0.5
            self.create_oval(
                dx + mov_x - tamanho,
                dy + mov_y - tamanho,
                dx + mov_x + tamanho,
                dy + mov_y + tamanho,
                fill="white",
                outline="",
                stipple=sp
            )  

    # Bolhas subindo
        self._draw_bubbles()

        # Textos
        self._draw_texts()

        self.after(18, self._animate)

    #Folha pontuda
    def _draw_leaf(self, cx, cy, length, width, angle_deg, stipple="gray75"):
        ang   = math.radians(angle_deg)
        cos_a, sin_a = math.cos(ang), math.sin(ang)

        tip_x,  tip_y  = cx + cos_a * length, cy + sin_a * length
        base_x, base_y = cx - cos_a * length, cy - sin_a * length
        perp_x, perp_y = -sin_a, cos_a

        points = []
        for i in range(20):
            t = i / 19
            c = math.sin(t * math.pi) * 1.6
            points += [base_x + (tip_x - base_x) * t + perp_x * width * c,
                       base_y + (tip_y - base_y) * t + perp_y * width * c]
        for i in range(20):
            t = 1 - i / 19
            c = math.sin(t * math.pi) * 1.6
            points += [base_x + (tip_x - base_x) * t - perp_x * width * c,
                       base_y + (tip_y - base_y) * t - perp_y * width * c]

        self.create_polygon(points, smooth=True, splinesteps=64,
                            outline="#f6eee3", fill="", width=0.7, stipple=stipple)
        self.create_line(base_x, base_y, tip_x, tip_y,
                         fill="#f7f1e8", width=1, stipple=stipple)

        for i in range(2):
            t    = (i + 1) / 4
            mx   = base_x + (tip_x - base_x) * t
            my   = base_y + (tip_y - base_y) * t
            size = width * (0.7 - t * 0.15)
            self.create_line(mx, my, mx - perp_x * size, my - perp_y * size,
                             fill="#f7f1e8", width=1, stipple="gray75")
            self.create_line(mx, my, mx + perp_x * size, my + perp_y * size,
                             fill="#f7f1e8", width=1, stipple="gray75")

    #Bolha
    def _draw_bubbles(self):
        for b in self._bubbles:
            b["y"] -= b["speed"]
            b["x"] += math.sin(self._t * 1.5 + b["phase"]) * 0.25
            if b["y"] < -10:
                b["y"] = self._H + self._rng.randint(10, 80)
                b["x"] = self._rng.uniform(0.08, 0.92) * self._W
            r = b["r"]
            self.create_oval(b["x"] - r, b["y"] - r, b["x"] + r, b["y"] + r,
                             fill="white", outline="",
                             stipple="gray75" if r < 2 else "gray50")

    #Textos
    def _draw_texts(self):
        self.create_image(self._W * 0.5, self._H * 0.17,  image=self._logo_tk,
                        anchor="center")
        
        self.create_text(self._W * 0.5, self._H * 0.33, text="SISTEMA DE GESTÃO",
                         anchor="center", fill="white", font=("Georgia", 18,"bold"))
        
        self.create_text(self._W * 0.5, self._H * 0.43,   text="Sabores do Pará",
                         anchor="center", fill="white", font=("Georgia", 50, "bold"))
            
        self.create_text(self._W * 0.5, self._H * 0.92,
                         text='"Sabores que contam história"',
                         anchor="center", fill="#f7f1e8", font=("Georgia", 13, "italic"))
        
    def parar(self):
        self._rodando = False 
          
        
