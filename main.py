import customtkinter as ctk

from app.utils.preferencias import carregar_preferencias

prefs = carregar_preferencias()
ctk.set_appearance_mode(prefs.get("tema", "Light"))
ctk.set_default_color_theme("green")


def main():
     # Cria a janela raiz — nunca aparece, só mantém o mainloop vivo
    root = ctk.CTk()
    root.withdraw()  # oculta a janela raiz imediatamente
    
    # 1. Abre o Splash instantaneamente
    from app.view.splash_view import SplashView
    splash = SplashView(root)
    
    # 2. Agenda o carregamento do LoginView após o splash estar visível
    def carregar_login():
        splash.set_status("Iniciando sistema...")
        from app.view.login_view import LoginView
        def exibir_login_quando_splash_fechar(login_view):
            splash.concluir(on_done=login_view.mostrar)

        root.login_view = LoginView(root, on_ready=exibir_login_quando_splash_fechar)
    root.after(80, carregar_login) 
    
    root.mainloop()  


if __name__ == "__main__":
    main()
