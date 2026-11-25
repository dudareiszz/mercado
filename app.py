import streamlit as st
from modelos import Mercado, Produto, Carrinho

# Configuração da página
st.set_page_config(page_title="Sistema de Mercado", page_icon="🛒", layout="wide")

# Inicialização dos objetos na sessão (Persiste os dados entre cliques)
if "mercado" not in st.session_state:
    mercado = Mercado("Supermercado POO")
    # Produtos iniciais para teste
    mercado.cadastrar_produto(Produto(101, "Arroz 5kg", 25.90, 15))
    mercado.cadastrar_produto(Produto(102, "Feijão 1kg", 8.50, 20))
    mercado.cadastrar_produto(Produto(103, "Leite Integral 1L", 4.80, 30))
    st.session_state.mercado = mercado

if "carrinho" not in st.session_state:
    st.session_state.carrinho = Carrinho()

# Atalhos para facilitar a leitura do código
mercado: Mercado = st.session_state.mercado
carrinho: Carrinho = st.session_state.carrinho

st.title(f"🛒 {mercado.nome}")

# Menu lateral de navegação
aba = st.sidebar.radio("Navegação", ["Frente de Caixa (PDV)", "Estoque e Cadastro"])

# --- TELA 1: FRENTE DE CAIXA ---
if aba == "Frente de Caixa (PDV)":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Produtos Disponíveis")
        produtos = mercado.listar_produtos()
        
        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            for p in produtos:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                    c1.write(f"**{p.nome}** (Cód: {p.codigo})")
                    c2.write(f"R$ {p.preco:.2f}")
                    c3.write(f"Estoque: {p.estoque}")
                    
                    qtd = c4.number_input("Qtd", min_value=1, max_value=max(1, p.estoque), key=f"qtd_{p.codigo}", label_visibility="collapsed")
                    if c4.button("Adicionar", key=f"btn_{p.codigo}", disabled=(p.estoque == 0)):
                        msg = carrinho.adicionar_item(p, qtd)
                        st.toast(msg)
                        st.rerun()

    with col2:
        st.subheader("🛍️ Carrinho Atual")
        if not carrinho.itens:
            st.write("O carrinho está vazio.")
        else:
            for item in carrinho.itens:
                st.write(f"- {item.quantidade}x **{item.produto.nome}** — R$ {item.calcular_subtotal():.2f}")
            
            st.divider()
            total = carrinho.calcular_total()
            st.metric("Total a Pagar", f"R$ {total:.2f}")
            
            if st.button("✅ Finalizar Compra", type="primary", use_container_width=True):
                sucesso, valor_pago = carrinho.finalizar_compra()
                if sucesso:
                    st.success(f"Venda concluída! Total: R$ {valor_pago:.2f}")
                    st.rerun()

# --- TELA 2: GESTÃO DE ESTOQUE ---
elif aba == "Estoque e Cadastro":
    st.subheader("Cadastrar Novo Produto")
    
    with st.form("form_cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        codigo = col1.number_input("Código do Produto", min_value=1, step=1)
        nome = col2.text_input("Nome do Produto")
        preco = col1.number_input("Preço (R$)", min_value=0.01, format="%.2f")
        estoque = col2.number_input("Estoque Inicial", min_value=1, step=1)
        
        submitted = st.form_submit_button("Salvar Produto")
        if submitted:
            if not nome.strip():
                st.error("O nome do produto é obrigatório.")
            else:
                novo_prod = Produto(int(codigo), nome, float(preco), int(estoque))
                if mercado.cadastrar_produto(novo_prod):
                    st.success(f"Produto '{nome}' cadastrado com sucesso!")
                else:
                    st.error("Já existe um produto com esse código.")

    st.divider()
    st.subheader("Visão Geral do Estoque")
    dados_tabela = [
        {"Código": p.codigo, "Produto": p.nome, "Preço (R$)": f"{p.preco:.2f}", "Estoque": p.estoque}
        for p in mercado.listar_produtos()
    ]
    st.dataframe(dados_tabela, use_container_width=True)
