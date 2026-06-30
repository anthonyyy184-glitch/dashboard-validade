import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Validades", layout="wide")
st.title("📦 Teste de Soma por Etapas")

# ETAPA 1: Upload
arquivo_subido = st.file_uploader("Suba o seu arquivo JSON original do coletor aqui", type=["json"])

if arquivo_subido is not None:
    try:
        dados = json.load(arquivo_subido)
        df_bruto = pd.DataFrame(dados['products'])
        
        # Limpa textos e garante que a contagem base seja 1 por linha
        df_bruto['barcode'] = df_bruto['barcode'].astype(str).str.strip()
        df_bruto['name'] = df_bruto['name'].astype(str).str.strip()
        df_bruto['quantity'] = 1  # Força cada linha do coletor a valer 1 item
        
        st.subheader("📋 Etapa 1: Dados Brutos do Coletor")
        st.write(f"O coletor enviou um total de **{len(df_bruto)}** linhas de bipes.")
        st.dataframe(df_bruto[['name', 'barcode', 'quantity']], use_container_width=True)
        
        st.markdown("---")
        st.subheader("🧮 Etapa 2: Unificação")
        st.write("Clique no botão abaixo para ver o Python caçar as linhas repetidas e somar:")
        
        if st.button("Somar e Agrupar Agora", type="primary"):
            # Agrupa e conta quantas vezes o código de barras se repete
            df_unificado = df_bruto.groupby('barcode').agg({
                'name': 'first',
                'quantity': 'sum'  # Conta quantos bipes idênticos foram feitos
            }).reset_index()
            
            df_final = df_unificado.rename(columns={
                'name': 'Produto',
                'barcode': 'Código de Barras',
                'quantity': 'Quantidade'
            })
            df_final['Data de Validade'] = ''
            df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]
            
            st.success(f"Feito! As {len(df_bruto)} linhas viraram {len(df_final)} produtos únicos.")
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"Erro: {e}")
