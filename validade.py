import streamlit as st
import pandas as pd
import json

# Configuração visual limpa
st.set_page_config(page_title="Painel de Validades", layout="wide")

st.title("📦 Editor de Estoque & Validades")
st.markdown("Suba o arquivo JSON e altere as quantidades e validades diretamente na tabela.")

# Inicializa o estoque salvo na memória para não perder as edições
if 'dados_originais' not in st.session_state:
    st.session_state.dados_originais = None

# Barra lateral apenas para o Upload
with st.sidebar:
    st.header("📂 Importação")
    arquivo_subido = st.file_uploader("Arraste seu arquivo JSON aqui", type=["json"])
    
    if st.button("🔄 Resetar / Subir Novo Arquivo"):
        st.session_state.dados_originais = None
        st.rerun()

# Se o usuário subiu o arquivo e a memória está vazia, carrega o arquivo
if arquivo_subido is not None and st.session_state.dados_originais is None:
    try:
        dados = json.load(arquivo_subido)
        lista_produtos = dados.get('products', dados) if isinstance(dados, dict) else dados
        
        linhas = []
        for item in lista_produtos:
            linhas.append({
                'Produto': str(item.get('name', 'S/ NOME')).strip(),
                'Código de Barras': str(item.get('barcode', 'S/ CÓDIGO')).strip(),
                'Data de Validade': '', # Campo limpo para ela digitar
                'Quantidade': int(item.get('quantity', 1)) # Pega a quantidade do arquivo (ou 1)
            })
            
        # Salva na memória do Streamlit para congelar o estado inicial
        st.session_state.dados_originais = pd.DataFrame(linhas)
        
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

# Se os dados já estão carregados na memória, mostra na tela para edição
if st.session_state.dados_originais is not None:
    st.subheader("📋 Tabela de Produtos (Clique duas vezes para editar)")
    
    # st.data_editor permite alterar qualquer valor na tela
    estoque_editado = st.data_editor(
        st.session_state.dados_originais,
        use_container_width=True,
        hide_index=True
    )
    
    # Salva o que ela digitou (Quantidade ou Validade) de volta na memória
    st.session_state.dados_originais = estoque_editado
else:
    st.info("Aguardando o upload do arquivo JSON na barra lateral...")
