import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

ARQUIVO = "dados.json"


# ---------------------- CLASSES (a lógica) ----------------------
class Produto:
    def __init__(self, nome, preco, estoque):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    def to_dict(self):
        return {"nome": self.nome, "preco": self.preco, "estoque": self.estoque}


class Venda:
    def __init__(self, produto_nome, quantidade, total):
        self.produto_nome = produto_nome
        self.quantidade = quantidade
        self.total = total

    def to_dict(self):
        return {
            "produto_nome": self.produto_nome,
            "quantidade": self.quantidade,
            "total": self.total,
        }


class Mercado:
    def __init__(self):
        self.produtos = []
        self.vendas = []
        self.carregar()

    def cadastrar_produto(self, nome, preco, estoque):
        self.produtos.append(Produto(nome, preco, estoque))
        self.salvar()

    def excluir_produto(self, indice):
        del self.produtos[indice]
        self.salvar()

    def vender(self, indice, quantidade):
        produto = self.produtos[indice]
        if quantidade > produto.estoque:
            raise ValueError(f"Estoque insuficiente! Disponível: {produto.estoque}")
        produto.estoque -= quantidade
        venda = Venda(produto.nome, quantidade, produto.preco * quantidade)
        self.vendas.append(venda)
        self.salvar()
        return venda

    def total_faturado(self):
        return sum(v.total for v in self.vendas)

    def salvar(self):
        dados = {
            "produtos": [p.to_dict() for p in self.produtos],
            "vendas": [v.to_dict() for v in self.vendas],
        }
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def carregar(self):
        if not os.path.exists(ARQUIVO):
            return
        with open(ARQUIVO, encoding="utf-8") as f:
            dados = json.load(f)
        self.produtos = [Produto(**p) for p in dados.get("produtos", [])]
        self.vendas = [Venda(**v) for v in dados.get("vendas", [])]


# ---------------------- INTERFACE (a janela) ----------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Mercado")
        self.geometry("720x480")
        self.mercado = Mercado()

        abas = ttk.Notebook(self)
        abas.pack(fill="both", expand=True, padx=10, pady=10)
        self.aba_produtos = ttk.Frame(abas)
        self.aba_vendas = ttk.Frame(abas)
        abas.add(self.aba_produtos, text="Produtos")
        abas.add(self.aba_vendas, text="Vendas")

        self.montar_produtos()
        self.montar_vendas()
        self.atualizar()

    # ----- aba Produtos -----
    def montar_produtos(self):
        form = ttk.Frame(self.aba_produtos)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Nome").grid(row=0, column=0, padx=5)
        ttk.Label(form, text="Preço").grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Estoque").grid(row=0, column=2, padx=5)

        self.e_nome = ttk.Entry(form, width=25)
        self.e_preco = ttk.Entry(form, width=10)
        self.e_estoque = ttk.Entry(form, width=10)
        self.e_nome.grid(row=1, column=0, padx=5)
        self.e_preco.grid(row=1, column=1, padx=5)
        self.e_estoque.grid(row=1, column=2, padx=5)

        ttk.Button(form, text="Cadastrar", command=self.cadastrar_produto).grid(
            row=1, column=3, padx=5
        )
        ttk.Button(form, text="Excluir selecionado", command=self.excluir_produto).grid(
            row=1, column=4, padx=5
        )

        self.tabela_produtos = ttk.Treeview(
            self.aba_produtos, columns=("nome", "preco", "estoque"), show="headings"
        )
        for col, titulo in (("nome", "Nome"), ("preco", "Preço"), ("estoque", "Estoque")):
            self.tabela_produtos.heading(col, text=titulo)
        self.tabela_produtos.pack(fill="both", expand=True, padx=10, pady=10)

    def cadastrar_produto(self):
        try:
            nome = self.e_nome.get().strip()
            preco = float(self.e_preco.get().replace(",", "."))
            estoque = int(self.e_estoque.get())
            if not nome or preco < 0 or estoque < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Preencha nome, preço e estoque corretamente.")
            return

        self.mercado.cadastrar_produto(nome, preco, estoque)
        for campo in (self.e_nome, self.e_preco, self.e_estoque):
            campo.delete(0, tk.END)
        self.atualizar()

    def excluir_produto(self):
        selecionado = self.tabela_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto na tabela.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o produto selecionado?"):
            self.mercado.excluir_produto(int(selecionado[0]))
            self.atualizar()

    # ----- aba Vendas -----
    def montar_vendas(self):
        form = ttk.Frame(self.aba_vendas)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Produto").grid(row=0, column=0, padx=5)
        ttk.Label(form, text="Quantidade").grid(row=0, column=1, padx=5)

        self.combo_produto = ttk.Combobox(form, state="readonly", width=30)
        self.e_quantidade = ttk.Entry(form, width=10)
        self.combo_produto.grid(row=1, column=0, padx=5)
        self.e_quantidade.grid(row=1, column=1, padx=5)

        ttk.Button(form, text="Vender", command=self.registrar_venda).grid(
            row=1, column=2, padx=5
        )

        self.tabela_vendas = ttk.Treeview(
            self.aba_vendas, columns=("produto", "qtd", "total"), show="headings"
        )
        for col, titulo in (("produto", "Produto"), ("qtd", "Qtd"), ("total", "Total")):
            self.tabela_vendas.heading(col, text=titulo)
        self.tabela_vendas.pack(fill="both", expand=True, padx=10, pady=10)

        self.lbl_total = ttk.Label(self.aba_vendas, font=("Arial", 12, "bold"))
        self.lbl_total.pack(pady=(0, 10))

    def registrar_venda(self):
        indice = self.combo_produto.current()
        if indice < 0:
            messagebox.showwarning("Atenção", "Escolha um produto.")
            return
        try:
            quantidade = int(self.e_quantidade.get())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida.")
            return

        try:
            venda = self.mercado.vender(indice, quantidade)
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return

        messagebox.showinfo("Venda realizada", f"Total: R$ {venda.total:.2f}")
        self.e_quantidade.delete(0, tk.END)
        self.atualizar()

    # ----- atualiza tudo na tela -----
    def atualizar(self):
        self.tabela_produtos.delete(*self.tabela_produtos.get_children())
        for i, p in enumerate(self.mercado.produtos):
            self.tabela_produtos.insert(
                "", tk.END, iid=str(i), values=(p.nome, f"R$ {p.preco:.2f}", p.estoque)
            )

        self.combo_produto["values"] = [
            f"{p.nome} (estoque: {p.estoque})" for p in self.mercado.produtos
        ]
        self.combo_produto.set("")

        self.tabela_vendas.delete(*self.tabela_vendas.get_children())
        for v in self.mercado.vendas:
            self.tabela_vendas.insert(
                "", tk.END, values=(v.produto_nome, v.quantidade, f"R$ {v.total:.2f}")
            )
        self.lbl_total.config(text=f"Total faturado: R$ {self.mercado.total_faturado():.2f}")


if __name__ == "__main__":
    App().mainloop()
