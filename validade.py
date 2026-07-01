import streamlit as st
import pandas as pd 
import json

st.set_page_config(page_title="Painel de Validades", layout="wide")

st.title("📦 Painel de Validades & Estoque")
st.markdown("Carregue o JSON na barra lateral. O sistema vai unificar e congelar os dados para edição.")

# 1. Inicializa a tabela definitiva na memória se ela não existir
if 'tabela_com_soma' not in st.session_state:
    st.session_state.tabela_com_soma = None

# ==========================================
#          BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("📂 Importação")
    arquivo_subido = st.file_uploader("Arraste seu arquivo JSON aqui", type=["json"])
    
    # Botão para resetar o sistema se quiser subir outro arquivo
    if st.button("🔄 Resetar e Subir Novo Arquivo"):
        st.session_state.tabela_com_soma = None
        st.rerun()

# ==========================================
#        LÓGICA DE CONVERSÃO ISOLADA
# ==========================================
# Só entra aqui se o arquivo foi subido E a tabela ainda não foi calculada
if arquivo_subido is not None and st.session_state.tabela_com_soma is None:
    try:
        dados = json.load(arquivo_subido)
        df_bruto = pd.DataFrame(dados['products'])

        # Limpeza radical de espaços
        df_bruto['barcode'] = df_bruto['barcode'].astype(str).str.strip()
        df_bruto['name'] = df_bruto['name'].astype(str).str.strip()

        # CONTAGEM REAL: Conta quantas vezes cada código de barras aparece no JSON bruto
        df_contagem = df_bruto.groupby('barcode').size().reset_index(name='Quantidade')
        
        # Pega o primeiro nome de cada produto para não duplicar colunas
        df_nomes = df_bruto[['barcode', 'name']].drop_duplicates(subset=['barcode'])
        
        # Junta o nome com a quantidade da contagem real
        df_processado = pd.merge(df_nomes, df_contagem, on='barcode')

        # Formata colunas para o seu padrão antigo
        df_processado = df_processado.rename(columns={'name': 'Produto', 'barcode': 'Código de Barras'})
        df_processado['Data de Validade'] = ''
        df_processado = df_processado[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

        # 🔥 SALVA NA MEMÓRIA E CONGELA. O Python não recalcula mais isso nas atualizações de tela!
        st.session_state.tabela_com_soma = df_processado
        st.success("🎉 Arquivo processado e quantidades somadas com sucesso!")

    except Exception as e:
        st.error(f"Erro no formato do JSON: {e}")

# ==========================================
#          EXIBIÇÃO NA TELA PRINCIPAL
# ==========================================
if st.session_state.tabela_com_soma is not None:
    st.subheader("📋 Tabela de Validades (Pronta para uso)")
    
    # Exibe o editor usando o dado congelado e seguro da memória
    estoque_editado = st.data_editor(
        st.session_state.tabela_com_soma,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )
    
    # Salva as edições de data que a cliente fizer sem quebrar a quantidade
    st.session_state.tabela_com_soma = estoque_editado
else:
    st.info("Aguardando o upload do arquivo JSON na barra lateral para gerar a tabela...")
