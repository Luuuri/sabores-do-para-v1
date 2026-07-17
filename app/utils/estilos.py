"""
=======================================================
estilos.py - Centraliza cores, fontes e ícones do app.
=======================================================

COMO USAR EM QUALQUER TELA:
    from app.utils.estilos import Cores, Fontes, Icones

    cores  = Cores()
    fontes = Fontes()
    icones = Icones()

    # Passe os três para cada componente/tela:
    tela = MinhaTela(root, cores, fontes, icones)
"""

import os
import ctypes
import customtkinter as ctk
from PIL import Image
from app.utils.helpers import get_asset_path, get_font_path
from PIL import ImageTk

#Registro de fontes (só funciona no Windows)
_FR_PRIVATE = 0x10
_FR_NOT_ENUM = 0x20

def carregar_fonte(caminho):
    """Registra fonte no sistema. No Linux/Mac é ignorado silenciosamente."""
    if os.name == "nt":  # "nt" = Windows
        ctypes.windll.gdi32.AddFontResourceExW(str(caminho), _FR_PRIVATE | _FR_NOT_ENUM, 0)


def carregar_imagem(nome_arquivo: str, tamanho: tuple) -> ctk.CTkImage:
    """Carrega um PNG da pasta assets/ e retorna CTkImage pronto para uso."""
    img = Image.open(get_asset_path(nome_arquivo))
    return ctk.CTkImage(light_image=img, size=tamanho)

def inverter_para_branco(nome_arquivo: str, tamanho: tuple) -> ctk.CTkImage:
    """Usa o mesmo PNG mas invertido (branco) para o tema escuro."""
    from PIL import ImageOps
    img = Image.open(get_asset_path(nome_arquivo)).convert("RGBA")
    r, g, b, a = img.split()
    rgb = Image.merge("RGB", (r, g, b))
    invertida = ImageOps.invert(rgb)
    img_escura = Image.merge("RGBA", (*invertida.split(), a))
    return ctk.CTkImage(light_image=img, dark_image=img_escura, size=tamanho)

def converter_ctkimage(ctk_img):
    pil = ctk_img._light_image
    return ImageTk.PhotoImage(pil)

#Paleta de cores
class CoresClaro:
    """Tema claro — cores originais do sistema."""
    """
    Agrupa todas as cores por contexto.
    Acesso: cores.fundo.principal, cores.texto.vermelho, etc.
    """

    class Fundo:
        def __init__(self):
            self.principal         = "#fff8f5"
            self.sidebar           = "#ffeada"
            self.secundario        = "#fff8f5"
            self.branco            = "#ffffff"
            self.preto             = "#1e1e1e"
            self.cinza             = "#d8d8d8"
            self.cinza_médio       = "#7B7B7B"
            self.cinza_escuro      = "#b4b4b4"
            self.cinza_claro       = "#dbdbdb"
            self.cinza_clarinho    = "#ededed"
            self.vermelho          = "#ff9b9b"
            self.verde             = "#71e4a0"
            self.amarelo           = "#ffea98"
            self.azul              = "#98d3f6"
            self.roxo              = "#e2d3ff"
            self.verde_amarelado   = "#B9C98A"
            self.cinza_muito_claro = "#ECECEC"
            self.bege_rosado       = "#D79B87"
            self.laranja           = "#D95C02"
            self.fundinho          = "#f9ebe1"
            

    class Barra:
        def __init__(self):
            self.topo = "#d9d9d9"

    class Texto:
        def __init__(self):
            self.principal         = "#2c2015"
            self.secundario        = "#555555"
            self.passivo           = "#7a6a58"
            self.inativo           = "#9b8d88"
            self.vermelho          = "#eb5757"
            self.vermelho_escuro   = "#b12424"
            self.amarelo           = "#ffbd59"
            self.verde             = "#47d481"
            self.verde_escuro      = "#379b60"
            self.branco            = "#ffffff"
            self.cinza_muito_claro = "#ECECEC"
            self.verde_jambu       = "#18392B"
            self.verde_jambu_leve  = "#c8d9b0"
            self.placeholder       = "#7B7B7B"
            self.laranja           = "#e8961e"
            self.coral             = "#f0802e"
            self.laranja_claro     = "#faf6f0"
            self.laranja_HOVER     = "#f2b49a"
            # Estoque
            self.ok                = "#2ecc71"
            self.baixo             = "#f39c12"
            self.zerado            = "#e74c3c"
            # Cards
            self.atrasado_txt      = "#93000a"
            self.pendente_txt      = "#534602"

    class Botao:
        def __init__(self):
            self.primario          = "#c7511b"
            self.primario_hover    = "#a63a00"
            self.secundario        = "#18392B"
            self.secundario_hover  = "#11281E"
            self.confirmar         = "#1e1e1e"
            self.confirmar_inativo = "#737373"
            self.cancelar          = "#737373"
            self.excluir           = "#f47e7e"
            self.passivo           = "#8d7166"
            self.ativo             = "#1e1e1e"
            self.ativo_secundario  = "#737373"
            self.hover             = "#f4ede4"
            self.novo              = "#cf4a00"
            self.novo_hover        = "#BF4F00"
            # CoresClaro → Botao
            self.id_badge          = "#1e1e1e"   # preto, igual ao atual
            self.id_badge_txt      = "#ffffff"
            self.borda             = "#e1bfb3"
            #Filtros
            self.filtro_hover      = "#bdbdbd"
            self.funil             = "#c8d9b0"
            self.funil_hover       = "#3a6b4a"
            self.limpar_filtro     = "#f8c882"
            self.limpar_filtro_hvr = "#e8961e"
            #Scroll
            self.scroll            = "#f8c882"
            self.scroll_hover      = "#e8961e"
            #View Login
            self.entrar            = "#cf4a00"
            self.entrar_hover      = "#BF4F00"
            #View Painel de Controle
            self.janelas           = "#ffffff"
            self.borda_janela      = "#E0D5C8"
            self.janelas_hover     = "#f4ede4"
    
    class Entry:
        def __init__(self):
            self.formulario        = "#fff1e8"
    class Card:
        def __init__(self):
            self.borda_card        = "#e1bfb3"
            self.atrasado_card     = "#ffdad6"
            self.pendentes_card    = "#f6e291"
            
    class Badge:
        def __init__(self):
            self.status_ativo      = "#c3e8d4"
            self.status_inativo    = "#ff9b9b"
    
    class Input:
        def __init__(self):
            self.borda_entry       = "#cc714e"


    def __init__(self):
        self.fundo = self.Fundo()
        self.barra = self.Barra()
        self.texto = self.Texto()
        self.botao = self.Botao()
        self.input = self.Input()
        self.entry = self.Entry()
        self.card  = self.Card()
        self.badge = self.Badge()

class CoresEscuro:
    """Tema escuro — versão noturna açaí do sistema."""

    class Fundo:
        def __init__(self):
            self.principal         = "#1A1025"   # fundo geral — açaí puro
            self.sidebar           = "#150E20"   # sidebar — açaí concentrado
            self.secundario        = "#1A1025"
            self.branco            = "#1F1535"   # superfície de cards/menus
            self.preto             = "#EDE0FF"   # invertido — texto lilás claro
            self.cinza             = "#2C1A42"   # separadores, linhas
            self.cinza_médio       = "#C0A0E8"   # placeholder e ícones — lilás claro legível
            self.cinza_escuro      = "#4A2E6A"
            self.cinza_claro       = "#3A2060"
            self.cinza_clarinho    = "#2C1A42"
            self.vermelho          = "#5C1A1A"
            self.verde             = "#0D3020"
            self.amarelo           = "#3A2C00"
            self.azul              = "#0D2040"
            self.roxo              = "#2C1A42"
            self.verde_amarelado   = "#1E2A0A"
            self.cinza_muito_claro = "#2C1A42"
            self.bege_rosado       = "#7A1A6E"   # borda dos campos — roxo visível
            self.laranja           = "#7A1A6E"   # ação primária no escuro
            self.fundinho          = "#150E20"

    class Barra:
        def __init__(self):
            self.topo = "#150E20"

    class Texto:
        def __init__(self):
            self.principal         = "#EDE0FF"   # branco-lilás
            self.secundario        = "#7B50A8"   # lilás médio — legível sobre fundo escuro
            self.passivo           = "#C0A0E8"
            self.inativo           = "#7B50A8"
            self.vermelho          = "#FF7090"
            self.vermelho_escuro   = "#FF9090"
            self.amarelo           = "#D4B800"
            self.verde             = "#50E090"
            self.verde_escuro      = "#40C070"
            self.branco            = "#EDE0FF"
            self.cinza_muito_claro = "#1A1025"  # bg do checkbox — tem que casar com o fundo
            # Texto
            self.verde_jambu       = "#EDE0FF"   # era #C8D9B0 — branco-lilás, mais legível no fundo escuro
            self.verde_jambu_leve  = "#1E2A0A"
            self.placeholder       = "#7B50A8"
            self.laranja           = "#E8961E"
            self.coral             = "#F0802E"
            self.laranja_claro     = "#1F1535"
            self.laranja_HOVER     = "#B030A0"  # hover do botão Entrar — mais diferente do primário
            # Estoque
            self.ok                = "#2ecc71"
            self.baixo             = "#f39c12"
            self.zerado            = "#e74c3c"
            # Cards
            self.atrasado_txt      = "#FF7090"
            self.pendente_txt      = "#D4B800"

    class Botao:
        def __init__(self):
            self.primario          = "#7A1A6E"   # roxo-vinho açaí
            self.primario_hover    = "#9B2A8E"
            self.secundario        = "#C8D9B0"
            self.secundario_hover  = "#A0B890"
            self.confirmar         = "#2C1A42"
            self.confirmar_inativo = "#4A2E6A"
            self.cancelar          = "#4A2E6A"
            self.excluir           = "#C05060"
            self.passivo           = "#7B50A8"
            self.ativo             = "#3A2060"
            self.ativo_secundario  = "#7B50A8"
            self.hover             = "#2C1A42"
            self.novo              = "#7A1A6E"
            self.novo_hover        = "#9B2A8E"
            self.id_badge          = "#2C1A42"   # badge de ID — roxo escuro, discreto
            self.id_badge_txt      = "#C0A0E8"   # texto do badge
            self.borda             = "#3A2060"
            # Filtros
            self.filtro_hover      = "#2C1A42"
            self.funil             = "#1E2A0A"
            self.funil_hover       = "#3A5A2A"
            self.limpar_filtro     = "#3A2C00"
            self.limpar_filtro_hvr = "#D4A800"
            # Scroll
            self.scroll            = "#3A2060"
            self.scroll_hover      = "#7A1A6E"
            # View Login
            self.entrar            = "#7A1A6E"
            self.entrar_hover      = "#9B2A8E"
            # View Painel de Controle
            self.janelas           = "#1F1535"
            self.borda_janela      = "#3A2060"
            self.janelas_hover     = "#2C1A42"

    class Entry:
        def __init__(self):
            self.formulario        = "#150E20"

    class Card:
        def __init__(self):
            self.borda_card        = "#3A2060"
            self.atrasado_card     = "#2D1020"   # vermelho-escuro mais visível
            self.pendentes_card    = "#2E2400"   # amarelo-escuro mais visível

    class Badge:
        def __init__(self):
            self.status_ativo      = "#0D3020"
            self.status_inativo    = "#2A0D1A"

    class Input:
        def __init__(self):
            self.borda_entry       = "#7A1A6E"

    def __init__(self):
        self.fundo = self.Fundo()
        self.barra = self.Barra()
        self.texto = self.Texto()
        self.botao = self.Botao()
        self.input = self.Input()
        self.entry = self.Entry()
        self.card  = self.Card()
        self.badge = self.Badge()
   
# Alias para compatibilidade — código antigo que usa Cores() continua funcionando
Cores = CoresClaro


def get_cores():
    """Retorna CoresClaro ou CoresEscuro conforme preferência salva."""
    from app.utils.preferencias import carregar_preferencias
    prefs = carregar_preferencias()
    if prefs.get("tema", "Light") == "Dark":
        return CoresEscuro()
    return CoresClaro()   


#Fontes
class Fontes:
    """
    Carrega e expõe as fontes customizadas do app com lazy loading.

    ATENÇÃO: get_font_path() deve apontar para a pasta fonts/ do projeto.
    Se uma fonte não carregar no Windows, verifique se o .otf/.ttf está na pasta certa.
    No Linux/Mac as fontes do sistema são usadas como fallback.
    """
    _FONTES = {
        # Cloud Soft
        "titulo_grande":         ("Cloud Soft", 24, "bold"),
        "titulo":                ("Cloud Soft", 20, "bold"),
        "titulo_italico":        ("Cloud Soft", 20, "bold", "italic"),
        "subtitulo":             ("Cloud Soft", 15, "bold"),
        "botao":                 ("Cloud Soft", 20, "bold"),
        "titulo_esquerdo":       ("Cloud Soft", 55, "bold"),
        "titulo_login":          ("Cloud Soft", 40, "bold"),
        "titulo_login_italico":  ("Cloud Soft", 10, "bold", "italic"),
        "janelas":               ("Cloud Soft", 16, "bold"),
        "titulo_card":           ("Cloud Soft", 12, "bold"),
        "valor":                 ("Cloud Soft", 28, "bold"),
        "cumprimentos":          ("Cloud Soft", 22, "bold"),
        # Open Sans
        "titulo_entry":          ("Open Sans", 14, "normal"),
        "texto_entry":           ("Open Sans", 14, "normal"),
        "sub_info":              ("Open Sans", 12, "normal"),
        "texto_info":            ("Open Sans", 12, "bold"),
        "nome_card":             ("Open Sans", 14, "bold"),
        "preço_card":            ("Open Sans", 14, "bold"),
        "pequeno":               ("Open Sans", 10, "bold"),
        "stepper":               ("Open Sans", 12, "bold"),
        "badge":                 ("Open Sans", 12, "bold"),
        "filtrar":               ("Open Sans", 14, "normal"),
        "subtitulo_login":       ("Open Sans", 25, "normal"),
        "senha_login":           ("Open Sans", 18, "normal"),
        "esqueci_senha":         ("Open Sans", 14),
        "email_senha":           ("Open Sans", 15, "bold"),
        "entrar":                ("Open Sans", 18, "bold"),
    }

    _instancia_unica = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia_unica is None:
            cls._instancia_unica = super().__new__(cls)
        return cls._instancia_unica

    def __init__(self):
        if '_inicializado' in self.__dict__:
            return
        self.__dict__['_inicializado'] = True
        carregar_fonte(get_font_path("CloudSoft-Bold.otf"))
        carregar_fonte(get_font_path("CloudSoft-Light.otf"))
        carregar_fonte(get_font_path("OpenSans-Bold.ttf"))
        carregar_fonte(get_font_path("OpenSans-Regular.ttf"))
        self._cache = {}

    def __getattr__(self, nome):
        if nome in self._cache:
            return self._cache[nome]
        
        if nome not in self._FONTES:
            raise AttributeError(f"'Fontes' não tem fonte '{nome}'")
        
        family, size, *extras = self._FONTES[nome]
        weight = "bold" if "bold" in extras else "normal"
        slant = "italic" if "italic" in extras else "roman"
        
        fonte = ctk.CTkFont(family=family, size=size, weight=weight, slant=slant)
        self._cache[nome] = fonte
        return fonte 

#Ícones
class Icones:
    """
    Carrega PNGs da pasta assets/ com lazy loading (só carrega quando acessado).

    Para adicionar um novo ícone:
        1. Coloque o PNG em assets/
        2. Adicione aqui: "meu_icone": ("meu_icone.png", (20, 20))
        3. Use em qualquer widget: image=self.icones.meu_icone
    """
    # Mapeamento de todos os ícones: nome -> (arquivo, tamanho)
    _ICONES = {
        # Layout
        "home":              ("home.png",              (20, 20)),
        "config":            ("config.png",            (20, 20)),
        "tela_lateral":      ("tela_lateral.png",      (20, 20)),
        # Comandos
        "editar":            ("editar.png",            (15, 15)),
        "apagar":            ("apagar.png",            (15, 15)),
        "voltar":            ("voltar.png",            (30, 30)),
        "voltar_pequeno":    ("voltar.png",            (20, 20)),
        "adicionar_preto":   ("adicionar_preto.png",   (15, 15)),
        "adicionar_branco":  ("adicionar_branco.png",  (15, 15)),
        "add_branco_pequeno":("adicionar_branco.png",  (10, 10)),
        "adicionar_cinza":   ("adicionar_cinza.png",   (15, 15)),
        "fechar_preto":      ("x_preto.png",           (22, 22)),
        "camera":            ("camera.png",            (55, 50)),
        # Formulários
        "nome":              ("nome.png",              (14, 12)),
        "descricao":         ("descricao.png",         (12, 14)),
        "unidade":           ("unidade.png",           (12, 14)),
        "status":            ("status.png",            (14, 14)),
        "dinheiro":          ("dinheiro.png",          (16, 12)),
        "categoria":         ("categoria.png",         (14, 14)),
        # Filtros
        "funil":             ("funil.png",             (15, 15)),
        "filtro_dec":        ("filtro_dec.png",        (15, 15)),
        "filtro_cresc":      ("filtro_cresc.png",      (15, 15)),
        "filtro_inativo":    ("filtro_inativo.png",    (15, 15)),
        # Busca
        "lupa":              ("lupa.png",              (15, 15)),
        # Janelas
        "funcionarios":      ("funcionarios.png",      (20, 20)),
        "clientes":          ("clientes.png",          (20, 20)),
        "produtos":          ("produtos.png",          (20, 20)),
        "estoque":           ("estoque.png",           (20, 20)),
        "caixa":             ("caixa.png",             (20, 20)),
        "delivery":          ("online.png",            (20, 20)),
        "online":            ("online.png",            (20, 20)),
        "relatorios":        ("relatorios.png",        (20, 20)),
        # Painel de Controle
        "funcionarios_btn":  ("funcionarios.png",      (20, 20)),
        "clientes_btn":      ("clientes.png",          (20, 20)),
        "produtos_btn":      ("produtos.png",          (20, 20)),
        "estoque_btn":       ("estoque.png",           (25, 25)),
        "caixa_btn":         ("caixa.png",             (20, 20)),
        "online_btn":        ("online.png",            (20, 20)),
        "relatorios_btn":    ("relatorios.png",        (18, 20)),
        # Decorativo
        "crescente":         ("crescente.png",         (20, 15)),
        "carteira":          ("carteira.png",          (15, 15)),
        "relogio":           ("relogio.png",           (15, 15)),
        "confirmacao":       ("confirmação.png",       (15, 15)),
        "seta":              ("seta.png",              (8, 8)),
        "imagem":            ("imagem.png",            (12, 12)),
        # Logo
        "logotipo":          ("logotipo.png",          (120, 90)),
        "logo":              ("logo.png",              (160, 160)),
        "logo_restaurante":  ("logo_restaurante.jpeg", (10, 10)),
        "logo_home":         ("logo.png",              (35, 35)),
    }
    

    _instancia_unica = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia_unica is None:
            cls._instancia_unica = super().__new__(cls)
        return cls._instancia_unica

    def __init__(self, logo_size=None):
        if '_inicializado' in self.__dict__:
            return
        self.__dict__['_inicializado'] = True
        self._cache = {}
        self._icones_locais = dict(self._ICONES)
        if logo_size:
            self._icones_locais["logotipo"] = ("logotipo.png", logo_size)

    _ICONES_INVERTIDOS = {
        "config", "lupa", "funil", "editar", "apagar", "tela_lateral",
        "voltar", "voltar_pequeno", "adicionar_preto", "fechar_preto",
        "filtro_dec", "filtro_cresc", "filtro_inativo",
        "home", "camera",
        "nome", "descricao", "unidade", "status", "dinheiro", "categoria",
        "funcionarios", "clientes", "produtos", "estoque", "caixa", "delivery", "online", "relatorios",
        "funcionarios_btn", "clientes_btn", "produtos_btn", "estoque_btn",
        "caixa_btn", "online_btn", "relatorios_btn",
        "crescente", "carteira", "relogio", "confirmacao", "seta", "imagem",
    }

    def __getattr__(self, nome):
        if nome in self._cache:
            return self._cache[nome]
        
        if nome not in self._icones_locais:
            raise AttributeError(f"'Icones' não tem ícone '{nome}'")
        
        arquivo, tamanho = self._icones_locais[nome]
        
        if nome in self._ICONES_INVERTIDOS:
            icone = inverter_para_branco(arquivo, tamanho)
        else:
            icone = carregar_imagem(arquivo, tamanho)
        
        self._cache[nome] = icone
        return icone