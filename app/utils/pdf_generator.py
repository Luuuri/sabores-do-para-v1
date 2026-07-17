# pdf_generator.py - Gerador de PDFs para relatórios
import os
from datetime import datetime
from tkinter import filedialog, messagebox

from app.utils.usuario_atual import usuario_atual

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)


# ── Cores do sistema
COR_LARANJA    = colors.HexColor("#D95C02")
COR_BEGE       = colors.HexColor("#faf6f0")
COR_BEGE_CARD  = colors.HexColor("#E8DDD0")
COR_BORDA      = colors.HexColor("#e1bfb3")
COR_TEXTO      = colors.HexColor("#2c2015")
COR_PASSIVO    = colors.HexColor("#7a6a58")
COR_VERMELHO   = colors.HexColor("#eb5757")
COR_VERDE      = colors.HexColor("#47d481")
COR_AMARELO    = colors.HexColor("#ffbd59")
COR_BRANCO     = colors.white


# ── Estilos de texto
def _estilo_titulo():
    return ParagraphStyle(
        "Titulo",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=COR_TEXTO,
        spaceAfter=4,
    )

def _estilo_subtitulo():
    return ParagraphStyle(
        "Subtitulo",
        fontName="Helvetica",
        fontSize=11,
        textColor=COR_PASSIVO,
        spaceBefore=8,
        spaceAfter=16,
    )

def _estilo_rodape():
    return ParagraphStyle(
        "Rodape",
        fontName="Helvetica",
        fontSize=9,
        textColor=COR_PASSIVO,
    )


# ── Cabeçalho do PDF
def _criar_cabecalho(titulo: str, subtitulo: str, logo_path: str = None) -> list:
    elementos = []

    # Logo + título lado a lado
    
    #agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=2*cm, height=2*cm)
        dados_topo = [[
            logo,
            Paragraph(f"<b>{titulo}</b>", _estilo_titulo()),
            
            #Paragraph(f"Gerado em: {agora}", _estilo_rodape()),
        ]]
        tabela_topo = Table(dados_topo, colWidths=[2.5*cm, 10.5*cm, 5*cm])
        tabela_topo.setStyle(TableStyle([
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",       (2, 0), (2, 0),   "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elementos.append(tabela_topo)
    else:
        dados_topo = [[
            Paragraph(f"<b>{titulo}</b>", _estilo_titulo()),
            
            #Paragraph(f"Gerado em: {agora}", _estilo_rodape())
        ]]
        tabela_topo = Table(dados_topo, colWidths=[13*cm, 5.5*cm])
        tabela_topo.setStyle(TableStyle([
            ("VALIGN",      (0, 0), (-1, -1), "BOTTOM"),
            ("ALIGN",       (1, 0), (1, 0),   "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),]))
        elementos.append(tabela_topo)
        elementos.append(Paragraph(subtitulo, _estilo_subtitulo()))



    # Linha separadora
    linha = Table([[""]], colWidths=[19*cm])
    linha.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1, COR_BORDA),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elementos.append(linha)
    elementos.append(Spacer(1, 0.4*cm))

    return elementos

def _criar_rodape(usuario: str = "") -> list:
    elementos = []
    elementos.append(Spacer(1, 0.5*cm))
    
    # Linha separadora
    linha = Table([[""]], colWidths=[19*cm])
    linha.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 1, COR_BORDA),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elementos.append(linha)
    
    # Texto do rodapé com usuário e data
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Linha 1 — quem gerou e quando
    elementos.append(Paragraph(
        f"Gerado por: {usuario}  |  {agora}",
        ParagraphStyle("R2", fontName="Helvetica", fontSize=8,
                       textColor=COR_PASSIVO, alignment=1, spaceBefore=6)
    ))
    
    # Linha 2 — nome do sistema
    elementos.append(Paragraph(
        "2026 Sabores do Pará · Sistema de Gestão",
        ParagraphStyle("R1", fontName="Helvetica-Bold", fontSize=9,
                       textColor=COR_PASSIVO, alignment=1, spaceBefore=2)
    ))
    return elementos


# ── Tabela de dados
def _criar_tabela_estoque(dados: list, colunas: list, larguras: list) -> Table:
    # Cabeçalho
    cabecalho = [Paragraph(f"<b>{col}</b>", ParagraphStyle(
        "Cab", fontName="Helvetica-Bold", fontSize=10,
        textColor=COR_BRANCO, alignment=1
    )) for col in colunas]

    linhas = [cabecalho]
    for i, item in enumerate(dados):
        cor_linha = COR_BEGE if i % 2 == 0 else COR_BRANCO
        linha = []
        for campo in item.values():
            linha.append(Paragraph(str(campo), ParagraphStyle(
                "Cel", fontName="Helvetica", fontSize=9,
                textColor=COR_TEXTO
            )))
        linhas.append(linha)

    tabela = Table(linhas, colWidths=larguras, repeatRows=1)
    tabela.setStyle(TableStyle([
        # Cabeçalho
        ("BACKGROUND",    (0, 0), (-1, 0),  COR_LARANJA),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [COR_BEGE, COR_BRANCO]),
        ("GRID",          (0, 0), (-1, -1), 0.5, COR_BORDA),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tabela

# ── Gráfico de barras horizontais em ReportLab
def _criar_grafico_barras(dados: list, titulo: str) -> Table:
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    from reportlab.graphics import renderPDF

    if not dados:
        return Spacer(1, 0.1*cm)

    largura_total = 500
    margem_esq    = 120
    margem_dir    = 60
    margem_topo   = 50
    margem_baixo  = 15
    largura_graf  = largura_total - margem_esq - margem_dir

    n = len(dados)
    altura_linha = 22
    espaco_barra = altura_linha * 0.6
    altura_graf  = n * altura_linha
    altura_total = altura_graf + margem_topo + margem_baixo

    max_qtd = max((item["quantidade"] for item in dados), default=1)
    if max_qtd == 0:
        max_qtd = 1

    d = Drawing(largura_total, altura_total)

    # Título (alinhado à esquerda, mesmo início das barras)
    from reportlab.pdfbase.pdfmetrics import stringWidth
    fonte_titulo = "Helvetica-Bold"
    tamanho_titulo = 11
    largura_titulo = stringWidth(titulo, fonte_titulo, tamanho_titulo)

    d.add(String(margem_esq, altura_total - 18, titulo,
                 textAnchor="start", fontSize=tamanho_titulo, fontName=fonte_titulo,
                 fillColor=COR_TEXTO))

    # Eixo Y (vertical, à esquerda da área do gráfico)
    base_y = margem_baixo
    topo_y = margem_baixo + altura_graf

    # Eixo X (horizontal, embaixo)
    d.add(Line(margem_esq, base_y, margem_esq + largura_graf, base_y,
               strokeColor=COR_BORDA, strokeWidth=1))

    # Barras (uma por produto, de cima para baixo)
    for i, item in enumerate(dados):
        qtd     = item.get("quantidade", 0)
        qtd_min = item.get("quantidade_minima", 0)
        nome    = item.get("nome", "")[:18]

        y = topo_y - (i + 1) * altura_linha + (altura_linha - espaco_barra) / 2
        largura_barra = (qtd / max_qtd) * largura_graf

        # Cor da barra baseada no status
        if qtd <= qtd_min:
            cor = colors.HexColor("#eb5757")   # vermelho — crítico
        elif qtd <= qtd_min * 1.5:
            cor = colors.HexColor("#ffbd59")   # amarelo — atenção
        else:
            cor = colors.HexColor("#47d481")   # verde — ok

        d.add(Rect(margem_esq, y, max(largura_barra, 2), espaco_barra,
                   fillColor=cor, strokeColor=None))

        # Nome do produto (à esquerda do eixo)
        d.add(String(margem_esq - 8, y + espaco_barra / 2 - 3, nome,
                     textAnchor="end", fontSize=7, fontName="Helvetica",
                     fillColor=COR_PASSIVO))

        # Valor ao final da barra
        d.add(String(margem_esq + largura_barra + 5, y + espaco_barra / 2 - 3, str(qtd),
                     textAnchor="start", fontSize=7, fontName="Helvetica-Bold",
                     fillColor=COR_TEXTO))

    # Legenda)
    largura_legenda = 3 * 56  # 3 itens, ~56pt cada
    espaco_minimo = 60
    cabe_na_mesma_linha = (margem_esq + largura_titulo + espaco_minimo + largura_legenda) <= largura_total

    if cabe_na_mesma_linha:
        legenda_x = largura_total - margem_dir - largura_legenda
        legenda_y = altura_total - 20
    else:
        legenda_x = margem_esq
        legenda_y = altura_total - 34

    for cor, texto in [
        (colors.HexColor("#47d481"), "OK"),
        (colors.HexColor("#ffbd59"), "Atenção"),
        (colors.HexColor("#eb5757"), "Crítico"),
    ]:
        d.add(Rect(legenda_x, legenda_y, 9, 9, fillColor=cor, strokeColor=None))
        d.add(String(legenda_x + 13, legenda_y, texto,
                     fontSize=7.5, fontName="Helvetica", fillColor=COR_PASSIVO))
        legenda_x += 56
        
    # Linha de base (eixo zero) — desenhada por cima das barras para garantir alinhamento visual nítido
    d.add(Line(margem_esq, base_y - 3, margem_esq, topo_y + 3,
               strokeColor=colors.HexColor("#999999"), strokeWidth=1.2))    

    tabela = Table([[d]], colWidths=[18.5*cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_BRANCO),
        ("BOX",        (0, 0), (-1, -1), 1, COR_BORDA),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tabela


# ── Funções públicas
def gerar_pdf_balanco_estoque(dados: list, logo_path: str = None):
    """
    Gera PDF do Balanço de Estoque.
    Abre diálogo para o usuário escolher onde salvar.
    """
    
    data = datetime.now().strftime("%d_%m_%y")
    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"balanco_estoque_{data}.pdf",
        title="Salvar Balanço de Estoque"
    )
    if not caminho:
        return

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        leftMargin=1*cm, rightMargin=1*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    elementos = _criar_cabecalho(
        titulo="Balanço de Estoque",
        subtitulo=f"Total de itens: {len(dados)}",
        logo_path=logo_path
    )

    # Gráfico
    elementos.append(Spacer(1, 0.3*cm))
    
    def _urgencia(item):
        qtd = item["quantidade"]
        qtd_min = item.get("quantidade_minima", 0) or 0
        if qtd_min == 0:
            return (1, qtd)
        razao = qtd / qtd_min
        return (0, razao)
    dados_grafico = sorted(dados, key=lambda item: item["quantidade"])[:20]
    elementos.append(_criar_grafico_barras(dados_grafico, "Quantidade em Estoque por Produto"))
    elementos.append(Spacer(1, 0.5*cm))

    # Tabela
    dados_tabela = [
        {
            "Nome":      item["nome"],
            "Categoria": item["categoria"],
            "Qtd":       item["quantidade"],
            "Mínimo":    item["quantidade_minima"],
            "Unidade":   item["unidade"],
            "Status":    "Crítico" if item["quantidade"] <= item["quantidade_minima"]
                         else "Atenção" if item["quantidade"] <= item["quantidade_minima"] * 1.5
                         else "OK",
        }
        for item in dados
    ]

    colunas   = ["Nome", "Categoria", "Qtd", "Mínimo", "Unidade", "Status"]
    larguras  = [5*cm, 3.5*cm, 2*cm, 2*cm, 2*cm, 2.5*cm]

    elementos.append(_criar_tabela_estoque(dados_tabela, colunas, larguras))
    
    
    elementos += _criar_rodape(usuario=usuario_atual.get("nome",""))  # ← adiciona rodapé

    doc.build(elementos)
    messagebox.showinfo("PDF Gerado", f"Arquivo salvo em:\n{caminho}")
    os.startfile(caminho)


def gerar_pdf_estoque_minimo(dados: list, logo_path: str = None):
    """
    Gera PDF dos produtos abaixo do estoque mínimo.
    """
    data = datetime.now().strftime("%d_%m_%y")
    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"estoque_minimo_{data}.pdf",
        title="Salvar Estoque Mínimo"
    )
    if not caminho:
        return

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        leftMargin=1*cm, rightMargin=1*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    elementos = _criar_cabecalho(
        titulo="Estoque Mínimo",
        subtitulo=f"Produtos abaixo do mínimo: {len(dados)}",
        logo_path=logo_path
    )

    if not dados:
        elementos.append(Paragraph(
            "Nenhum produto abaixo do estoque mínimo.",
            ParagraphStyle("Ok", fontName="Helvetica", fontSize=12,
                           textColor=COR_VERDE, spaceAfter=12)
        ))
    else:
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(_criar_grafico_barras(dados, "Produtos em Situação Crítica"))
        elementos.append(Spacer(1, 0.5*cm))

        dados_tabela = [
            {
                "Nome":      item["nome"],
                "Categoria": item["categoria"],
                "Qtd Atual": item["quantidade"],
                "Qtd Mín":   item["quantidade_minima"],
                "Unidade":   item["unidade"],
                "Faltam":    max(0, item["quantidade_minima"] - item["quantidade"]),
            }
            for item in dados
        ]

        colunas  = ["Nome", "Categoria", "Qtd Atual", "Qtd Mín", "Unidade", "Faltam"]
        larguras = [5*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm]

        elementos.append(_criar_tabela_estoque(dados_tabela, colunas, larguras))
    
    elementos += _criar_rodape(usuario=usuario_atual.get("nome", ""))  # ← adiciona rodapé
    doc.build(elementos)
    messagebox.showinfo("PDF Gerado", f"Arquivo salvo em:\n{caminho}")
    os.startfile(caminho)


def gerar_pdf_comprovante(dados_pedido: dict, pagamentos: list, logo_path: str = None):
    """
    Gera PDF do comprovante de pagamento de um pedido (layout estreito, estilo recibo).
    """
    LARGURA = 10 * cm

    data = datetime.now().strftime("%d_%m_%y")
    id_pedido = dados_pedido.get("id_pedido", 0)
    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"comprovante_pedido_{id_pedido:03d}_{data}.pdf",
        title="Salvar Comprovante"
    )
    if not caminho:
        return

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        leftMargin=5.5*cm, rightMargin=5.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    elementos = []

    # ── Cabeçalho (estilo recibo)
    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*cm, height=1.5*cm)
        dados_logo = [[logo, Paragraph(
            "<b>Comprovante de Pagamento</b>",
            ParagraphStyle("TitRecibo", fontName="Helvetica-Bold", fontSize=13,
                           textColor=COR_TEXTO)
        )]]
        tabela_logo = Table(dados_logo, colWidths=[2*cm, 8*cm])
        tabela_logo.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elementos.append(tabela_logo)
    else:
        elementos.append(Paragraph(
            "<b>Comprovante de Pagamento</b>",
            ParagraphStyle("TitRecibo", fontName="Helvetica-Bold", fontSize=13,
                           textColor=COR_TEXTO)
        ))

    # Info do pedido
    origem = dados_pedido.get("origem", "")
    num_mesa = dados_pedido.get("num_mesa")
    if origem == "Mesa" and num_mesa:
        info_pedido = f"Mesa {num_mesa} · Pedido #{id_pedido:03d}"
    elif origem == "Balcão":
        info_pedido = f"Balcão · Pedido #{id_pedido:03d}"
    else:
        info_pedido = f"Pedido #{id_pedido:03d}"

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    estilo_info = ParagraphStyle(
        "InfoRecibo", fontName="Helvetica", fontSize=9,
        textColor=COR_PASSIVO, spaceBefore=4, spaceAfter=2
    )
    elementos.append(Paragraph(info_pedido, estilo_info))
    elementos.append(Paragraph(agora, estilo_info))

    # Separador
    _adicionar_separador(elementos, LARGURA)

    # ── Itens
    estilo_secao = ParagraphStyle(
        "SecaoRecibo", fontName="Helvetica-Bold", fontSize=10,
        textColor=COR_TEXTO, spaceBefore=6, spaceAfter=4
    )
    elementos.append(Paragraph("ITENS", estilo_secao))

    itens = dados_pedido.get("itens", [])
    if itens:
        estilo_cel = ParagraphStyle(
            "CelRecibo", fontName="Helvetica", fontSize=8, textColor=COR_TEXTO
        )
        estilo_cab = ParagraphStyle(
            "CabRecibo", fontName="Helvetica-Bold", fontSize=8,
            textColor=COR_TEXTO, alignment=1
        )

        cabecalho = [
            Paragraph("Produto", estilo_cab),
            Paragraph("Qtd", estilo_cab),
            Paragraph("Valor", estilo_cab),
        ]
        linhas = [cabecalho]

        for item in itens:
            nome = item.get("nome", "")
            qtd = item.get("qtd", 1)
            preco = item.get("preco", 0)
            subtotal = preco * qtd
            linhas.append([
                Paragraph(nome, estilo_cel),
                Paragraph(str(qtd), estilo_cel),
                Paragraph(f"R$ {subtotal:.2f}".replace(".", ","), estilo_cel),
            ])

        tabela_itens = Table(linhas, colWidths=[5*cm, 1.5*cm, 3.5*cm], repeatRows=1)
        tabela_itens.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  COR_LARANJA),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [COR_BEGE, COR_BRANCO]),
            ("GRID",          (0, 0), (-1, -1), 0.5, COR_BORDA),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tabela_itens)
    else:
        elementos.append(Paragraph("Nenhum item registrado.", estilo_info))

    _adicionar_separador(elementos, LARGURA)

    # ── Resumo financeiro
    estilo_valor = ParagraphStyle(
        "ValorRecibo", fontName="Helvetica", fontSize=9,
        textColor=COR_TEXTO, spaceBefore=1, spaceAfter=1
    )
    estilo_valor_total = ParagraphStyle(
        "ValorTotalRecibo", fontName="Helvetica-Bold", fontSize=10,
        textColor=COR_TEXTO, spaceBefore=1, spaceAfter=1
    )

    subtotal = dados_pedido.get("subtotal", 0)
    taxa = dados_pedido.get("taxa_servico", 0)
    total = subtotal + taxa

    dados_resumo = [
        [Paragraph("Subtotal", estilo_valor),
         Paragraph(f"R$ {subtotal:.2f}".replace(".", ","), estilo_valor)],
        [Paragraph("Taxa de Serviço", estilo_valor),
         Paragraph(f"R$ {taxa:.2f}".replace(".", ","), estilo_valor)],
        [Paragraph("<b>TOTAL</b>", estilo_valor_total),
         Paragraph(f"<b>R$ {total:.2f}</b>".replace(".", ","), estilo_valor_total)],
    ]

    tabela_resumo = Table(dados_resumo, colWidths=[6*cm, 4*cm])
    tabela_resumo.setStyle(TableStyle([
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",     (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(tabela_resumo)

    _adicionar_separador(elementos, LARGURA)

    # ── Pagamentos
    elementos.append(Paragraph("PAGAMENTOS", estilo_secao))

    if pagamentos:
        estilo_pag = ParagraphStyle(
            "PagRecibo", fontName="Helvetica", fontSize=9, textColor=COR_TEXTO
        )
        estilo_pag_detalhe = ParagraphStyle(
            "PagDetRecibo", fontName="Helvetica", fontSize=7, textColor=COR_PASSIVO
        )

        for pag in pagamentos:
            metodo = pag.get("metodo", "")
            valor = pag.get("valor", 0)
            horario = pag.get("horario", "")
            detalhes = pag.get("detalhes")

            linha = [Paragraph(metodo, estilo_pag),
                     Paragraph(f"R$ {valor:.2f}".replace(".", ","), estilo_pag)]
            tabela_pag = Table([linha], colWidths=[6*cm, 4*cm])
            tabela_pag.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",  (1, 0), (1, 0),   "RIGHT"),
                ("TOPPADDING",    (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            elementos.append(tabela_pag)

            if detalhes:
                elementos.append(Paragraph(f"  {detalhes}", estilo_pag_detalhe))
            if horario:
                elementos.append(Paragraph(f"  {horario}", estilo_pag_detalhe))

        # Troco
        pago = sum(p.get("valor", 0) for p in pagamentos)
        troco = pago - total
        if troco > 0:
            elementos.append(Spacer(1, 0.2*cm))
            elementos.append(Paragraph(
                f"<b>Troco: R$ {troco:.2f}</b>".replace(".", ","),
                ParagraphStyle("TrocoRecibo", fontName="Helvetica-Bold", fontSize=10,
                               textColor=COR_VERDE, spaceBefore=4)
            ))
    else:
        elementos.append(Paragraph("Nenhum pagamento registrado.", estilo_info))

    # ── Observações
    obs = dados_pedido.get("obs", "")
    if obs:
        _adicionar_separador(elementos, LARGURA)
        elementos.append(Paragraph("OBSERVAÇÕES", estilo_secao))
        estilo_obs = ParagraphStyle(
            "ObsRecibo", fontName="Helvetica", fontSize=8,
            textColor=COR_TEXTO, spaceBefore=2
        )
        elementos.append(Paragraph(obs, estilo_obs))

    # ── Rodapé (estilo recibo)
    _adicionar_separador(elementos, LARGURA)
    usuario = usuario_atual.get("nome", "")
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    estilo_rodape = ParagraphStyle(
        "RodapeRecibo", fontName="Helvetica", fontSize=7,
        textColor=COR_PASSIVO, alignment=1, spaceBefore=4
    )
    elementos.append(Paragraph(f"Gerado por: {usuario}  |  {agora}", estilo_rodape))
    elementos.append(Paragraph(
        "2026 Sabores do Pará",
        ParagraphStyle("RodapeRecibo2", fontName="Helvetica-Bold", fontSize=8,
                       textColor=COR_PASSIVO, alignment=1, spaceBefore=2)
    ))

    doc.build(elementos)
    messagebox.showinfo("PDF Gerado", f"Comprovante salvo em:\n{caminho}")
    os.startfile(caminho)


def _adicionar_separador(elementos: list, largura: float):
    """Adiciona uma linha separadora fina na largura especificada."""
    linha = Table([[""]], colWidths=[largura])
    linha.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, COR_BORDA),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elementos.append(Spacer(1, 0.2*cm))
    elementos.append(linha)
    elementos.append(Spacer(1, 0.2*cm))


def gerar_comanda(dados_pedido: dict, logo_path: str = None) -> str:
    """
    Gera PDF de comanda para cozinha.
    Retorna o caminho do arquivo gerado.
    """
    LARGURA = 8 * cm

    data = datetime.now().strftime("%d_%m_%y")
    id_pedido = dados_pedido.get("id_pedido", 0)
    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"comanda_{id_pedido:03d}_{data}.pdf",
        title="Salvar Comanda"
    )
    if not caminho:
        return ""

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        leftMargin=6.5*cm, rightMargin=6.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    elementos = []

    # ── Cabeçalho
    estilo_titulo_comanda = ParagraphStyle(
        "TituloComanda", fontName="Helvetica-Bold", fontSize=12,
        textColor=COR_TEXTO, alignment=1
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloComanda", fontName="Helvetica", fontSize=9,
        textColor=COR_PASSIVO, alignment=1, spaceBefore=2
    )

    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2*cm, height=1.2*cm)
        dados_logo = [[logo, Paragraph("COMANDA", estilo_titulo_comanda)]]
        tabela_logo = Table(dados_logo, colWidths=[1.5*cm, 6.5*cm])
        tabela_logo.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ]))
        elementos.append(tabela_logo)
    else:
        elementos.append(Paragraph("COMANDA", estilo_titulo_comanda))

    # Info do pedido
    origem = dados_pedido.get("origem", "mesa")
    num_mesa = dados_pedido.get("num_mesa")
    if origem == "mesa" and num_mesa:
        info_pedido = f"Mesa {num_mesa} · Pedido #{id_pedido:03d}"
    elif origem == "balcao":
        info_pedido = f"Balcão · Pedido #{id_pedido:03d}"
    else:
        info_pedido = f"Pedido #{id_pedido:03d}"

    elementos.append(Paragraph(info_pedido, estilo_subtitulo))

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos.append(Paragraph(agora, estilo_subtitulo))

    _adicionar_separador(elementos, LARGURA)

    # ── Itens
    estilo_secao = ParagraphStyle(
        "SecaoComanda", fontName="Helvetica-Bold", fontSize=10,
        textColor=COR_TEXTO, spaceBefore=4, spaceAfter=4
    )
    estilo_item = ParagraphStyle(
        "ItemComanda", fontName="Helvetica", fontSize=9,
        textColor=COR_TEXTO, spaceBefore=1, spaceAfter=1
    )
    estilo_obs = ParagraphStyle(
        "ObsComanda", fontName="Helvetica-Oblique", fontSize=8,
        textColor=COR_PASSIVO, spaceBefore=1, spaceAfter=2, leftIndent=10
    )

    elementos.append(Paragraph("ITENS", estilo_secao))

    itens = dados_pedido.get("itens", [])
    if itens:
        for item in itens:
            nome = item.get("nome", "")
            qtd = item.get("quantidade", 1)
            obs_item = item.get("observacoes", "")

            elementos.append(Paragraph(f"{qtd}x {nome}", estilo_item))
            if obs_item:
                elementos.append(Paragraph(f"  Obs: {obs_item}", estilo_obs))
    else:
        elementos.append(Paragraph("Nenhum item.", estilo_item))

    _adicionar_separador(elementos, LARGURA)

    # ── Observações gerais
    obs_geral = dados_pedido.get("observacoes", "")
    if obs_geral:
        elementos.append(Paragraph("OBSERVAÇÕES", estilo_secao))
        estilo_obs_geral = ParagraphStyle(
            "ObsGeralComanda", fontName="Helvetica", fontSize=9,
            textColor=COR_TEXTO, spaceBefore=2
        )
        elementos.append(Paragraph(obs_geral, estilo_obs_geral))
        _adicionar_separador(elementos, LARGURA)

    # ── Tempo estimado
    tempo_estimado = dados_pedido.get("tempo_estimado", 30)
    if tempo_estimado:
        estilo_tempo = ParagraphStyle(
            "TempoComanda", fontName="Helvetica-Bold", fontSize=10,
            textColor=COR_LARANJA, alignment=1, spaceBefore=6
        )
        elementos.append(Paragraph(f"Tempo estimado: {tempo_estimado} min", estilo_tempo))

    doc.build(elementos)
    return caminho