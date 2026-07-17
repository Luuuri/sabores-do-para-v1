# tela_clientes.py - View de Clientes (só UI)
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.controller.cliente_controller import (
    salvar_cliente, 
    excluir_cliente, 
    listar_clientes,
    buscar_clientes
)


# ===========================================================
# VARIÁVEIS DE ESTADO
# ===========================================================
current_client_id = None
table = None


# ===========================================================
# FUNÇÕES DE NAVEGAÇÃO (VIEW)
# ===========================================================
def show_form(dados=None):
    """Mostra o formulário de cliente."""
    list_screen.pack_forget()
    form_screen.pack(fill="both", expand=True)
    address_frame.pack_forget()
    
    # Limpa campos
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_cpf.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_cep.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    
    global current_client_id
    
    if dados:
        # Modo edição - preenche campos
        current_client_id = dados.get("id")
        entry_name.insert(0, dados.get("nome", ""))
        entry_phone.insert(0, dados.get("telefone", ""))
        entry_cpf.insert(0, dados.get("cpf", ""))
        entry_email.insert(0, dados.get("email", ""))
        entry_cep.insert(0, dados.get("cep", ""))
        entry_address.insert(0, dados.get("logradouro", ""))
    else:
        # Modo novo
        current_client_id = None


def show_list():
    """Mostra a lista de clientes."""
    form_screen.pack_forget()
    list_screen.pack(fill="both", expand=True)
    recarregar_tabela()


def open_address_fields():
    """Mostra campos de endereço."""
    address_frame.pack(pady=10)


def on_salvar():
    """Salva cliente (chama controller)."""
    global current_client_id
    
    nome = entry_name.get()
    telefone = entry_phone.get()
    cpf = entry_cpf.get()
    email = entry_email.get()
    cep = entry_cep.get()
    logradouro = entry_address.get()
    
    if nome == "":
        messagebox.showwarning("Aviso", "O campo Nome é obrigatório!")
        return
    
    dados = {
        "id": current_client_id,
        "nome": nome,
        "telefone": telefone,
        "cpf": cpf,
        "email": email,
        "cep": cep,
        "logradouro": logradouro,
    }
    
    salvar_cliente(dados)
    
    if current_client_id:
        messagebox.showinfo("Sucesso", "Cliente atualizado!")
    else:
        messagebox.showinfo("Sucesso", "Cliente cadastrado!")
    
    show_list()


def on_editar():
    """Edita cliente selecionado."""
    selected = table.focus()
    if not selected:
        messagebox.showinfo("Editar", "Selecione um cliente na lista.")
        return
    
    dados = table.item(selected)
    valores = dados.get("values", [])
    
    if not valores:
        return
    
    dados_cliente = {
        "id": valores[0],
        "nome": valores[1],
        "telefone": valores[2],
        "cpf": valores[5] if len(valores) > 5 else "",
        "email": valores[6] if len(valores) > 6 else "",
        "cep": valores[7] if len(valores) > 7 else "",
        "logradouro": valores[8] if len(valores) > 8 else "",
    }
    
    show_form(dados_cliente)


def on_excluir():
    """Exclui cliente selecionado."""
    selected = table.focus()
    if not selected:
        messagebox.showwarning("Excluir", "Selecione um cliente para excluir.")
        return
    
    if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir?"):
        return
    
    dados = table.item(selected)
    valores = dados.get("values", [])
    
    if valores:
        excluir_cliente(valores[0])
        recarregar_tabela()


def on_buscar(event=None):
    """Busca clientes."""
    termo = entry_busca.get()
    resultados = buscar_clientes(termo)
    popular_tabela(resultados)


def recarregar_tabela():
    """Recarrega dados na tabela."""
    clientes = listar_clientes()
    popular_tabela(clientes)


def popular_tabela(dados):
    """Popula tabela com dados."""
    for item in table.get_children():
        table.delete(item)
    
    for cliente in dados:
        table.insert("", "end", values=(
            cliente.get("id", ""),
            cliente.get("nome", ""),
            cliente.get("telefone", ""),
            cliente.get("email", ""),
            "Ativo"
        ))


# ===========================================================
# JANELA PRINCIPAL
# ===========================================================
root = tk.Tk()
root.title("Point dos Sabores - Gestão de Clientes")
root.geometry("1100x700")
root.configure(bg="#f5f5f5")
root.minsize(1100, 650)


# ===========================================================
# TELA DE LISTA
# ===========================================================
list_screen = tk.Frame(root, bg="#f5f5f5")
list_screen.pack(fill="both", expand=True)

header = tk.Frame(list_screen, bg="#f5f5f5")
header.pack(fill="x", padx=20, pady=20)

tk.Label(header, text="Clientes", font=("Arial", 18, "bold"), bg="#f5f5f5").pack(side="left")

entry_busca = tk.Entry(header, width=30)
entry_busca.pack(side="left", padx=10)
entry_busca.bind("<KeyRelease>", on_buscar)

tk.Button(header, text="+ Novo Cliente", bg="#2ecc71", fg="white", command=lambda: show_form()).pack(side="right", padx=5)
tk.Button(header, text="Editar", command=on_editar).pack(side="right", padx=5)
tk.Button(header, text="Excluir", bg="#ff8a8a", command=on_excluir).pack(side="right", padx=5)

columns = ("ID", "Nome", "Telefone", "Email", "Status")
table = ttk.Treeview(list_screen, columns=columns, show="headings")

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=150)

table.pack(fill="both", expand=True, padx=20, pady=10)


# ===========================================================
# TELA DE FORMULÁRIO
# ===========================================================
form_screen = tk.Frame(root, bg="#f5f5f5")

tk.Label(form_screen, text="Informações do Cliente", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=20)

tk.Label(form_screen, text="Nome*", bg="#f5f5f5").pack()
entry_name = tk.Entry(form_screen, width=45)
entry_name.pack(pady=5)

tk.Label(form_screen, text="Telefone", bg="#f5f5f5").pack()
entry_phone = tk.Entry(form_screen, width=45)
entry_phone.pack(pady=5)

tk.Label(form_screen, text="CPF", bg="#f5f5f5").pack()
entry_cpf = tk.Entry(form_screen, width=45)
entry_cpf.pack(pady=5)

tk.Label(form_screen, text="Email", bg="#f5f5f5").pack()
entry_email = tk.Entry(form_screen, width=45)
entry_email.pack(pady=5)

tk.Button(form_screen, text="+ Adicionar Endereço", command=open_address_fields, fg="blue", bd=0).pack(pady=10)

address_frame = tk.Frame(form_screen, bg="#f5f5f5")

tk.Label(address_frame, text="CEP", bg="#f5f5f5").pack()
entry_cep = tk.Entry(address_frame, width=45)
entry_cep.pack()

tk.Label(address_frame, text="Logradouro / Cidade", bg="#f5f5f5").pack()
entry_address = tk.Entry(address_frame, width=45)
entry_address.pack()

button_area = tk.Frame(form_screen, bg="#f5f5f5")
button_area.pack(pady=30)

tk.Button(button_area, text="Salvar", bg="black", fg="white", width=15, command=on_salvar).pack(side="left", padx=10)
tk.Button(button_area, text="Cancelar", width=15, command=show_list).pack(side="left", padx=10)


# ===========================================================
# INICIALIZAÇÃO
# ===========================================================
recarregar_tabela()
root.mainloop()