class Produto:
    def __init__(self, codigo: int, nome: str, preco: float, estoque: int):
        self.codigo = codigo
        self.nome = nome
        self._preco = preco  # Atributo protegido (Encapsulamento)
        self._estoque = estoque

    @property
    def preco(self) -> float:
        return self._preco

    @preco.setter
    def preco(self, novo_preco: float):
        if novo_preco < 0:
            raise ValueError("O preço não pode ser negativo.")
        self._preco = novo_preco

    @property
    def estoque(self) -> int:
        return self._estoque

    def adicionar_estoque(self, quantidade: int):
        if quantidade > 0:
            self._estoque += quantidade

    def remover_estoque(self, quantidade: int) -> bool:
        if 0 < quantidade <= self._estoque:
            self._estoque -= quantidade
            return True
        return False


class ItemCarrinho:
    def __init__(self, produto: Produto, quantidade: int):
        self.produto = produto
        self.quantidade = quantidade

    def calcular_subtotal(self) -> float:
        return self.produto.preco * self.quantidade


class Carrinho:
    def __init__(self):
        self.itens: list[ItemCarrinho] = []

    def adicionar_item(self, produto: Produto, quantidade: int) -> str:
        if quantidade <= 0:
            return "Quantidade inválida."
        if produto.estoque < quantidade:
            return f"Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque}"

        # Verifica se o produto já está no carrinho para somar a quantidade
        for item in self.itens:
            if item.produto.codigo == produto.codigo:
                if produto.estoque < (item.quantidade + quantidade):
                    return "Estoque insuficiente para adicionar mais unidades."
                item.quantidade += quantidade
                return f"Quantidade de {produto.nome} atualizada no carrinho!"

        self.itens.append(ItemCarrinho(produto, quantidade))
        return f"{produto.nome} adicionado ao carrinho!"

    def calcular_total(self) -> float:
        return sum(item.calcular_subtotal() for item in self.itens)

    def finalizar_compra(self) -> tuple[bool, float]:
        if not self.itens:
            return False, 0.0
        
        total = self.calcular_total()
        # Dá baixa no estoque de cada produto
        for item in self.itens:
            item.produto.remover_estoque(item.quantidade)
        
        self.itens.clear()
        return True, total


class Mercado:
    def __init__(self, nome: str):
        self.nome = nome
        self.produtos: dict[int, Produto] = {}

    def cadastrar_produto(self, produto: Produto) -> bool:
        if produto.codigo in self.produtos:
            return False
        self.produtos[produto.codigo] = produto
        return True

    def listar_produtos(self) -> list[Produto]:
        return list(self.produtos.values())
