import time
from app.database.db_config import conectar
from app.utils.validacoes import normalizar_texto

from app.model.erros_produto import ProdutoDuplicadoError


class ProdutoModel:
    _cache_lista = None
    _cache_lista_time = 0
    _cache_lista_ttl = 30

    def listar_produtos(self, force=False):
        agora = time.time()
        if not force and self._cache_lista is not None and agora - self._cache_lista_time < self._cache_lista_ttl:
            return self._cache_lista

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id_produto, nome, preco, categoria, descricao, status, unidade, foto
        FROM produto               
        """)

        produtos = cursor.fetchall()

        self._cache_lista = produtos
        self._cache_lista_time = agora
        return produtos

    def _invalidar_cache_lista(self):
        self._cache_lista = None
        self._cache_lista_time = 0

    def _produto_existe_por_nome_e_descricao(self, nome: str, descricao: str, excluir_id: int | None = None) -> bool:
        """Verifica duplicidade por (nome + descricao).

        A comparação é feita normalizando caixa e acentos.
        """
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_produto, nome, descricao FROM produto"
        )

        produtos = cursor.fetchall()

        nome_norm = normalizar_texto(nome)
        desc_norm = normalizar_texto(descricao)

        for (id_prod, nome_db, desc_db) in produtos:
            if excluir_id is not None and id_prod == excluir_id:
                continue
            if normalizar_texto(nome_db) == nome_norm and normalizar_texto(desc_db) == desc_norm:
                return True
        return False

    def salvar_produto(self, nome, preco, categoria, descricao, unidade, status, foto=None):

        if self._produto_existe_por_nome_e_descricao(nome, descricao):
            raise ProdutoDuplicadoError("Já existe um produto com o mesmo nome e descrição.")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
                INSERT INTO produto (nome, preco, categoria, descricao, unidade, status, foto)
                VALUES (%s, %s, %s, %s, %s, %s, %s)           
            """,
            (nome, preco, categoria, descricao, unidade, status, foto),
        )

        conn.commit()
        self._invalidar_cache_lista()

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
        if self._produto_existe_por_nome_e_descricao(nome, descricao, excluir_id=id_produto):
            raise ProdutoDuplicadoError("Já existe um produto com o mesmo nome e descrição.")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE produto
            SET nome=%s,
                preco=%s,
                categoria=%s,
                descricao=%s,
                unidade=%s,
                status=%s,
                foto=%s
            WHERE id_produto=%s               
        """,
            (
                nome,
                preco,
                categoria,
                descricao,
                unidade,
                status,
                foto,
                id_produto,
            ),
        )

        conn.commit()
        self._invalidar_cache_lista()

    def buscar_produto(self, id_produto):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_produto, nome, preco, categoria, descricao, status, unidade, foto FROM produto WHERE id_produto = %s",
            (id_produto,),
        )
        resultado = cursor.fetchone()
        return resultado

    def deletar_produto(self, id_produto):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))

        conn.commit()
        self._invalidar_cache_lista()
