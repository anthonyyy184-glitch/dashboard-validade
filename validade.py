import streamlit as st
import pandas as pd

# Configuração da página para ficar bem larga e aproveitar o espaço
st.set_page_config(page_title="Controle de Validades", layout="wide")

st.title("📲 Sistema Coletor de Estoque & Validades")
st.markdown("Use o leitor de código de barras ou digite as informações diretamente na tabela abaixo.")

# Inicializa o estoque na memória do navegador
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade'])

# ==========================================
#          BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("📥 Entrada de Produtos")
    st.markdown("Mantenha o cursor na caixa abaixo para bipar em sequência.")
    
    # Formulário de bipes na barra lateral
    with st.form(key='formulario_bipagem', clear_on_submit=True):
        codigo_bipado = st.text_input("Bipe o Código de Barras aqui:", key="input_codigo")
        botao_enviar = st.form_submit_button("Adicionar Produto ➕")

    st.markdown("---")
    st.header("⚙ Ações do Sistema")
    
    # Botão para limpar tudo com confirmação visual
    if st.button("🗑 Limpar Todo o Estoque", type="secondary"):
        st.session_state.estoque = pd.DataFrame(columns=['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade'])
        st.toast("Estoque reiniciado do zero!", icon="🗑")
        st.rerun()

# Lógica de inserção ao bipar (Executada nos bastidores)
if botao_enviar and codigo_bipado:
    codigo_limpo = str(codigo_bipado).strip()
    
    if codigo_limpo != "":
        df_atual = st.session_state.estoque
        
        # Se o produto já foi bipado, soma +1
        if codigo_limpo in df_atual['Código de Barras'].values:
            st.session_state.estoque.loc[df_atual['Código de Barras'] == codigo_limpo, 'Quantidade'] += 1
            st.toast(f"Código {codigo_limpo}: Quantidade +1", icon="➕")
        else:
            # Se for novo, cria a linha iniciando com 1
            nova_linha = pd.DataFrame([{
                'Produto': f'Produto Novo ({codigo_limpo})',
                'Código de Barras': codigo_limpo,
                'Data de Validade': '',
                'Quantidade': 1
            }])
            st.session_state.estoque = pd.concat([df_atual, nova_linha], ignore_index=True)
            st.toast(f"Novo código {codigo_limpo} adicionado!", icon="✨")

# ==========================================
#          PAINEL PRINCIPAL (EDITOR)
# ==========================================
st.subheader("📋 Painel de Estoque Atualizado")

if not st.session_state.estoque.empty:
    st.markdown("💡 *Dica: Dê um duplo clique em qualquer célula para alterar o Nome, a Validade ou a Quantidade manualmente.*")
    
    # Editor de dados interativo na tela principal
    estoque_editado = st.data_editor(
        st.session_state.estoque,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"  # Permite deletar linhas se a cliente errar o bipe
    )
    
    # Mantém os dados da memória sincronizados com o que foi digitado na tela
    st.session_state.estoque = estoque_editado
else:
    st.info("Nenhum item bipado. Use a barra lateral para começar a preencher o estoque!")
