import streamlit as st
import pandas as pd

st.set_page_config(page_title="Coletor de Validades", layout="wide")

st.title("📲 Coletor de Estoque & Validades Digital")
st.markdown("Bipe ou altere as quantidades diretamente na tabela abaixo.")

# Inicializa o estoque na memória do navegador
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade'])

# --- ÁREA DE BIPAGEM ---
# O formulário garante que o "Enter" do leitor envie o dado na hora
with st.form(key='formulario_bipagem', clear_on_submit=True):
    codigo_bipado = st.text_input("Bipe o Código de Barras aqui:", key="input_codigo")
    # CORRIGIDO: Comando correto do botão de envio do formulário
    botao_enviar = st.form_submit_button("Adicionar Produto")

if botao_enviar and codigo_bipado:
    codigo_limpo = str(codigo_bipado).strip()
    
    if codigo_limpo != "":
        df_atual = st.session_state.estoque
        
        if codigo_limpo in df_atual['Código de Barras'].values:
            # Se já existe, soma +1 em cima do valor atual (mesmo se alterado na mão)
            st.session_state.estoque.loc[df_atual['Código de Barras'] == codigo_limpo, 'Quantidade'] += 1
            st.toast(f"Código {codigo_limpo} já estava na lista. Somado +1!", icon="➕")
        else:
            # Produto novo começa com quantidade 1
            nova_linha = pd.DataFrame([{
                'Produto': f'Produto Novo ({codigo_limpo})',
                'Código de Barras': codigo_limpo,
                'Data de Validade': '',
                'Quantidade': 1
            }])
            st.session_state.estoque = pd.concat([df_atual, nova_linha], ignore_index=True)
            st.toast(f"Novo código {codigo_limpo} adicionado!", icon="✨")

st.markdown("---")

# --- TABELA EDITÁVEL ---
st.subheader("📋 Estoque em Tempo Real (Clique para alterar o que quiser)")

if not st.session_state.estoque.empty:
    # Tabela 100% editável para alterar Nome, Validade e Quantidade na mão
    estoque_editado = st.data_editor(
        st.session_state.estoque,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )
    
    # Salva as edições manuais que ela fizer na tabela
    st.session_state.estoque = estoque_editado

    if st.button("🗑 Limpar Todo o Estoque"):
        st.session_state.estoque = pd.DataFrame(columns=['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade'])
        st.rerun()
else:
    st.info("Aguardando o primeiro bipe...")
