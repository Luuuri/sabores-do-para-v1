import customtkinter as ctk
from app.utils.usuario_atual import usuario_atual
from app.controller.funcionario_controller import buscar_funcionario, salvar_funcionario
from app.utils.preferencias import carregar_preferencias, salvar_preferencias


class MenuConfig:
    """
    Menu dropdow de configuraçöes no estilo CustoTkiter.
    Segue o mesmo padräo do BotaoFunil dso componentes.py
    Use no _criar_barra_topo do FrameLayoutPadrao:
      from app.util.menu_config import MenuConfig
      
      self.menu_config = MenuConfig()
      bnt_config = Botoes.BotaoConfig(frame_direita, self.icones, self.cores)
      btn_config.configure(command=lambda: self.menu_config.abrir(btn_config, self.cores,self.fontes))
      btn_config.pack(side="rigth", padx=15, pady=10)
    """
    
    def __init__(self):
        self.menu = None
        
    def abrir(self, widget, cores, fontes):
        self._widget_ref = widget
        self._cores = cores   # ✅ salva cores e fontes para usar no _sair
        self._fontes = fontes
        self._atualizar_usuario_atual()
        
        # Se já estiver aberto, fecha
        if self.menu and self.menu.winfo_exists():
            self.menu.destroy()
            self.menu = None
            return
        
        self.menu = ctk.CTkToplevel(widget.winfo_toplevel())
        self.menu.geometry("220x200")
        self.menu.overrideredirect(True)
        self.menu.configure(fg_color=cores.fundo.branco)
       
        # Posição abaixo do botão
        posicao_x = widget.winfo_rootx() - 160
        posicao_y = widget.winfo_rooty() + widget.winfo_height() + 4
        
        self.menu.geometry(f"+{posicao_x}+{posicao_y}")
        self.menu.lift()
        self.menu.attributes("-topmost", True)
       
        # Fecha ao clicar fora
        widget.winfo_toplevel().bind("<Button-1>", self._clique_fora, add="+")
         
        # Conteúdo
        conteudo = ctk.CTkFrame(self.menu, fg_color=cores.fundo.branco, corner_radius=12,
                                border_width=2, border_color=cores.card.borda_card)
        conteudo.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Nome e cargo do usuário logado
        nome = usuario_atual.get("nome", "Usuário")
        cargo = usuario_atual.get("cargo", "")
        
        ctk.CTkLabel(conteudo, text=f"👤  {nome}", font=ctk.CTkFont(size=13, weight="bold"), 
                     text_color=cores.texto.principal, anchor="w").pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(conteudo, text=f"  {cargo}", font=ctk.CTkFont(size=11), text_color=cores.texto.secundario,
                     anchor="w").pack(fill="x", padx=14, pady=(0, 6))
        
        # Botão Editar Perfil
        botao_editar = ctk.CTkButton(conteudo, text="⚙️  Editar perfil", fg_color="transparent", hover_color=cores.fundo.cinza,
                                     text_color=cores.texto.principal, font=ctk.CTkFont(size=12), anchor="w", height=36,
                                     command=lambda: self._confirmar_senha(widget, cores, fontes))
        botao_editar.pack(fill="x", padx=8, pady=(6, 0))
        
        # Botão Modo Escuro/Claro
        def _texto_tema():
            return"☀️  Modo Claro" if ctk.get_appearance_mode() == "Dark" else "🌙  Modo Escuro"
        
        def _alternar_tema():
            modo = ctk.get_appearance_mode()
            novo = "Dark" if modo == "Light" else "Light"
            salvar_preferencias({"tema": novo})
            self._fechar()
            
            def _aplicar():
                ctk.set_appearance_mode(novo)
                topo = widget.winfo_toplevel()
                if hasattr(topo, "_recarregar_tema"):
                    topo._recarregar_tema()
                
            widget.winfo_toplevel().after(50, _aplicar)
            
        botao_tema = ctk.CTkButton(conteudo, text=_texto_tema(), fg_color="transparent", 
                                   hover_color=cores.fundo.cinza, text_color=cores.texto.principal, 
                                   font=ctk.CTkFont(size=12), anchor="w", height=36,
                                   command=_alternar_tema)
        botao_tema.pack(fill="x", padx=8, pady=(0, 0))    
        
        # Separador
        ctk.CTkFrame(conteudo, fg_color=cores.card.borda_card, height=1).pack(fill="x", padx=10)
        
        # Botão Sair
        botao_sair = ctk.CTkButton(conteudo, text="↪ Sair do sistema", fg_color="transparent", hover_color=cores.fundo.cinza,
                                   text_color=cores.botao.excluir, font=ctk.CTkFont(size=12), anchor="w",
                                   height=36, command=self._sair)
        botao_sair.pack(fill="x", padx=8, pady=6)
        
        self.menu.bind("<FocusOut>", lambda e: self._fechar())
        self.menu.bind("<Escape>",   lambda e: self._fechar())
        
    def _confirmar_senha(self, widget, cores, fontes):
        self._fechar()

        janela_pai = widget.winfo_toplevel()

        dialogo = ctk.CTkToplevel(janela_pai)
        dialogo.title(" 🔐  Confirmar identidade")
        dialogo.geometry("380x240")
        dialogo.resizable(False, False)
        dialogo.configure(fg_color=cores.fundo.principal)
        dialogo.lift()
        dialogo.attributes("-topmost", True)

        # Centraliza na janela pai
        x = janela_pai.winfo_rootx() + janela_pai.winfo_width() // 2 - 190
        y = janela_pai.winfo_rooty() + janela_pai.winfo_height() // 2 - 120
        dialogo.geometry(f"+{x}+{y}")

        # Borda arredondada
        frame = ctk.CTkFrame(dialogo, fg_color=cores.fundo.branco,
                            corner_radius=16, border_width=2,
                            border_color=cores.card.borda_card)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Digite sua senha para continuar",
                    font=ctk.CTkFont(size=11),
                    text_color=cores.texto.passivo).pack(pady=(20, 10))

        campo_senha = ctk.CTkEntry(
            frame, show="*", height=42,
            placeholder_text="Sua senha atual...",
            placeholder_text_color=cores.texto.passivo,
            fg_color=cores.entry.formulario,
            border_width=0, corner_radius=8,
            font=ctk.CTkFont(size=13),
            text_color=cores.texto.principal
        )
        campo_senha.pack(padx=20, fill="x")

        lbl_erro = ctk.CTkLabel(frame, text="",
                                text_color=cores.texto.vermelho,
                                font=ctk.CTkFont(size=11))
        lbl_erro.pack(pady=(4, 0))

        def confirmar():
            from app.model.login_model import autenticar_usuario
            email = usuario_atual.get("email", "")
            senha = campo_senha.get()
            if not senha:
                lbl_erro.configure(text="❌ Digite sua senha.")
                return
            resultado = autenticar_usuario(email, senha)
            if resultado:
                dialogo.destroy()
                self._abrir_editar_perfil(widget, cores, fontes)
            else:
                lbl_erro.configure(text="❌ Senha incorreta. Tente novamente.")
                campo_senha.delete(0, "end")

        ctk.CTkButton(
            frame, text="Confirmar", height=42,
            fg_color=cores.fundo.laranja,
            hover_color=cores.texto.laranja_HOVER,
            text_color=cores.texto.branco,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=confirmar
        ).pack(padx=20, fill="x", pady=(8, 16))

        campo_senha.bind("<Return>", lambda e: confirmar())
        dialogo.after(100, lambda: campo_senha.focus())

    def _atualizar_usuario_atual(self):
        id_funcionario = usuario_atual.get("id")
        if not id_funcionario:
            return
        dados = buscar_funcionario(id_funcionario)
        if not dados:
            return
        usuario_atual.update({
            "id": dados.get("id"),
            "id_funcionario": dados.get("id"),
            "nome": dados.get("nome"),
            "email": dados.get("email"),
            "cargo": dados.get("cargo"),
            "ativo": dados.get("ativo"),
        })
        
        
    def _abrir_editar_perfil(self, widget, cores, fontes):
        from app.view.tela_funcionarios_cad import TelaFuncionarios
        from app.utils.estilos import Icones
        
        self._fechar()
        
        nivel = usuario_atual.get("nivel_acesso", "")
        janela_pai = widget.winfo_toplevel()
        
        dados = {
            "id":        usuario_atual.get("id"),
            "nome":      usuario_atual.get("nome"),
            "email":     usuario_atual.get("email"),
            "telefone":  usuario_atual.get("telefone", ""),
            "cargo":     usuario_atual.get("cargo"),
            "ativo":     True,
        }

        # garante que o formulário receba telefone também
        if "telefone" not in dados:
            dados["telefone"] = ""


        
        if nivel == "administrador" and hasattr(janela_pai, "_abrir_cadatro"):
            janela_pai._abrir_cadatro(dados)
            return
        
        janela = ctk.CTkToplevel(janela_pai)
        janela.title("Editar Perfil")
        janela.geometry("1200x780")

        
        icones = Icones()
        # Permite que qualquer funcionário altere sua própria senha no modo de edição,
        # mantendo o campo de senha oculto até o botão "Alterar Senha" ser pressionado.
        def salvar_perfil(dados):
            salvar_funcionario(dados)
            self._notificar_usuario_atualizado(janela_pai)

        tela = TelaFuncionarios(
            janela, cores, fontes, icones,
            on_salvar=salvar_perfil,
            on_voltar=janela.destroy,
            show_password_button=True,
            mostrar_senha_no_editar=False,
        )
        tela.pack(fill="both", expand=True)
        
        tela.preencher_dados(dados)
        tela.update_idletasks()
        janela.after(10, lambda: tela.update_idletasks())
        
        # Permissões por nível
        if nivel == "administrador":
            # Admin pode tudo
            tela.frame_cadastro.cargo.menu.configure(state="normal")
            tela.frame_cadastro.email.entry.configure(state="normal")
        else:
            # Funcionário pode editar nome, email e senha, mas não cargo
            tela.frame_cadastro.cargo.menu.configure(state="disabled")

    def _notificar_usuario_atualizado(self, janela):
        if hasattr(janela, "atualizar_usuario"):
            janela.atualizar_usuario()
             
         
        
    def _clique_fora(self, evento):
        if not self.menu or not self.menu.winfo_exists():
            self._widget_ref.winfo_toplevel().unbind("<Button-1>")  # ✅ era self._widget
            return
        x1 = self.menu.winfo_rootx()
        y1 = self.menu.winfo_rooty()
        x2 = x1 + self.menu.winfo_width()
        y2 = y1 + self.menu.winfo_height()
        clicou_dentro = (x1 <= evento.x_root <= x2 and y1 <= evento.y_root <= y2) 
        
        if not clicou_dentro:
            self._fechar()
            self._widget_ref.winfo_toplevel().unbind("<Button-1>")
            
    def _fechar(self):
        if self.menu and self.menu.winfo_exists():
            self.menu.destroy()
            self.menu = None
        try:
            self._widget_ref.winfo_toplevel().unbind("<Button-1>")
        except Exception:
            pass
            
    def _sair(self):
        self._fechar()
        # Identifica a janela topo (a janela atual) e a janela raiz (master)
        topo = self._widget_ref.winfo_toplevel()
        root = getattr(topo, 'master', topo)
        # Resolve o root real caminhando pelos masters (mais robusto)
        curr = topo
        visited = []
        while True:
            visited.append(repr(curr))
            parent = getattr(curr, 'master', None)
            if not parent or parent is curr:
                break
            curr = parent
        root = curr
        # Fecha as janelas filhas do root de forma segura (não destroi o root em si)
        try:
            filhos = list(root.winfo_children())
            for janela in filhos:
                if janela is root:
                    continue
                try:
                    if janela.winfo_exists():
                        janela.destroy()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            root.update_idletasks()
        except Exception:
            pass

        try:
            root.update_idletasks()
        except Exception:
            pass

        # Agendar a criação da tela de login para o próximo ciclo de eventos
        def _criar_login():
            try:
                if root.winfo_viewable():
                    root.withdraw()
                if hasattr(root, "login_view") and getattr(root.login_view, "winfo_exists", lambda: False)():
                    try:
                        root.login_view.destroy()
                    except Exception:
                        pass
                from app.view.login_view import LoginView
                root.login_view = LoginView(root, on_ready=lambda lv: lv.mostrar())
                root.withdraw()
                root.update_idletasks()
            except Exception:
                import traceback as _tb
                _tb.print_exc()

        try:
            root.withdraw()
        except Exception:
            pass

        try:
            root.after_idle(_criar_login)
        except Exception:
            # fallback síncrono caso after falhe
            _criar_login()
