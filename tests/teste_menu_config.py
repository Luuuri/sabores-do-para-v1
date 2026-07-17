import customtkinter as ctk

from app.utils.componentes import Frames, Barras, Botoes
from app.utils.menu_config import MenuConfig
from app.utils.usuario_atual import usuario_atual
from app.utils.estilos import Cores, Fontes


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

usuario_atual["nome"] = "Admin"
usuario_atual["cargo"] = "garçom"


tela =ctk.CTk()
tela.geometry("400x200")
tela.title("Teste - Menu Config")

cores = Cores()
fontes = Fontes()

cabecalho = ctk.CTkFrame(tela,fg_color="white", height=60, corner_radius=0)
cabecalho.pack(fill="x")
cabecalho.pack_propagate(False)

ctk.CTkLabel(cabecalho,text="⚙ Teste Menu Config", font=ctk.CTkFont(size=16, weight="bold")).pack(
    side="left", padx=20)

menu_config = MenuConfig()

btn_config = ctk.CTkButton(cabecalho, text="⚙", width=38, height=38, corner_radius=8,
                           fg_color="transparent", hover_color="#f0f0f0",text_color="#555",
                           font=ctk.CTkFont(size=18))
btn_config.configure(command=lambda: menu_config.abrir(btn_config, cores, fontes))
btn_config.pack(side="right", padx=16, pady=10)

ctk.CTkLabel(tela, text="Clique no botäo ⚙ para abrir o menu", 
             font=ctk.CTkFont(size=14), text_color="#888").pack(expand=True)

tela.mainloop()
