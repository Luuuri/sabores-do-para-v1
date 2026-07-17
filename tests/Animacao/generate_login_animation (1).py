#!/usr/bin/env python3
"""
generate_login_animation.py
Gera o arquivo login_panel.webp — painel botânico animado do login "Sabores do Pará".

Execute UMA VEZ antes de rodar login_window.py:
    python generate_login_animation.py

Requer:
    pip install pillow

Tempo estimado de geração: 1-3 minutos (160 frames, operação única).
"""

from PIL import Image, ImageDraw, ImageFilter
import math
import os
import sys

# ═══════════════════════════════════════════════════════════════
#  CONFIGURAÇÕES — ajuste aqui se necessário
# ═══════════════════════════════════════════════════════════════

W, H      = 800, 900        # dimensões de referência (redimensionado em tempo real pelo canvas)
FPS       = 20              # frames por segundo (20 = suave, leve)
LOOP_S    = 8.0             # duração do loop em segundos
N_FRAMES  = int(FPS * LOOP_S)  # 160 frames total
RADIUS    = 0               # 0 = sem arredondamento (o canvas já tem bordas retas)

# Paleta de cores — baseada no design web
CORAL_D   = (184,  65,  24)   # topo do gradiente  (#B84118)
CORAL_M   = (201,  78,  26)   # meio do gradiente  (#C94E1A)
LEAF_G    = (143, 168,  85)   # base do gradiente  (#8FA855)
WHITE     = (255, 255, 255)
GOLD      = (255, 235, 150)   # cor das partículas
GOLD_BRI  = (255, 248, 200)   # variante mais clara

OUT_FILE  = os.path.join(os.path.dirname(__file__), "login_panel.webp")


# ═══════════════════════════════════════════════════════════════
#  FUNÇÕES DE EASING E ANIMAÇÃO
# ═══════════════════════════════════════════════════════════════

def eio(t):
    """Ease-in-out coseno: entrada 0..1, saída 0..1 com aceleração suave."""
    return (1.0 - math.cos(t * math.pi)) / 2.0


def anim_t(frame, delay_s, dur_s, alternate=True):
    """
    Retorna o progresso [0..1] da animação para o frame dado.
    - delay_s: atraso inicial (em segundos)
    - dur_s:   duração de uma iteração (em segundos)
    - alternate: True = vai-e-volta suave (infinite alternate)
                 False = apenas vai de 0→1 e recomeça
    """
    t_s = (frame / FPS - delay_s) % LOOP_S
    t_s = max(t_s, 0.0)
    raw = (t_s % dur_s) / dur_s   # progresso linear 0..1 dentro do ciclo
    if alternate:
        raw = raw * 2.0
        if raw > 1.0:
            raw = 2.0 - raw
    return eio(raw)


# ═══════════════════════════════════════════════════════════════
#  GEOMETRIA — curvas de Bézier e polígonos botânicos
# ═══════════════════════════════════════════════════════════════

def cubic_bezier(t, p0, p1, p2, p3):
    u = 1.0 - t
    return (
        u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
        u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1],
    )


def leaf_polygon(size, n_per_seg=14):
    """
    Polígono que aproxima a folha de Jambu do SVG original.
    O path SVG foi: M 0,-44 C 14,-40 32,-22 33,-3 C 34,16 20,36 0,44
                    C -20,36 -34,16 -33,-3 C -32,-22 -14,-40 0,-44 Z
    """
    scale = size / 44.0
    segs = [
        ((0,-44), (14,-40), (32,-22), (33,-3)),
        ((33,-3), (34, 16), (20, 36), ( 0, 44)),
        ((0, 44), (-20,36), (-34,16), (-33,-3)),
        ((-33,-3),(-32,-22),(-14,-40),(  0,-44)),
    ]
    pts = []
    for seg in segs:
        for i in range(n_per_seg):
            x, y = cubic_bezier(i / n_per_seg, *seg)
            pts.append((x * scale, y * scale))
    return pts


def petal_polygon(size, n_per_seg=14):
    """Pétala — mais estreita e alongada que a folha."""
    scale = size / 46.0
    segs = [
        (( 0,-46), (14,-34), (18, -8), (14, 14)),
        ((14, 14), (10, 30), ( 5, 36), ( 0, 36)),
        (( 0, 36), (-5, 36), (-10,30), (-14,14)),
        ((-14,14), (-18,-8), (-14,-34),(  0,-46)),
    ]
    pts = []
    for seg in segs:
        for i in range(n_per_seg):
            x, y = cubic_bezier(i / n_per_seg, *seg)
            pts.append((x * scale, y * scale))
    return pts


def rotate_pts(pts, angle_deg):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return [(x*cos_a - y*sin_a, x*sin_a + y*cos_a) for x, y in pts]


def translate_pts(pts, cx, cy):
    return [(x + cx, y + cy) for x, y in pts]


def to_int(pts):
    return [(int(round(x)), int(round(y))) for x, y in pts]


# ═══════════════════════════════════════════════════════════════
#  MÁSCARA DE CANTOS ARREDONDADOS
# ═══════════════════════════════════════════════════════════════

def make_corner_mask(w, h, r):
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=r, fill=255)
    return mask

CORNER_MASK = make_corner_mask(W, H, RADIUS)


# ═══════════════════════════════════════════════════════════════
#  ELEMENTOS DA CENA
#  Todos os tempos são ajustados para fechar loop perfeito em 8s
# ═══════════════════════════════════════════════════════════════

# (cx_frac, cy_frac, size_px, rotacao_base, delay_s, dur_s, alpha_0_255)
LEAVES = [
    (0.10, 0.60, 60,  20,  0.0, 4.0,  55),
    (0.62, 0.73, 46, -15,  1.6, 4.0,  45),
    (0.40, 0.52, 38,  35,  3.2, 4.0,  40),
    (0.76, 0.42, 55, -25,  0.8, 4.0,  50),
    (0.24, 0.78, 33,   8,  2.4, 4.0,  36),
    (0.84, 0.63, 44,  45,  4.0, 4.0,  48),
]

PETALS = [
    (0.52, 0.32, 34,  60,  0.5, 4.0,  44),
    (0.16, 0.42, 28, -30,  2.0, 4.0,  38),
    (0.72, 0.26, 24,  15,  3.6, 4.0,  36),
    (0.90, 0.52, 26, -50,  1.2, 4.0,  40),
]

# (cx_frac, cy_frac, raio, delay_s, dur_s, variante_clara)
PARTICLES = [
    (0.12, 0.88, 3, 0.0, 4.0, False),
    (0.28, 0.92, 2, 1.6, 5.0, True),
    (0.45, 0.86, 4, 3.2, 3.5, False),
    (0.58, 0.94, 2, 0.8, 4.5, True),
    (0.72, 0.89, 3, 4.0, 4.0, False),
    (0.84, 0.84, 2, 2.0, 4.3, True),
    (0.35, 0.80, 3, 4.8, 3.3, False),
    (0.65, 0.78, 2, 2.9, 4.8, True),
    (0.06, 0.74, 4, 6.4, 4.0, False),
    (0.92, 0.76, 2, 3.6, 5.0, True),
]


# ═══════════════════════════════════════════════════════════════
#  GRADIENTE BASE (gerado uma vez, copiado por frame)
# ═══════════════════════════════════════════════════════════════

def build_gradient():
    img = Image.new("RGBA", (W, H))
    d   = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        if t < 0.40:
            u = t / 0.40
            c = tuple(int(CORAL_D[i] + (CORAL_M[i] - CORAL_D[i]) * u) for i in range(3))
        else:
            u = (t - 0.40) / 0.60
            c = tuple(int(CORAL_M[i] + (LEAF_G[i] - CORAL_M[i]) * u) for i in range(3))
        d.line([(0, y), (W - 1, y)], fill=(*c, 255))
    return img

BG_GRADIENT = build_gradient()


# ═══════════════════════════════════════════════════════════════
#  RENDERIZAÇÃO DE UM FRAME
# ═══════════════════════════════════════════════════════════════

def render_frame(fn):
    base = BG_GRADIENT.copy()

    # ── Orbe de brilho dourado (canto superior direito) ───────
    gt = anim_t(fn, 0.0, 4.5)
    g_alpha = int(110 + 80 * gt)
    g_scale = 1.0 + 0.12 * gt
    gw, gh  = int(220 * g_scale), int(175 * g_scale)
    gcx, gcy = int(W * 0.76), int(H * 0.12)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [gcx - gw//2, gcy - gh//2, gcx + gw//2, gcy + gh//2],
        fill=(*GOLD, g_alpha)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=52))
    base = Image.alpha_composite(base, glow)

    # ── Overlay de brilho que "respira" ───────────────────────
    bt = anim_t(fn, 0.0, 4.0)
    b_alpha = int(70 + 60 * bt)
    breathe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(breathe).ellipse(
        [int(W * 0.22), -60, int(W * 1.12), int(H * 0.58)],
        fill=(*GOLD_BRI, b_alpha)
    )
    breathe = breathe.filter(ImageFilter.GaussianBlur(radius=82))
    base = Image.alpha_composite(base, breathe)

    # ── Folha grande girando devagar ──────────────────────────
    big_rot = (fn / N_FRAMES) * 360.0  # 1 giro completo em 8s
    big_pts = leaf_polygon(size=220)
    big_pts = rotate_pts(big_pts, big_rot)
    big_pts = translate_pts(big_pts, W * 0.54, H * 0.43)

    big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd  = ImageDraw.Draw(big)
    bd.polygon(to_int(big_pts), fill=(*WHITE, 20))
    spine_top = rotate_pts([(0.0, -220.0)], big_rot)[0]
    spine_bot = rotate_pts([(0.0,  220.0)], big_rot)[0]
    cx_b, cy_b = int(W * 0.54), int(H * 0.43)
    bd.line(
        [(int(cx_b + spine_top[0]), int(cy_b + spine_top[1])),
         (int(cx_b + spine_bot[0]), int(cy_b + spine_bot[1]))],
        fill=(*WHITE, 28), width=2
    )
    base = Image.alpha_composite(base, big)

    # ── Folhas flutuantes ─────────────────────────────────────
    for (cfx, cfy, sz, brot, delay, dur, alpha) in LEAVES:
        t = anim_t(fn, delay, dur, alternate=True)
        dx   = 12.0 * t
        dy   = -22.0 * t
        drot = 7.0 * t

        cx = int(cfx * W + dx)
        cy = int(cfy * H + dy)
        pts = leaf_polygon(size=sz)
        pts = rotate_pts(pts, brot + drot)
        pts = translate_pts(pts, cx, cy)

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld    = ImageDraw.Draw(layer)
        ld.polygon(to_int(pts), fill=(*WHITE, alpha))

        # Nervura central
        st = rotate_pts([(0.0, float(-sz))], brot + drot)[0]
        sb = rotate_pts([(0.0, float( sz))], brot + drot)[0]
        ld.line(
            [(int(cx + st[0]), int(cy + st[1])),
             (int(cx + sb[0]), int(cy + sb[1]))],
            fill=(*WHITE, min(alpha + 40, 255)), width=1
        )
        base = Image.alpha_composite(base, layer)

    # ── Pétalas flutuantes ────────────────────────────────────
    for (cfx, cfy, sz, brot, delay, dur, alpha) in PETALS:
        t = anim_t(fn, delay, dur, alternate=True)
        dx   = 14.0 * t
        dy   = -35.0 * t
        drot = 10.0 * t

        cx = int(cfx * W + dx)
        cy = int(cfy * H + dy)
        pts = petal_polygon(size=sz)
        pts = rotate_pts(pts, brot + drot)
        pts = translate_pts(pts, cx, cy)

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon(to_int(pts), fill=(*WHITE, alpha))
        base = Image.alpha_composite(base, layer)

    # ── Partículas subindo ────────────────────────────────────
    p_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p_layer)

    for (cfx, cfy, r, delay, dur, is_bright) in PARTICLES:
        t = anim_t(fn, delay, dur, alternate=False)

        # Opacidade: aparece, sobe, desaparece
        if t < 0.15:
            a = int(200 * (t / 0.15))
        elif t > 0.75:
            a = int(200 * (1.0 - t) / 0.25)
        else:
            a = 200

        cy_cur = int(cfy * H - 115.0 * t)
        cx_cur = int(cfx * W + 7.0 * math.sin(t * 2.0 * math.pi))
        color  = GOLD_BRI if is_bright else GOLD

        # Glow suave: círculos concêntricos decrescentes
        for gr in [r * 3, r * 2, r]:
            ga = int(a * (r / gr) * 0.35)
            pd.ellipse(
                [cx_cur - gr, cy_cur - gr, cx_cur + gr, cy_cur + gr],
                fill=(*color, ga)
            )
        # Núcleo da partícula
        pd.ellipse(
            [cx_cur - r, cy_cur - r, cx_cur + r, cy_cur + r],
            fill=(*color, a)
        )

    base = Image.alpha_composite(base, p_layer)

    # ── Aplica máscara de cantos arredondados ─────────────────
    base.putalpha(CORNER_MASK)

    return base


# ═══════════════════════════════════════════════════════════════
#  MAIN — geração e exportação
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Verifica versão mínima do Pillow
    from PIL import __version__ as PIL_VER
    major = int(PIL_VER.split(".")[0])
    if major < 9:
        print(f"[ERRO] Pillow >= 9.1.0 necessário para WebP animado. Versão atual: {PIL_VER}")
        print("       Execute: pip install --upgrade pillow")
        sys.exit(1)

    print(f"Gerando {N_FRAMES} frames  ({FPS} fps · {LOOP_S}s loop · {W}×{H}px)")
    print(f"Saída: {OUT_FILE}")
    print()

    frames = []
    for i in range(N_FRAMES):
        if i % 20 == 0:
            pct = int(i / N_FRAMES * 100)
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"  [{bar}] {pct:3d}%  frame {i+1:>3}/{N_FRAMES}", end="\r")
        frames.append(render_frame(i))

    print(f"\n  Exportando WebP animado…")

    frames[0].save(
        OUT_FILE,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),   # ms por frame
        loop=0,                      # 0 = loop infinito
        quality=85,
        method=4,
    )

    size_mb = os.path.getsize(OUT_FILE) / 1024 / 1024
    print(f"\n✓ login_panel.webp salvo com sucesso! ({size_mb:.1f} MB, {N_FRAMES} frames)")
    print("  Agora execute login_window.py para ver o resultado no customtkinter.")
