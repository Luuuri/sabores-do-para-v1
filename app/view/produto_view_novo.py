import customtkinter as ctk
from tkinter import messagebox
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import (
    Frames, TabelaGenerica, Celulas, Badges,
    DialogoConfirmacao, Campos
)
from app.controller.produto_controller import ProdutoController
from app.utils.validacoes import formatar_preco
from app.utils.permissoes import tem_acao


CATEGORIAS = ["Comidas Típicas", "Sobremesas", "Bebidas", "Descartáveis", "Limpeza", "Outros"]
CATEGORIAS.sort()

UNIDADES = ["Porção", "Litro", "Kg", "Und"]


class ProdutosView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Produtos")
        self.minsize(1100, 700)
        self.after(0, lambda: self.state('zoomed'))
        self.lift()
        self.focus_force()

        self.cores = get_cores()
        self.fontes = Fontes()
        self.icones = Icones()
        self.controller = ProdutoController()

        self.configure(fg_color=self.cores.fundo.principal)

        self._telas = {"lista": None, "cad": None}
        self._mostrar_lista()
        self.protocol("WM_DELETE_WINDOW", self._voltar_painel)

    def _recarregar_tema(self):
        self.cores = get_cores()
        self.configure(fg_color=self.cores.fundo.principal)
        for widget in self.winfo_children():
            widget.destroy()
        self._telas = {"lista": None, "cad": None}
        self._mostrar_lista()

    def _voltar_painel(self):
        self.destroy()
        from app.view.tela_painel_controle import PainelControleView
        PainelControleView(self.master)

    def _abrir_clientes(self):
        self.destroy()
        from app.view.clientes_view import ClientesView
        ClientesView(self.master)

    def _abrir_estoque(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("estoque", self, None):
            return
        self.destroy()
        from app.view.estoque_view import EstoqueView
        EstoqueView(self.master)

    def _abrir_funcionarios(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("funcionarios", self, None):
            return
        self.destroy()
        from app.view.funcionarios_view import FuncionariosView
        FuncionariosView(self.master)

    def _abrir_caixa(self):
        self.destroy()
        from app.view.caixa_view import CaixaView
        CaixaView(self.master)

    def _abrir_relatorios(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("relatorios", self, None):
            return
        self.destroy()
        from app.view.relatorio_view import RelatoriosView
        RelatoriosView(self.master)

    def _abrir_delivery(self):
        self.destroy()
        from app.view.delivery_list_view import DeliveryListView
        DeliveryListView(self.master)

    def _mostrar_lista(self):
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()

        if not self._telas["lista"]:
            self._telas["lista"] = TelaProdutosLista(
                self, self.cores, self.fontes, self.icones,
                controller=self.controller,
                on_novo=self._abrir_cadastro,
                on_editar=self._abrir_cadastro,
                on_excluir=self._excluir_produto,
                on_home=self._voltar_painel,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._abrir_delivery,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._mostrar_lista,
                    "relatorios": self._abrir_relatorios,
                },
            )
        self._telas["lista"].pack(fill="both", expand=True)
        self._telas["lista"].recarregar()

    def _abrir_cadastro(self, dados=None):
        if self._telas["lista"]:
            self._telas["lista"].pack_forget()

        if not self._telas["cad"]:
            self._telas["cad"] = TelaProdutosCad(
                self, self.cores, self.fontes, self.icones,
                on_voltar=self._mostrar_lista,
                on_salvar=self._salvar_produto,
                on_excluir=self._excluir_produto,
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._abrir_delivery,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._mostrar_lista,
                    "relatorios": self._abrir_relatorios,
                },
            )
        self._telas["cad"].limpar_formulario()

        if dados:
            self._telas["cad"].preencher_dados(dados)
        else:
            self._telas["cad"].definir_modo("novo")

        self._telas["cad"].pack(fill="both", expand=True)
        self.update()

    def _salvar_produto(self, id_produto, nome, preco, categoria, descricao, unidade, ativo, foto=""):
        from app.model.erros_produto import ProdutoDuplicadoError

        status = "Ativo" if ativo else "Inativo"

        try:
            if id_produto:
                self.controller.atualizar_produto(
                    id_produto, nome, preco, categoria, descricao, unidade, status, foto
                )
            else:
                self.controller.salvar_produto(
                    nome, preco, categoria, descricao, unidade, status, foto
                )

        except ProdutoDuplicadoError as e:
            messagebox.showerror("Erro", str(e))
            return

        self._mostrar_lista()

    def _excluir_produto(self, id_produto):
        self.controller.deletar_produto(id_produto)
        self._mostrar_lista()


class TelaProdutosLista(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 controller=None, on_novo=None, on_editar=None, on_excluir=None, on_home=None,
                 menu_callbacks=None):

        super().__init__(
            master, cores, fontes, icones,
            titulo="Produtos",
            icone=icones.produtos,
            on_novo=on_novo if tem_acao("produtos", "adicionar") else None,
            on_home=on_home,
            menu_callbacks=menu_callbacks
        )

        self.cores = cores
        self.fontes = fontes
        self.icones = icones
        self.on_editar = on_editar
        self.on_excluir = on_excluir
        self.controller = controller or ProdutoController()

        self._criar_area_conteudo()

    def recarregar(self):
        dados = self.controller.listar_produtos()
        categorias = sorted(set(d["categoria"] for d in dados if d.get("categoria")))
        opcoes = [{"label": c, "valor": c} for c in categorias]

        self.tabela.atualizar_opcoes_filtro("categoria", opcoes)
        self.tabela.carregar(dados)

    def _criar_area_conteudo(self):
        frame_conteudo = Frames.FrameConteudoTabela(self.area_tela, self.cores)
        frame_conteudo.pack(expand=True, fill="both", padx=30, pady=20)

        self.tabela = TabelaGenerica(
            frame_conteudo,
            self.cores,
            self.fontes,
            self.icones,
            placeholder_busca="Produtos",
            colunas=[
                {
                    "titulo": "Produto",
                    "campo": "produto",
                    "peso": 3,
                    "min": 200,
                    "limite": 30,
                    "render": Celulas.CelulaNomeDescricao
                },
                {
                    "titulo": "Categoria",
                    "campo": "categoria",
                    "peso": 2,
                    "min": 140,
                    "limite": 18,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Preço",
                    "campo": "preco_formatado",
                    "peso": 1,
                    "min": 90,
                    "limite": 10,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Status",
                    "campo": "ativo",
                    "limite": 10,
                    "render": Celulas.CelulaStatus
                },
                {
                    "titulo": "Ações",
                    "campo": "acoes",
                    "limite": 5,
                    "align": "nw",
                    "render": Celulas.CelulaAcoes
                },
            ],
            on_editar=lambda d: self.on_editar(d),
            on_excluir=lambda id: self._acao_excluir(id),
            mostrar_busca=True,
            filtros_inline=[
                {
                    "campo": "categoria",
                    "titulo": "Categoria",
                    "opcoes": [
                        {"label": "Comidas Típicas", "valor": "Comidas Típicas"},
                        {"label": "Sobremesas", "valor": "Sobremesas"},
                        {"label": "Bebidas", "valor": "Bebidas"},
                    ]
                },
                {
                    "campo": "ativo",
                    "titulo": "Status",
                    "opcoes": [
                        {"label": "Ativo", "valor": True},
                        {"label": "Inativo", "valor": False},
                    ]
                },
            ]
        )

        self.tabela.pack(expand=True, fill="both", padx=5, pady=10)

    def _acao_excluir(self, id_produto):
        if self.on_excluir:
            self.on_excluir(id_produto)


class TelaProdutosCad(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_voltar=None, on_salvar=None, on_excluir=None, on_home=None,
                 menu_callbacks=None, on_click_titulo=None):

        super().__init__(
            master, cores, fontes, icones,
            titulo="Produtos",
            icone=icones.produtos,
            on_novo=None,
            on_home=on_home,
            menu_callbacks=menu_callbacks,
            on_click_titulo=on_click_titulo
        )

        self.cores = cores
        self.fontes = fontes
        self.icones = icones
        self.on_voltar = on_voltar
        self.on_salvar = on_salvar
        self.on_excluir = on_excluir

        self.id_produto = None
        self._modo = "novo"

        self._criar_formulario()

    def definir_modo(self, modo: str):
        self._modo = modo
        pode_excluir = modo == "editar" and tem_acao("produtos", "excluir")
        self.frame_comandos.mostrar_excluir(pode_excluir)

    def limpar_formulario(self):
        self.id_produto = None
        self._modo = "novo"

        self.lbl_titulo_form.configure(text="Novo Produto")
        self.campo_nome.set("")
        self.campo_descricao.set("")
        self.campo_preco.set("")
        self.campo_unidade.set(UNIDADES[0])
        self.campo_categoria.set(CATEGORIAS[0])
        self.campo_foto.limpar()
        self.status_var.set("Ativo")

    def preencher_dados(self, dados: dict):
        self.id_produto = dados.get("id_produto")

        self.lbl_titulo_form.configure(text="Editar Produto")
        self.campo_nome.set(dados.get("nome", ""))
        self.campo_descricao.set(dados.get("descricao", ""))
        self.campo_preco.set(str(dados.get("preco", "")))
        self.campo_unidade.set(dados.get("unidade", UNIDADES[0]))
        self.campo_categoria.set(dados.get("categoria", CATEGORIAS[0]))
        self.campo_foto.set(dados.get("foto", ""))
        self.status_var.set("Ativo" if dados.get("ativo", True) else "Inativo")

        self.definir_modo("editar")

    def _criar_formulario(self):
        conteudo = Frames.FrameConteudo(self.area_tela, self.cores)
        conteudo.pack(expand=True, fill="both", padx=20, pady=20)

        cabecalho = ctk.CTkFrame(conteudo, fg_color="transparent")
        cabecalho.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkButton(
            cabecalho,
            text="",
            image=self.icones.voltar,
            width=90,
            height=30,
            fg_color="transparent",
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.secundario,
            font=ctk.CTkFont(size=12),
            command=self.on_voltar
        ).pack(side="left")

        self.lbl_titulo_form = ctk.CTkLabel(
            cabecalho,
            text="Novo Produto",
            font=self.fontes.titulo_grande,
            text_color=self.cores.texto.principal
        )
        self.lbl_titulo_form.pack(side="left", padx=10)

        self.badge_status = Badges.Ativo(cabecalho, self.cores, self.fontes)
        self.badge_status.pack(side="left", padx=10)

        body_frame = ctk.CTkFrame(
            conteudo,
            fg_color=self.cores.fundo.branco,
            border_width=2,
            border_color=self.cores.card.borda_card,
            corner_radius=20
        )
        body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        center_container = ctk.CTkFrame(body_frame, fg_color="transparent")
        center_container.pack(expand=True, fill="both", padx=40, pady=20)

        center_container.grid_columnconfigure(0, weight=3)
        center_container.grid_columnconfigure(1, weight=2)

        form_frame = ctk.CTkFrame(
            center_container,
            fg_color=self.cores.fundo.branco
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)

        form_inner = ctk.CTkFrame(
            form_frame,
            fg_color=self.cores.fundo.branco
        )
        form_inner.pack(fill="both", expand=True, padx=20, pady=20)

        self.campo_nome = Campos.CampoTexto(
            form_inner,
            self.icones.nome,
            " Nome",
            "Nome do produto",
            self.cores,
            self.fontes
        )
        self.campo_nome.pack(fill="x", pady=6)

        self.campo_descricao = Campos.CampoTexto(
            form_inner,
            self.icones.descricao,
            " Descrição",
            "Descrição do produto",
            self.cores,
            self.fontes
        )
        self.campo_descricao.pack(fill="x", pady=6)

        self.campo_categoria = Campos.CampoOpcao(
            form_inner,
            self.icones.categoria,
            " Categoria",
            CATEGORIAS,
            self.cores,
            self.fontes
        )
        self.campo_categoria.pack(fill="x", pady=6)

        preco_unidade_frame = ctk.CTkFrame(
            form_inner,
            fg_color="transparent"
        )
        preco_unidade_frame.pack(fill="x", pady=6)

        preco_unidade_frame.grid_columnconfigure(0, weight=2)
        preco_unidade_frame.grid_columnconfigure(1, weight=1)

        self.campo_preco = Campos.CampoTexto(
            preco_unidade_frame,
            self.icones.dinheiro,
            " Preço",
            "0,00",
            self.cores,
            self.fontes,
            validacao=lambda e: formatar_preco(e, self.campo_preco.entry)
        )
        self.campo_preco.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.campo_unidade = Campos.CampoOpcao(
            preco_unidade_frame,
            self.icones.unidade,
            " Unidade",
            UNIDADES,
            self.cores,
            self.fontes
        )
        self.campo_unidade.grid(row=0, column=1, sticky="nsew")

        status_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        status_frame.pack(fill="x", pady=(10, 6))

        ctk.CTkLabel(
            status_frame,
            image=self.icones.status,
            text=" Status",
            font=self.fontes.texto_info,
            text_color=self.cores.texto.principal,
            compound="left"
        ).pack(side="left")

        self.status_var = ctk.StringVar(value="Ativo")
        self.status_var.trace_add("write", lambda *_: self._atualizar_botao_status())

        self.btn_status = ctk.CTkButton(
            status_frame,
            text="✓ Ativo",
            width=100,
            height=32,
            fg_color=self.cores.fundo.verde,
            text_color=self.cores.texto.branco,
            corner_radius=20,
            command=self._alternar_status
        )
        self.btn_status.pack(side="left", padx=10)

        foto_container = ctk.CTkFrame(
            center_container,
            fg_color="transparent"
        )
        foto_container.grid(row=0, column=1, sticky="nsew", padx=(20, 0), pady=10)

        self.campo_foto = Campos.CampoFoto(
            foto_container,
            self.cores,
            self.fontes,
            self.icones,
            tamanho_preview=(400, 400)
        )
        self.campo_foto.pack(fill="both", expand=True)

        self.frame_comandos = Frames.FrameComandos(
            conteudo,
            self.cores,
            self.fontes,
            self.icones,
            modo=self._modo
        )
        self.frame_comandos.pack(fill="x", padx=40, pady=20)

        self.frame_comandos.set_callbacks(
            salvar=self._salvar,
            cancelar=self.on_voltar,
            excluir=self._excluir,
        )

    def _alternar_status(self):
        atual = self.status_var.get()

        if atual == "Ativo":
            self.status_var.set("Inativo")
        else:
            self.status_var.set("Ativo")

    def _atualizar_botao_status(self):
        if self.status_var.get() == "Ativo":
            self.btn_status.configure(
                text="✓ Ativo",
                fg_color=self.cores.fundo.verde
            )
            self.badge_status.configure(
                text="● ATIVO",
                fg_color=self.cores.badge.status_ativo,
                text_color=self.cores.texto.verde_escuro
            )
        else:
            self.btn_status.configure(
                text="✗ Inativo",
                fg_color=self.cores.fundo.vermelho
            )
            self.badge_status.configure(
                text="● INATIVO",
                fg_color=self.cores.badge.status_inativo,
                text_color=self.cores.texto.vermelho_escuro
            )

    def _excluir(self):
        if self.id_produto and self.on_excluir:
            DialogoConfirmacao(
                self.winfo_toplevel(),
                self.cores,
                self.fontes,
                titulo="Confirmar Exclusão",
                mensagem="Deseja realmente excluir este produto?",
                on_confirmar=lambda: self.on_excluir(self.id_produto)
            )

    def _salvar(self):
        nome = self.campo_nome.get().strip()
        descricao = self.campo_descricao.get().strip()
        categoria = self.campo_categoria.get()
        preco = self.campo_preco.get().strip().replace(",", ".")
        unidade = self.campo_unidade.get()
        status = self.status_var.get()
        foto = self.campo_foto.get()

        if not nome:
            messagebox.showerror("Erro", "Preencha o nome do produto.")
            return

        if not preco:
            messagebox.showerror("Erro", "Preencha o preço do produto.")
            return

        try:
            float(preco)

        except ValueError:
            messagebox.showerror("Erro", "Preço inválido. Use apenas números.")
            return

        ativo = status == "Ativo"

        if self.on_salvar:
            self.on_salvar(
                self.id_produto,
                nome,
                preco,
                categoria,
                descricao,
                unidade,
                ativo,
                foto
            )


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()

    ProdutosView(root)

    root.mainloop()