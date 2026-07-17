from PIL import Image, ImageDraw

_cache_fotos_pil = {}
_cache_fotos_ctk = {}
_qr_pix = None


def get_foto_processada(caminho, tamanho, raio):
    chave = (caminho, tuple(tamanho), raio)
    if chave in _cache_fotos_pil:
        return _cache_fotos_pil[chave]

    imagem = Image.open(caminho).convert("RGBA")
    largura_alvo, altura_alvo = tamanho
    ratio_alvo = largura_alvo / altura_alvo
    ratio_img = imagem.size[0] / imagem.size[1]

    if ratio_img > ratio_alvo:
        nova_largura = int(imagem.size[1] * ratio_alvo)
        esquerda = (imagem.size[0] - nova_largura) // 2
        imagem = imagem.crop((esquerda, 0, esquerda + nova_largura, imagem.size[1]))
    else:
        nova_altura = int(imagem.size[0] / ratio_alvo)
        topo = (imagem.size[1] - nova_altura) // 2
        imagem = imagem.crop((0, topo, imagem.size[0], topo + nova_altura))

    imagem = imagem.resize(tamanho, Image.LANCZOS)
    mascara = Image.new("L", tamanho, 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [(0, 0), (tamanho[0] - 1, tamanho[1] - 1)],
        radius=raio, fill=255
    )
    imagem.putalpha(mascara)
    _cache_fotos_pil[chave] = imagem
    return imagem


def get_foto_quadrada(caminho, tamanho, raio):
    chave = (caminho, tuple(tamanho), raio)
    if chave in _cache_fotos_pil:
        return _cache_fotos_pil[chave]

    imagem = Image.open(caminho).convert("RGBA")
    lado = min(imagem.size)
    esquerda = (imagem.size[0] - lado) // 2
    topo = (imagem.size[1] - lado) // 2
    imagem = imagem.crop((esquerda, topo, esquerda + lado, topo + lado))
    imagem = imagem.resize(tamanho, Image.LANCZOS)
    mascara = Image.new("L", tamanho, 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [(0, 0), (tamanho[0] - 1, tamanho[1] - 1)],
        radius=raio, fill=255
    )
    imagem.putalpha(mascara)
    _cache_fotos_pil[chave] = imagem
    return imagem


def get_foto_ctk(caminho, tamanho):
    import customtkinter as ctk
    chave = (caminho, tuple(tamanho))
    if chave in _cache_fotos_ctk:
        return _cache_fotos_ctk[chave]

    img = Image.open(caminho)
    ctk_img = ctk.CTkImage(light_image=img, size=tamanho)
    _cache_fotos_ctk[chave] = ctk_img
    return ctk_img


def get_qr_pix():
    global _qr_pix
    if _qr_pix is None:
        import qrcode
        _qr_pix = qrcode.make("chave-pix-exemplo@dominio.com")
    return _qr_pix


def limpar():
    global _qr_pix
    _cache_fotos_pil.clear()
    _cache_fotos_ctk.clear()
    _qr_pix = None
