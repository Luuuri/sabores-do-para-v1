from app.model.produto_model import ProdutoModel
from app.utils.componentes import PASTA_PRODUTOS
from app.utils.validacoes import status_para_bool
import os

class ProdutoController:
    def __init__(self):
        self.model = ProdutoModel()
        
    def listar_produtos(self):
        dados = self.model.listar_produtos()
        return [
            {
                "id_produto": p[0], "nome": p[1], "preco": p[2],
                "preco_formatado": f"R$ {p[2]:.2f}".replace(".", ","),
                "categoria": p[3], "descricao": p[4], "status": p[5],
                "unidade": p[6], "foto": p[7],
                "ativo": status_para_bool(p[5])
            }
            for p in dados
        ]
    
    def salvar_produto(self, nome, preco, categoria, descricao, unidade, status, foto=None):
        # Deixa a validação de duplicidade crescer até a View.
        self.model.salvar_produto(
            nome,
            preco,
            categoria,
            descricao,
            unidade,
            status,
            foto,
        )

    def atualizar_produto(
        self,
        id_produto,
        nome,
        preco,
        categoria,
        descricao,
        unidade,
        status,
        foto=None,
    ):
        # Deixa a validação de duplicidade crescer até a View.
        self.model.atualizar_produto(
            id_produto,
            nome,
            preco,
            categoria,
            descricao,
            unidade,
            status,
            foto,
        )
        
    def deletar_produto(self, id_produto):
        dados = self.model.buscar_produto(id_produto)
        if dados and dados[7]:
            caminho = os.path.join(PASTA_PRODUTOS, dados[7])
            print(f"[DEBUG] Tentando deletar foto: {caminho} (existe: {os.path.isfile(caminho)})")
            if os.path.isfile(caminho):
                os.remove(caminho)
        self.model.deletar_produto(id_produto)