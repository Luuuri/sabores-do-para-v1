# Importa o caminho das imagens e as famílias de fontes

import os
from pathlib import Path
from PIL import Image, ImageDraw
from app.utils.cache import get_foto_quadrada, get_foto_processada

BASE_DIR = Path(__file__).resolve().parent.parent

def get_asset_path(nome_arquivo):
    return BASE_DIR / "utils" / "assets" / nome_arquivo

def get_font_path(nome_arquivo):
    return BASE_DIR / "utils" / "assets" / "fonts" / nome_arquivo


def preparar_foto(caminho, tamanho_saida=(40, 40), raio=12):
    return get_foto_quadrada(caminho, tamanho_saida, raio)


def preparar_foto_retangular(caminho, tamanho_saida=(250, 130), raio=10):
    return get_foto_processada(caminho, tamanho_saida, raio)