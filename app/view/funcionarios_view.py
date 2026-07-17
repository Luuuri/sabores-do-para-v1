import customtkinter as ctk
from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import Frames, TabelaGenerica, Celulas
from app.controller.funcionario_controller import (
    listar_funcionarios,
    excluir_funcionario,
    salvar_funcionario,
)


class FuncionariosView(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        def _voltar():
            self.destroy() 
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)
            
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("funcionarios", self, _voltar):
            return
        
        self.title("Funcionários")
        self.minsize(1100, 700)
        self.after(0, lambda: self.state('zoomed'))
        self.lift()
        self.focus_force()

        self.cores   = get_cores()
        self.fontes  = Fontes()
        self.icones  = Icones()

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

    def _mostrar_lista(self):
        if self._telas["cad"]:
            self._telas["cad"].pack_forget()
        if not self._telas["lista"]:
            self._telas["lista"] = TelaFuncionariosLista(
                self, self.cores, self.fontes, self.icones,
                on_novo=self._abrir_cadastro,
                on_editar=self._abrir_cadastro,
                on_excluir=excluir_funcionario,
                on_home=self._voltar_painel,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._abrir_delivery,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._mostrar_lista,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                }
            )
        self._telas["lista"].pack(fill="both", expand=True)
        self._telas["lista"].recarregar()

    def _abrir_cadastro(self, dados=None):
        from app.view.tela_funcionarios_cad import TelaFuncionarios
        if self._telas["lista"]:
            self._telas["lista"].pack_forget()
        if not self._telas["cad"]:
            self._telas["cad"] = TelaFuncionarios(
                self, self.cores, self.fontes, self.icones,
                on_voltar=self._mostrar_lista,
                on_salvar=salvar_funcionario,
                on_excluir=excluir_funcionario,
                on_home=self._voltar_painel,
                on_click_titulo=self._mostrar_lista,
                menu_callbacks={
                    "caixa": self._abrir_caixa,
                    "delivery": self._abrir_delivery,
                    "clientes": self._abrir_clientes,
                    "estoque": self._abrir_estoque,
                    "funcionarios": self._mostrar_lista,
                    "produtos": self._abrir_produtos,
                    "relatorios": self._abrir_relatorios,
                },
                show_password_button=True,
                mostrar_senha_no_editar=True,
            )
        self._telas["cad"].limpar_formulario()
        if dados:
            self._telas["cad"].preencher_dados(dados)
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

    def _abrir_clientes(self):
        from app.view.clientes_view import ClientesView
        self._navegar(ClientesView)

    def _abrir_estoque(self):
        from app.view.estoque_view import EstoqueView
        self._navegar(EstoqueView)

    def _abrir_produtos(self):
        from app.view.produto_view_novo import ProdutosView
        self._navegar(ProdutosView)

    def _abrir_relatorios(self):
        from app.view.relatorio_view import RelatoriosView
        self._navegar(RelatoriosView)

    def _abrir_delivery(self):
        from app.view.delivery_list_view import DeliveryListView
        self._navegar(DeliveryListView)


class TelaFuncionariosLista(Frames.FrameLayoutPadrao):
    def __init__(self, master, cores, fontes, icones,
                 on_novo=None, on_editar=None, on_excluir=None, on_home=None, menu_callbacks=None):
        super().__init__(master, cores, fontes, icones,
                         titulo="Funcionários", icone=icones.funcionarios,
                         on_novo=on_novo, on_home=on_home, menu_callbacks=menu_callbacks)
        self.cores, self.fontes, self.icones = cores, fontes, icones
        self.on_editar  = on_editar
        self.on_excluir = on_excluir
        self._criar_area_conteudo()

    def recarregar(self):
        dados = listar_funcionarios()
        cargos = sorted(set(d["cargo"] for d in dados if d.get("cargo")))
        self.tabela.atualizar_opcoes_filtro("cargo", [
            {"label": c, "valor": c} for c in cargos
        ])
        self.tabela.carregar(dados)

    def _criar_area_conteudo(self):
        frame_conteudo = Frames.FrameConteudoTabela(self.area_tela, self.cores)
        frame_conteudo.pack(expand=True, fill="both", padx=30, pady=20)

        self.tabela = TabelaGenerica(
            frame_conteudo,
            self.cores,
            self.fontes,
            self.icones,
            placeholder_busca="Funcionários",
            colunas=[
                {"titulo": "Nome",   "campo": "nome",  "peso": 3, "min": 180, "limite": 25, "render": Celulas.CelulaTextoSimples},
                {"titulo": "Email",  "campo": "email", "peso": 4, "min": 260, "limite": 35, "render": Celulas.CelulaTextoSimples},
                {"titulo": "Telefone","campo": "telefone", "peso": 2, "min": 140, "limite": 20, "render": Celulas.CelulaTextoSimples},
                {"titulo": "Cargo",  "campo": "cargo", "peso": 2, "min": 140, "limite": 15, "render": Celulas.CelulaTextoSimples},
                {"titulo": "Entregador", "campo": "is_entregador", "peso": 1, "min": 100, "limite": 12, "render": Celulas.CelulaEntregador},
                {"titulo": "Status", "campo": "ativo", "limite": 10, "render": Celulas.CelulaStatus},
                {"titulo": "Ações",  "campo": "acoes", "limite": 5,  "align": "nw", "render": Celulas.CelulaAcoes},
            ],
            on_editar=lambda d: self.on_editar(d),
            on_excluir=lambda id: self._acao_excluir(id),
            mostrar_busca=True,
            filtros_inline=[
                {
                    "campo": "cargo",
                    "titulo": "Cargo",
                    "opcoes": [],
                },
                {
                    "campo": "is_entregador",
                    "titulo": "Entregador",
                    "opcoes": [
                        {"label": "Sim", "valor": True},
                        {"label": "Não", "valor": False},
                    ]
                },
                {
                    "campo": "ativo",
                    "titulo": "Status",
                    "opcoes": [
                        {"label": "Ativo",   "valor": True},
                        {"label": "Inativo", "valor": False},
                    ]
                },
            ]
        )
        self.tabela.pack(expand=True, fill="both", padx=5, pady=10)

    def _acao_excluir(self, id_funcionario):
        if self.on_excluir:
            self.on_excluir(id_funcionario)
        self.recarregar()
        
if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()  # esconde a janela principal

    FuncionariosView(root)

    root.mainloop()

