import re
import unicodedata

# ── NORMALIZAR (remover acentos, lowercase) ─────────────────────────────────

def normalizar_texto(texto: str) -> str:
    """Remove acentos e converte para minúsculas para comparação."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")
    return texto.strip().lower()


# ── CAPITALIZAR (português) ─────────────────────────────────────────────────

_PREPOSICOES = {"da", "das", "de", "do", "dos", "e"}

def capitalizar_campo(event, entrada):
    texto = entrada.get().strip()
    if not texto:
        return
    palavras = texto.split()
    resultado = []
    for i, pal in enumerate(palavras):
        if i == 0 or pal.lower() not in _PREPOSICOES:
            resultado.append(pal.capitalize())
        else:
            resultado.append(pal.lower())
    entrada.delete(0, "end")
    entrada.insert(0, " ".join(resultado))

# VALIDAR EMAIL

def validar_email(email):

    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    return re.match(padrao, email) is not None


# VALIDAR CELULAR
# FORMATO: (93) 9 9999-9999

def validar_celular(celular):

    padrao = r"^\(\d{2}\) \d \d{4}-\d{4}$"

    return re.match(padrao, celular) is not None


# FORMATAR CELULAR


def formatar_celular(event, entrada):
    texto = entrada.get()
    numeros = re.sub(r"\D", "", texto)
    numeros = numeros[:11]

    resultado = ""

    if len(numeros) >= 1:
        resultado += "(" + numeros[:2]        # (91

    if len(numeros) >= 3:
        resultado += ") " + numeros[2:3]      # ) 9

    if len(numeros) >= 4:
        resultado += " " + numeros[3:7]       # 8888

    if len(numeros) >= 8:
        resultado += "-" + numeros[7:11]      # -8888

    entrada.delete(0, "end")
    entrada.insert(0, resultado)


# FORMATAR CPF
# FORMATO: 000.000.000-00

def formatar_cpf(event, entrada):

    texto = entrada.get()

    numeros = re.sub(r"\D", "", texto)

    numeros = numeros[:11]

    resultado = ""

    # 000
    if len(numeros) >= 1:
        resultado += numeros[:3]

    # .000
    if len(numeros) >= 4:
        resultado += "." + numeros[3:6]

    # .000
    if len(numeros) >= 7:
        resultado += "." + numeros[6:9]

    # -00
    if len(numeros) >= 10:
        resultado += "-" + numeros[9:11]

    entrada.delete(0, "end")

    entrada.insert(0, resultado)

# VALIDAR CPF

def cpf_valido(cpf):

    """"# remove pontos e traços
    cpf = ''.join(filter(str.isdigit, cpf))

    # verifica tamanho
    if len(cpf) != 11:
        return False

    # evita cpf repetido
    if cpf == cpf[0] * 11:
        return False

    # primeiro dígito
    soma = 0

    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    digito1 = (soma * 10) % 11

    if digito1 == 10:
        digito1 = 0

    if digito1 != int(cpf[9]):
        return False

    # segundo dígito
    soma = 0

    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    digito2 = (soma * 10) % 11

    if digito2 == 10:
        digito2 = 0

    if digito2 != int(cpf[10]):
        return False

    return True"""
    
    # VALIDAR CPF
# Para uso acadêmico: valida apenas formato, não os dígitos verificadores

def cpf_valido(cpf):

    # remove pontos e traços
    cpf = ''.join(filter(str.isdigit, cpf))

    # verifica tamanho
    if len(cpf) != 11:
        return False

    # evita cpf com todos os dígitos iguais (ex: 111.111.111-11)
    # REMOVA essa verificação se quiser aceitar até esses casos
    if cpf == cpf[0] * 11:
        return False

    return True


# FORMATAR PREÇO EM TEMPO REAL
# Aceita apenas números, vírgula ou ponto (um único separador decimal)

def formatar_preco(event, entrada):
    texto = entrada.get()
    numeros = ""
    tem_separador = False
    pos_separador = -1

    for i, char in enumerate(texto):
        if char.isdigit():
            numeros += char
        elif char in ",." and not tem_separador:
            tem_separador = True
            pos_separador = len(numeros)
            numeros += ","

    if tem_separador:
        parte_inteira = numeros[:pos_separador]
        parte_decimal = numeros[pos_separador + 1:pos_separador + 3]
        resultado = parte_inteira + "," + parte_decimal
    else:
        resultado = numeros

    entrada.delete(0, "end")
    entrada.insert(0, resultado)


# VALIDAR PREÇO

def validar_preco(preco):
    if not preco:
        return False
    try:
        valor = float(preco.replace(",", "."))
        return valor > 0
    except ValueError:
        return False


# STATUS DO BANCO PARA BOOLEANO

def status_para_bool(status):
    return str(status).strip().lower() == "ativo"


def bool_para_status(ativo):
    return "Ativo" if ativo else "Inativo"


# ── FORMATAR CEP ────────────────────────────────────────────────────────────
# FORMATO: 00000-000

def formatar_cep(event, entrada):
    texto = entrada.get()
    numeros = re.sub(r"\D", "", texto)
    numeros = numeros[:8]

    resultado = ""
    if len(numeros) >= 1:
        resultado += numeros[:5]
    if len(numeros) >= 6:
        resultado += "-" + numeros[5:8]

    entrada.delete(0, "end")
    entrada.insert(0, resultado)


# ── ACEITAR APENAS DÍGITOS (Número) ───────────────────────────────────────

def formatar_apenas_digitos(event, entrada):
    texto = entrada.get()
    apenas_digitos = re.sub(r"\D", "", texto)
    if texto != apenas_digitos:
        entrada.delete(0, "end")
        entrada.insert(0, apenas_digitos)


# ── ACEITAR APENAS LETRAS (Bairro / Cidade) ───────────────────────────────

def formatar_apenas_letras(event, entrada):
    texto = entrada.get()
    apenas_letras = re.sub(r"[^a-zA-ZÀ-ÿ\s\-']", "", texto)
    if texto != apenas_letras:
        entrada.delete(0, "end")
        entrada.insert(0, apenas_letras)