import customtkinter as ctk
from tkinter import Canvas
import random
from PIL import Image, ImageTk
import os

ctk.set_appearance_mode("light")

app = ctk.CTk()
app.geometry("1100x650")
app.configure(fg_color="#e9e3dc")

# =========================
# FRAME ESQUERDO
# =========================
left_frame = ctk.CTkFrame(
    app,
    width=500,
    corner_radius=25,
    fg_color="transparent"
)
left_frame.pack(side="left", padx=40, pady=40)

canvas = Canvas(
    left_frame,
    width=500,
    height=550,
    highlightthickness=0
)
canvas.pack()

# =========================
# FUNDO GRADIENTE
# =========================
def draw_gradient():
    r1, g1, b1 = (207, 77, 35)
    r2, g2, b2 = (219, 185, 72)

    for i in range(550):
        r = int(r1 + (r2 - r1) * i / 550)
        g = int(g1 + (g2 - g1) * i / 550)
        b = int(b1 + (b2 - b1) * i / 550)

        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, 500, i, fill=color)

draw_gradient()

# =========================
# TEXTO
# =========================
canvas.create_text(
    40,
    50,
    text="SISTEMA DE GESTÃO",
    anchor="nw",
    fill="white",
    font=("Montserrat", 10, "bold")
)

canvas.create_text(
    40,
    90,
    text="Sabores\ndo Pará",
    anchor="nw",
    fill="white",
    font=("Georgia", 34, "bold")
)

canvas.create_text(
    40,
    500,
    text='"Sabores que contam história"',
    anchor="sw",
    fill="white",
    font=("Georgia", 16, "italic")
)

# =========================
# FOLHAS ANIMADAS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

image_path = os.path.join(BASE_DIR, "leaf.png")

print(image_path)
print(os.path.exists(image_path))

img = Image.open(image_path).resize((30, 30))
leaf_img = ImageTk.PhotoImage(img)

particles = []

for _ in range(15):

    x = random.randint(20, 480)
    y = random.randint(20, 550)

    # cria imagem no canvas
    leaf = canvas.create_image(
        x,
        y,
        image=leaf_img
    )

    particles.append({
        "id": leaf,
        "speed": random.uniform(0.3, 1)
    })
# =========================
# ANIMAÇÃO
# =========================
def animate():
    for particle in particles:
        canvas.move(particle["id"], 0, -particle["speed"])

        coords = canvas.coords(particle["id"])

        # quando sair da tela volta embaixo
        if coords[3] < 0:
            x = random.randint(20, 480)

            canvas.coords(
                particle["id"],
                x,
                560,
                x + 20,
                570
            )

    app.after(30, animate)

animate()

app.mainloop()