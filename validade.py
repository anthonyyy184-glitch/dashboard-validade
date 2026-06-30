import streamlit as st
import pandas as pd
import json

# Mantém a sua interface limpa e elegante de antes
st.set_page_config(page_title="Validades", layout="wide")

st.title("📦 Conversor de Estoque & Validades")
st.markdown("Arraste o arquivo **JSON** extraído do seu coletor abaixo.")

# Upload de arquivo discreto
arquivo_subido = st.file_uploader("", type=["json"])

if arquivo_subido is not None:
    try:
        # 1. Carrega o JSON bruto enviado por você
        dados = json.load(arquivo_subido)

        # 2. Transforma os produtos mapeados em uma tabela inicial do Pandas
        df_bruto = pd.DataFrame(dados['products'])

        # 3. Garante que a coluna de quantidade seja tratada como número antes de somar
        if 'quantity' in df_bruto.columns:
            df_bruto['quantity'] = pd.to_numeric(df_bruto['quantity'], errors='coerce').fillna(1)
        else:
            df_bruto['quantity'] = 1

        # 4. NOVA ETAPA: Agrupa por código de barras, traz o primeiro nome e SOMA as quantidades
        df_unificado = df_bruto.groupby('barcode').agg({
            'name': 'first',       # Mantém o nome do produto
            'quantity': 'sum'      # Soma todas as quantidades repetidas (1+1+1...)
        }).reset_index()

        # 5. Renomeia as colunas para o seu padrão visual antigo
        df_final = df_unificado.rename(columns={
            'name': 'Produto',
            'barcode': 'Código de Barras',
            'quantity': 'Quantidade'
        })

        # 6. Cria a coluna de validade vazia pronta para ser preenchida
        df_final['Data de Validade'] = ''
        
        # Organiza a ordem exata das colunas na tela
        df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

        # 7. Mostra a tabela final perfeitamente unificada
        st.markdown("---")
        st.dataframe(df_final, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error("Erro ao processar o JSON. Certifique-se de que é o arquivo bruto do coletor.")
else:
    st.info("Aguardando o upload do arquivo JSON...")
