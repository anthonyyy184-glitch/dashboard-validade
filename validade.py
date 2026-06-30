import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Configura a página para o visual antigo/limpo que você prefere
st.set_page_config(page_title="Validades", layout="wide")
st.title("📦 Painel de Validades do Estoque")

try:
    # 2. Cria a conexão direta com o Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 3. Puxa os dados da planilha em tempo real
    # (Você bota o link da sua planilha no arquivo de configuração do Streamlit)
    df = conn.read()
    
    # 4. Mostra a tabela limpa, direto na tela
    st.markdown("---")
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Erro ao conectar com a planilha do Google. Verifique as credenciais.")
