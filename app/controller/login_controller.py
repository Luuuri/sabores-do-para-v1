# login_controller.py - Controller de autenticação
from tkinter import messagebox
from app.model.login_model import autenticar_usuario

from app.utils.usuario_atual import usuario_atual


def login(email: str, senha: str) -> dict | None:
    """
    Valida credenciais do usuário.
    Retorna dados do usuário se sucesso, None se falhar.
    """
    if not email or not senha:
        messagebox.showwarning("Aviso", "Preencha email e senha")
        return None
    
    usuario = autenticar_usuario(email, senha)
    
    if usuario:
        # Ajusta chaves compatíveis (o SELECT retorna id_funcionario)
        usuario_id = usuario.get("id") or usuario.get("id_funcionario")
        usuario_atual["id"] = usuario_id
        usuario_atual["id_funcionario"] = usuario_id
        usuario_atual["nome"] = usuario.get("nome")
        usuario_atual["email"] = usuario.get("email")
        usuario_atual["telefone"] = usuario.get("telefone")
        usuario_atual["cargo"] = usuario.get("cargo")
        usuario_atual["nivel_acesso"] = usuario.get("nivel_acesso")
        usuario_atual["ativo"] = usuario.get("ativo")
        
        return usuario
    else:
        messagebox.showerror("Erro", "Email ou senha inválidos")
        return None


def verificar_acesso(usuario: dict) -> bool:
    """
    Verifica se o usuário tem acesso ao sistema.
    """
    if not usuario:
        return False
    
    if not usuario.get("ativo"):
        messagebox.showerror("Erro", "Usuário inativo")
        return False
    
    return True
