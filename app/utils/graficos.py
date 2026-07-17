from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from datetime import datetime


def renderizar_grafico(frame, figura):
    for w in frame.winfo_children():
        w.destroy()
    canvas = FigureCanvasTkAgg(figura, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    return canvas


def criar_grafico_vazio(cores, mensagem="Nenhum dado disponÃ­vel"):
    fig = Figure(figsize=(7, 4), dpi=100, facecolor=cores.fundo.principal)
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, mensagem, ha="center", va="center",
            fontsize=14, color=cores.texto.principal)
    ax.set_facecolor(cores.fundo.principal)
    return fig


def criar_grafico_barras(cores, labels, values, titulo, xlabel="", ylabel="", cor=None):
    if cor is None:
        cor = cores.texto.verde
    figura = Figure(figsize=(7, 4), dpi=100, facecolor=cores.fundo.principal)
    ax = figura.add_subplot(111)
    x = range(len(labels))
    ax.bar(x, values, width=0.7, color=cor,
           edgecolor=cores.texto.principal, linewidth=0.7)
    ax.set_title(titulo, fontsize=14, fontweight="bold", color=cores.texto.principal)
    ax.set_xlabel(xlabel, color=cores.texto.principal)
    ax.set_ylabel(ylabel, color=cores.texto.principal)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", color=cores.texto.principal)
    ax.tick_params(axis='y', colors=cores.texto.principal)
    ax.set_facecolor(cores.fundo.principal)
    figura.tight_layout()
    return figura


def criar_grafico_linha(cores, labels, values, titulo, xlabel="", ylabel=""):
    figura = Figure(figsize=(7, 4), dpi=100, facecolor=cores.fundo.principal)
    ax = figura.add_subplot(111)
    ax.plot(range(len(labels)), values, marker="o",
            color=cores.texto.laranja, linewidth=2, markersize=5)
    ax.set_title(titulo, fontsize=14, fontweight="bold", color=cores.texto.principal)
    ax.set_xlabel(xlabel, color=cores.texto.principal)
    ax.set_ylabel(ylabel, color=cores.texto.principal)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", color=cores.texto.principal)
    ax.tick_params(axis='y', colors=cores.texto.principal)
    ax.set_facecolor(cores.fundo.principal)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    figura.tight_layout()
    return figura


def criar_grafico_pizza(cores, labels, values, titulo):
    paleta = [
        cores.texto.laranja,
        cores.texto.amarelo,
        getattr(cores.fundo, "verde_amarelado", cores.texto.principal),
        getattr(cores.fundo, "verde", cores.texto.principal),
        getattr(cores.fundo, "azul", cores.texto.principal),
        getattr(cores.texto, "coral", cores.texto.principal),
        getattr(cores.fundo, "laranja", cores.texto.principal),
    ]
    figura = Figure(figsize=(7, 4), dpi=100, facecolor=cores.fundo.principal)
    ax = figura.add_subplot(111)
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90,
           colors=paleta[:max(len(values), 1)],
           textprops={"fontsize": 10, "color": cores.texto.principal})
    ax.set_title(titulo, fontsize=14, fontweight="bold", color=cores.texto.principal)
    figura.tight_layout()
    return figura


def criar_grafico_vendas(
    cores,
    dados_hoje,
    dados_ontem,
    horario_atual=None,
    destaque="ambos",
):
    hoje_lookup = {d["hora"]: d["vendas"] for d in dados_hoje}
    ontem_lookup = {d["hora"]: d["vendas"] for d in dados_ontem}

    horas = list(range(8, 24))
    hoje_valores = [hoje_lookup.get(h, 0) for h in horas]
    ontem_valores = [ontem_lookup.get(h, 0) for h in horas]

    alpha_hoje = 0.3 if destaque == "ontem" else 1.0
    alpha_ontem = 0.3 if destaque == "hoje" else 1.0

    figura = Figure(figsize=(8, 3.5), dpi=100, facecolor=cores.fundo.principal)
    ax = figura.add_subplot(111)
    ax.set_facecolor(cores.fundo.principal)

    ax.fill_between(horas, hoje_valores, alpha=0.08 * alpha_hoje,
                     color=cores.texto.laranja, zorder=1)

    linha_hoje, = ax.plot(
        horas, hoje_valores,
        color=cores.texto.laranja,
        linewidth=2.5,
        alpha=alpha_hoje,
        label="Hoje",
    )
    linha_ontem, = ax.plot(
        horas, ontem_valores,
        color=cores.texto.passivo,
        linewidth=1.5,
        alpha=alpha_ontem * 0.5,
        linestyle="--",
        label="Ontem",
    )

    if horario_atual is None:
        horario_atual = datetime.now().hour
    if 8 <= horario_atual <= 23:
        ax.axvline(x=horario_atual, color=cores.texto.laranja,
                   linestyle=":", linewidth=1.5, alpha=0.6, zorder=0)

    ax.set_xticks(range(8, 24, 2))
    ax.set_xticklabels([f"{h}h" for h in range(8, 24, 2)])
    ax.tick_params(axis='both', colors=cores.texto.principal, labelsize=9)
    ax.set_xlim(7.5, 23.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
    ax.grid(axis="y", linestyle="-", alpha=0.12, linewidth=0.7, color=cores.texto.passivo)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(cores.texto.passivo)
    ax.spines["bottom"].set_color(cores.texto.passivo)

    ax.legend(loc="upper left", fontsize=10, frameon=False,
              labelcolor=cores.texto.principal)

    figura.tight_layout()
    return figura, linha_hoje, linha_ontem
