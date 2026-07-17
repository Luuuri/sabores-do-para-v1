"""
tela_clientes_cad.py - Cadastro e edição de clientes.

Recebe callbacks do Controller (salvar, excluir, voltar) e usa componentes reutilizáveis.
Segue exatamente o mesmo padrão de tela_funcionarios_cad.py.
"""
import re
import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import (
    Frames, Botoes, Campos, DialogoConfirmacao, TabelaGenerica, Celulas
)
from app.controller.cliente_controller import salvar_cliente
from app.controller.endereco_controller import (
    listar_enderecos, salvar_endereco, excluir_endereco,
    definir_endereco_principal,
)
from app.utils.validacoes import (
    validar_email, validar_celular, formatar_celular,
    formatar_cpf, cpf_valido, capitalizar_campo,
    formatar_cep, formatar_apenas_digitos, formatar_apenas_letras,
)

def main():
    """Ponto de entrada para testar a tela isolada."""
    root = ctk.CTk()
    root.title("Point dos Sabores - Clientes")
    root.geometry("1100x700")

    cores, fontes, icones = get_cores(), Fontes(), Icones()
    tela = TelaClientesCad(
        root, cores, fontes, icones,
        on_salvar=salvar_cliente,
        on_voltar=root.destroy,
    )
    tela.pack(fill="both", expand=True)
    root.mainloop()


# ── TELA PRINCIPAL ──────────────────────────────────────────────────────────────
class TelaClientesCad(Frames.FrameLayoutPadrao):
    """
    Tela de cadastro/edição de clientes.
    API: .preencher_dados(dict), .limpar_formulario(), .definir_modo('novo'/'editar')
    """

    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_salvar=None, on_excluir=None,
                 on_home=None, menu_callbacks=None, on_click_titulo=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Clientes", icone=icones.clientes,
                         on_novo=None, on_home=on_home,
                         menu_callbacks=menu_callbacks,
                         on_click_titulo=on_click_titulo)
        self.cores, self.fontes, self.icones = cores, fontes, icones
        self.on_voltar = on_voltar
        self.on_salvar, self.on_excluir = on_salvar, on_excluir

        self.id_cliente = None
        self._modo = "novo"
        self._enderecos = []
        self._endereco_editando_id = None
        self._criar_formulario()

    # ── Modo ────────────────────────────────────────────────────────────────────
    def definir_modo(self, modo: str):
        self._modo = modo
        titulo = "Editar Cliente" if modo == "editar" else "Cadastrar Cliente"
        self._lbl_titulo.configure(text=titulo)
        
        from app.utils.permissoes import tem_acao
        pode_excluir = modo == "editar" and tem_acao("clientes", "excluir")
        self._frame_comandos.mostrar_excluir(pode_excluir)
        if modo == "editar" and not self._endereco_visivel:
            self._tabela_pedidos_frame.pack(
                side="left", fill="both", expand=True, padx=(20, 0))
        else:
            self._tabela_pedidos_frame.pack_forget()
            
    # ── Dados ────────────────────────────────────────────────────────────────────
    def obter_dados(self) -> dict:
        """Retorna dados do formulário (endereços são gerenciados via tabela enderecos)."""
        return {
            "id":          self.id_cliente,
            "nome":        self._nome.get(),
            "telefone":    self._telefone.get(),
            "cpf":         self._cpf.get(),
            "email":       self._email.get(),
        }

    def preencher_dados(self, dados: dict):
        """Preenche formulário e carrega endereços da tabela enderecos."""
        self.id_cliente = dados.get("id_cliente") or dados.get("id")
        self._nome.set(dados.get("nome", ""))
        self._telefone.set(dados.get("telefone", ""))
        self._cpf.set(dados.get("cpf", ""))
        self._email.set(dados.get("email", ""))
        self._limpar_campos_endereco()
        # Carrega endereços
        self._enderecos = dados.get("enderecos", [])
        self._renderizar_enderecos()
        if self._enderecos and not self._endereco_visivel:
            self._toggle_endereco()
        self.definir_modo("editar")
        pedidos = dados.get("pedidos", [])
        self._tabela_pedidos.carregar(pedidos)

    # ── Ações ────────────────────────────────────────────────────────────────────
    def acao_salvar(self):
        dados = self.obter_dados()
        erro = self._validar_dados(dados)
        if erro:
            self._lbl_feedback.configure(
                text=erro, text_color=self.cores.texto.vermelho)
            return
        try:
            self.on_salvar(dados)
            self._lbl_feedback.configure(
                text="Salvo com sucesso!", text_color=self.cores.texto.verde)
            if self.on_voltar:
                self.after(300, self.on_voltar)
        except Exception as e:
            self._lbl_feedback.configure(
                text=str(e), text_color=self.cores.texto.vermelho)

    def acao_cancelar(self):
        self.limpar_formulario()
        if self.on_voltar:
            self.on_voltar()

    def acao_voltar(self):
        self.limpar_formulario()
        if self.on_voltar:
            self.on_voltar()

    def acao_excluir(self):
        if not self.on_excluir or self.id_cliente is None:
            return
        DialogoConfirmacao(
            self.winfo_toplevel(), self.cores, self.fontes,
            titulo="Excluir Cliente",
            mensagem="Tem certeza que deseja excluir este cliente? Esta ação não pode ser desfeita.",
            on_confirmar=self._confirmar_exclusao,
        )

    def _confirmar_exclusao(self):
        try:
            self.on_excluir(self.id_cliente)
            self.limpar_formulario()
            if self.on_voltar:
                self.on_voltar()
        except Exception as e:
            self._lbl_feedback.configure(
                text=str(e), text_color=self.cores.texto.vermelho)

    def limpar_formulario(self):
        self.id_cliente = None
        for campo in [self._nome, self._telefone, self._cpf, self._email]:
            campo.set("")
        self._limpar_campos_endereco()
        self._enderecos = []
        for w in self._enderecos_lista_frame.winfo_children():
            w.destroy()
        self._lbl_feedback.configure(text="")
        if self._endereco_visivel:
            self._toggle_endereco()
        self.definir_modo("novo")

    # ── Validação ────────────────────────────────────────────────────────────────
    def _validar_dados(self, dados) -> str | None:
        erros = []
        if not dados["nome"].strip():
            erros.append("• Nome é obrigatório")
        if not dados["telefone"].strip():
            erros.append("• Telefone é obrigatório")
        elif not validar_celular(dados["telefone"].strip()):
            erros.append("• Telefone inválido — use (93)99999-9999")
        if dados["cpf"].strip() and not cpf_valido(dados["cpf"].strip()):
            erros.append("• CPF inválido")
        if dados["email"].strip() and not validar_email(dados["email"].strip()):
            erros.append("• Email inválido")
        return "\n".join(erros) if erros else None

    # ── Gerenciamento de Endereços (inline) ────────────────────────────────────
    def _carregar_enderecos(self):
        """Carrega endereços do cliente do banco e renderiza a lista."""
        if not self.id_cliente:
            return
        self._enderecos = listar_enderecos(self.id_cliente)
        self._renderizar_enderecos()

    def _renderizar_enderecos(self):
        """Renderiza a lista de endereços no frame abaixo dos campos."""
        for w in self._enderecos_lista_frame.winfo_children():
            w.destroy()
        if not self._enderecos:
            ctk.CTkLabel(
                self._enderecos_lista_frame,
                text="Nenhum endereço cadastrado.",
                font=self.fontes.texto_info,
                text_color=self.cores.texto.passivo
            ).pack(pady=10)
            return
        for end in self._enderecos:
            self._criar_card_endereco(end)

    def _criar_card_endereco(self, end):
        card = ctk.CTkFrame(
            self._enderecos_lista_frame,
            fg_color=self.cores.fundo.branco,
            border_width=1,
            border_color=self.cores.card.borda_card,
            corner_radius=8,
        )
        card.pack(fill="x", pady=4)

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=10, pady=(8, 2))

        apelido = end.get("apelido") or "Sem apelido"
        principal = end.get("principal", 0)
        if principal:
            ctk.CTkLabel(
                topo, text="⭐ " + apelido,
                font=self.fontes.texto_info,
                text_color=self.cores.texto.principal
            ).pack(side="left")
            ctk.CTkLabel(
                topo, text="Principal",
                font=self.fontes.pequeno,
                text_color=self.cores.texto.verde
            ).pack(side="left", padx=(8, 0))
        else:
            ctk.CTkLabel(
                topo, text=apelido,
                font=self.fontes.texto_info,
                text_color=self.cores.texto.principal
            ).pack(side="left")

        logradouro = end.get("logradouro", "")
        numero = end.get("numero", "")
        bairro = end.get("bairro", "")
        cidade = end.get("cidade", "")
        endereco_str = f"{logradouro}, {numero} - {bairro}, {cidade}".strip(", ").strip("- ")
        if endereco_str:
            ctk.CTkLabel(
                card, text=endereco_str,
                font=self.fontes.pequeno,
                text_color=self.cores.texto.passivo
            ).pack(anchor="w", padx=10, pady=(0, 4))

        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=10, pady=(0, 8))

        if not principal:
            ctk.CTkButton(
                botoes, text="Definir Principal", height=24, corner_radius=4,
                fg_color=self.cores.fundo.cinza_claro,
                text_color=self.cores.texto.principal,
                font=self.fontes.pequeno,
                command=lambda e=end: self._definir_principal(e)
            ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            botoes, text="Editar", height=24, corner_radius=4,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.pequeno,
            command=lambda e=end: self._editar_endereco(e)
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            botoes, text="Excluir", height=24, corner_radius=4,
            fg_color=self.cores.fundo.vermelho,
            text_color=self.cores.texto.vermelho_escuro,
            font=self.fontes.pequeno,
            command=lambda e=end: self._excluir_endereco(e)
        ).pack(side="left")

    def _limpar_campos_endereco(self):
        self._cep.set("")
        self._numero.set("")
        self._logradouro.set("")
        self._bairro.set("")
        self._cidade.set("")
        self._complemento.set("")
        self._endereco_editando_id = None

    def _salvar_endereco(self):
        if not self.id_cliente:
            self._lbl_feedback.configure(
                text="Salve o cliente primeiro antes de adicionar endereços.",
                text_color=self.cores.texto.vermelho)
            return
        dados = {
            "id_cliente": self.id_cliente,
            "cep": self._cep.get().strip(),
            "logradouro": self._logradouro.get().strip(),
            "numero": self._numero.get().strip(),
            "bairro": self._bairro.get().strip(),
            "cidade": self._cidade.get().strip(),
            "complemento": self._complemento.get().strip(),
            "principal": 0,
        }
        if self._endereco_editando_id:
            dados["id_endereco"] = self._endereco_editando_id
            for end in self._enderecos:
                if end["id_endereco"] == self._endereco_editando_id:
                    dados["principal"] = end.get("principal", 0)
                    break
        salvar_endereco(dados)
        self._limpar_campos_endereco()
        self._carregar_enderecos()

    def _editar_endereco(self, end):
        self._cep.set(end.get("cep", ""))
        self._numero.set(end.get("numero", ""))
        self._logradouro.set(end.get("logradouro", ""))
        self._bairro.set(end.get("bairro", ""))
        self._cidade.set(end.get("cidade", ""))
        self._complemento.set(end.get("complemento", ""))
        self._endereco_editando_id = end.get("id_endereco")

    def _excluir_endereco(self, end):
        from app.utils.componentes import DialogoConfirmacao
        DialogoConfirmacao(
            self, self.cores, self.fontes,
            titulo="Excluir Endereço",
            mensagem=f"Excluir endereço '{end.get('apelido') or 'Sem apelido'}'?",
            on_confirmar=lambda: self._confirmar_exclusao_endereco(end["id_endereco"]),
        )

    def _confirmar_exclusao_endereco(self, id_endereco):
        excluir_endereco(id_endereco)
        self._carregar_enderecos()

    def _definir_principal(self, end):
        definir_endereco_principal(end["id_endereco"], self.id_cliente)
        self._carregar_enderecos()

    # ── Toggle endereço ──────────────────────────────────────────────────────────
    def _toggle_endereco(self):
        if self._endereco_visivel:
            self._col_dir.pack_forget()
            self._btn_endereco.configure(image=self.icones.adicionar_preto)
            self._endereco_visivel = False
            if self._modo == "editar":
                self._tabela_pedidos_frame.pack(
                    side="left", fill="both", expand=True, padx=(20, 0))
        else:
            self._tabela_pedidos_frame.pack_forget()
            self._col_dir.pack(side="left", fill="both", expand=True, padx=(20, 0))
            self._btn_endereco.configure(image=self.icones.fechar_preto)
            self._endereco_visivel = True

    # ── Layout ───────────────────────────────────────────────────────────────────
    def _criar_formulario(self):
        self._endereco_visivel = False

        conteudo = ctk.CTkFrame(self, fg_color="transparent")
        conteudo.place(relx=0.06, rely=0.12, relwidth=0.88, relheight=0.82)

        conteudo.grid_columnconfigure(0, weight=1)
        conteudo.grid_rowconfigure(0, weight=0)  # cabeçalho
        conteudo.grid_rowconfigure(1, weight=1)  # campos
        conteudo.grid_rowconfigure(2, weight=0)  # botões

        # ── Cabeçalho: voltar + título + feedback ──────────────────────────────
        cabecalho = ctk.CTkFrame(conteudo, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ctk.CTkButton(
            cabecalho, fg_color="transparent",
            image=self.icones.voltar, cursor="hand2",
            hover_color=self.cores.botao.passivo,
            text="", width=20,
            command=self.acao_voltar,
        ).pack(side="left", padx=(0, 5), pady=(5, 5))

        self._lbl_titulo = ctk.CTkLabel(
            cabecalho,
            text="Cadastrar Cliente",
            font=self.fontes.titulo_grande,
            text_color=self.cores.texto.principal,
        )
        self._lbl_titulo.pack(side="left", padx=(5, 20), pady=(5, 5))

        self._lbl_feedback = ctk.CTkLabel(
            cabecalho, text="",
            font=self.fontes.texto_info,
            text_color=self.cores.texto.vermelho,
            wraplength=500,
        )
        self._lbl_feedback.pack(side="left", pady=(5, 5))

        # ── Área de campos (duas colunas lado a lado) ──────────────────────────
        area_campos = ctk.CTkFrame(conteudo, fg_color="transparent")
        area_campos.grid(row=1, column=0, sticky="nsew")

        # Coluna esquerda: dados principais (sempre visível)
        col_esq = ctk.CTkFrame(area_campos, fg_color="transparent", width=420)
        col_esq.pack(side="left", fill="y", padx=(0, 0))
        col_esq.pack_propagate(False)

        self._nome = Campos.CampoTexto(
            col_esq, self.icones.nome, "Nome *", "Digite o nome completo", self.cores, self.fontes)
        self._nome.pack(fill="x", pady=(5, 5))
        self._nome.entry.focus()

        self._telefone = Campos.CampoTexto(
            col_esq, self.icones.descricao, "Telefone *", "Ex: (93) 9 9999-9999", self.cores, self.fontes)
        self._telefone.pack(fill="x", pady=(5, 5))
        
        self._telefone.entry.bind(
            "<KeyRelease>",
            lambda e: formatar_celular(e, self._telefone.entry)
        )
        
        self._cpf = Campos.CampoTexto(
            col_esq, self.icones.descricao, "CPF", "Ex: 000.000.000-00", self.cores, self.fontes)
        self._cpf.pack(fill="x", pady=(5, 5))

        self._cpf.entry.bind(
            "<KeyRelease>",
            lambda e: formatar_cpf(e, self._cpf.entry)
        )

        self._email = Campos.CampoTexto(
            col_esq, self.icones.descricao, "Email", "Digite o email", self.cores, self.fontes)
        self._email.pack(fill="x", pady=(5, 5))

        self._nome.entry.bind("<FocusOut>", lambda e: capitalizar_campo(e, self._nome.entry))

        # Botão toggle endereço
        self._btn_endereco = Botoes.BotaoEndereco(
            col_esq,
            self.icones, self.cores, self.fontes,
            comando=self._toggle_endereco
        )
        self._btn_endereco.pack(fill="x", pady=(15, 5), padx=(0,250))

        # Coluna direita: endereço (oculta por padrão)
        self._col_dir = ctk.CTkScrollableFrame(
            area_campos, fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=self.cores.fundo.cinza_claro,
            scrollbar_button_hover_color=self.cores.fundo.cinza_claro,
        )
        # não faz pack aqui — começa oculto

        # CEP + Número na mesma linha
        linha_cep = ctk.CTkFrame(self._col_dir, fg_color="transparent")
        linha_cep.pack(fill="x", pady=(0, 5))
        linha_cep.grid_columnconfigure(0, weight=2)
        linha_cep.grid_columnconfigure(1, weight=1)

        self._cep = Campos.CampoTexto(
            linha_cep, self.icones.descricao, "CEP", "00000-000", self.cores, self.fontes)
        self._cep.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._cep.entry.bind(
            "<KeyRelease>",
            lambda e: formatar_cep(e, self._cep.entry)
        )

        self._numero = Campos.CampoTexto(
            linha_cep, self.icones.descricao, "Número", "Nº", self.cores, self.fontes)
        self._numero.grid(row=0, column=1, sticky="ew")
        self._numero.entry.bind(
            "<KeyRelease>",
            lambda e: formatar_apenas_digitos(e, self._numero.entry)
        )

        self._logradouro = Campos.CampoTexto(
            self._col_dir, self.icones.descricao, "Logradouro", "Rua, Av., Travessa...", self.cores, self.fontes)
        self._logradouro.pack(fill="x", pady=(5, 5))

        self._bairro = Campos.CampoTexto(
            self._col_dir, self.icones.descricao, "Bairro", "Digite o bairro", self.cores, self.fontes)
        self._bairro.pack(fill="x", pady=(5, 5))
        self._bairro.entry.bind(
            "<KeyRelease>",
            lambda e: formatar_apenas_letras(e, self._bairro.entry),
        )

        self._cidade = Campos.CampoTexto(
            self._col_dir, self.icones.descricao, "Cidade", "Digite a cidade", self.cores, self.fontes)
        self._cidade.pack(fill="x", pady=(5, 5))
        self._cidade.entry.bind(
            "<KeyRelease>",
            lambda e: formatar_apenas_letras(e, self._cidade.entry),
        )

        self._complemento = Campos.CampoTexto(
            self._col_dir, self.icones.descricao, "Complemento", "Apto, bloco, referência...", self.cores, self.fontes)
        self._complemento.pack(fill="x", pady=(5, 5))

        self._logradouro.entry.bind("<FocusOut>", lambda e: capitalizar_campo(e, self._logradouro.entry))
        self._bairro.entry.bind("<FocusOut>", lambda e: capitalizar_campo(e, self._bairro.entry))
        self._cidade.entry.bind("<FocusOut>", lambda e: capitalizar_campo(e, self._cidade.entry))
        self._complemento.entry.bind("<FocusOut>", lambda e: capitalizar_campo(e, self._complemento.entry))

        # Botões Salvar / Limpar
        btn_end_frame = ctk.CTkFrame(self._col_dir, fg_color="transparent")
        btn_end_frame.pack(fill="x", pady=(10, 5))

        self._btn_salvar_endereco = ctk.CTkButton(
            btn_end_frame, text="Salvar Endereço", height=30, corner_radius=8,
            fg_color=self.cores.botao.novo,
            hover_color=self.cores.botao.novo_hover,
            text_color=self.cores.texto.branco,
            font=self.fontes.texto_info,
            command=self._salvar_endereco
        )
        self._btn_salvar_endereco.pack(side="left", padx=(0, 6))

        self._btn_limpar_endereco = ctk.CTkButton(
            btn_end_frame, text="Limpar", height=30, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            command=self._limpar_campos_endereco
        )
        self._btn_limpar_endereco.pack(side="left")

        # Separador
        ctk.CTkFrame(self._col_dir, height=1, fg_color=self.cores.card.borda_card).pack(
            fill="x", pady=(8, 5))

        # Lista de endereços salvos
        ctk.CTkLabel(
            self._col_dir, text="Endereços Salvos",
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.principal
        ).pack(anchor="w", pady=(5, 5))

        self._enderecos_lista_frame = ctk.CTkFrame(self._col_dir, fg_color="transparent")
        self._enderecos_lista_frame.pack(fill="both", expand=True)

        # ── Tabela de pedidos ──
        self._tabela_pedidos_frame = ctk.CTkFrame(area_campos, fg_color=self.cores.fundo.principal, corner_radius=50)

        ctk.CTkLabel(
            self._tabela_pedidos_frame,
            text="Pedidos do Cliente",
            font=self.fontes.subtitulo,
            text_color=self.cores.texto.verde_jambu,
        ).pack(anchor="w", pady=(5, 8), padx=(100,0))

        self._tabela_pedidos = TabelaGenerica(
            self._tabela_pedidos_frame,
            self.cores, self.fontes, self.icones,
            colunas=[
                {"titulo": "ID",        "campo": "id_pedido",  "peso": 1, "min": 60,  "limite": 6},
                {"titulo": "Origem",    "campo": "origem",     "peso": 2, "min": 100, "limite": 12, "render": Celulas.CelulaTextoSimples},
                {"titulo": "Data",      "campo": "data",       "peso": 2, "min": 100, "limite": 12, "render": Celulas.CelulaTextoSimples},
                {"titulo": "Status",    "campo": "status",     "peso": 2, "min": 100, "limite": 12, "render": Celulas.CelulaTextoSimples},
                {"titulo": "Pagamento", "campo": "pagamento",  "peso": 2, "min": 100, "limite": 12, "render": Celulas.CelulaTextoSimples},
            ],
            mostrar_busca=False,
            mostrar_filtros=False,
        )
        self._tabela_pedidos.pack(fill="both", expand=True, padx=(100,0),pady=(0,200))

        # ── Botões Salvar / Cancelar / Excluir ────────────────────────────────
        self._frame_comandos = Frames.FrameComandos(
            conteudo, self.cores, self.fontes, self.icones, modo=self._modo)
        self._frame_comandos.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        self._frame_comandos.set_callbacks(
            salvar=self.acao_salvar,
            cancelar=self.acao_cancelar,
            excluir=self.acao_excluir,
        )


if __name__ == "__main__":
    main()