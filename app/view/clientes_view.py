import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import Frames, TabelaGenerica, Celulas
from app.controller.cliente_controller import (
    listar_clientes,
    excluir_cliente,
    salvar_cliente,
)


class ClientesView(ctk.CTkToplevel):
    def __init__(self, master, on_selecionar=None):
        super().__init__(master)
        self.title("Clientes")
        self.after(0, lambda: self.state('zoomed'))
        self.minsize(1100, 700)
        self.lift()
        self.focus_force()

        self.cores = get_cores()
        self.fontes = Fontes()
        self.icones = Icones()
        self._on_selecionar = on_selecionar

        self._telas = {"lista": None, "cad": None}
        self._mostrar_lista()
        if on_selecionar:
            self.protocol("WM_DELETE_WINDOW", self.destroy)
        else:
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

    def _mostrar_lista(self):
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()
        if not self._telas["lista"]:
            self._telas["lista"] = TelaClientesLista(
                self, self.cores, self.fontes, self.icones,
                on_novo=self._abrir_cadastro if not self._on_selecionar else None,
                on_editar=self._abrir_cadastro if not self._on_selecionar else None,
                on_excluir=excluir_cliente if not self._on_selecionar else None,
                on_home=self._voltar_painel if not self._on_selecionar else None,
                on_selecionar=self._on_selecionar,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._abrir_delivery,
                    "clientes": self._mostrar_lista,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                }
            )
        self._telas["lista"].pack(fill="both", expand=True)
        self._telas["lista"].recarregar()

    def _abrir_cadastro(self, dados=None):
        from app.view.clientes_cad_view import TelaClientesCad
        from app.controller.cliente_controller import buscar_cliente
        if self._telas["lista"]:
            self._telas["lista"].pack_forget()
        if not self._telas["cad"]:
            self._telas["cad"] = TelaClientesCad(
                self, self.cores, self.fontes, self.icones,
                on_voltar=self._mostrar_lista,
                on_salvar=salvar_cliente,
                on_excluir=excluir_cliente,
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._abrir_delivery,
                    "clientes": self._mostrar_lista,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._abrir_funcionarios,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                }
            )
        self._telas["cad"].limpar_formulario()
        if dados:
            id_cliente = dados.get("id_cliente") or dados.get("id")
            dados_completos = buscar_cliente(id_cliente) or dados
            self._telas["cad"].preencher_dados(dados_completos)
        else:
            self._telas["cad"].definir_modo("novo")
        self._telas["cad"].pack(fill="both", expand=True)
        self.update()

    def _navegar(self, view_class):
        self.destroy()
        view_class(self.master)

    def _abrir_caixa(self):
        from app.view.caixa_view import CaixaView
        self._navegar(CaixaView)

    def _abrir_estoque(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("estoque", self, None):
            return
        from app.view.estoque_view import EstoqueView
        self._navegar(EstoqueView)

    def _abrir_funcionarios(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("funcionarios", self, None):
            return
        from app.view.funcionarios_view import FuncionariosView
        self._navegar(FuncionariosView)

    def _abrir_produtos(self):
        from app.view.produto_view_novo import ProdutosView
        self._navegar(ProdutosView)

    def _abrir_relatorios(self):
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("relatorios", self, None):
            return
        from app.view.relatorio_view import RelatoriosView
        self._navegar(RelatoriosView)

    def _abrir_delivery(self):
        from app.view.delivery_list_view import DeliveryListView
        self._navegar(DeliveryListView)


class TelaClientesLista(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_novo=None, on_editar=None, on_excluir=None, on_home=None,
                 on_selecionar=None, menu_callbacks=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Clientes", icone=icones.clientes,
                         on_novo=on_novo, on_home=on_home,
                         menu_callbacks=menu_callbacks)
        self.cores, self.fontes, self.icones = cores, fontes, icones
        self.on_editar, self.on_excluir = on_editar, on_excluir
        self._on_selecionar = on_selecionar
        self._criar_area_conteudo()
        if on_selecionar:
            self._adicionar_botao_cancelar()

    def _adicionar_botao_cancelar(self):
        btn = ctk.CTkButton(
            self.area_tela,
            text="Cancelar", height=32, corner_radius=8,
            fg_color=self.cores.fundo.cinza_claro,
            text_color=self.cores.texto.principal,
            font=self.fontes.texto_info,
            command=self._cancelar_selecao
        )
        btn.pack(anchor="ne", padx=30, pady=(0, 10))

    def _cancelar_selecao(self):
        self.winfo_toplevel().destroy()

    def _selecionar_cliente(self, dados):
        if self._on_selecionar:
            self._on_selecionar(dados)
            self.winfo_toplevel().destroy()

    def recarregar(self):
        dados = listar_clientes()
        self._atualizar_filtros_dinamicos(dados)
        self.tabela.carregar(dados)

    def _atualizar_filtros_dinamicos(self, dados: list):
        cidades = sorted({
            d.get("cidade", "").strip()
            for d in dados
            if d.get("cidade", "").strip()
        })
        bairros = sorted({
            d.get("bairro", "").strip()
            for d in dados
            if d.get("bairro", "").strip()
        })

        self.tabela.atualizar_opcoes_filtro("cidade", [
            {"label": c, "valor": c} for c in cidades
        ])
        self.tabela.atualizar_opcoes_filtro("bairro", [
            {"label": b, "valor": b} for b in bairros
        ])

    def _criar_area_conteudo(self):
        frame_conteudo = Frames.FrameConteudoTabela(self.area_tela, self.cores)
        frame_conteudo.pack(expand=True, fill="both", padx=30, pady=20)

        if self._on_selecionar:
            col_acoes = {
                "titulo": "Selecionar",
                "campo": "acoes",
                "limite": 5,
                "align": "nw",
                "render": Celulas.CelulaAcoes
            }
            on_editar = lambda d: self._selecionar_cliente(d)
            on_excluir = None
        else:
            col_acoes = {
                "titulo": "Ações",
                "campo": "acoes",
                "limite": 5,
                "align": "nw",
                "render": Celulas.CelulaAcoes
            }
            on_editar = lambda d: self.on_editar(d) if self.on_editar else None
            on_excluir = lambda id: self._acao_excluir(id)

        self.tabela = TabelaGenerica(
            frame_conteudo,
            self.cores,
            self.fontes,
            self.icones,
            placeholder_busca="Clientes",
            colunas=[
                {
                    "titulo": "ID",
                    "campo": "id_cliente",
                    "peso": 1,
                    "min": 60,
                    "limite": 6,
                    "render": Celulas.CelulaID
                },
                {
                    "titulo": "Nome",
                    "campo": "nome",
                    "peso": 3,
                    "min": 180,
                    "limite": 25,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Telefone",
                    "campo": "telefone",
                    "peso": 2,
                    "min": 150,
                    "limite": 20,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Bairro",
                    "campo": "bairro",
                    "peso": 2,
                    "min": 140,
                    "limite": 20,
                    "render": Celulas.CelulaTextoSimples
                },
                {
                    "titulo": "Nº Pedidos",
                    "campo": "total_pedidos",
                    "peso": 1,
                    "min": 100,
                    "limite": 8,
                    "render": Celulas.CelulaTextoSimples
                },
                col_acoes,
            ],
            on_editar=on_editar,
            on_excluir=on_excluir,
            mostrar_busca=True,
            filtros_inline=[
                {"campo": "cidade", "titulo": "Cidade", "opcoes": []},
                {"campo": "bairro", "titulo": "Bairro", "opcoes": []},
            ],
        )
        self.tabela.pack(expand=True, fill="both", padx=5, pady=10)

    def _acao_excluir(self, id_cliente):
        if self.on_excluir:
            self.on_excluir(id_cliente)
        self.recarregar()


