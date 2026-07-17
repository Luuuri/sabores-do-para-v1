import json
import os

CAMINHO = os.path.join(os.path.dirname(__file__), 'preferencias.json')

def carregar_preferencias() -> dict:
    if os.path.exists(CAMINHO):
        try:
            with open(CAMINHO, "r") as f:
                dados = json.load(f)
                if isinstance(dados, dict):
                    return dados
        except Exception:
            pass
    return {"tema": "Light"}

def salvar_preferencias(dados: dict):
    with open(CAMINHO, "w") as f:
        json.dump(dados, f)  