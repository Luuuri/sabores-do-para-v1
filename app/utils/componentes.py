"""
componentes.py - Widgets reutilizáveis do app.

Importação básica:
    from app.utils.componentes import Frames, Botoes, Campos, Barras, TabelaGenerica

Exemplo rápido:
    btn   = Botoes.BotaoSalvar(master, cores, fontes)
    campo = Campos.CampoTexto(master, "Nome", "Digite...", cores, fontes)
    valor = campo.get()
    campo.set("abc")
"""

import os
import shutil
import customtkinter as ctk
from tkinter import filedialog as fd
from PIL import Image
from app.utils.estilos import Cores, Fontes, Icones
from app.utils.helpers import preparar_foto, preparar_foto_retangular

PASTA_PRODUTOS = os.path.join(os.path.dirname(__file__), "assets", "produtos")
from tkinter import messagebox


# ── FRAMES ─────────────────────────────────────────────────────────────────────
class Frames:
    class FrameFundo(ctk.CTkFrame): # pack(expand=True, fill="both) -> Fundo
        def __init__(self, master, cores:Cores, **kwargs):
            super().__init__(
                master,
                fg_color=cores.fundo.principal)

    class FrameLayoutPadrao(ctk.CTkFrame): # pack(expand=True, fill="both) -> Fundo, Barra de Topo e Lateral
        """
        Frame principal com barra superior + lateral unificadas.

        Uso:
            layout = Frames.FrameLayoutPadrao(
                root, cores, fontes, icones,
                titulo="Clientes",
                icone=icones.clientes,
                on_novo=novo_cliente
            )

        Parâmetros:
            - titulo: texto do título (ex: "Clientes", "Produtos")
            - icone: ícone da tela (ex: icones.clientes, icones.produtos)
            - on_novo: callback do botão "Novo [Tela]". Ex: "Novo Cliente"

        O on_home é fixo - sempre volta ao painel de controle.
        """
        
        def __init__(self, master, cores, fontes, icones,
                     titulo="", icone=None, on_novo=None, usuario=None,
                     on_home=None, menu_callbacks=None, texto_novo=None, texto_info=None,
                     on_click_titulo=None, **kwargs):
            super().__init__(master, fg_color=cores.fundo.principal, **kwargs)
            self.cores = cores
            self.fontes = fontes
            self.icones = icones
            self.on_novo = on_novo
            self.titulo = titulo
            self.usuario = usuario
            self.lbl_usuario = None
            self._on_home_callback = on_home
            self._menu_callbacks = menu_callbacks or {}
            self._texto_novo = texto_novo
            self._texto_info = texto_info
            self._on_click_titulo = on_click_titulo
            
            self._criar_barra_topo(icone, usuario)
            
            self.frame_conteudo = ctk.CTkFrame(
                self,
                fg_color=self.cores.fundo.principal
            )

            self.frame_conteudo.pack(
                fill="both",
                expand=True
            )    

            if self._menu_callbacks:
                self._criar_barra_lateral()

        def atualizar_info(self, texto):
            """Atualiza o texto do label de informação (ex: 'Pedido {id}')"""
            if self.label_info:
                if texto:
                    self.label_info.configure(text=texto)
                    self.label_info.pack(side="right", padx=(0, 5), pady=10)
                else:
                    self.label_info.pack_forget()

        def _criar_barra_topo(self, icone, usuario):
            topo = ctk.CTkFrame(self,
                                fg_color=self.cores.fundo.branco,
                                height=75,
                                border_color=self.cores.card.borda_card,
                                border_width=1)
            topo.pack(fill="x", side="top")
            topo.pack_propagate(False)
            
            frame_esquerda = ctk.CTkFrame(topo, fg_color="transparent")
            frame_esquerda.pack(side="left", padx=15)

            frame_centro = ctk.CTkFrame(topo, fg_color="transparent", height=20)
            frame_centro.pack(side="left", expand=True, padx=(0, 120))

            frame_direita = ctk.CTkFrame(topo, fg_color="transparent")
            frame_direita.pack(side="right", padx=15)

            # Botão Home
            btn_home = Botoes.BotaoHome(frame_esquerda, self.icones, self.cores)
            btn_home.pack(side="left", padx=(5, 15), pady=(5,10))

            # Ícone da tela + Título (clicável — volta à tela inicial do módulo)
            if icone:
                ctk.CTkLabel(frame_esquerda, image=icone,
                             fg_color="transparent", text="").pack(side="left", padx=(10, 0), pady=10)
            self._lbl_titulo = Titulos.TituloTopo(frame_esquerda, cores=self.cores,
                               fontes=self.fontes, texto=self.titulo)
            self._lbl_titulo.pack(side="left", padx=5, pady=10)
            self._lbl_titulo.configure(cursor="hand2")
            if self._on_click_titulo:
                self._lbl_titulo.bind("<Button-1>", lambda e: self._on_click_titulo())

            if self.titulo != "Painel de Controle":
                btn_home.configure(command=self._on_home)

            if usuario:
                seta = ctk.CTkLabel(frame_centro, image=self.icones.seta, text="")
                seta.pack(side="left", padx=(0, 5), pady=(0, 5))

                ctk.CTkLabel(frame_centro, text="Olá,",
                             font=self.fontes.cumprimentos,
                             text_color=self.cores.texto.principal,
                             fg_color="transparent").pack(side="left", padx=(0, 5))

                self.lbl_usuario = ctk.CTkLabel(
                    frame_centro,
                    text=f"{self.usuario}!",
                    font=self.fontes.cumprimentos,
                    text_color=self.cores.texto.laranja,
                    fg_color="transparent",
                )
                self.lbl_usuario.pack(side="left")

            # Botão Config
            from app.utils.menu_config import MenuConfig
            self.menu_config = MenuConfig()
            btn_config = Botoes.BotaoConfig(frame_direita, self.icones, self.cores)
            btn_config.configure(command=lambda: self.menu_config.abrir(btn_config, self.cores, self.fontes))
            btn_config.pack(side="right", padx=15, pady=10)

            # Label de informação (ex: "Pedido {id}")
            self.label_info = None
            if self._texto_info:
                self.label_info = ctk.CTkLabel(
                    frame_direita,
                    text=self._texto_info,
                    font=self.fontes.titulo,
                    text_color=self.cores.texto.branco,
                    fg_color=self.cores.texto.verde_escuro,
                    corner_radius=8,
                    padx=10,
                    pady=5
                )
                self.label_info.pack(side="right", padx=(0, 5), pady=10)

            # Botão Novo
            if self.on_novo:
                texto_btn = self._texto_novo if self._texto_novo else f"Novo {self.titulo[:-1] if self.titulo.endswith('s') else self.titulo}"
                btn_novo = Botoes.BotaoAdicionar(
                    frame_direita, self.icones, self.cores, self.fontes,
                    texto=texto_btn)
                btn_novo.configure(command=self.on_novo)
                btn_novo.pack(side="right", padx=15, pady=10)

        def atualizar_usuario(self, nome):
            self.usuario = nome
            if self.lbl_usuario:
                self.lbl_usuario.configure(text=f"{nome}!")

        def _criar_barra_lateral(self):
            from app.utils.botaolateralmenus import MenuLateral
            self.menu_lateral = MenuLateral(self.frame_conteudo, callbacks=self._menu_callbacks)

            self.area_tela = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
            self.area_tela.pack(side="left", fill="both", expand=True)

        def _on_home(self):
            if self._on_home_callback:
                self._on_home_callback()
            else:
                master = self.winfo_toplevel().master
                self.winfo_toplevel().destroy()
                from app.view.tela_painel_controle import PainelControleView
                PainelControleView(master)
                
    class MetricCard(ctk.CTkFrame):
        """Card de métrica reutilizável com ícone, título, valor e subtítulo opcional.

        Uso:
            card = Frames.MetricCard(
                parent, cores, fontes,
                icone=icones.crescente,
                titulo="Vendas do dia",
                valor="R$ 0,00",
                subtexto="+12,5% vs ontem",
                cor_card=cores.botao.janelas,
                cor_valor=cores.texto.verde_jambu
            )
            card.pack(side="left", expand=True, fill="both", padx=10, pady=5)
            # Atualizar depois:
            card.set_valor("R$ 150,00")
            card.set_subtexto("+8,2% vs ontem")

        destaque=True: fundo cheio (cores.fundo.laranja) e texto branco para card principal.
        """
        def __init__(self, master, cores, fontes, *,
                     icone=None, titulo="", valor="0", subtexto="",
                     cor_card=None, cor_titulo=None, cor_valor=None,
                     destaque=False):
            self._cores = cores
            self._fontes = fontes

            if destaque:
                bg = cores.fundo.laranja
                titulo_cor = cores.texto.branco
                valor_cor = cores.texto.branco
                sub_cor = cores.texto.branco
            else:
                bg = cor_card or cores.botao.janelas
                titulo_cor = cor_titulo or cores.texto.passivo
                valor_cor = cor_valor or cores.texto.verde_jambu
                sub_cor = cores.texto.passivo

            super().__init__(
                master,
                fg_color=bg,
                corner_radius=15
            )

            cabecalho = ctk.CTkFrame(self, fg_color="transparent")
            cabecalho.pack(side="top", fill="x", padx=(15, 20), pady=(15, 5))

            self._icone_titulo = None
            if icone:
                self._icone_titulo = ctk.CTkLabel(cabecalho, image=icone, text="")
                self._icone_titulo.pack(side="left", padx=(0, 8))

            self._titulo_label = ctk.CTkLabel(
                cabecalho,
                text=titulo,
                font=fontes.titulo_card,
                text_color=titulo_cor,
            )
            self._titulo_label.pack(side="left")
            self._atualizar_wraplength()
            self.bind("<Configure>", self._atualizar_wraplength, add="+")

            self.sub_label = ctk.CTkLabel(
                self,
                text=subtexto,
                font=fontes.pequeno,
                text_color=sub_cor,
            )

            self.valor_label = ctk.CTkLabel(
                self,
                text=str(valor),
                font=fontes.valor,
                text_color=valor_cor
            )

            if subtexto:
                self.sub_label.pack(side="bottom", padx=(15, 20), pady=(0, 2), anchor="nw")
            self.valor_label.pack(side="bottom", padx=(15, 20), pady=(0, 15), anchor="nw")

        def _atualizar_wraplength(self, event=None):
            disp = self.winfo_width() - 15 - 20 - 10
            if self._icone_titulo is not None:
                disp -= 28
            self._titulo_label.configure(wraplength=max(disp, 20))

        def set_valor(self, texto):
            self.valor_label.configure(text=str(texto))

        def set_subtexto(self, texto):
            self.sub_label.configure(text=str(texto))
            if texto:
                self.sub_label.pack_forget()
                self.valor_label.pack_forget()
                self.sub_label.pack(side="bottom", padx=(15, 20), pady=(0, 2), anchor="nw")
                self.valor_label.pack(side="bottom", padx=(15, 20), pady=(0, 15), anchor="nw")
            else:
                self.sub_label.pack_forget()

    class FrameConteudo(ctk.CTkFrame): # pack(expand=True, fill="both", padx=100, pady=70) -> Frame para todo conteúdo na tela
        def __init__(self, master, cores:Cores):
            super().__init__(master, fg_color=cores.fundo.principal, corner_radius=20)
            
    class FrameCadastro(ctk.CTkFrame):
        """
        Frame principal com: voltar, título, feedback, nome, cargo, email,
        toggle ativo/inativo e botão 'Alterar Senha' (só visível no modo editar).

        Atributos públicos:
            .nome           → Campos.CampoTexto
            .cargo          → Campos.CampoOpcao
            .email          → Campos.CampoTexto
            .voltar_bttn    → CTkButton (configure o command externamente)
            .senha_bttn     → CTkButton | None
            .senha_frame    → atribuído externamente pela tela pai (FrameSenha)
            .visivel_senha  → bool

        Métodos úteis:
            .get_ativo()            → bool
            .set_ativo(bool)
            .preencher_dados(dict)  → preenche todos os campos
            .mostrar_feedback(msg, tipo="erro"|"sucesso")
            .definir_modo("novo"|"editar")
            .toggle_senha()         → mostra/oculta o FrameSenha
        """

        def __init__(self, master, cores, fontes, icones, modo="novo", show_password_button=True, show_password_button_edit_mode=False, **kwargs):
            super().__init__(master, fg_color="transparent", **kwargs)
            self.cores  = cores
            self.fontes = fontes
            self.icones = icones
            self.modo   = modo
            self.show_password_button = show_password_button
            self.show_password_button_edit_mode = show_password_button_edit_mode

            self.visivel_senha = False
            self.senha_frame   = None  # ligado pela tela pai após instanciar

            self._criar_formulario()

        def _criar_formulario(self):
            # ── Título + botão voltar ──
            grupo_titulo = ctk.CTkFrame(self, fg_color="transparent")
            grupo_titulo.pack(fill="x", pady=(5, 5))

            self.voltar_bttn = ctk.CTkButton(
                grupo_titulo, fg_color="transparent",
                image=self.icones.voltar, cursor="hand2",
                hover_color=self.cores.botao.passivo, text="", width=20,
            )
            self.voltar_bttn.pack(side="left", pady=(10, 5), padx=(5, 5))

            self.titulo = ctk.CTkLabel(
                grupo_titulo, font=self.fontes.titulo_grande,
                text_color=self.cores.texto.principal,
                text="Editar Funcionário" if self.modo == "editar" else "Cadastrar Funcionário",
            )
            self.titulo.pack(side="left", pady=(10, 5), padx=(5, 10))

            # ── Feedback (erros / sucesso) ──
            self.lbl_feedback = ctk.CTkLabel(
                self, text="", font=self.fontes.texto_info,
                text_color=self.cores.texto.vermelho, wraplength=350,
            )
            self.lbl_feedback.pack(pady=5)

            # ── Campos de texto ──
            self.nome = Campos.CampoTexto(self, self.icones.nome, "Nome *",  "Digite o nome",  self.cores, self.fontes)
            self.nome.entry.focus()
            self.nome.pack(fill="x", pady=(5, 5))

            self.cargo = Campos.CampoOpcao(self, self.icones.funcionarios, "Cargo *", ["Administrador", "Funcionário"], self.cores, self.fontes)
            self.cargo.pack(fill="x", pady=(5, 5))
            self.cargo.set("Funcionário")

            self.email = Campos.CampoTexto(self, self.icones.descricao, "Email *", "Digite o email", self.cores, self.fontes)
            self.email.pack(fill="x", pady=(5, 5))

            # Telefone: usa ícone 'ligar' se existir, senão cai no ícone 'descricao'.
            telefone_icone = getattr(self.icones, "ligar", None) or getattr(self.icones, "descricao", None)
            self.telefone = Campos.CampoTexto(
                self,
                telefone_icone,
                "Telefone *",
                "Digite o telefone",
                self.cores,
                self.fontes,
            )
            self.telefone.pack(fill="x", pady=(5, 5))

        # ── Toggle ativo/inativo ──
            grupo_ativo = ctk.CTkFrame(self, fg_color="transparent")
            grupo_ativo.pack(fill="x", pady=(10, 5))

            ctk.CTkLabel(grupo_ativo, text="Status", font=self.fontes.subtitulo,
                         text_color=self.cores.texto.principal).pack(side="left", padx=(0, 12))

            self.status_var = ctk.StringVar(value="Ativo")
            self.status_var.trace_add("write", lambda *_: self._atualizar_botao_status())

            self.toggle_ativo = ctk.CTkButton(
                grupo_ativo, text="✓ Ativo", font=self.fontes.texto_info,
                width=140, height=36, corner_radius=18,
                fg_color=self.cores.fundo.verde,
                hover_color=self.cores.fundo.verde,
                text_color=self.cores.fundo.branco,
                command=self._alternar_status_ativo,
            )
            self.toggle_ativo.pack(side="left")

        # ── Helpers internos ──
        def _alternar_status_ativo(self):
            novo_valor = "Inativo" if self.status_var.get() == "Ativo" else "Ativo"
            self.status_var.set(novo_valor)

        def _atualizar_botao_status(self):
            if self.status_var.get() == "Ativo":
                self.toggle_ativo.configure(
                    text="✓ Ativo",
                    fg_color=self.cores.fundo.verde,
                    hover_color=self.cores.fundo.verde,
                )
            else:
                self.toggle_ativo.configure(
                    text="Inativo",
                    fg_color=self.cores.fundo.cinza_escuro,
                    hover_color=self.cores.fundo.cinza_escuro,
                )

        # ── Toggle entregador ──
            grupo_entregador = ctk.CTkFrame(self, fg_color="transparent")
            grupo_entregador.pack(fill="x", pady=(5, 5))

            ctk.CTkLabel(grupo_entregador, text="Entregador", font=self.fontes.subtitulo,
                         text_color=self.cores.texto.principal).pack(side="left", padx=(0, 12))

            self._entregador_var = ctk.BooleanVar(value=False)
            self.toggle_entregador = ctk.CTkSwitch(
                grupo_entregador, text="", variable=self._entregador_var,
                onvalue=True, offvalue=False,
                progress_color=self.cores.botao.confirmar,
                button_color=self.cores.fundo.branco,
                fg_color=self.cores.fundo.cinza_escuro,
            )
            self.toggle_entregador.pack(side="left")

        # ── API pública ──
        def get_ativo(self) -> bool:
            return self.status_var.get() == "Ativo"

        def set_ativo(self, valor: bool):
            self.status_var.set("Ativo" if valor else "Inativo")

        def get_entregador(self) -> bool:
            return self._entregador_var.get()

        def set_entregador(self, valor: bool):
            self._entregador_var.set(valor)    

        def toggle_senha(self):
            """Mostra ou oculta o painel de senha lateral."""
            if self.senha_frame is None:
                raise ValueError("senha_frame não definido. Atribua-o antes de chamar toggle_senha().")
            # Em modo 'novo' o painel de senha deve permanecer visível
            # (senha é obrigatória no cadastro). Apenas foca o campo.
            if getattr(self, 'modo', '') == 'novo':
                try:
                    self.senha_frame.mostrar-Campos()
                    self.visivel_senha = True
                    # foca no campo de senha
                    if hasattr(self.senha_frame, 'senha') and hasattr(self.senha_frame.senha, 'entry'):
                        try:
                            self.senha_frame.senha.entry.focus()
                        except Exception:
                            pass
                except Exception:
                    pass
                return

            # comportamento padrão: alterna visibilidade
            if self.visivel_senha:
                self.senha_frame.ocultar_campos()
                self.visivel_senha = False
            else:
                self.senha_frame.mostrar_campos()
                self.visivel_senha = True

        def definir_modo(self, modo: str):
            """
            Alterna entre 'novo' e 'editar'.
            - Atualiza o título
            - Mostra/oculta o botão 'Alterar Senha'
            """
            self.modo = modo
            self.titulo.configure(
                text="Editar Funcionário" if modo == "editar" else "Cadastrar Funcionário"
            )
            
            if self.senha_frame is not None:
                texto_botao = "Cadastrar Senha" if modo == "novo" else "Alterar Senha"
                self.senha_frame.definir_texto_botao(texto_botao)
                
            if modo == "editar" and not self.show_password_button_edit_mode:
                if self.senha_frame is not None:
                    self.senha_frame.ocultar_campos()
                self.visivel_senha = False
                
            else:
                if self.senha_frame is not None:
                    self.senha_frame.mostrar_campos()
                self.visivel_senha = True    

            # Quando em modo edição e sem permissão para mostrar senha automaticamente,
            # garante que o painel de senha esteja oculto até o botão ser pressionado.
            if modo == "editar" and not self.show_password_button_edit_mode:
                if self.senha_frame is not None:
                    self.senha_frame.grid_remove()
                self.visivel_senha = False

        def preencher_dados(self, dados: dict):
            """
            Preenche o formulário com dados vindos do banco.

            CONEXÃO COM SQL:
                O dict 'dados' deve vir da função de busca no CRUD.
            """
            self.nome.set(dados.get("nome", ""))
            self.email.set(dados.get("email", ""))
            if hasattr(self, "telefone"):
                self.telefone.set(dados.get("telefone", ""))
            self.cargo.set(dados.get("cargo", "Funcionário"))
            self.set_ativo(dados.get("ativo", True))
            self.set_entregador(dados.get("is_entregador", False))


        def mostrar_feedback(self, mensagem: str, tipo: str = "erro"):
            """Exibe mensagem de erro (vermelho) ou sucesso (verde) abaixo do título."""
            cor = self.cores.texto.vermelho if tipo == "erro" else self.cores.texto.verde
            self.lbl_feedback.configure(text=mensagem, text_color=cor)

    class FrameConteudoTabela(ctk.CTkFrame):
        """
        Frame container para tabela com cor cinza e bordas arredondadas.
        
        Uso:
            frame = Frames.FrameConteudoTabela(parent, cores)
            frame.pack(...)
            
            # depois adiciona a tabela dentro
            tabela = TabelaGenerica(frame, ...)
        """
        def __init__(self, master, cores, corner_radius=20, **kwargs):
            super().__init__(master, 
                             fg_color=cores.fundo.branco,
                             corner_radius=corner_radius,
                             border_width=2,
                             border_color=cores.botao.borda,
                             **kwargs)

    class FrameSenha(ctk.CTkFrame):
        """
        Painel lateral com os campos 'Senha' e 'Confirmar Senha'.
        Aparece/desaparece via grid() e grid_remove() pela tela pai.
        """
        def __init__(self, master, cores, fontes, icones, on_toggle=None, **kwargs):
            super().__init__(master, fg_color="transparent", **kwargs)
            self.cores  = cores
            self.fontes = fontes
            self.icones = icones
            self.on_toggle = on_toggle
            self._criar_campos()

        def _criar_campos(self):
            self.senha = Campos.CampoTexto(
                self, self.icones.descricao, "Senha *", "Digite a senha",
                self.cores, self.fontes, password=True
            )
            self.senha.pack(fill="x", pady=(10, 5), padx=20)

            self.confirmar_senha = Campos.CampoTexto(
                self, self.icones.descricao, "Confirmar Senha *", "Digite a senha novamente",
                self.cores, self.fontes, password=True
            )
            self.confirmar_senha.pack(fill="x", pady=(10, 5), padx=20)
            
            # Botão Alterar Senha abaixo dos campos
            self.btn_alterar_senha = ctk.CTkButton(
                self, image=self.icones.editar,
                text="Alterar Senha", font=self.fontes.titulo,
                fg_color=self.cores.botao.passivo,
                text_color=self.cores.texto.principal,
                corner_radius=8, cursor="hand2",
                hover_color=self.cores.botao.ativo_secundario,
                command=self.on_toggle if self.on_toggle else lambda: None,
            )
            self.btn_alterar_senha.pack(fill="x", pady=(20, 5), padx=20)
            
        def ocultar_campos(self):
            self.senha.pack_forget()
            self.confirmar_senha.pack_forget()

        def mostrar_campos(self):
            self.senha.pack(fill="x", pady=(10, 5), padx=20)
            self.confirmar_senha.pack(fill="x", pady=(10, 5), padx=20)
            self.btn_alterar_senha.pack_forget()
            self.btn_alterar_senha.pack(fill="x", pady=(20, 5), padx=20)   
            
        def definir_texto_botao(self, texto: str):
            self.btn_alterar_senha.configure(text=texto)     

        def limpar(self):
            self.senha.set("")
            self.confirmar_senha.set("")

    class FrameComandos(ctk.CTkFrame):
        """
        Barra inferior com Salvar, Cancelar e (opcionalmente) Excluir.

        Uso:
            frame_comandos.set_callbacks(
                salvar=self.acao_salvar,
                cancelar=self.acao_cancelar,
                excluir=self.acao_excluir,
            )
        """
        def __init__(self, master, cores, fontes, icones, modo="novo", **kwargs):
            super().__init__(master, fg_color="transparent", **kwargs)
            self.cores  = cores
            self.fontes = fontes
            self.icones = icones

            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(side="left", fill="x", expand=True)

            self.btn_salvar   = Botoes.BotaoSalvar(container, cores, fontes)
            self.btn_salvar.pack(side="left", padx=10)

            self.btn_cancelar = Botoes.BotaoCancelar(container, cores, fontes)
            self.btn_cancelar.pack(side="left", padx=10)

            # Excluir começa oculto; aparece apenas no modo editar
            self.btn_excluir  = Botoes.BotaoExcluir(container, cores, fontes)
            if modo == "editar":
                self.btn_excluir.pack(side="left", padx=10)

        def set_callbacks(self, salvar, cancelar, excluir):
            """Liga os callbacks aos botões. Chame depois de instanciar."""
            self.btn_salvar.configure(command=salvar)
            self.btn_cancelar.configure(command=cancelar)
            self.btn_excluir.configure(command=excluir)

        def mostrar_excluir(self, visivel: bool):
            if visivel:
                self.btn_excluir.pack(side="left", padx=10)
            else:
                self.btn_excluir.pack_forget()

    class StepperPassos(ctk.CTkFrame):
        """
        Stepper de passos reutilizável.

        Uso:
            stepper = Frames.StepperPassos(
                parent, cores, fontes,
                etapas=[{"num": "1", "label": "Itens"}, ...],
                etapa_atual=1
            )
            stepper.atualizar(2)  # muda para etapa 2
        """
        def __init__(self, master, cores, fontes, etapas, etapa_atual=1,
                     padx_circle=(0, 6), padx_label=(0, 20), **kwargs):
            super().__init__(master, fg_color="transparent", **kwargs)
            self.cores = cores
            self.fontes = fontes
            self.etapas = etapas
            self.etapa_atual = etapa_atual
            self.padx_circle = padx_circle
            self.padx_label = padx_label

            self._container = ctk.CTkFrame(self, fg_color="transparent")
            self._container.pack(expand=True)

            self._blocos = []
            self._desenhar()

        def _desenhar(self):
            for w in self._container.winfo_children():
                w.destroy()
            self._blocos = []

            for i, etapa in enumerate(self.etapas):
                num_etapa = i + 1
                if num_etapa < self.etapa_atual:
                    texto = "✓"
                    cor_circle = self.cores.texto.verde_escuro
                    cor_texto = self.cores.texto.branco
                    cor_label = self.cores.texto.verde_escuro
                elif num_etapa == self.etapa_atual:
                    texto = str(num_etapa)
                    cor_circle = self.cores.botao.novo
                    cor_texto = self.cores.texto.branco
                    cor_label = self.cores.botao.novo
                else:
                    texto = str(num_etapa)
                    cor_circle = self.cores.fundo.fundinho
                    cor_texto = self.cores.texto.passivo
                    cor_label = self.cores.texto.passivo

                frame_circle = ctk.CTkFrame(
                    self._container, width=32, height=32,
                    corner_radius=16, fg_color=cor_circle
                )
                frame_circle.pack(side="left", padx=self.padx_circle)
                frame_circle.pack_propagate(False)

                lbl_circle = ctk.CTkLabel(
                    frame_circle, text=texto,
                    fg_color="transparent",
                    text_color=cor_texto, font=ctk.CTkFont(size=13, weight="bold")
                )
                lbl_circle.pack(expand=True)

                lbl = ctk.CTkLabel(
                    self._container, text=etapa["label"],
                    font=self.fontes.stepper, text_color=cor_label
                )
                lbl.pack(side="left", padx=self.padx_label)

                if i < len(self.etapas) - 1:
                    ctk.CTkFrame(
                        self._container, width=50, height=2,
                        fg_color=self.cores.fundo.principal
                    ).pack(side="left", padx=(0, 10))

                self._blocos.append({
                    "circle": frame_circle,
                    "label_circle": lbl_circle,
                    "label": lbl
                })

        def atualizar(self, nova_etapa):
            self.etapa_atual = nova_etapa
            for i, bloco in enumerate(self._blocos):
                num_etapa = i + 1
                if num_etapa < self.etapa_atual:
                    texto = "✓"
                    cor_circle = self.cores.texto.verde_escuro
                    cor_texto = self.cores.texto.branco
                    cor_label = self.cores.texto.verde_escuro
                elif num_etapa == self.etapa_atual:
                    texto = str(num_etapa)
                    cor_circle = self.cores.botao.novo
                    cor_texto = self.cores.texto.branco
                    cor_label = self.cores.botao.novo
                else:
                    texto = str(num_etapa)
                    cor_circle = self.cores.fundo.fundinho
                    cor_texto = self.cores.texto.passivo
                    cor_label = self.cores.texto.passivo

                bloco["circle"].configure(fg_color=cor_circle)
                bloco["label_circle"].configure(text=texto, text_color=cor_texto)
                bloco["label"].configure(text_color=cor_label)


# ── BOTÕES ─────────────────────────────────────────────────────────────────────
class Botoes:
    """
    Botões padronizados. Todos aceitam .configure(command=...) após instanciar.

    Exemplo:
        btn = Botoes.BotaoSalvar(master, cores, fontes)
        btn.configure(command=minha_funcao)
        btn.pack(...)
    """

    class BotaoHome(ctk.CTkButton):
        """Botão de ícone Home (sem texto)."""
        def __init__(self, master, icones, cores):
            super().__init__(master, image=icones.logo_home, text="",
                             hover_color=cores.botao.hover, fg_color="transparent",
                             width=20, height=35, cursor="hand2")

    class BotaoConfig(ctk.CTkButton):
        """Botão de ícone Configurações (sem texto)."""
        def __init__(self, master, icones:Icones, cores:Cores):
            super().__init__(master, image=icones.config, text="",
                             hover_color=cores.botao.hover, fg_color="transparent",
                             width=20, height=35, cursor="hand2")

    class BotaoSalvar(ctk.CTkButton):
        """Botão verde de confirmação (Salvar/Confirmar)."""
        def __init__(self, master, cores, fontes):
            super().__init__(master, text="Salvar", font=fontes.titulo,
                             text_color=cores.texto.branco, fg_color=cores.botao.confirmar,
                             hover_color=cores.botao.ativo,
                             width=150, height=45, cursor="hand2", corner_radius=50)

    class BotaoCancelar(ctk.CTkButton):
        """Botão cinza de cancelamento."""
        def __init__(self, master, cores, fontes):
            super().__init__(master, text="Cancelar", font=fontes.titulo,
                             text_color=cores.texto.principal, fg_color=cores.botao.cancelar,
                             width=150, height=45, cursor="hand2", corner_radius=50)

    class BotaoExcluir(ctk.CTkButton):
        """Botão vermelho de exclusão."""
        def __init__(self, master, cores, fontes):
            super().__init__(master, text="Excluir", font=fontes.titulo,
                             text_color=cores.texto.branco, fg_color=cores.botao.excluir,
                             width=150, height=45, cursor="hand2", corner_radius=50)

    class BotaoEditar(ctk.CTkButton):
        def __init__(self, master, cores, icones, command=None):
            super().__init__(
                master,
                image=icones.editar,
                text="",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color=cores.fundo.cinza_claro,
                cursor="hand2",
                command=command)
            
    class BotaoApagar(ctk.CTkButton):
        def __init__(self, master, cores, icones, command=None):
            super().__init__(
                master,
                image=icones.apagar,
                text="",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color=cores.fundo.cinza_claro,
                cursor="hand2",
                command=command
            )

    class BotaoLateral(ctk.CTkFrame):
        """Botão de menu lateral com barra indicadora de hover."""
        def __init__(self, master, cores, icones):
            super().__init__(master, fg_color="transparent")
            self.cores  = cores
            self.icones = icones

            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(fill="both", expand=True)

            self.indicator = ctk.CTkFrame(container, width=3, height=20, fg_color="transparent")
            self.indicator.pack(side="left", padx=(0, 3))

            self.button = ctk.CTkButton(
                container, image=icones.tela_lateral, text="",
                fg_color="transparent", hover_color=cores.botao.hover,
                width=30, height=20, cursor="hand2",
            )
            self.button.pack(side="left", padx=5)

            self.button.bind("<Enter>", self._on_enter)
            self.button.bind("<Leave>", self._on_leave)

        def _on_enter(self, _event):
            self.indicator.configure(fg_color=self.cores.botao.passivo)
            self.button.configure(fg_color=self.cores.fundo.cinza_clarinho)

        def _on_leave(self, _event):
            self.indicator.configure(fg_color="transparent")
            self.button.configure(fg_color="transparent")

    class BotaoAdicionar(ctk.CTkButton):
        """Botão 'Novo' no topo da tela:
        'Novo Pedido', 'Novo Cliente',
        'Novo Item', 'Novo Funcionário'
        """
        def __init__(self, master, icones, cores, fontes, texto=""):
            super().__init__(
                master, text=texto,
                image=icones.adicionar_branco, compound="left",
                font=fontes.subtitulo,
                text_color=cores.texto.branco,
                fg_color=cores.botao.novo,
                hover_color=cores.botao.novo_hover,
                cursor="hand2", width=120, height=30, corner_radius=50,
            )

    class BotaoEndereco(ctk.CTkButton):
        """Botão 'Endereço' no formulário da tela Cliente
        """
        def __init__(self, master, icones, cores, fontes, texto="Endereço", comando=""):
            super().__init__(
                master, text=texto,
                image=icones.adicionar_preto, compound="left",
                font=fontes.subtitulo,
                text_color=cores.texto.branco,
                fg_color=cores.botao.novo,
                hover_color=cores.botao.novo_hover,
                cursor="hand2", width=120, height=30, corner_radius=50,
                command=comando
            )


    class BotaoFunil(ctk.CTkButton):
        """
        Botão de filtro com menu flutuante.
        Ex: BotaoFunil(master, icones, cores, fontes, tabela=minha_tabela,
                        filtros=[("Categoria: Pizza", "cat", "Pizza"), ...])
        """
        def __init__(self, master, icones, cores, fontes, tabela=None,
                     filtros=None, on_filtrar=None):
            super().__init__(
                master, image=icones.funil,
                width=20, height=20, fg_color="transparent", text="",
                hover_color=cores.fundo.cinza_clarinho,
                cursor="hand2", command=self._abrir_menu
            )
            self.fontes = fontes
            self.cores = cores
            self.tabela = tabela
            self.on_filtrar = on_filtrar
            self.filtros = filtros or [
                ("Cargo: Administrador", "cargo", "Administrador"),
                ("Cargo: Funcionário",   "cargo", "Funcionário"),
                ("Status: Ativo",        "status", True),
                ("Status: Inativo",      "status", False),
            ]
            self.menu = None

        def _abrir_menu(self):
            if self.menu and self.menu.winfo_exists():
                self.menu.destroy()
                self.menu = None
                return

            self.menu = ctk.CTkToplevel(self.winfo_toplevel())            
            self.menu.geometry("200x210")
            self.menu.overrideredirect(True)
            
            #Cor da borda
            self.menu.configure(fg_color=self.cores.fundo.branco)
            
            x, y = self.winfo_rootx(), self.winfo_rooty() + 30
            self.menu.geometry(f"+{x}+{y}")

            self.menu.lift()
            self.menu.attributes("-topmost", True)

            self.winfo_toplevel().bind(
                "<Button-1>",
                self._clique_fora_menu,
                add="+"
            )

            conteudo = ctk.CTkFrame(self.menu,
                                    fg_color=self.cores.fundo.principal,
                                    corner_radius=12,
                                    border_width=2,
                                    border_color=self.cores.botao.borda,
                                    )
            conteudo.pack(fill="both", expand=True, padx=2, pady=2)
            
            ctk.CTkLabel(conteudo, text="Filtrar por:",
                         font=self.fontes.filtrar,
                         text_color=self.cores.texto.verde_jambu).pack(pady=5)
            for texto, tipo, valor in self.filtros:
                
                btn = ctk.CTkButton(
                    conteudo, text=texto,
                    command=lambda t=tipo, v=valor: self._filtrar(t, v),
                    fg_color=self.cores.botao.funil,
                    hover_color=self.cores.botao.funil_hover,
                    text_color=self.cores.texto.verde_jambu,
                    corner_radius=15,
                    height=30
                )
                
                btn.bind(
                    "<Enter>",
                    lambda e, b=btn: b.configure(
                        fg_color=self.cores.botao.funil_hover,
                        text_color=self.cores.texto.laranja_claro
                    )
                )
                
                btn.bind(
                    "<Leave>",
                    lambda e, b=btn: b.configure(
                        fg_color=self.cores.botao.funil,
                        text_color=self.cores.texto.verde_jambu
                    )
                )
                
                btn.pack(fill="x", padx=10, pady=2)

            limpar = ctk.CTkButton(conteudo, 
                          text="Limpar Filtros", 
                          command=self._limpar_filtro,
                          fg_color=self.cores.botao.limpar_filtro,
                          hover_color=self.cores.botao.limpar_filtro_hvr,
                          text_color=self.cores.texto.coral,
                          height=30,
                          corner_radius=15)
            
            limpar.bind(
                "<Enter>",
                lambda e, b=limpar: b.configure(
                    fg_color=self.cores.botao.limpar_filtro_hvr,
                    text_color=self.cores.texto.laranja_claro
                )
            )
            
            limpar.bind(
                "<Leave>",
                lambda e, b=limpar: b.configure(
                    fg_color=self.cores.botao.limpar_filtro,
                    text_color=self.cores.texto.coral
                )
            )
            
            limpar.pack(fill="x", padx=10, pady=5)
            self.menu.bind("<FocusOut>", lambda e: self._fechar_menu())
            self.menu.bind("<Escape>",   lambda e: self._fechar_menu())

        def _clique_fora_menu(self, event):

                        if not self.menu or not self.menu.winfo_exists():
                            return

                        x1 = self.menu.winfo_rootx()
                        y1 = self.menu.winfo_rooty()

                        x2 = x1 + self.menu.winfo_width()
                        y2 = y1 + self.menu.winfo_height()

                        clicou_dentro = (
                            x1 <= event.x_root <= x2 and
                            y1 <= event.y_root <= y2
                        )

                        if not clicou_dentro:
                            self._fechar_menu()
                            
        def _fechar_menu(self):
            if self.menu and self.menu.winfo_exists():
                self.menu.destroy()
                
                self.menu = None
                
                self.winfo_toplevel().unbind("<Button-1>")

        def _filtrar(self, tipo, valor):
            if self.on_filtrar:
                self.on_filtrar(tipo, valor)
            elif self.tabela:
                self.tabela.aplicar_filtro(tipo, valor)
            self._fechar_menu()

        def _limpar_filtro(self):
            if self.on_filtrar:
                self.on_filtrar(None, None)
            elif self.tabela:
                self.tabela.remover_filtro()
            self._fechar_menu()

    # ── Botões específicos de pedidos ──────────────────────────────────────────

    class BotaoCircular(ctk.CTkButton):
        """Botão circular com ícone (genérico)."""
        def __init__(self, master, cores, icone, tamanho=36,
                     cor_fundo=None, comando=None):
            if cor_fundo is None:
                cor_fundo = cores.fundo.cinza_claro
            super().__init__(
                master, image=icone, text="",
                width=tamanho, height=tamanho,
                corner_radius=tamanho // 2,
                fg_color=cor_fundo,
                hover_color=cores.botao.hover,
                cursor="hand2",
                command=comando
            )

    class BotaoAvancarStatus(ctk.CTkButton):
        """Botão de avanço de status do pedido — texto e comando dinâmicos.
        Use .atualizar(status) para trocar texto; a view define o command."""
        def __init__(self, master, cores, fontes):
            super().__init__(
                master, text="✅ Confirmar Pedido",
                height=34, corner_radius=8,
                fg_color=cores.botao.novo,
                hover_color=cores.botao.novo_hover,
                text_color=cores.texto.branco,
                font=fontes.texto_info,
                state="disabled"
            )
            self.cores = cores
            self._status = "criado"

        def atualizar(self, status):
            self._status = status
            if status in ("criado", "confirmado", "em_preparo", "pronto", "entregue"):
                self.configure(state="normal")
            else:
                self.configure(state="disabled")

            if status == "criado":
                self.configure(text="✅ Confirmar Pedido")
            elif status == "confirmado":
                self.configure(text="▶ Preparar Pedido")
            elif status == "em_preparo":
                self.configure(text="✅ Pedido Pronto")
            elif status == "pronto":
                self.configure(text="✅ Pedido Entregue")
            elif status == "entregue":
                self.configure(text="✅ Concluir Pedido")
            else:
                self.configure(text="✅", state="disabled")

    class BotaoCancelarPedido(ctk.CTkButton):
        """Botão 'Cancelar Pedido' — apenas visual, view define o command."""
        def __init__(self, master, cores, fontes):
            super().__init__(
                master, text="Cancelar Pedido",
                height=34, corner_radius=8,
                fg_color=cores.fundo.cinza_claro,
                text_color=cores.texto.vermelho,
                font=fontes.texto_info,
                state="disabled"
            )
            self.cores = cores

    class BotaoReverter(ctk.CTkFrame):
        """Botão circular ↩ com label 'Reverter' ao lado.
        A view define o command e chama .atualizar() para enable/disable."""
        def __init__(self, master, cores, fontes):
            super().__init__(master, fg_color="transparent")
            self.cores = cores

            self._btn = ctk.CTkButton(
                self, text="↩", width=30, height=30,
                corner_radius=15,
                fg_color=cores.fundo.cinza_claro,
                hover_color=cores.botao.hover,
                text_color=cores.texto.principal,
                font=ctk.CTkFont(size=14),
                cursor="hand2"
            )
            self._btn.pack(side="left")

            self._lbl = ctk.CTkLabel(
                self, text="Reverter",
                font=fontes.texto_info,
                text_color=cores.texto.passivo
            )
            self._lbl.pack(side="left", padx=(4, 0))

        def atualizar(self, habilitado=True):
            if habilitado:
                self._btn.configure(state="normal")
                self._lbl.configure(text_color=self.cores.texto.principal)
            else:
                self._btn.configure(state="disabled")
                self._lbl.configure(text_color=self.cores.texto.passivo)

        def configure(self, command=None):
            """Encaminha command para o botão circular interno."""
            if command:
                self._btn.configure(command=command)

    class BotaoExcluirPedido(ctk.CTkButton):
        """Botão 'Excluir' para pedidos cancelados — apenas visual, view define o command."""
        def __init__(self, master, cores, fontes):
            super().__init__(
                master, text="🗑 Excluir",
                height=34, corner_radius=8,
                fg_color=cores.fundo.cinza_claro,
                text_color=cores.texto.vermelho,
                font=fontes.texto_info
            )

# ── HEADER DE BUSCA ────────────────────────────────────────────────────────────
class Barras:
    class HeaderBusca(ctk.CTkFrame):
        """
        Campo de busca genérico. Recebe search_callback(termo) ou tabela (retrocompatível).
        Ex: HeaderBusca(master, cores, fontes, icones, placeholder="Buscar...",
                        search_callback=lambda t: minha_tabela.filtrar(t))
        """
        def __init__(self, master, cores, fontes, icones,
                    placeholder="", search_callback=None, tabela=None,
                    altura=30, **kwargs):
            super().__init__(master, fg_color=cores.fundo.principal,
                            width=350, height=altura, corner_radius=50, **kwargs)

            self.search_callback = search_callback
            if self.search_callback is None and tabela is not None:
                self.search_callback = lambda termo: tabela.filtrar_por_texto(termo)

            ctk.CTkLabel(self, image=icones.lupa, fg_color="transparent", text="").pack(side="left", padx=10)
            self.busca = ctk.CTkEntry(
                self,
                
                placeholder_text =(
                    f"Buscar {placeholder[:-1]}"
                    if placeholder.endswith("s")
                    else (
                        f"Buscar {placeholder}"
                        if placeholder
                        else "Buscar..."
                    )
                ),
                
                font = fontes.texto_entry, 
                fg_color = cores.fundo.principal,
                height= 15, width=300,
                border_width=0, 
                corner_radius=15,
            )
            self.busca.pack(side="left", padx=5, pady=10)
            if self.search_callback:
                self.busca.bind("<KeyRelease>", lambda _e: self.search_callback(self.busca.get().strip()))


# ── CAMPOS ─────────────────────────────────────────────────────────────────────
class Campos:
    class CampoTexto(ctk.CTkFrame):
        def __init__(self, master, icone, label, placeholder, cores, fontes, password=False, validacao=None, **kwargs):
            super().__init__(master, fg_color="transparent", **kwargs)
            self._icone = icone
            self._placeholder = placeholder
            self._password = password
            self._cores = cores
            self._fontes = fontes
            self._validacao = validacao

            self._lbl_icone = ctk.CTkLabel(self, image=icone,
                        text=label, font=fontes.titulo_entry,
                        text_color=cores.texto.principal,
                        compound="left")
            self._lbl_icone.pack(anchor="w")

            self.entry = ctk.CTkEntry(
                self, fg_color=cores.entry.formulario, font=fontes.texto_entry,
                border_width=0, corner_radius=8,
                show="*" if password else "",
                placeholder_text=placeholder,
                placeholder_text_color=cores.texto.passivo,
                height=60
            )
            self.entry.pack(fill="x", pady=5)

            self.entry.bind("<FocusIn>",  self._ao_ganhar_foco)
            self.entry.bind("<FocusOut>", self._ao_perder_foco)
            if validacao:
                self.entry.bind("<KeyRelease>", validacao)

            # Mostra placeholder manualmente ao criar
            self._mostrar_placeholder()

        def _mostrar_placeholder(self):
            if not self.entry.get():
                self.entry.configure(
                    text_color=self._cores.texto.passivo,
                )
                # Insere o placeholder manualmente como texto cinza
                self.entry.delete(0, "end")
                self.entry.insert(0, self._placeholder)
                self._placeholder_ativo = True
            else:
                self._placeholder_ativo = False

        def _ao_ganhar_foco(self, event):
            if getattr(self, "_placeholder_ativo", False):
                self.entry.delete(0, "end")
                self.entry.configure(
                    text_color=self._cores.texto.principal,
                    show="*" if self._password else "",
                )
                self._placeholder_ativo = False

        def _ao_perder_foco(self, event):
            if not self.entry.get():
                self._mostrar_placeholder()

        def get(self) -> str:
            if getattr(self, "_placeholder_ativo", False):
                return ""
            return self.entry.get()

        def set(self, valor: str):
            self._placeholder_ativo = False
            self.entry.configure(text_color=self._cores.texto.principal)
            self.entry.delete(0, "end")
            if valor:
                self.entry.insert(0, valor)
            else:
                self._mostrar_placeholder()

    class CampoOpcao(ctk.CTkFrame):
        """
        Label + OptionMenu genérico.

        Métodos:
            .get()        → str  (opção selecionada)
            .set(valor)   → None (seleciona uma opção)
        """
        def __init__(self, master, icone, label, valores, cores, fontes):
            super().__init__(master, fg_color="transparent")

            self._lbl_icone = ctk.CTkLabel(self, image=icone, 
                        text=label, font=fontes.titulo_entry,
                        text_color=cores.texto.principal,
                        compound="left")
            self._lbl_icone.pack(anchor="w")

            self.menu = ctk.CTkOptionMenu(
                self, values=valores,
                fg_color=cores.entry.formulario,
                button_color=cores.entry.formulario,
                button_hover_color=cores.entry.formulario,
                font=fontes.texto_entry,
                text_color=cores.texto.passivo,
                dropdown_fg_color=cores.fundo.branco,
                dropdown_font=fontes.texto_info,
                dropdown_text_color=cores.texto.passivo,
                dropdown_hover_color=cores.fundo.cinza_muito_claro,
                corner_radius=8,
                height=60
            )
            self.menu.pack(fill="x", pady=5)

        def get(self) -> str:
            return self.menu.get()

        def set(self, valor: str):
            self.menu.set(valor)

    class CampoFoto(ctk.CTkFrame):
        """
        Componente de seleção de foto com preview.

        Uso:
            campo = Campos.CampoFoto(master, cores, fontes, icones)
            campo.set("foto.jpg")          # define pelo nome do arquivo
            caminho = campo.get()           # retorna só o nome do arquivo
            campo.limpar()                  # reseta
        """
        def __init__(self, master, cores, fontes, icones, tamanho_preview=(200, 200), **kwargs):
            super().__init__(master, fg_color="transparent", **kwargs)
            self._cores = cores
            self._fontes = fontes
            self._icones = icones
            self._tamanho_preview = tamanho_preview
            self.caminho_foto = ""
            self._imagem_preview = None

            os.makedirs(PASTA_PRODUTOS, exist_ok=True)

            ctk.CTkLabel(self, text=" Foto do Produto",
                         image=icones.imagem, compound="left",
                         font=fontes.titulo_entry,
                         text_color=cores.texto.principal).pack(anchor="w")

            self._icone_camera = icones.camera
            self.preview = ctk.CTkButton(
                self, text="", image=self._icone_camera,
                fg_color=cores.fundo.principal,
                corner_radius=12,
                border_color=cores.botao.borda,
                border_width=2,
                hover=False,
                command=self._selecionar_foto
            )
            self.preview.pack(fill="both", expand=True, pady=5)

            self._lbl_adicionar = ctk.CTkLabel(
                self.preview, text="Adicionar Foto",
                font=fontes.texto_info,
                text_color=cores.texto.principal,
                fg_color="transparent"
            )
            self._lbl_adicionar.place(anchor="center", relx=0.5, rely=0.6)

            self._lbl_descricao = ctk.CTkLabel(
                self.preview, text="Formatos aceitos:\nJPG ou PNG (Máx 5MB)",
                font=fontes.sub_info,
                text_color=cores.texto.passivo,
                fg_color="transparent"
            )
            self._lbl_descricao.place(anchor="center", relx=0.5, rely=0.7)

            self._lbl_alterar = ctk.CTkLabel(
                self, text="Clique para alterar foto",
                font=fontes.sub_info,
                text_color=cores.texto.passivo
            )

            self._btn_remover = ctk.CTkButton(
                self, text="Remover foto",
                font=fontes.sub_info,
                fg_color=cores.botao.excluir,
                hover_color=self._cores.botao.excluir,
                text_color=cores.texto.branco,
                width=100, height=28,
                corner_radius=14,
                command=self._remover_foto
            )

        def _selecionar_foto(self):
            filetypes = (("Imagens", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*"))
            caminho = fd.askopenfilename(title="Escolher foto", filetypes=filetypes)
            if caminho:
                nome_arquivo = os.path.basename(caminho)
                destino = os.path.join(PASTA_PRODUTOS, nome_arquivo)
                if caminho != destino:
                    if os.path.isfile(destino) and self.caminho_foto != nome_arquivo:
                        DialogoConfirmacao(
                            self.winfo_toplevel(), self._cores, self._fontes,
                            titulo="Foto Existente",
                            mensagem=f"Já existe uma foto '{nome_arquivo}'. Deseja substituir?",
                            on_confirmar=lambda: self._aplicar_foto(caminho, nome_arquivo)
                        )
                    else:
                        self._aplicar_foto(caminho, nome_arquivo)
                else:
                    self.set(nome_arquivo)

        def _aplicar_foto(self, caminho, nome_arquivo):
            tamanho_max = 5 * 1024 * 1024
            if os.path.getsize(caminho) > tamanho_max:
                messagebox.showerror("Erro", "A foto deve ter no máximo 5MB.")
                return
            destino = os.path.join(PASTA_PRODUTOS, nome_arquivo)
            if self.caminho_foto and self.caminho_foto != nome_arquivo:
                antigo = os.path.join(PASTA_PRODUTOS, self.caminho_foto)
                if os.path.isfile(antigo):
                    os.remove(antigo)
            shutil.copy2(caminho, destino)
            self.set(nome_arquivo)

        def set(self, caminho: str):
            if not caminho:
                self._limpar_preview()
                return

            if os.path.isfile(caminho):
                origem = caminho
            else:
                origem = os.path.join(PASTA_PRODUTOS, caminho)

            if not os.path.isfile(origem):
                self._limpar_preview()
                return

            try:
                imagem = preparar_foto(origem, tamanho_saida=self._tamanho_preview, raio=8)
                self._imagem_preview = ctk.CTkImage(
                    light_image=imagem, size=self._tamanho_preview
                )
                self.caminho_foto = os.path.basename(origem)
                self.preview.configure(image=self._imagem_preview, text="")
                self._lbl_adicionar.place_forget()
                self._lbl_descricao.place_forget()
                self._lbl_alterar.pack(pady=(5, 0))
                self._btn_remover.pack(pady=(5, 0))
            except Exception:
                self._limpar_preview()

        def _limpar_preview(self):
            self.caminho_foto = ""
            self._imagem_preview = None
            self.preview.configure(image=self._icone_camera, text="")
            self._lbl_adicionar.place(anchor="center", relx=0.5, rely=0.6)
            self._lbl_descricao.place(anchor="center", relx=0.5, rely=0.7)
            self._lbl_alterar.pack_forget()
            self._btn_remover.pack_forget()

        def _remover_foto(self):
            if self.caminho_foto:
                DialogoConfirmacao(
                    self.winfo_toplevel(), self._cores, self._fontes,
                    titulo="Remover Foto",
                    mensagem="Deseja realmente remover esta foto?",
                    on_confirmar=self._confirmar_remocao
                )

        def _confirmar_remocao(self):
            caminho = os.path.join(PASTA_PRODUTOS, self.caminho_foto)
            if os.path.isfile(caminho):
                os.remove(caminho)
            self._limpar_preview()

        def get(self) -> str:
            return self.caminho_foto

        def limpar(self):
            self._limpar_preview()


# ── DIÁLOGO DE CONFIRMAÇÃO ─────────────────────────────────────────────────────
class DialogoConfirmacao(ctk.CTkToplevel):
    """
    Janela modal de confirmação.

    Uso:
        DialogoConfirmacao(
            master, cores, fontes,
            titulo="Excluir?",
            mensagem="Esta ação não pode ser desfeita.",
            on_confirmar=minha_funcao,
        )
    """
    def __init__(self, master, cores, fontes,
                 titulo="Confirmar", mensagem="Tem certeza?", on_confirmar=None):
        super().__init__(master)
        self.on_confirmar = on_confirmar

        self.title(titulo)
        self.geometry("400x180")
        self.resizable(False, False)
        self.grab_set()                    # torna modal (bloqueia a janela pai)
        self.lift()
        self.attributes("-topmost", True)
        self.configure(fg_color=cores.fundo.principal)

        # Centraliza sobre a janela pai
        self.update_idletasks()
        px = master.winfo_rootx() + (master.winfo_width()  - 400) // 2
        py = master.winfo_rooty() + (master.winfo_height() - 180) // 2
        self.geometry(f"400x180+{px}+{py}")

        ctk.CTkLabel(self, text=titulo,   font=fontes.titulo_grande,
                     text_color=cores.texto.principal).pack(pady=(20, 5))
        ctk.CTkLabel(self, text=mensagem, font=fontes.texto_info,
                     text_color=cores.texto.passivo, wraplength=360).pack(pady=(0, 15))

        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack()

        ctk.CTkButton(frame_btns, text="Cancelar",  font=fontes.botao,
                      fg_color=cores.botao.cancelar, text_color=cores.texto.principal,
                      width=140, height=40, corner_radius=50,
                      command=self.destroy).pack(side="left", padx=10)

        ctk.CTkButton(frame_btns, text="Confirmar", font=fontes.botao,
                      fg_color=cores.botao.excluir,  text_color=cores.texto.branco,
                      width=140, height=40, corner_radius=50,
                      command=self._confirmar).pack(side="left", padx=10)

    def _confirmar(self):
        self.destroy()
        if self.on_confirmar:
            self.on_confirmar()


class DialogoConfirmacaoProduto(ctk.CTkToplevel):
    """
    Janela modal de confirmação de exclusão — estilo produto_view.
    Centralizada na janela pai, com ícone de alerta, botões coloridos.

    Uso:
        DialogoConfirmacaoProduto(
            master, cores, fontes,
            titulo="Confirmar Exclusão",
            mensagem="Deseja realmente excluir este produto?",
            on_confirmar=minha_funcao,
        )
    """
    def __init__(self, master, cores, fontes,
                 titulo="Confirmar Exclusão",
                 mensagem="Deseja realmente excluir\neste produto?",
                 on_confirmar=None):
        super().__init__(master)
        self.on_confirmar = on_confirmar

        self.title(titulo)
        self.geometry("350x180")
        self.resizable(False, False)
        self.configure(fg_color=cores.fundo.principal)
        self.transient(master)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width()  - 350) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 180) // 2
        self.geometry(f"350x180+{x}+{y}")

        ctk.CTkLabel(
            self, text=f"⚠️ {mensagem}",
            font=fontes.titulo_grande,
            text_color=cores.texto.principal
        ).pack(pady=(30, 20))

        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack()

        ctk.CTkButton(
            frame_btns, text="Sim, excluir",
            width=120, height=38,
            fg_color=cores.botao.excluir, hover_color=cores.botao.excluir,
            text_color=cores.texto.branco, corner_radius=20,
            command=self._confirmar
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_btns, text="Cancelar",
            width=120, height=38,
            fg_color=cores.botao.cancelar, hover_color=cores.botao.cancelar,
            text_color=cores.texto.branco, corner_radius=20,
            command=self.destroy
        ).pack(side="left", padx=10)

    def _confirmar(self):
        self.destroy()
        if self.on_confirmar:
            self.on_confirmar()


# ── TABELA  ─────────────────────────────────────────────────────────────
class TabelaGenerica(ctk.CTkFrame):
    """
    Tabela genérica com busca, filtro, ordenação e ações.

    Uso:
        # Completo (com busca e filtros).
        tabela = TabelaGenerica(
            frame, cores, fontes, icones,
            colunas=[("Nome", "nome"), ("Email", "email")],
            on_editar=lambda d: editar(d),
            on_excluir=lambda id: excluir(id),
            mostrar_busca=True,
            mostrar_filtros=True
        )
        
        # Simples (só tabela)
        tabela = TabelaGenerica(
            frame, cores, fontes, icones,
            colunas=[("Nome", "nome")],
            mostrar_busca=False
        )

    Parâmetros:
        - colunas: lista de tuplas (nome_exibição, chave_dados)
        - on_editar: callback quando clicar editar
        - on_excluir: callback quando clicar excluir
        - mostrar_busca: mostra campo de busca (default True)
        - mostrar_filtros: mostra botão de filtros (default True)
        - filtros: lista de filtros customizados

    Métodos:
        - carregar(lista): carrega dados
        - filtrar(termo): filtra por termo
    """
    def __init__(self, master, cores, fontes, icones,
                 colunas, on_editar=None, on_excluir=None,
                 on_alterar_quantidade=None,
                 mostrar_busca=True, mostrar_filtros=False,
                 filtros=None, filtros_inline=None, placeholder_busca="", **kwargs):
        super().__init__(master, fg_color=cores.fundo.branco, corner_radius=20, **kwargs)
        self.cores = cores
        self.fontes = fontes
        self.icones = icones
        self.colunas = colunas
        self.on_editar = on_editar
        self.on_excluir = on_excluir
        self.on_alterar_quantidade = on_alterar_quantidade
        self.mostrar_busca = mostrar_busca
        self.mostrar_filtros = mostrar_filtros
        self.filtros = filtros if filtros is not None else []
        self.filtros_inline = filtros_inline if filtros_inline is not None else []
        self.dados_originais = []
        self.dados = []
        self._linhas = {}
        self._linhas_map = {}
        self.filtros_ativos = {}
        self.filtro_ativo = None
        self.ordem_crescente = True
        self._indice_ord = None
        self._salva_ordem_crescente = True
        self.placeholder_busca = placeholder_busca

        # Cria área de busca/filtros (opcional)
        if self.mostrar_busca or self.mostrar_filtros:
            self._criar_area_busca()
        
        # Cria barra de filtros inline (se houver filtros_inline)
        if self.filtros_inline:
            self._criar_area_filtros_inline()
            self.after(300, self._vincular_clique_global)
        
        self._criar_cabecalho()
        self._criar_area_scroll()
        self._criar_estado_vazio()

    def _criar_cabecalho(self):

        self.cabecalho = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=50
        )

        self.cabecalho.pack(fill="x", padx=15, pady=(10, 5))

        self.botoes_filtro = [None] * len(self.colunas)

        total_colunas = len(self.colunas)

        for i, coluna in enumerate(self.colunas):

            config = self._config_coluna(coluna)

            nome = config["titulo"]
            peso = config["peso"]
            largura_min = config["min"]

            self.cabecalho.grid_columnconfigure(i, weight=peso, minsize=largura_min)

            frame = ctk.CTkFrame(
                self.cabecalho,
                fg_color="transparent"
            )

            frame.grid(
                row=0,
                column=i,
                sticky="ew",
                padx=(5, 5)
            )

            frame.grid_columnconfigure(0, weight=1)

            lbl = ctk.CTkLabel(
                frame,
                text=nome,
                font=self.fontes.texto_info,
                text_color=self.cores.texto.passivo,
                anchor="w"
            )

            lbl.grid(
                row=0,
                column=0,
                sticky="w"
            )
            lbl.bind("<Button-1>", lambda e, idx=i: self._ao_clicar_ordenacao(idx))
            lbl.configure(cursor="hand2")

            if nome.lower() != "ações":

                btn = ctk.CTkButton(
                    frame,
                    text="",
                    image=self.icones.filtro_inativo,
                    fg_color="transparent",
                    width=20,
                    height=20,
                    hover_color=self.cores.botao.filtro_hover,
                    command=lambda idx=i: self._ao_clicar_ordenacao(idx)
                )

                btn.grid(
                    row=0,
                    column=1,
                    sticky="e",
                    padx=(2, 0)
                )

                self.botoes_filtro[i] = btn

    def _criar_area_busca(self):
        """Cria a área superior com campo de busca e botão de filtros."""
        self.area_busca = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.area_busca.pack(side="top", fill="x", padx=20, pady=(15, 5))
        self.area_busca.pack_propagate(False)
        
        if self.mostrar_busca:
            self.header_busca = Barras.HeaderBusca(
                self.area_busca, self.cores, self.fontes, self.icones,
                placeholder=self.placeholder_busca ,search_callback=self.filtrar
            )
            self.header_busca.pack(side="left", padx=10)
        
        if self.mostrar_filtros:
            self.botao_filtro = Botoes.BotaoFunil(
                self.area_busca, self.icones, self.cores, self.fontes,
                filtros=self.filtros,
                on_filtrar=self.aplicar_filtro
            )
            self.botao_filtro.pack(side="left", padx=2)
        
        self.frame_filtros_ativos = ctk.CTkFrame(
            self.area_busca,
            fg_color="transparent"
        )
        
        self.frame_filtros_ativos_visivel = False

    def _criar_area_scroll(self):
            self.area_scroll = ctk.CTkScrollableFrame(
                self, fg_color=self.cores.fundo.branco, 
                corner_radius=20,
                scrollbar_fg_color="transparent",
                scrollbar_button_color=self.cores.botao.scroll,
                scrollbar_button_hover_color=self.cores.botao.scroll_hover,
                height=100
            )
            self.area_scroll.pack(expand=True, fill="both", padx=10, pady=(0, 5))
            self.area_scroll._scrollbar.configure(width=12)

    def _criar_estado_vazio(self):
        self.frame_vazio = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.frame_vazio, text="📭", font=("Arial", 40)).pack(pady=20)
        self.lbl_vazio = ctk.CTkLabel(self.frame_vazio, text="Nenhum registro encontrado",
                                font=self.fontes.texto_info,
                                text_color=self.cores.texto.passivo)
        self.lbl_vazio.pack()
        self.frame_vazio.pack_forget()

    def _mostrar_vazio(self, mensagem=None):
        self.area_scroll.pack_forget()
        self.frame_vazio.pack(expand=True, fill="both")
        if mensagem:
            self.lbl_vazio.configure(text=mensagem)

    def _esconder_vazio(self):
        self.frame_vazio.pack_forget()
        self.area_scroll.pack(expand=True, fill="both", padx=10, pady=(0, 5))
        self.area_scroll.lift()

    def carregar(self, dados: list):
        ids_novos = set()
        for d in dados:
            id_registro = self._obter_id(d)
            if id_registro is not None:
                ids_novos.add(id_registro)

        ids_remover = set(self._linhas.keys()) - ids_novos
        for id_registro in ids_remover:
            linha = self._linhas.pop(id_registro)
            linha.destroy()
            self._linhas_map.pop(id_registro, None)
            
        dados_antigos = {self._obter_id(d): d for d in self.dados_originais}    

        for d in dados:
            id_registro = self._obter_id(d)
            if id_registro is None:
                continue
            if id_registro not in self._linhas:
                self._criar_linha(0, d)
            elif dados_antigos.get(id_registro) != d:
                linha = self._linhas.pop(id_registro)
                linha.destroy()
                self._linhas_map.pop(id_registro, None)
                self._criar_linha(0, d)    

        self.dados_originais = dados.copy()
        self.dados = dados.copy()
        if self._indice_ord is not None:
            self.ordem_crescente = not self._salva_ordem_crescente
            self._ordenar_por_coluna(self._indice_ord)
        else:
            self._renderizar()

    def atualizar_celula(self, id_registro, campo, valor, cor=None):
        """Atualiza o texto de uma celula especifica sem recriar a linha.
        Funciona apenas para CelulaTextoSimples (possui self.lbl).
        
        Parametros:
            id_registro: valor do campo id do dado (ex: id_pedido)
            campo: nome do campo da coluna (ex: "tempo")
            valor: novo texto a exibir
            cor: cor opcional para o texto (ex: "#eb5757" para vermelho)
        
        Retorna True se atualizou, False se nao encontrou.
        """
        if not hasattr(self, "_linhas_map"):
            return False
        celula = self._linhas_map.get(id_registro, {}).get(campo)
        if celula is None:
            return False
        if hasattr(celula, "lbl"):
            celula.lbl.configure(text=valor)
            if cor:
                celula.lbl.configure(text_color=cor)
            return True
        return False

    def _atualizar_scrollbar(self):
        self.update_idletasks()

        canvas = self.area_scroll._parent_canvas

        inicio, fim = canvas.yview()

        precisa_scroll = not (
            inicio <= 0.0 and fim >= 1.0
        )

        if precisa_scroll:
            self.area_scroll._scrollbar.grid()
        else:
            self.area_scroll._scrollbar.grid_remove()

    def _renderizar(self):
        ids_visiveis = set()
        for d in self.dados:
            id_registro = self._obter_id(d)
            if id_registro is not None:
                ids_visiveis.add(id_registro)

        # Esconde todas, depois repõe na ordem de self.dados
        for linha in self._linhas.values():
            linha.pack_forget()

        for d in self.dados:
            id_registro = self._obter_id(d)
            if id_registro is not None and id_registro in self._linhas:
                self._linhas[id_registro].pack(fill="x", pady=4, padx=5)

        if not self.dados:
            self._mostrar_vazio()
        else:
            self._esconder_vazio()

        self.after(50, self._atualizar_scrollbar)

    def _truncar_texto(self, texto, limite=30):
        
        if not isinstance(texto, str):
            return texto
        
        texto = texto.strip()
        
        if len(texto) <= limite:
            return texto
        
        return texto[:limite] + "..."

    def _mostrar_tooltip(self, event, texto):
        
        if not texto:
            return
        
        self._esconder_tooltip()
        self.tooltip = ctk.CTkToplevel(self)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        
        x = event.x_root + 10
        y = event.y_root + 10
        
        self.tooltip.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(
            self.tooltip,
            fg_color=self.cores.fundo.branco,
            corner_radius=8,
            border_width=1,
            border_color=self.cores.botao.borda
        )
        frame.pack()

        ctk.CTkLabel(
            frame,
            text=str(texto),
            font=self.fontes.texto_info,
            text_color=self.cores.texto.principal,
            padx=10,
            pady=5,
            wraplength=400,
            justify="left"
        ).pack()

    def _esconder_tooltip(self):

        if hasattr(self, "tooltip") and self.tooltip:

            try:
                self.tooltip.destroy()
            except:
                pass

            self.tooltip = None

    def _config_coluna(self, coluna):
        default = {
            "peso":1,
            "min": 120,
            "limite": 30,
            "align": "w",
            "sortable": True,
            "render": None,
            "tipo": "auto"
        }
        
        return {
            **default,
            **coluna
        }

    def _obter_id(self, dados):
        return (
            dados.get("id")
            or dados.get("id_pedido")
            or dados.get("id_cliente")
            or dados.get("id_funcionario")
            or dados.get("id_produto")
            or dados.get("id_estoque")
        )

    def _criar_linha(self, num, dados):

        id_registro = self._obter_id(dados)

        linha = ctk.CTkFrame(
            self.area_scroll,
            fg_color="transparent",
            corner_radius=15
        )

        linha.pack(
            fill="x",
            pady=4,
            padx=5
        )

        if id_registro is not None:
            self._linhas[id_registro] = linha

        for col, coluna in enumerate(self.colunas):

            config = self._config_coluna(coluna)

            chave = config["campo"]
            _eh_id = (
                chave == "id"
                or chave.startswith("id_")
                or chave.endswith("_id")
            )

            peso = config["peso"]

            largura_min = config["min"]

            alinhamento = config["align"]

            render = (
                config["render"]
                or (Celulas.CelulaID if _eh_id else Celulas.CelulaTextoSimples)
            )

            linha.grid_columnconfigure(
                col,
                weight=peso,
                minsize=largura_min
            )

            container = ctk.CTkFrame(
                linha,
                fg_color="transparent"
            )

            container.grid(
                row=0,
                column=col,
                sticky="ew",
                padx=5,
                pady=5
            )

            def _fixar_largura():
                w = container.winfo_width()
                if w > 10:
                    container.configure(width=w)
                    container.pack_propagate(False)
            container.after_idle(_fixar_largura)

            valor = dados.get(chave, "")

            widget = render(
                container,
                tabela=self,
                dados=dados,
                valor=valor,
                config=config
            )

            widget.pack(
                fill="x",
                anchor=alinhamento
            )

            if id_registro is not None:
                if id_registro not in self._linhas_map:
                    self._linhas_map[id_registro] = {}
                self._linhas_map[id_registro][chave] = widget

    def _pedir_confirmacao_exclusao(self, dados):
            
            primeira_coluna = self._config_coluna(
                self.colunas[0]
            )
            
            nome = dados.get(
                primeira_coluna["campo"],
                "este registro"
            )
            # Tenta ID como 'id', 'id_cliente', 'id_funcionario', 'id_pedido' ou 'id_produto'
            id_registro = (
                dados.get("id")
                or dados.get("id_cliente")
                or dados.get("id_funcionario")
                or dados.get("id_pedido")
                or dados.get("id_produto")
            )
            
            DialogoConfirmacao(
                self.winfo_toplevel(), self.cores, self.fontes,
                titulo="Confirmar Exclusão",
                mensagem=f"Tem certeza que deseja excluir '{nome}'?",
                on_confirmar=lambda: self.on_excluir(id_registro) if self.on_excluir else None
            )
        
    def _ao_clicar_ordenacao(self, idx):
        btn = self.botoes_filtro[idx]
        if self.filtro_ativo is not None and self.filtro_ativo != idx:
            ant = self.botoes_filtro[self.filtro_ativo]
            if ant:
                ant.configure(image=self.icones.filtro_inativo)
        if btn:
            btn.configure(image=self.icones.filtro_dec)
        self.filtro_ativo = idx
        self._ordenar_por_coluna(idx)
        self._indice_ord = idx
        self._salva_ordem_crescente = self.ordem_crescente

    def _ordenar_por_coluna(self, idx):

        if idx >= len(self.colunas):
            return
        cfg = self._config_coluna(self.colunas[idx])
        chave = cfg["campo"]
        tipo = cfg["tipo"]

        rev = not self.ordem_crescente

        def _chave(f):
            v = f.get(chave)
            if tipo == "numero":
                try:
                    return (0, float(v))
                except (TypeError, ValueError):
                    return (1, str(v).lower())
            if tipo == "data":
                v = str(v) if v is not None else ""
                import re
                m = re.match(r"(\d{2})/(\d{2})/(\d{4})\s*(\d{2}):(\d{2})?", v)
                if m:
                    return (0, (int(m[3]), int(m[2]), int(m[1]), int(m[4]), int(m[5])))
                return (1, v.lower())
            if tipo == "texto":
                return (1, str(v).lower() if v is not None else "")
            # auto
            if isinstance(v, (int, float)):
                return (0, v)
            try:
                return (0, float(v))
            except (TypeError, ValueError):
                return (1, str(v).lower() if v is not None else "")

        self.dados.sort(key=_chave, reverse=rev)
        
        btn = self.botoes_filtro[idx]
        
        if btn:
            icone = (
                self.icones.filtro_cresc
                if self.ordem_crescente
                else self.icones.filtro_dec
            )
            
            btn.configure(image=icone)
        
        self.ordem_crescente = not self.ordem_crescente
        
        self._renderizar()

    def filtrar(self, termo: str):
        
        termo = termo.lower().strip()
        
        if not termo:
            
            self.dados = self.dados_originais.copy()
            
        else:
            
            self.dados = [
                
                f for f in self.dados_originais
                if any(
                    termo in str(
                        f.get(
                            self._config_coluna(col)["campo"],
                            ""
                        )
                    ).lower()
                    for col in self.colunas
                )
            ]
            
        self._renderizar()

    def _filtrar_dados(self):
        self.dados = self.dados_originais.copy()
        
        for tipo, valor in self.filtros_ativos.items():
            self.dados = [
                f for f in self.dados
                if f.get(tipo) == valor
            ]
        
        # Se não temos filtros inline, renderiza chips de filtros ativos
        if not self.filtros_inline:
            self._renderizar_filtros_ativos()
        
        self._renderizar()

    def _renderizar_filtros_ativos(self):

        # limpa chips antigos
        for widget in self.frame_filtros_ativos.winfo_children():
            widget.destroy()

        if not self.filtros_ativos:

            if self.frame_filtros_ativos_visivel:

                self.frame_filtros_ativos.pack_forget()

        self.frame_filtros_ativos_visivel = False

    def _criar_area_filtros_inline(self):
        """Cria a barra de filtros inline com botões pill na área de busca."""
        # Botão "Todos" à esquerda
        self.btn_todos = ctk.CTkButton(
            self.area_busca,
            text="Todos",
            height=32,
            corner_radius=16,
            fg_color=self.cores.botao.novo if not self.filtros_ativos else self.cores.fundo.secundario,
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.branco if not self.filtros_ativos else self.cores.texto.principal,
            font=self.fontes.texto_info,
            width=0,
            command=self._limpar_todos_filtros_inline
        )
        self.btn_todos.pack(side="left", padx=(10, 5))
        
        # Botões de filtro
        self.botoes_filtro_inline = {}
        for filtro in self.filtros_inline:
            btn = self._criar_botao_filtro_inline(filtro)
            self.botoes_filtro_inline[filtro["campo"]] = btn

    def _criar_botao_filtro_inline(self, filtro):
        """Cria um botão de filtro inline com dropdown."""
        campo = filtro["campo"]
        titulo = filtro["titulo"]
        opcoes = filtro.get("opcoes", [])
        
        frame = ctk.CTkFrame(self.area_busca, fg_color="transparent")
        frame.pack(side="left", padx=(0, 5))
        
        # Botão principal do filtro
        btn = ctk.CTkButton(
            frame,
            text=f"▾ {titulo}",
            height=32,
            corner_radius=16,
            fg_color=self.cores.fundo.secundario,
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            width=0,
            command=lambda c=campo: self._toggle_dropdown(c)
        )
        btn.pack()
        
        # Frame do dropdown (inicialmente oculto) - criado como janela Toplevel
        dropdown = ctk.CTkToplevel(self.winfo_toplevel())
        dropdown.overrideredirect(True)
        dropdown.attributes("-topmost", True)
        dropdown.configure(fg_color=self.cores.fundo.branco)
        dropdown.withdraw()
        
        # Armazenar referências
        btn._campo = campo
        btn._dropdown = dropdown
        btn._opcoes = opcoes
        btn._ativo = False
        btn._dropdown_aberto = False
        btn._frame_pai = frame
        
        return btn

    def _toggle_dropdown(self, campo):
        """Abre ou fecha o dropdown de um filtro."""
        btn = self.botoes_filtro_inline.get(campo)
        if not btn:
            return
        
        # Se já está ativo, não abre dropdown (precisa clicar no ✕ para remover)
        if btn._ativo:
            return
        
        # Fecha outros dropdowns abertos
        self._fechar_todos_dropdowns(exeto=campo)
        
        if btn._dropdown_aberto:
            # Fecha o dropdown
            btn._dropdown.withdraw()
            btn._dropdown_aberto = False
            btn.configure(text=f"▾ {btn._campo.title()}",
                         fg_color=self.cores.fundo.secundario,
                         text_color=self.cores.texto.principal)
        else:
            # Abre o dropdown
            self._criar_opcoes_dropdown(btn)
            # Posiciona o dropdown abaixo do botão (coordenadas absolutas na tela)
            x = btn.winfo_rootx()
            y = btn.winfo_rooty() + btn.winfo_height() + 5
            btn._dropdown.geometry(f"+{x}+{y}")
            btn._dropdown.deiconify()
            btn._dropdown_aberto = True
            btn.configure(text=f"▴ {btn._campo.title()}", 
                         fg_color=self.cores.botao.hover,
                         text_color=self.cores.texto.branco)

    def _fechar_todos_dropdowns(self, exeto=None):
        """Fecha todos os dropdowns, exceto o especificado."""
        for campo, btn in self.botoes_filtro_inline.items():
            if campo != exeto and btn._dropdown_aberto:
                btn._dropdown.withdraw()
                btn._dropdown_aberto = False
                btn.configure(text=f"▾ {campo.title()}",
                             fg_color=self.cores.fundo.secundario,
                             text_color=self.cores.texto.principal)

    def _criar_opcoes_dropdown(self, btn):
        """Cria as opções dentro do dropdown."""
        # Limpa opções anteriores
        for widget in btn._dropdown.winfo_children():
            widget.destroy()
        
        for opcao in btn._opcoes:
            label = opcao.get("label", str(opcao.get("valor", "")))
            valor = opcao.get("valor", label)
            
            opcao_btn = ctk.CTkButton(
                btn._dropdown,
                text=label,
                height=28,
                corner_radius=4,
                fg_color="transparent",
                hover_color=self.cores.botao.hover,
                text_color=self.cores.texto.principal,
                font=self.fontes.texto_info,
                anchor="w",
                command=lambda v=valor, c=btn._campo: self._aplicar_filtro_inline(c, v)
            )
            opcao_btn.pack(fill="x", padx=5, pady=2)

    def _aplicar_filtro_inline(self, campo, valor):
        """Aplica um filtro inline."""
        # Fecha o dropdown
        btn = self.botoes_filtro_inline.get(campo)
        if btn:
            btn._dropdown.withdraw()
            btn._dropdown_aberto = False
        
        # Atualiza o estado do filtro
        self.filtros_ativos[campo] = valor
        
        # Atualiza visual do botão
        self._atualizar_visual_filtro(campo, valor)
        
        # Atualiza botão "Todos"
        self._atualizar_botao_todos()
        
        # Aplica a filtragem
        self._filtrar_dados()

    def _atualizar_visual_filtro(self, campo, valor):
        """Atualiza o visual de um botão de filtro para o estado ativo."""
        btn = self.botoes_filtro_inline.get(campo)
        if not btn:
            return
        
        # Encontra o label da opção selecionada
        label = str(valor)
        for opcao in btn._opcoes:
            if opcao.get("valor") == valor:
                label = opcao.get("label", str(valor))
                break
        
        # Atualiza o botão para estado ativo
        btn.configure(
            text=f"{label} ✕",
            fg_color=self.cores.botao.novo,
            hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco
        )
        btn._ativo = True
        
        # Remove comando de toggle e adiciona comando para remover filtro
        btn.configure(command=lambda c=campo: self._remover_filtro_inline(c))

    def _remover_filtro_inline(self, campo):
        """Remove um filtro inline específico."""
        if campo in self.filtros_ativos:
            del self.filtros_ativos[campo]
        
        # Restaura visual do botão
        btn = self.botoes_filtro_inline.get(campo)
        if btn:
            btn.configure(
                text=f"▾ {campo.title()}",
                fg_color=self.cores.fundo.secundario,
                hover_color=self.cores.botao.hover,
                text_color=self.cores.texto.principal
            )
            btn._ativo = False
            btn.configure(command=lambda c=campo: self._toggle_dropdown(c))
        
        # Atualiza botão "Todos"
        self._atualizar_botao_todos()
        
        # Aplica a filtragem
        self._filtrar_dados()

    def _limpar_todos_filtros_inline(self):
        """Limpa todos os filtros inline."""
        self.filtros_ativos.clear()
        
        # Restaura visuais de todos os botões
        for campo, btn in self.botoes_filtro_inline.items():
            btn.configure(
                text=f"▾ {campo.title()}",
                fg_color=self.cores.fundo.secundario,
                hover_color=self.cores.botao.hover,
                text_color=self.cores.texto.passivo
            )
            btn._ativo = False
            btn.configure(command=lambda c=campo: self._toggle_dropdown(c))
        
        # Atualiza botão "Todos"
        self._atualizar_botao_todos()
        
        # Aplica a filtragem
        self._filtrar_dados()

    def atualizar_opcoes_filtro(self, campo, opcoes):
        """Atualiza as opções de um filtro inline (ex: categorias dinâmicas)."""
        btn = self.botoes_filtro_inline.get(campo)
        if not btn:
            return
        btn._opcoes = opcoes
        for filtro in self.filtros_inline:
            if filtro["campo"] == campo:
                filtro["opcoes"] = opcoes
                break

    def _atualizar_botao_todos(self):
        """Atualiza o visual do botão 'Todos' baseado nos filtros ativos."""
        if not self.filtros_ativos:
            # Nenhum filtro ativo - botão destacado
            self.btn_todos.configure(
                fg_color=self.cores.botao.novo,
                text_color=self.cores.texto.branco
            )
        else:
            # Há filtros ativos - botão neutro
            self.btn_todos.configure(
                fg_color=self.cores.fundo.secundario,
                text_color=self.cores.texto.principal
            )

    def _clique_externo(self, event):
        """Fecha todos os dropdowns ao clicar fora."""
        # Verifica se há dropdowns abertos
        tem_dropdown_aberto = False
        for campo, btn in self.botoes_filtro_inline.items():
            if btn._dropdown_aberto:
                tem_dropdown_aberto = True
                break
        
        if not tem_dropdown_aberto:
            return
        
        # Fecha todos os dropdowns
        self._fechar_todos_dropdowns()

    def _bind_clique_externo(self):
        pass

    def _configurar_fechar_dropdowns(self):
        pass

    def _verificar_fechamento(self, campo):
        pass

    def _vincular_clique_global(self):
        """Vincula clique global para fechar dropdowns."""
        root = self.winfo_toplevel()
        root.bind("<Button-1>", self._ao_clicar_global, add="+")

    def _ao_clicar_global(self, event):
        """Fecha todos os dropdowns ao clicar fora."""
        widget = event.widget
        
        # Verifica se o clique foi em qualquer botão de filtro
        for campo, btn in self.botoes_filtro_inline.items():
            try:
                w = widget
                for _ in range(5):
                    if w == btn:
                        return
                    if hasattr(w, 'master'):
                        w = w.master
                    else:
                        break
            except:
                pass
        
        # Verifica se o clique foi dentro de algum dropdown
        for campo, btn in self.botoes_filtro_inline.items():
            if btn._dropdown_aberto:
                try:
                    w = widget
                    for _ in range(5):
                        if w == btn._dropdown:
                            return
                        if hasattr(w, 'master'):
                            w = w.master
                        else:
                            break
                except:
                    pass
        
        # Fecha todos os dropdowns
        self._fechar_todos_dropdowns()

    def _atualizar_filtros_ativos(self):
        """Atualiza a exibição dos filtros ativos."""
        # Remove chips antigos
        for widget in self.frame_filtros_ativos.winfo_children():
            widget.destroy()
        
        if not self.filtros_ativos:
            self.frame_filtros_ativos.pack_forget()
            self.frame_filtros_ativos_visivel = False
            return
        
        if not self.frame_filtros_ativos_visivel:

            self.frame_filtros_ativos.pack(
                side="left",
                padx=5
            )
            
            self.frame_filtros_ativos.update_idletasks()

            self.frame_filtros_ativos_visivel = True

        # cria chips novos
        for tipo, valor in self.filtros_ativos.items():
            
            if valor is True:
                texto = "Ativos"

            elif valor is False:
                texto = "Inativos"

            else:
                texto = str(valor)

            chip = ctk.CTkButton(
                self.frame_filtros_ativos,

                text=f"{texto} ✕",

                height=30,
                corner_radius=50,
                fg_color=self.cores.botao.funil,
                hover_color=self.cores.botao.funil_hover,
                text_color=self.cores.texto.verde_jambu,
                font=self.fontes.texto_info,
                width=20,
                command=lambda t=tipo: self.remover_filtro(t)
            )

            chip.pack(
                side="left",
                padx=3
            )

    def aplicar_filtro(self, tipo, valor):
        if tipo is None:
            self.remover_filtro()
            return
    
        self.filtros_ativos[tipo] = valor
        
        # Se não temos filtros inline, renderiza chips de filtros ativos
        if not self.filtros_inline:
            self._renderizar_filtros_ativos()
        
        self._filtrar_dados()

    def remover_filtro(self, tipo=None):

        # remove filtro específico
        if tipo:

            if tipo in self.filtros_ativos:
                del self.filtros_ativos[tipo]

        # remove todos
        else:

            self.filtros_ativos.clear()

        self._filtrar_dados()
        
        # Se não temos filtros inline, renderiza chips de filtros ativos
        if not self.filtros_inline:
            self._renderizar_filtros_ativos()


# ── TÍTULOS ────────────────────────────────────────────────────────────────────
class Titulos:
    """Títulos padronizados para barras superiores."""

    class TituloTopo(ctk.CTkLabel):
        """Label de título para a barra superior."""
        def __init__(self, master, cores, fontes, texto="", imagem=None, **kwargs):
            super().__init__(master, text=texto, image=imagem,
                             text_color=cores.texto.verde_jambu,
                             font=fontes.titulo, fg_color="transparent", **kwargs)
      
      
# ── BADGE ──────────────────────────────────────────────────────────────────────────

class Badges:
    
    class Ativo(ctk.CTkLabel):
        def __init__(self, master, cores, fontes, texto="● Ativo"):
            super().__init__(master,text=texto,
                             fg_color=cores.badge.status_ativo,
                             text_color=cores.texto.verde_escuro,
                             font=fontes.badge,
                             height=20,
                             corner_radius=50)
    
    class Inativo(ctk.CTkLabel):
        def __init__(self, master, cores, fontes, texto="● Inativo"):
            super().__init__(master,text=texto,
                             fg_color=cores.fundo.vermelho,
                             text_color=cores.texto.vermelho_escuro,
                             font=fontes.badge,
                             corner_radius=50)

     
# ── INFORMAÇÕES ────────────────────────────────────────────────────────────────────

class CardProduto(ctk.CTkFrame):
    """Card de produto para grid de seleção (ex: tela de caixa)."""

    def __init__(self, master, cores, fontes, icones, produto, on_adicionar=None):
        super().__init__(
            master,
            fg_color=cores.fundo.secundario,
            border_width=1,
            border_color=cores.card.borda_card,
            corner_radius=10,
            height=220
        )
        self.pack_propagate(False)
        self.cores = cores
        self.fontes = fontes
        self.icones = icones
        self.produto = produto
        self.on_adicionar = on_adicionar

        self._criar_conteudo()

        self.bind("<Enter>", self._ao_passar_mouse)
        self.bind("<Leave>", self._ao_sair_mouse)

    def _ao_passar_mouse(self, event=None):
        self.configure(border_color=self.cores.botao.novo, border_width=2)

    def _ao_sair_mouse(self, event=None):
        self.configure(border_color=self.cores.card.borda_card, border_width=1)

    def _criar_conteudo(self):
        foto = self.produto.get("foto", "")

        # Imagem
        frame_foto = ctk.CTkFrame(
            self, fg_color=self.cores.fundo.secundario,
            corner_radius=10, height=100
        )
        frame_foto.pack(fill="x", padx=10, pady=(5, 2))
        frame_foto.pack_propagate(False)

        foto_label = ctk.CTkLabel(
            frame_foto, text="", font=("Arial", 18),
            fg_color="transparent"
        )
        foto_label.pack(fill="both", expand=True, pady=(5, 0))

        self._foto_caminho = ""
        self._foto_label = foto_label
        self._frame_foto = frame_foto
        self._resize_job = None

        if foto:
            caminho = os.path.join(PASTA_PRODUTOS, foto)
            if os.path.isfile(caminho):
                self._foto_caminho = caminho
                self._atualizar_foto()

        frame_foto.bind("<Configure>", self._on_frame_resize)

        # Textos (nome + descrição)
        frame_textos = ctk.CTkFrame(self, fg_color="transparent")
        frame_textos.pack(fill="x", padx=10, pady=(2, 0))

        self._nome_label = ctk.CTkLabel(
            frame_textos, text=self.produto["nome"],
            font=self.fontes.nome_card,
            text_color=self.cores.texto.principal
        )
        self._nome_label.pack(anchor="w")
        self._nome_label.bind("<Configure>", self._ajustar_fonte_nome)

        desc = self.produto.get("descricao") or ""
        if desc:
            texto_desc = desc[:30] + "..." if len(desc) > 30 else desc
            ctk.CTkLabel(
                frame_textos, text=texto_desc,
                font=self.fontes.pequeno,
                text_color=self.cores.texto.passivo
            ).pack(anchor="w")
        else:
            texto_desc = desc[:30] + "..." if len(desc) > 30 else desc
            ctk.CTkLabel(
                frame_textos, text="",
                font=self.fontes.pequeno,
                text_color=self.cores.texto.passivo
            ).pack(anchor="w")

        # Preço + Botão
        frame_preco = ctk.CTkFrame(self, fg_color="transparent")
        frame_preco.pack(fill="x", padx=(10,12), pady=(2, 4))

        preco = self.produto.get("preco", 0)
        texto_preco = f"R$ {preco:.2f}".replace(".", ",")
        ctk.CTkLabel(
            frame_preco, text=texto_preco,
            font=self.fontes.preço_card,
            text_color=self.cores.texto.verde_escuro
        ).pack(side="left", anchor="nw")

        ctk.CTkButton(
            frame_preco, text="", image=self.icones.add_branco_pequeno,
            height=30, width=30,
            corner_radius=5,
            fg_color=self.cores.botao.novo,
            hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco,
            font=self.fontes.pequeno,
            command=self._adicionar
        ).pack(side="right")

    def _on_frame_resize(self, event):
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self._atualizar_foto)

    def _atualizar_foto(self):
        if not self._foto_caminho:
            return
        largura = self._frame_foto.winfo_width()
        altura = self._frame_foto.winfo_height()
        if largura < 10 or altura < 10:
            return
        try:
            imagem = preparar_foto_retangular(self._foto_caminho, tamanho_saida=(largura, altura), raio=10)
            img_preview = ctk.CTkImage(light_image=imagem, size=(largura, altura))
            self._foto_label.configure(image=img_preview, text="", fg_color="transparent")
            self._foto_label._img_ref = img_preview
        except Exception:
            pass

    def _adicionar(self):
        if self.on_adicionar:
            self.on_adicionar(self.produto)

    def _ajustar_fonte_nome(self, event):
        texto = self.produto["nome"]
        largura = event.width
        for tamanho in [14, 13, 12, 11, 10]:
            fonte = ctk.CTkFont(family="Open Sans", size=tamanho, weight="bold")
            if fonte.measure(texto) <= largura:
                self._nome_label.configure(font=fonte)
                return


class Celulas:
    
    class CelulaBase(ctk.CTkFrame):
        def __init__(
            self,
            master,
            tabela,
            dados,
            valor,
            config
        ):
            super().__init__(
                master,
                fg_color="transparent"
            )
            
            self.tabela = tabela
            self.dados = dados
            self.valor = valor
            self.config = config

            self.cores = tabela.cores
            self.fontes = tabela.fontes
            self.icones = tabela.icones

            self.align = config["align"]
            self.limite = config["limite"]
            self.campo = config["campo"]
    class CelulaNomeDescricao(CelulaBase): # Foto + Nome em cima, Descrição embaixo

        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            nome = dados.get("nome", "")
            descricao = dados.get("descricao", "")
            foto = dados.get("foto", "")

            frame_principal = ctk.CTkFrame(self, fg_color="transparent")
            frame_principal.pack(fill="both", expand=True, padx=4, pady=2)

            frame_foto = ctk.CTkFrame(frame_principal, fg_color="transparent",
                                       width=44, height=44)
            frame_foto.pack(side="left", padx=(0, 8), pady=2)
            frame_foto.pack_propagate(False)

            foto_label = ctk.CTkLabel(frame_foto, text="",
                                       width=40, height=40,
                                       fg_color=self.cores.fundo.cinza_claro,
                                       corner_radius=8)
            foto_label.place(relx=0.5, rely=0.5, anchor="center")

            if foto:
                caminho = os.path.join(PASTA_PRODUTOS, foto)
                if os.path.isfile(caminho):
                    try:
                        imagem = preparar_foto(caminho, tamanho_saida=(80, 80), raio=12)
                        img_preview = ctk.CTkImage(light_image=imagem, size=(40, 40))
                        foto_label.configure(image=img_preview, text="", fg_color="transparent")
                        foto_label._img_ref = img_preview
                    except Exception:
                        foto_label.configure(image=self.icones.imagem, text="")
                else:
                    foto_label.configure(image=self.icones.imagem, text="")
            else:
                foto_label.configure(image=self.icones.imagem, text="")

            frame_textos = ctk.CTkFrame(frame_principal, fg_color="transparent")
            frame_textos.pack(side="left", fill="both", expand=True)

            lbl_nome = ctk.CTkLabel(
                frame_textos, text=nome,
                font=self.fontes.texto_info,
                text_color=self.cores.texto.principal,
                anchor="w"
            )
            lbl_nome.pack(fill="x", anchor="w", pady=(5, 0))

            if descricao:
                texto_desc = tabela._truncar_texto(descricao, 40)
                lbl = ctk.CTkLabel(
                    frame_textos, text=texto_desc,
                    font=self.fontes.pequeno,
                    text_color=self.cores.texto.passivo,
                    anchor="nw"
                )
                lbl.place(relx=0, rely=0.5)
                if texto_desc != descricao:
                    lbl.bind("<Enter>", lambda e, t=descricao: tabela._mostrar_tooltip(e, t))
                    lbl.bind("<Leave>", lambda e: tabela._esconder_tooltip())

    class CelulaItem(ctk.CTkFrame): # Item + Descrição    
        pass
    class CelulaTextoSimples(CelulaBase): # Nome, email, cargo, categoria, telefone, cidade

        def __init__(
            self,
            master,
            tabela,
            dados,
            valor,
            config
        ):

            super().__init__(
                master,
                tabela,
                dados,
                valor,
                config
            )

            texto_original = valor

            texto_exibido = tabela._truncar_texto(
                texto_original,
                self.limite
            )

            self.lbl = ctk.CTkLabel(
                self,
                text=texto_exibido,
                font=self.fontes.texto_info,
                text_color=self.cores.texto.principal,
                anchor=self.align
            )
            label = self.lbl

            label.pack(
                fill="x",
                anchor=self.align
            )

            if (
                isinstance(texto_original, str)
                and texto_exibido != texto_original
            ):

                label.bind(
                    "<Enter>",
                    lambda e, t=texto_original:
                        tabela._mostrar_tooltip(e, t)
                )

                label.bind(
                    "<Leave>",
                    lambda e:
                        tabela._esconder_tooltip()
                )
    class CelulaStatus(CelulaBase): # Ativo/inativo, pagamento, estoque

        def __init__(
            self,
            master,
            tabela,
            dados,
            valor,
            config
        ):

            super().__init__(
                master,
                tabela,
                dados,
                valor,
                config
            )

            ativo = dados.get(
                "ativo",
                dados.get("status", True)
            )

            cor = (
                self.cores.fundo.verde
                if ativo else
                self.cores.fundo.cinza
            )

            txt = (
                "Ativo"
                if ativo else
                "Inativo"
            )

            ctk.CTkLabel(
                self,
                text=txt,
                font=self.fontes.texto_info,
                fg_color=cor,
                text_color=(
                    self.cores.texto.verde_escuro
                    if ativo else
                    self.cores.texto.passivo
                ),
                corner_radius=50
            ).pack(anchor=self.align)
            
    class CelulaEntregador(CelulaBase):
        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            is_entregador = bool(valor) if valor is not None else bool(dados.get("is_entregador", False))

            cor = self.cores.fundo.verde if is_entregador else self.cores.fundo.cinza
            txt = "Sim" if is_entregador else "Não"
            txt_cor = self.cores.texto.verde_escuro if is_entregador else self.cores.texto.passivo

            ctk.CTkLabel(
                self,
                text=txt,
                font=self.fontes.texto_info,
                fg_color=cor,
                text_color=txt_cor,
                corner_radius=50
            ).pack(anchor=self.align)
            
    class CelulaStatusEstoque(CelulaBase):  # OK / Baixo / Zerado
        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            quantidade = dados.get("quantidade", 0)
            quantidade_minima = dados.get("quantidade_minima", 0)

            if quantidade == 0:
                status, cor, txt_cor = "Zerado", self.cores.texto.vermelho, self.cores.texto.branco
            elif quantidade <= quantidade_minima:
                status, cor, txt_cor = "Baixo", self.cores.texto.amarelo, self.cores.texto.principal
            else:
                status, cor, txt_cor = "OK", self.cores.fundo.verde, self.cores.texto.verde_escuro

            ctk.CTkLabel(
                self,
                text=status,
                font=self.fontes.texto_info,
                fg_color=cor,
                text_color=txt_cor,
                corner_radius=50,
                padx=8,
                pady=2,
                anchor="center",
            ).pack(anchor=self.align)

    class CelulaControleQuantidade(CelulaBase):  # Botões − / + de estoque
        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            self.dados = dados
            self.id_estoque = dados.get("id_estoque")

            ctk.CTkButton(
                self,
                text="−",
                width=26,
                height=26,
                corner_radius=13,
                fg_color=self.cores.botao.excluir,
                hover_color=self.cores.botao.excluir,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.decrementar
            ).pack(side="left", padx=(0, 4))

            self.rotulo = ctk.CTkLabel(
                self,
                text=str(self.dados.get("quantidade", 0)),
                font=ctk.CTkFont(size=13, weight="bold"),
                width=30,
                anchor="center"
            )
            self.rotulo.pack(side="left")

            ctk.CTkButton(
                self,
                text="+",
                width=26,
                height=26,
                corner_radius=13,
                fg_color=self.cores.texto.ok,
                hover_color=self.cores.texto.ok,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.incrementar
            ).pack(side="left", padx=(4, 0))

        def incrementar(self):
            nova = self.dados.get("quantidade", 0) + 1
            self._alterar(nova)

        def decrementar(self):
            atual = self.dados.get("quantidade", 0)
            if atual > 0:
                self._alterar(atual - 1)

        def _alterar(self, nova_quantidade):
            self.dados["quantidade"] = nova_quantidade
            self.rotulo.configure(text=str(nova_quantidade))
            if hasattr(self.tabela, "on_alterar_quantidade") and self.tabela.on_alterar_quantidade:
                self.tabela.on_alterar_quantidade(self.dados, nova_quantidade)
    
    class CelulaID(CelulaBase): # Badge estilizado para colunas de ID
        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            ctk.CTkLabel(
                self,
                text=f"#{str(valor).zfill(3)}" if valor != "" else "—",
                font=self.fontes.texto_info,
                fg_color=self.cores.botao.id_badge,
                text_color=self.cores.botao.id_badge_txt,
                corner_radius=50,
                padx=8,
                pady=2,
                anchor="center",
            ).pack(anchor=self.align)

    class CelulaIDCaixa(CelulaBase): # Badge estilizado para ID no caixa
        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            texto = f"ID {str(valor).zfill(3)}" if valor else "—"
            ctk.CTkLabel(
                self,
                text=texto,
                font=self.fontes.texto_info,
                fg_color=self.cores.botao.id_badge,
                text_color=self.cores.texto.branco,
                corner_radius=50,
                padx=8,
                pady=2,
                anchor="center",
            ).pack(anchor=self.align)

    class CelulaStatusPedido(CelulaBase): # Badge de status do pedido
        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            cores_map = {
                "Criado": self.cores.fundo.cinza_claro,
                "Confirmado": self.cores.fundo.verde,
                "Em Preparo": self.cores.botao.novo,
                "Pronto": self.cores.fundo.azul,
                "Entregue": self.cores.texto.verde,
                "Concluido": self.cores.fundo.cinza_claro,
                "Cancelado": self.cores.texto.vermelho,
            }
            texto_cor_map = {
                "Criado": self.cores.texto.passivo,
                "Confirmado": self.cores.texto.branco,
                "Em Preparo": self.cores.texto.branco,
                "Pronto": self.cores.texto.branco,
                "Entregue": self.cores.texto.branco,
                "Concluido": self.cores.texto.passivo,
                "Cancelado": self.cores.texto.branco,
            }

            cor = cores_map.get(valor, self.cores.fundo.cinza_claro)
            txt_cor = texto_cor_map.get(valor, self.cores.texto.passivo)

            ctk.CTkLabel(
                self,
                text=valor if valor else "—",
                font=self.fontes.texto_info,
                fg_color=cor,
                text_color=txt_cor,
                corner_radius=50,
                padx=8,
                pady=2,
                anchor="center",
            ).pack(anchor=self.align)

    class CelulaStatusPagamento(CelulaBase): # Badge de status do pagamento
        def __init__(self, master, tabela, dados, valor, config):
            super().__init__(master, tabela, dados, valor, config)

            cores_map = {
                "Pago": self.cores.texto.verde,
                "Parcial": self.cores.texto.amarelo,
                "Pendente": self.cores.texto.amarelo,
                "Aguardando": self.cores.texto.amarelo,
                "Cancelado": self.cores.texto.vermelho,
            }
            texto_cor_map = {
                "Pago": self.cores.texto.branco,
                "Parcial": self.cores.texto.principal,
                "Pendente": self.cores.texto.principal,
                "Aguardando": self.cores.texto.principal,
                "Cancelado": self.cores.texto.branco,
            }

            cor = cores_map.get(valor, self.cores.fundo.cinza_claro)
            txt_cor = texto_cor_map.get(valor, self.cores.texto.passivo)

            ctk.CTkLabel(
                self,
                text=valor if valor else "—",
                font=self.fontes.texto_info,
                fg_color=cor,
                text_color=txt_cor,
                corner_radius=50,
                padx=8,
                pady=2,
                anchor="center",
            ).pack(anchor=self.align)

    class CelulaAcoes(CelulaBase): # Editar, excluir, visualizar, menu
        def __init__(
            self,
            master,
            tabela,
            dados,
            valor,
            config
        ):
            super().__init__(
                master,
                tabela,
                dados,
                valor,
                config
            )

            frame_acoes = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )

            frame_acoes.pack(anchor=self.align)

            if self.tabela.on_editar:
                ctk.CTkButton(
                    frame_acoes,
                    image=self.icones.editar,
                    text="",
                    width=25,
                    height=25,
                    fg_color="transparent",
                    hover_color=self.cores.fundo.cinza_claro,
                    cursor="hand2",
                    command=lambda: self.tabela.on_editar(dados)
                ).pack(side="left", padx=3)

            if self.tabela.on_excluir:
                ctk.CTkButton(
                    frame_acoes,
                    image=self.icones.apagar,
                    text="",
                    width=25,
                    height=25,
                    fg_color="transparent",
                    hover_color=self.cores.fundo.cinza_claro,
                    cursor="hand2",
                    command=lambda: self.tabela._pedir_confirmacao_exclusao(dados)
                ).pack(side="left", padx=3)


class TabelaPaginada(ctk.CTkFrame):
    """
    Tabela com paginação incremental ("Carregar mais").

    Uso:
        tabela = TabelaPaginada(frame, cores, fontes, icones,
                                colunas=[("Nome", "nome"), ...],
                                limite=50)
        tabela.pack(fill="both", expand=True)

        # Carregar primeira página
        tabela.recarregar(primeiros_dados)

        # Anexar próxima página
        tabela.anexar(mais_dados)
        # Se mais_dados < limite, oculta o botão automaticamente
    """
    def __init__(self, master, cores, fontes, icones,
                 colunas, limite=50,
                 on_editar=None, on_excluir=None,
                 mostrar_busca=True, mostrar_filtros=False,
                 filtros=None, filtros_inline=None,
                 placeholder_busca="", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.cores = cores
        self.fontes = fontes
        self._limite = limite
        self._offset = 0
        self._dados = []

        self.tabela = TabelaGenerica(
            self, cores, fontes, icones,
            colunas=colunas,
            on_editar=on_editar,
            on_excluir=on_excluir,
            mostrar_busca=mostrar_busca,
            mostrar_filtros=mostrar_filtros,
            filtros=filtros,
            filtros_inline=filtros_inline,
            placeholder_busca=placeholder_busca,
        )
        self.tabela.pack(fill="both", expand=True)

        self._frame_btn = ctk.CTkFrame(self, fg_color=cores.fundo.branco)
        self._btn_mais = ctk.CTkButton(
            self._frame_btn,
            text="Carregar mais ↓",
            font=fontes.texto_info,
            fg_color=cores.fundo.cinza_claro,
            text_color=cores.texto.principal,
            height=36,
            corner_radius=10,
            cursor="hand2",
            command=self._ao_clicar_mais,
        )
        self._btn_mais.pack(fill="x", padx=30, pady=10)
        self._callback_mais = None
        self._frame_btn.pack(fill="x", side="bottom")

    def definir_callback_carregar_mais(self, callback):
        self._callback_mais = callback

    def recarregar(self, dados):
        self._offset = len(dados)
        self._dados = list(dados)
        self.tabela.carregar(self._dados)
        self._mostrar_btn(len(dados) >= self._limite)

    def anexar(self, dados):
        if not dados:
            self._mostrar_btn(False)
            return
        self._offset += len(dados)
        self._dados.extend(dados)
        self.tabela.carregar(self._dados)
        self._mostrar_btn(len(dados) >= self._limite)

    def _ao_clicar_mais(self):
        if self._callback_mais:
            self._btn_mais.configure(state="disabled", text="Carregando...")
            try:
                novos = self._callback_mais(self._offset, self._limite)
                self.anexar(novos)
            finally:
                self._btn_mais.configure(state="normal", text="Carregar mais ↓")

    def _mostrar_btn(self, visivel):
        if visivel:
            self._frame_btn.pack(fill="x", side="bottom")
        else:
            self._frame_btn.pack_forget()