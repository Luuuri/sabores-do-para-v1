#COMEÇA POR ESSE CODIGO
#CHAMA TODAS AS TELAS


import tkinter as tk
from tkinter import messagebox
#from app.model.login_model import autenticar_usuario
#from app.view.tela_painel_controle import main
import customtkinter as ctk

# CONFIGURAÇÃO DO CUSTOMTKINTER
# ==============================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")



#JANELA PRINCIPAL
#===========================
janela = ctk.CTk()
janela.title("Login do Sistema")
janela.geometry("900x700")
janela.config(bg="#e9e9e9")
janela.resizable(True, True)

#FUNÇÔES
#============================
def clicar_login():
    email = entrada_email.get()
    senha = entrada_senha.get()

    if email == "" or senha == "":
        messagebox.showwarning("Aviso", "Preencha email e senha")
        return
    
    usuario = autenticar_usuario(email, senha)
    if usuario:
        nome = usuario.get("nome", "Usuário")
        messagebox.showinfo("Sucesso", f"Bem-vindo, {nome}!")
        
        janela.withdraw()  # esconde login
        main()
        
    else:
        messagebox.showerror("Erro", "Email ou senha inválidos")    

def recuperar_senha():
    messagebox.showinfo("Recuperação", "Função de recuperação de senha")
    
        
#TÍTULOS

label_ola = tk.Label(janela, text="Olá!", font=("Arial", 22, "bold"), bg="#e9e9e9", fg="black")
label_ola.place(relx=0.5, rely=0.10, anchor="center")

label_titulo = tk.Label(janela,text="Acesse o sistema",font=("Arial", 34, "bold"),bg="#e9e9e9",fg="black")
label_titulo.place(relx=0.5, rely=0.18, anchor="center")

#CAMPO EMAIL

label_email = tk.Label(janela, text="Email", font=("Arial", 15), bg= "#e9e9e9", fg="black")
label_email.place(relx=0.22, rely=0.33)

entrada_email = tk.Entry(janela, font=("Arial", 16), bd=0, bg="#bdbdbd", fg="black")
entrada_email.place(relx=0.22, rely=0.37, relwidth=0.42, height=50)

#CAMPO SENHA

label_senha = tk.Label(janela, text="Senha", font=("Arial",15), bg="#e9e9e9", fg="black")
label_senha.place(relx=0.22, rely=0.49)

entrada_senha = tk.Entry(janela, font=("Arial", 16), bd=0, bg="#bdbdbd", fg="black", show="*")
entrada_senha.place(relx=0.22, rely=0.53,relwidth=0.42, height=50)

#ESQUECEU A SENHA

botao_esqueceu = tk.Button(janela,text="Esqueceu a senha?",font=("Arial", 13, "bold"),bg="#e9e9e9",fg="#808080",bd=0, activebackground="#e9e9e9",activeforeground="black",cursor="hand2",command=recuperar_senha)
botao_esqueceu.place(relx=0.22, rely=0.65, anchor="w")

#CHECK BOX

variavel_lembrar = tk.IntVar()

check_lembrar = tk.Checkbutton(janela, text="Lembrar senha", font=("Arial", 15, "bold"), bg="#e9e9e9", fg="black", activebackground="#e9e9e9", selectcolor="#bdbdbd", variable=variavel_lembrar)
check_lembrar.place(relx=0.22, rely=0.68)

#BOTÃO ENTRAR

botao_entrar = tk.Button(janela,text="ENTRAR",font=("Arial", 22, "bold"), bg="black",fg="white",activebackground="black",activeforeground="white",  bd=0,cursor="hand2",command=clicar_login)
botao_entrar.place(relx=0.5, rely=0.84, anchor="center", relwidth=0.28, height=90)


janela.mainloop()
