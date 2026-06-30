import streamlit as st
import pandas as pd
import json

# Interface limpa antiga
st.set_page_config(page_title="Validades", layout="wide")

st.title("📦 Conversor de Estoque & Validades")
st.markdown("Arraste o arquivo **JSON** extraído do seu coletor abaixo.")

arquivo_subido = st.file_uploader("", type=["json"])

if arquivo_subido is not None:
    try:
        # 1. Carrega o JSON bruto
        dados = json.load(arquivo_subido)
        df_bruto = pd.DataFrame(dados['products'])

        # 2. LIMPEZA DOS DADOS (Remove espaços invisíveis que impedem a soma)
        df_bruto['barcode'] = df_bruto['barcode'].astype(str).str.strip()
        df_bruto['name'] = df_bruto['name'].astype(str).str.strip()

        # 3. Garante que a quantidade seja lida como número
        if 'quantity' in df_bruto.columns:
            df_bruto['quantity'] = pd.to_numeric(df_bruto['quantity'], errors='coerce').fillna(1)
        else:
            df_bruto['quantity'] = 1

        # 4. AGRUPAMENTO E SOMA REAL
        # Agrupa pelo código de barras, pega o primeiro nome limpo e soma as quantidades
        df_unificado = df_bruto.groupby('barcode').agg({
            'name': 'first',       
            'quantity': 'sum'      
        }).reset_index()

        # 5. Renomeia para o padrão visual antigo
        df_final = df_unificado.rename(columns={
            'name': 'Produto',
            'barcode': 'Código de Barras',
            'quantity': 'Quantidade'
        })

        # 6. Cria a coluna de validade vazia
        df_final['Data de Validade'] = ''
        
        # Reordena as colunas exatamente no seu padrão
        df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

        # 7. Exibe a tabela perfeitamente limpa
        st.markdown("---")
        st.dataframe(df_final
