import os
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox
from app.utils.graficos import renderizar_grafico, criar_grafico_vazio, criar_grafico_barras, criar_grafico_linha, criar_grafico_pizza

from app.utils.estilos import get_cores, Fontes, Icones
from app.utils.componentes import Frames

from app.controller.relatorio_controller import (
    carregar_balanco_estoque,
    carregar_estoque_minimo,
    carregar_extrato_vendas,
    carregar_evolucao_vendas,
    carregar_taxa_servico,
    carregar_deliveries,
    carregar_vendas_produto,
    carregar_totais_caixa,
    carregar_formas_pagamento,
)

from app.controller.pdf_relatorio_controller import (
    buscar_dados_balanco_estoque,
    buscar_dados_estoque_minimo,
)


LOGO_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "utils",
    "assets",
    "logo.png"
)


class RelatoriosView(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)
        
        def _voltar():
            self.destroy()
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)
            
        from app.utils.permissoes import bloquear_se_sem_acesso
        if bloquear_se_sem_acesso("relatorios", self, _voltar):
            return

        self.title("Sabores do Pará")
        self.minsize(800, 500)
        self.after(0, lambda: self.state("zoomed"))
        self.lift()
        self.focus_force()

        self.cores = get_cores()
        fontes = Fontes()
        icones = Icones()

        self.configure(
            fg_color=self.cores.fundo.principal
        )

        def voltar_painel():

            self.destroy()

            from app.view.tela_painel_controle import PainelControleView

            PainelControleView(self.master)

        TelaRelatorios(
            self,
            self.cores,
            fontes,
            icones,
            on_home=voltar_painel
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            voltar_painel
        )

    def _recarregar_tema(self):
        self.cores = get_cores()
        self.configure(fg_color=self.cores.fundo.principal)
        for widget in self.winfo_children():
            widget.destroy()
        from app.utils.estilos import Fontes, Icones
        fontes = Fontes()
        icones = Icones()

        def voltar_painel():
            self.destroy()
            from app.view.tela_painel_controle import PainelControleView
            PainelControleView(self.master)

        TelaRelatorios(self, self.cores, fontes, icones, on_home=voltar_painel)
        self.protocol("WM_DELETE_WINDOW", voltar_painel)


class TelaRelatorios:

    def __init__(self, root, cores, fontes, icones, on_home=None):

        self.root = root
        self.cores = cores
        self.fontes = fontes
        self.icones = icones
        self.on_home = on_home

        self.relatorio_atual = "menu"

        self._filtros_entries = {}
        self._on_filtrar = None

        self._periodo_ativo = None
        self._botoes_periodo = {}

        self._ultimo_tipo_relatorio = None
        self._ultimo_renderizar = None
        self._ultimo_on_filtrar = None

        self.layout = Frames.FrameLayoutPadrao(
            root,
            cores,
            fontes,
            icones,
            titulo="Relatórios",
            icone=icones.relatorios,
            on_home=on_home,
            on_click_titulo=self._reiniciar,
            menu_callbacks={
                "caixa": self._abrir_caixa,
                "delivery": self._abrir_delivery,
                "clientes": self._abrir_clientes,
                "estoque": self._abrir_estoque,
                "funcionarios": self._abrir_funcionarios,
                "produtos": self._abrir_produtos,
                "relatorios": self._reiniciar,
            }
        )

        self.layout.pack(
            expand=True,
            fill="both"
        )

        self.mostrar_menu_relatorios()

    def _reiniciar(self):

        self.mostrar_menu_relatorios()

    def _abrir_clientes(self):

        self.root.destroy()

        from app.view.clientes_view import ClientesView

        ClientesView(self.root.master)

    def _abrir_estoque(self):

        self.root.destroy()

        from app.view.estoque_view import EstoqueView

        EstoqueView(self.root.master)

    def _abrir_funcionarios(self):

        self.root.destroy()

        from app.view.funcionarios_view import FuncionariosView

        FuncionariosView(self.root.master)

    def _abrir_caixa(self):

        self.root.destroy()

        from app.view.caixa_view import CaixaView

        CaixaView(self.root.master)

    def _abrir_produtos(self):

        self.root.destroy()

        from app.view.produto_view_novo import ProdutosView

        ProdutosView(self.root.master)

    def _abrir_delivery(self):

        self.root.destroy()

        from app.view.delivery_list_view import DeliveryListView

        DeliveryListView(self.root.master)

    def limpar_area(self):

        for widget in self.layout.area_tela.winfo_children():
            widget.destroy()

    def mostrar_menu_relatorios(self):

        self.limpar_area()

        self.relatorio_atual = "menu"

        container = ctk.CTkFrame(
            self.layout.area_tela,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        coluna_esquerda = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        coluna_esquerda.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 15),
            anchor="n"
        )

        coluna_direita = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        coluna_direita.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(15, 0),
            anchor="n"
        )

        self.criar_titulo_secao(coluna_esquerda, "Comercial")

        self.criar_botao_menu(
            coluna_esquerda,
            "Evolução de Vendas",
            "📈",
            self.mostrar_evolucao_vendas
        )

        self.criar_botao_menu(
            coluna_esquerda,
            "Extrato de Vendas",
            "📋",
            self.mostrar_extrato_vendas
        )

        self.criar_botao_menu(
            coluna_esquerda,
            "Taxa de Serviço",
            "💰",
            self.mostrar_taxa_servico
        )

        self.criar_botao_menu(
            coluna_esquerda,
            "Deliveries Finalizados",
            "🛵",
            self.mostrar_deliveries
        )

        self.criar_botao_menu(
            coluna_esquerda,
            "Vendas por Produtos",
            "🍽️",
            self.mostrar_venda_produto
        )

        self.criar_titulo_secao(coluna_direita, "Operações de Caixa")

        self.criar_botao_menu(
            coluna_direita,
            "Totais em Caixa",
            "🧾",
            self.mostrar_totais_caixa
        )

        self.criar_botao_menu(
            coluna_direita,
            "Totais por Forma de Pagamento",
            "💳",
            self.mostrar_formas_pagamento
        )

        self.criar_titulo_secao(coluna_direita, "Estoque")

        self.criar_botao_menu(
            coluna_direita,
            "Balanço de Estoque",
            "📦",
            self.mostrar_balanco_estoque
        )

        self.criar_botao_menu(
            coluna_direita,
            "Estoque Mínimo",
            "⚠️",
            self.mostrar_estoque_minimo
        )

    def criar_titulo_secao(self, pai, texto):

        ctk.CTkLabel(
            pai,
            text=texto,
            font=("Arial", 22, "bold"),
            text_color=self.cores.texto.verde_jambu,
            anchor="w"
        ).pack(
            fill="x",
            pady=(10, 8)
        )

    def criar_botao_menu(self, pai, texto, icone, comando):

        ctk.CTkButton(
            pai,
            text=f"{icone}  {texto}",
            height=80,
            fg_color=self.cores.entry.formulario,
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            anchor="w",
            corner_radius=10,
            font=("Arial", 18),
            command=comando
        ).pack(
            fill="x",
            pady=18
        )

    def criar_cabecalho_tela(self, titulo, icone):

        cabecalho = ctk.CTkFrame(
            self.layout.area_tela,
            fg_color="transparent"
        )

        cabecalho.pack(
            fill="x",
            padx=30,
            pady=(25, 10)
        )

        ctk.CTkButton(
            cabecalho,
            text="← Voltar",
            width=90,
            height=32,
            fg_color="transparent",
            hover_color=self.cores.botao.hover,
            text_color=self.cores.texto.principal,
            command=self.mostrar_menu_relatorios
        ).pack(
            side="left",
            padx=(0, 15)
        )

        ctk.CTkLabel(
            cabecalho,
            text=f"{icone} {titulo}",
            font=("Arial", 22, "bold"),
            text_color=self.cores.texto.principal
        ).pack(
            side="left"
        )

    def _aplicar_periodo(self, periodo):

        hoje = datetime.now()

        map_periodo = {
            "Hoje": (hoje, hoje),
            "7 D": (hoje - timedelta(days=7), hoje),
            "1 M": (hoje - timedelta(days=30), hoje),
            "6 M": (hoje - timedelta(days=180), hoje),
            "1 A": (hoje - timedelta(days=365), hoje),
        }

        data_ini, data_fim = map_periodo.get(periodo, (hoje, hoje))

        inicio_str = data_ini.strftime("%d/%m/%Y")
        fim_str = data_fim.strftime("%d/%m/%Y")

        for label, entry in self._filtros_entries.items():

            if "Início" in label:
                entry.delete(0, "end")
                entry.insert(0, inicio_str)

            elif "Final" in label:
                entry.delete(0, "end")
                entry.insert(0, fim_str)

    def _on_mudar_periodo(self, periodo):

        if periodo not in {"Hoje", "7 D", "1 M", "6 M", "1 A"}:
            return

        self._periodo_ativo = periodo

        self._aplicar_periodo(periodo)

        cor_ativo = self.cores.texto.laranja
        cor_inativo_bg = "transparent"

        texto_ativo = self.cores.texto.branco
        texto_inativo = self.cores.texto.passivo

        for p, btn in self._botoes_periodo.items():

            eh_ativo = p == periodo

            btn.configure(
                fg_color=cor_ativo if eh_ativo else cor_inativo_bg,
                text_color=texto_ativo if eh_ativo else texto_inativo,
            )

        if self._ultimo_on_filtrar:
            self._ultimo_on_filtrar()

    def criar_abas_periodo(self, pai, ativo="Hoje"):

        frame = ctk.CTkFrame(
            pai,
            fg_color="transparent"
        )

        frame.pack(
            fill="x",
            pady=(5, 20)
        )

        self._periodo_ativo = ativo
        self._botoes_periodo = {}

        cor_ativo = self.cores.texto.laranja
        cor_hover = self.cores.texto.laranja_HOVER
        cor_borda = self.cores.botao.borda

        cor_inativo_bg = "transparent"
        cor_inativo_txt = self.cores.texto.passivo

        for periodo in ["Hoje", "7 D", "1 M", "6 M", "1 A"]:

            eh_ativo = periodo == ativo

            cor = cor_ativo if eh_ativo else cor_inativo_bg
            texto = self.cores.texto.branco if eh_ativo else cor_inativo_txt

            btn = ctk.CTkButton(
                frame,
                text=periodo,
                width=70,
                height=30,
                fg_color=cor,
                hover_color=cor_hover,
                text_color=texto,
                border_width=1,
                border_color=cor_borda,
                command=lambda p=periodo: self._on_mudar_periodo(p),
            )

            btn.pack(
                side="left",
                padx=4
            )

            self._botoes_periodo[periodo] = btn

    def _criar_area_resultado(self, pai):

        frame = ctk.CTkFrame(
            pai,
            fg_color="transparent",
            corner_radius=12
        )

        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15)
        )

        self._area_resultado = ctk.CTkTextbox(
            frame,
            fg_color=self.cores.fundo.principal,
            text_color=self.cores.texto.principal,
            corner_radius=8,
            wrap="word"
        )

        self._area_resultado.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        return frame

    # =====================================================
    # ALTERAÇÃO FEITA AQUI
    # CAMPOS COM EXEMPLO / PLACEHOLDER
    # =====================================================

    def _definir_placeholder(self, campo):
        nome = campo if isinstance(campo, str) else campo.get("nome", "")

        if "Período" in nome and "Início" in nome:
            return "Ex: 19/06/2026 00:00"

        if "Período" in nome and "Final" in nome:
            return "Ex: 19/06/2026 23:59"

        if "Hora Inicial" in nome:
            return "Ex: 0 horas"

        if "Hora Final" in nome:
            return "Ex: 23 horas"

        if "Cliente" in nome:
            return "Ex: Maria"

        if "Entregador" in nome:
            return "Ex: João"

        if "Ordenação" in nome:
            return "Ex: Valor, quantidade ou descrição"

        if "Produto" in nome:
            return "Ex: Tambaqui assado"

        if "Categoria" in nome:
            return "Ex: Bebidas, Peixes ou Entradas"

        if "Operador" in nome:
            return "Ex: Milene"

        if "Forma de Pagamento" in nome:
            return "Ex: Pix, dinheiro ou cartão"

        return f"Digite {nome.lower()}"

    def _criar_painel_filtros(self, pai, campos, on_filtrar=None):

        painel_filtros = ctk.CTkFrame(
            pai,
            width=300,
            fg_color="transparent",
            corner_radius=12
        )

        painel_filtros.pack(
            side="right",
            fill="y",
            padx=(15, 0)
        )

        painel_filtros.pack_propagate(False)

        ctk.CTkLabel(
            painel_filtros,
            text="FILTROS",
            font=("Arial", 14, "bold"),
            text_color=self.cores.texto.passivo
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        entries = {}

        for campo in campos:
            nome_campo = campo if isinstance(campo, str) else campo.get("nome", "")
            tipo_campo = campo.get("tipo", "entry") if isinstance(campo, dict) else "entry"

            ctk.CTkLabel(
                painel_filtros,
                text=nome_campo,
                font=("Arial", 12, "bold"),
                text_color=self.cores.texto.passivo,
                anchor="w"
            ).pack(
                fill="x",
                padx=20,
                pady=(8, 4)
            )

            if tipo_campo == "segmented":
                opcoes = campo.get("opcoes", ["Sim", "Não"])
                widget = ctk.CTkSegmentedButton(
                    painel_filtros,
                    values=opcoes,
                    height=34,
                    corner_radius=8,
                    selected_color=self.cores.botao.novo,
                    selected_hover_color=self.cores.botao.novo_hover,
                    unselected_color=self.cores.fundo.cinza_claro,
                    unselected_hover_color=self.cores.botao.hover,
                    text_color=self.cores.texto.principal,
                    font=("Arial", 12),
                )
                widget.set(opcoes[0])
                widget.pack(fill="x", padx=20)
            else:
                placeholder = self._definir_placeholder(campo)
                widget = ctk.CTkEntry(
                    painel_filtros,
                    height=42,
                    fg_color=self.cores.entry.formulario,
                    border_color=self.cores.card.borda_card,
                    text_color=self.cores.texto.principal,
                    placeholder_text=placeholder,
                    placeholder_text_color=self.cores.texto.passivo,
                    corner_radius=8
                )
                widget.pack(fill="x", padx=20)

            entries[nome_campo] = widget

        btn_filtrar = ctk.CTkButton(
            painel_filtros,
            text="Filtrar",
            height=38,
            fg_color=self.cores.botao.excluir,
            hover_color=self.cores.botao.primario_hover,
            text_color=self.cores.texto.branco,
            command=on_filtrar or (lambda: None)
        )

        btn_filtrar.pack(
            fill="x",
            padx=20,
            pady=20
        )

        return painel_filtros, entries

    def _get_filtro_valor(self, nome_campo):

        entry = self._filtros_entries.get(nome_campo)

        return entry.get().strip() if entry else ""

    def _exibir_dados(self, dados, titulo="Resultado"):

        self._area_resultado.delete("1.0", "end")

        if not dados:
            self._area_resultado.insert("1.0", "Nenhum registro encontrado.")
            return

        if isinstance(dados, dict):

            linhas = []

            resumo = dados.get("resumo")

            if resumo:

                linhas.append("═ RESUMO ═══════════════════════════════")
                linhas.append(f"  Total pago:      R$ {float(resumo.get('total_pago', 0)):.2f}")
                linhas.append(f"  Total pendente:  R$ {float(resumo.get('total_pendente', 0)):.2f}")
                linhas.append(f"  Total cancelado: R$ {float(resumo.get('total_cancelado', 0)):.2f}")
                linhas.append(f"  Transações:      {resumo.get('total_transacoes', 0)}")

            detalhes = dados.get("detalhes")

            if detalhes:

                linhas.append("")
                linhas.append("═ DETALHES ═════════════════════════════")

                for item in detalhes:

                    data = item.get("data_pagamento", "")
                    tipo = item.get("tipo_de_pagamento", "")
                    valor = float(item.get("valor", 0))
                    status = item.get("status_pagamento", "")

                    linhas.append(f"  {data}  {tipo:<12} R$ {valor:>8.2f}  {status}")

            self._area_resultado.insert(
                "1.0",
                "\n".join(linhas) if linhas else "Sem dados."
            )

            return

        cabecalho = list(dados[0].keys())

        linhas = [cabecalho]

        for item in dados:
            linhas.append([str(item.get(col, "")) for col in cabecalho])

        col_larg = max(len(str(v)) for linha in linhas for v in linha) + 2

        separador = "-" * (col_larg * len(cabecalho) + len(cabecalho) + 1)

        texto = []

        texto.append(separador)
        texto.append("| " + " | ".join(h.ljust(col_larg) for h in cabecalho) + " |")
        texto.append(separador)

        for linha in linhas[1:]:
            texto.append("| " + " | ".join(v.ljust(col_larg) for v in linha) + " |")

        texto.append(separador)

        self._area_resultado.insert(
            "1.0",
            "\n".join(texto)
        )

    def _tela_relatorio_generica(
        self,
        titulo,
        icone,
        periodo_ativo,
        campos,
        on_filtrar,
        on_pdf=None
    ):

        self.limpar_area()

        self.criar_cabecalho_tela(titulo, icone)

        conteudo = ctk.CTkFrame(
            self.layout.area_tela,
            fg_color="transparent"
        )

        conteudo.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        self.criar_abas_periodo(
            conteudo,
            periodo_ativo
        )

        self._criar_area_resultado(conteudo)

        painel, self._filtros_entries = self._criar_painel_filtros(
            conteudo,
            campos,
            on_filtrar
        )

        self._ultimo_tipo_relatorio = "texto"
        self._ultimo_on_filtrar = on_filtrar

        if on_pdf:

            ctk.CTkButton(
                painel,
                text="📄  Gerar PDF",
                height=42,
                fg_color=self.cores.fundo.laranja,
                hover_color=self.cores.botao.novo_hover,
                text_color=self.cores.texto.branco,
                font=("Arial", 13, "bold"),
                corner_radius=8,
                command=on_pdf
            ).pack(
                fill="x",
                padx=20,
                pady=(0, 20)
            )

    def _tela_relatorio_grafico(
        self,
        titulo,
        icone,
        periodo_ativo,
        campos,
        on_filtrar,
        on_renderizar,
        on_pdf=None
    ):

        self.limpar_area()

        self.criar_cabecalho_tela(
            titulo,
            icone
        )

        conteudo = ctk.CTkFrame(
            self.layout.area_tela,
            fg_color="transparent"
        )

        conteudo.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        self.criar_abas_periodo(
            conteudo,
            periodo_ativo
        )

        self._area_grafico = ctk.CTkFrame(
            conteudo,
            fg_color="transparent",
            corner_radius=12
        )

        self._area_grafico.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15)
        )

        def filtrar_e_renderizar():

            if on_filtrar:
                on_filtrar()

            if on_renderizar:
                on_renderizar(self._area_grafico)

        painel, self._filtros_entries = self._criar_painel_filtros(
            conteudo,
            campos,
            on_filtrar=filtrar_e_renderizar
        )

        self._ultimo_tipo_relatorio = "grafico"
        self._ultimo_on_filtrar = filtrar_e_renderizar
        self._ultimo_renderizar = None

        if on_pdf:

            ctk.CTkButton(
                painel,
                text="📄  Gerar PDF",
                height=42,
                fg_color=self.cores.fundo.laranja,
                hover_color=self.cores.botao.novo_hover,
                text_color=self.cores.texto.branco,
                font=("Arial", 13, "bold"),
                corner_radius=8,
                command=on_pdf
            ).pack(
                fill="x",
                padx=20,
                pady=(0, 20)
            )

        if on_renderizar:
            on_renderizar(self._area_grafico)

    def mostrar_extrato_vendas(self):

        def filtrar():
            tipo = self._get_filtro_valor("Tipo de Venda")
            if tipo == "Todos":
                tipo = None

            dados = carregar_extrato_vendas(
                self._get_filtro_valor("Período — Início"),
                self._get_filtro_valor("Período — Final"),
                tipo,
            )

            self._exibir_dados(
                dados,
                "Extrato de Vendas"
            )

        self._tela_relatorio_generica(
            "Extrato de Vendas",
            "📋",
            "Hoje",
            [
                "Período — Início",
                "Período — Final",
                {"nome": "Tipo de Venda", "tipo": "segmented", "opcoes": ["Todos", "Presencial", "Delivery"]},
            ],
            on_filtrar=filtrar
        )

    def mostrar_taxa_servico(self):

        def filtrar():

            dados = carregar_taxa_servico(
                self._get_filtro_valor("Período — Início"),
                self._get_filtro_valor("Período — Final"),
            )

            self._exibir_dados(
                dados,
                "Taxa de Serviço"
            )

        self._tela_relatorio_generica(
            "Taxa de Serviço",
            "💰",
            "1 M",
            [
                "Período — Início",
                "Período — Final"
            ],
            on_filtrar=filtrar
        )

    def mostrar_deliveries(self):

        def filtrar():

            dados = carregar_deliveries(
                self._get_filtro_valor("Período — Início"),
                self._get_filtro_valor("Período — Final"),
                self._get_filtro_valor("Cliente") or None,
            )

            self._exibir_dados(
                dados,
                "Deliveries Finalizados"
            )

        self._tela_relatorio_generica(
            "Deliveries Finalizados",
            "🛵",
            "7 D",
            [
                "Período — Início",
                "Período — Final",
                "Cliente",
            ],
            on_filtrar=filtrar
        )

    def mostrar_venda_produto(self):

        def filtrar():

            dados = carregar_vendas_produto()

            self._exibir_dados(
                dados,
                "Vendas por Produto"
            )

        self._tela_relatorio_generica(
            "Venda por Produto",
            "🍽️",
            "1 M",
            [
                "Período — Início",
                "Período — Final",
                "Ordenação",
                "Produto"
            ],
            on_filtrar=filtrar
        )

    def mostrar_estoque_minimo(self):

        def filtrar():
            renderizar(self._area_grafico)

        def renderizar(frame):
            dados = carregar_estoque_minimo(
                self._get_filtro_valor("Produto") or None,
                self._get_filtro_valor("Categoria") or None,
            )
            if dados:
                labels = [d["nome"] for d in dados]
                values = [float(d["quantidade"]) for d in dados]
                fig = criar_grafico_barras(self.cores,
                    labels, values,
                    "Estoque Mínimo — Produtos Abaixo do Limite",
                    xlabel="Produtos", ylabel="Quantidade Atual"
                )
            else:
                fig = criar_grafico_vazio(self.cores,
                    "Nenhum produto abaixo do estoque mínimo"
                )
            renderizar_grafico(frame, fig)

        self._tela_relatorio_grafico(
            "Estoque Mínimo", "⚠️", "Hoje",
            ["Produto", "Categoria"],
            on_filtrar=filtrar,
            on_renderizar=renderizar,
            on_pdf=self._gerar_pdf_estoque_minimo
        )

    def mostrar_balanco_estoque(self):

        def filtrar():

            pass

        def renderizar(frame):

            dados = carregar_balanco_estoque(
                self._get_filtro_valor("Produto") or None,
            )

            if dados:

                labels = [d["nome"] for d in dados]
                values = [float(d["quantidade"]) for d in dados]

                fig = criar_grafico_linha(self.cores, 
                    labels,
                    values,
                    "Balanço de Estoque",
                    xlabel="Produtos",
                    ylabel="Quantidade"
                )

            else:

                fig = criar_grafico_vazio(self.cores, )

            renderizar_grafico(
                frame,
                fig
            )

        self._tela_relatorio_grafico(
            "Balanço de Estoque",
            "📦",
            "6 M",
            [
                "Período — Início",
                "Período — Final",
                "Produto"
            ],
            on_filtrar=filtrar,
            on_renderizar=renderizar,
            on_pdf=self._gerar_pdf_balanco
        )

    def mostrar_evolucao_vendas(self):

        def filtrar():

            pass

        def renderizar(frame):

            dados = carregar_evolucao_vendas(
                self._get_filtro_valor("Período — Início"),
                self._get_filtro_valor("Período — Final"),
            )

            if dados:

                labels = [str(d["data"]) for d in dados]
                values = [float(d["total_vendas"]) for d in dados]

                fig = criar_grafico_linha(self.cores, 
                    labels,
                    values,
                    "Evolução de Vendas",
                    xlabel="Data",
                    ylabel="Total de Vendas (R$)"
                )

            else:

                fig = criar_grafico_vazio(self.cores, )

            renderizar_grafico(
                frame,
                fig
            )

        self._tela_relatorio_grafico(
            "Evolução de Vendas",
            "📈",
            "7 D",
            [
                "Período — Início",
                "Período — Final",
                "Hora Inicial",
                "Hora Final"
            ],
            on_filtrar=filtrar,
            on_renderizar=renderizar
        )

    def mostrar_totais_caixa(self):

        def filtrar():

            pass

        def renderizar(frame):

            dados = carregar_totais_caixa(
                self._get_filtro_valor("Período — Início"),
                self._get_filtro_valor("Período — Final"),
            )

            resumo = dados.get("resumo")

            if resumo:

                labels = [
                    "Pago",
                    "Pendente",
                    "Cancelado"
                ]

                values = [
                    float(resumo.get("total_pago", 0)),
                    float(resumo.get("total_pendente", 0)),
                    float(resumo.get("total_cancelado", 0)),
                ]

                fig = criar_grafico_barras(self.cores, 
                    labels,
                    values,
                    "Totais em Caixa por Status",
                    ylabel="Valor (R$)"
                )

            else:

                fig = criar_grafico_vazio(self.cores, )

            renderizar_grafico(
                frame,
                fig
            )

        self._tela_relatorio_grafico(
            "Totais em Caixa",
            "🧾",
            "Hoje",
            [
                "Período — Início",
                "Período — Final",
                "Operador"
            ],
            on_filtrar=filtrar,
            on_renderizar=renderizar
        )

    def mostrar_formas_pagamento(self):

        def filtrar():

            pass

        def renderizar(frame):

            dados = carregar_formas_pagamento(
                self._get_filtro_valor("Período — Início"),
                self._get_filtro_valor("Período — Final"),
            )

            if dados:

                labels = [d["tipo_de_pagamento"] for d in dados]
                values = [float(d["total"]) for d in dados]

                fig = criar_grafico_pizza(self.cores, 
                    labels,
                    values,
                    "Vendas por Forma de Pagamento"
                )

            else:

                fig = criar_grafico_vazio(self.cores, )

            renderizar_grafico(
                frame,
                fig
            )

        self._tela_relatorio_grafico(
            "Totais por Forma de Pagamento",
            "💳",
            "Hoje",
            [
                "Período — Início",
                "Período — Final",
                "Forma de Pagamento"
            ],
            on_filtrar=filtrar,
            on_renderizar=renderizar
        )

    def _gerar_pdf_balanco(self):

        try:

            from app.utils.pdf_generator import gerar_pdf_balanco_estoque

            dados = buscar_dados_balanco_estoque()

            gerar_pdf_balanco_estoque(
                dados,
                logo_path=LOGO_PATH
            )

        except Exception as e:

            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar o PDF:\n{e}"
            )

    def _gerar_pdf_estoque_minimo(self):

        try:

            from app.utils.pdf_generator import gerar_pdf_estoque_minimo

            dados = buscar_dados_estoque_minimo()

            gerar_pdf_estoque_minimo(
                dados,
                logo_path=LOGO_PATH
            )

        except Exception as e:

            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar o PDF:\n{e}"
            )


if __name__ == "__main__":

    TelaRelatorios(
        ctk.CTk(),
        get_cores(),
        Fontes(),
        Icones()
    )

