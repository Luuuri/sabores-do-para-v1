import os
import customtkinter as ctk
from tkinter import messagebox
from app.utils.estilos import Cores, Fontes, Icones
from app.utils.componentes import Frames
from app.controller.pdf_relatorio_controller import (
    buscar_dados_balanco_estoque,
    buscar_dados_estoque_minimo,
)
from app.utils.pdf_generator import (
    gerar_pdf_balanco_estoque,
    gerar_pdf_estoque_minimo,
)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..","utils", "assets", "logo.png")

class TelaRelatorios:

    def __init__(self):

        self.root = ctk.CTk()
        self.root.title("Relatórios")
        self.root.geometry("1200x700")

        self.cores = Cores()
        self.fontes = Fontes()
        self.icones = Icones()

        self.root.configure(fg_color=self.cores.fundo.principal)

        self.relatorio_atual = "menu"

        self.criar_area_principal()
        self.mostrar_menu_relatorios()

        self.root.mainloop()

    # =====================================================
    # TOPO
    # =====================================================

    def criar_topo(self):

        self.topo = ctk.CTkFrame(
            self.root,
            fg_color="#F5EFE6",
            height=80
        )
        self.topo.pack(fill="x", padx=30, pady=(20, 10))

        self.titulo = ctk.CTkLabel(
            self.topo,
            text="📈 Relatórios",
            font=("Arial", 28, "bold"),
            text_color="#1C2526"
        )
        self.titulo.pack(side="left")

        self.btn_salvar = ctk.CTkButton(
            self.topo,
            text="Salvar",
            fg_color="#C0392B",
            hover_color="#A93226",
            text_color="white",
            width=120,
            height=35,
            command=self.salvar_relatorio
        )
        self.btn_salvar.pack(side="right")

    # =====================================================
    # ÁREA PRINCIPAL
    # =====================================================

    def criar_area_principal(self):

        self.area_principal = Frames.FrameLayoutPadrao(
            self.root, self.cores, self.fontes, self.icones,
            titulo="Relatórios",
            icone=self.icones.relatorios,
        )
        self.area_principal.pack(fill="both", expand=True, padx=30, pady=20)

    def limpar_area(self):

        for widget in self.area_principal.area_tela.winfo_children():
            widget.destroy()

    # =====================================================
    # MENU PRINCIPAL DE RELATÓRIOS
    # =====================================================

    def mostrar_menu_relatorios(self):

        self.limpar_area()
        self.relatorio_atual = "menu"

        container = ctk.CTkFrame(
            self.area_principal.area_tela,
            fg_color="#FDFAF6"
        )
        container.pack(fill="both", expand=True, padx=30, pady=30)

        coluna_esquerda = ctk.CTkFrame(container, fg_color="#FDFAF6")
        coluna_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 15))

        coluna_direita = ctk.CTkFrame(container, fg_color="#FDFAF6")
        coluna_direita.pack(side="right", fill="both", expand=True, padx=(15, 0))

        self.criar_titulo_secao(coluna_esquerda, "Comercial")

        self.criar_botao_menu(coluna_esquerda, "Evolução de Vendas", "📈", self.mostrar_evolucao_vendas)
        self.criar_botao_menu(coluna_esquerda, "Extrato de Vendas", "📋", self.mostrar_extrato_vendas)
        self.criar_botao_menu(coluna_esquerda, "Taxa de Serviço", "💰", self.mostrar_taxa_servico)
        self.criar_botao_menu(coluna_esquerda, "Deliveries Finalizados", "🛵", self.mostrar_deliveries)
        self.criar_botao_menu(coluna_esquerda, "Vendas por Produtos", "🍽️", self.mostrar_venda_produto)

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

    # =====================================================
    # COMPONENTES PADRÃO
    # =====================================================

    def criar_titulo_secao(self, pai, texto):

        label = ctk.CTkLabel(
            pai,
            text=texto,
            font=("Arial", 18, "bold"),
            text_color="#1C2526",
            anchor="w"
        )
        label.pack(fill="x", pady=(10, 8))

    def criar_botao_menu(self, pai, texto, icone, comando):

        botao = ctk.CTkButton(
            pai,
            text=f"{icone}  {texto}",
            height=45,
            fg_color="#E8DDD0",
            hover_color="#C0392B",
            text_color="#1C2526",
            anchor="w",
            corner_radius=8,
            font=("Arial", 14, "bold"),
            command=comando
        )
        botao.pack(fill="x", pady=5)

    def criar_cabecalho_tela(self, titulo, icone):

        cabecalho = ctk.CTkFrame(
            self.area_principal.area_tela,
            fg_color="#FDFAF6"
        )
        cabecalho.pack(fill="x", padx=30, pady=(25, 10))

        btn_voltar = ctk.CTkButton(
            cabecalho,
            text="← Voltar",
            width=90,
            height=32,
            fg_color="#E8DDD0",
            hover_color="#C0392B",
            text_color="#1C2526",
            command=self.mostrar_menu_relatorios
        )
        btn_voltar.pack(side="left", padx=(0, 15))

        label = ctk.CTkLabel(
            cabecalho,
            text=f"{icone} {titulo}",
            font=("Arial", 22, "bold"),
            text_color="#1C2526"
        )
        label.pack(side="left")

    def criar_abas_periodo(self, pai, ativo="Hoje"):

        frame = ctk.CTkFrame(pai, fg_color="#FDFAF6")
        frame.pack(fill="x", pady=(5, 20))

        periodos = ["Hoje", "7 D", "1 M", "6 M", "1 A"]

        for periodo in periodos:

            cor = "#C0392B" if periodo == ativo else "#FDFAF6"
            texto = "white" if periodo == ativo else "#7A6A5A"

            botao = ctk.CTkButton(
                frame,
                text=periodo,
                width=70,
                height=30,
                fg_color=cor,
                hover_color="#C0392B",
                text_color=texto,
                border_width=1,
                border_color="#D4A97A"
            )
            botao.pack(side="left", padx=4)

    def criar_tela_relatorio(self, titulo, icone, periodo_ativo, texto_area, campos):

        self.limpar_area()

        self.criar_cabecalho_tela(titulo, icone)

        conteudo = ctk.CTkFrame(
            self.area_principal.area_tela,
            fg_color="#FDFAF6"
        )
        conteudo.pack(fill="both", expand=True, padx=30, pady=10)

        self.criar_abas_periodo(conteudo, periodo_ativo)

        area_esquerda = ctk.CTkFrame(
            conteudo,
            fg_color="#E8DDD0",
            corner_radius=12
        )
        area_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 15))

        label_area = ctk.CTkLabel(
            area_esquerda,
            text=texto_area,
            font=("Arial", 20, "bold"),
            text_color="#7A6A5A"
        )
        label_area.pack(expand=True)

        painel_filtros = ctk.CTkFrame(
            conteudo,
            width=300,
            fg_color="#E8DDD0",
            corner_radius=12
        )
        painel_filtros.pack(side="right", fill="y", padx=(15, 0))
        painel_filtros.pack_propagate(False)
        
        self._ultimo_painel_filtros = painel_filtros  # ← guarda referência

        titulo_filtro = ctk.CTkLabel(
            painel_filtros,
            text="FILTROS",
            font=("Arial", 14, "bold"),
            text_color="#7A6A5A"
        )
        titulo_filtro.pack(anchor="w", padx=20, pady=(20, 15))

        for campo in campos:
            self.criar_campo_filtro(painel_filtros, campo)

        btn_filtrar = ctk.CTkButton(
            painel_filtros,
            text="Filtrar",
            height=38,
            fg_color="#C0392B",
            hover_color="#A93226",
            text_color="white",
            command=lambda: messagebox.showinfo("Filtro", "Relatório filtrado com sucesso!")
        )
        btn_filtrar.pack(fill="x", padx=20, pady=20)

    def criar_campo_filtro(self, pai, texto):

        label = ctk.CTkLabel(
            pai,
            text=texto,
            font=("Arial", 12, "bold"),
            text_color="#7A6A5A",
            anchor="w"
        )
        label.pack(fill="x", padx=20, pady=(8, 4))

        entrada = ctk.CTkEntry(
            pai,
            height=35,
            fg_color="#FDFAF6",
            border_color="#D4A97A",
            text_color="#1C2526"
        )
        entrada.pack(fill="x", padx=20)

    # =====================================================
    # TELAS DOS RELATÓRIOS
    # =====================================================

    def mostrar_extrato_vendas(self):

        self.criar_tela_relatorio(
            titulo="Extrato de Vendas",
            icone="📋",
            periodo_ativo="Hoje",
            texto_area="📊 Área do Relatório",
            campos=[
                "Período — Início",
                "Período — Final",
                "Tipo de Venda"
            ]
        )

    def mostrar_evolucao_vendas(self):

        self.criar_tela_relatorio(
            titulo="Evolução de Vendas",
            icone="📈",
            periodo_ativo="7 D",
            texto_area="📉 Gráfico de Evolução",
            campos=[
                "Período — Início",
                "Período — Final",
                "Hora Inicial",
                "Hora Final"
            ]
        )

    def mostrar_taxa_servico(self):

        self.criar_tela_relatorio(
            titulo="Taxa de Serviço",
            icone="💰",
            periodo_ativo="1 M",
            texto_area="🧾 Área do Relatório",
            campos=[
                "Período — Início",
                "Período — Final"
            ]
        )

    def mostrar_deliveries(self):

        self.criar_tela_relatorio(
            titulo="Deliveries Finalizados",
            icone="🛵",
            periodo_ativo="7 D",
            texto_area="🗺️ Área do Relatório",
            campos=[
                "Período — Início",
                "Período — Final",
                "Cliente",
                "Entregador"
            ]
        )

    def mostrar_venda_produto(self):

        self.criar_tela_relatorio(
            titulo="Venda por Produto",
            icone="🍽️",
            periodo_ativo="1 M",
            texto_area="🏆 Ranking de Produtos",
            campos=[
                "Período — Início",
                "Período — Final",
                "Ordenação",
                "Produto"
            ]
        )

    def mostrar_balanco_estoque(self):
        self.criar_tela_relatorio(
            titulo="Balanço de Estoque",
            icone="📦",
            periodo_ativo="6 M",
            texto_area="📦 Extrato de Estoque",
            campos=[
                "Período — Início",
                "Período — Final",
                "Produto"
            ]
        )
        # Botão PDF adicionado ao painel de filtros
        ctk.CTkButton(
            self._ultimo_painel_filtros,
            text="📄  Gerar PDF",
            height=42,
            fg_color="#D95C02",
            hover_color="#BF4F00",
            text_color="white",
            font=("Arial", 13, "bold"),
            corner_radius=8,
            command=self._gerar_pdf_balanco
        ).pack(fill="x", padx=20, pady=(0, 20))
        
        
    def mostrar_estoque_minimo(self):
        self.criar_tela_relatorio(
            titulo="Estoque Mínimo",
            icone="⚠️",
            periodo_ativo="Hoje",
            texto_area="⚠️ Produtos com Estoque Mínimo",
            campos=[
                "Produto",
                "Categoria"
            ]
        )
        # Botão PDF adicionado ao painel de filtros
        ctk.CTkButton(
            self._ultimo_painel_filtros,
            text="📄  Gerar PDF",
            height=42,
            fg_color="#D95C02",
            hover_color="#BF4F00",
            text_color="white",
            font=("Arial", 13, "bold"),
            corner_radius=8,
            command=self._gerar_pdf_estoque_minimo
        ).pack(fill="x", padx=20, pady=(0, 20))

    def mostrar_totais_caixa(self):

        self.criar_tela_relatorio(
            titulo="Totais em Caixa",
            icone="🧾",
            periodo_ativo="Hoje",
            texto_area="🧾 Fechamentos, Sangrias e Suprimentos",
            campos=[
                "Período — Início",
                "Período — Final",
                "Operador"
            ]
        )

    def mostrar_formas_pagamento(self):

        self.criar_tela_relatorio(
            titulo="Totais por Forma de Pagamento",
            icone="💳",
            periodo_ativo="Hoje",
            texto_area="💳 Dinheiro, PIX, Cartão e Outros",
            campos=[
                "Período — Início",
                "Período — Final",
                "Forma de Pagamento"
            ]
        )
        
    def _gerar_pdf_balanco(self):
        try:
            dados = buscar_dados_balanco_estoque()
            gerar_pdf_balanco_estoque(dados, logo_path=LOGO_PATH)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar o PDF:\n{e}")

    def _gerar_pdf_estoque_minimo(self):
        try:
            dados = buscar_dados_estoque_minimo()
            gerar_pdf_estoque_minimo(dados, logo_path=LOGO_PATH)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar o PDF:\n{e}")    

    # =====================================================
    # AÇÕES
    # =====================================================

    def salvar_relatorio(self):

        messagebox.showinfo(
            "Salvar",
            "Relatório salvo com sucesso!"
        )


if __name__ == "__main__":
    TelaRelatorios()