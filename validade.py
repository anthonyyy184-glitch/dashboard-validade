import streamlit as st
import pandas as pd
import json

# Configuração da página idêntica ao seu visual limpo antigo
st.set_page_config(page_title="Validades", layout="wide")

st.title("📦 Conversor de Estoque & Validades")
st.markdown("Arraste o arquivo **JSON** extraído do seu coletor abaixo.")

# Campo de upload discreto
arquivo_subido = st.file_uploader("", type=["json"])

if arquivo_subido is not None:
    try:
        # 1. Carrega o JSON bruto
        dados = json.load(arquivo_subido)

        # 2. Transforma a lista de produtos em tabela
        df_bruto = pd.DataFrame(dados['products'])

        # 3. Garante que a coluna de quantidade seja número para podermos somar
        if 'quantity' in df_bruto.columns:
            df_bruto['quantity'] = pd.to_numeric(df_bruto['quantity'], errors='coerce').fillna(1)
        else:
            df_bruto['quantity'] = 1

        # 4. AQUI ESTÁ A CORREÇÃO: Agrupa pelo código de barras e SOMA as quantidades reais
        df_contagem = df_bruto.groupby('barcode')['quantity'].sum().reset_index(name='Quantidade')
        
        # 5. Pega os nomes correspondentes tirando os duplicados
        df_nomes = df_bruto[['barcode', 'name']].drop_duplicates(subset=['barcode'])
        
        # 6. Junta o nome do produto com a quantidade somada
        df_final = pd.merge(df_nomes, df_contagem, on='barcode')

        # 7. Renomeia as colunas para o seu padrão visual
        df_final = df_final.rename(columns={
            'name': 'Produto',
            'barcode': 'Código de Barras'
        })

        # 8. Cria a coluna de validade limpa para você usar
        df_final['Data de Validade'] = ''
        
        # Organiza a ordem exata das colunas
        df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

        # 9. Mostra a tabela limpa na tela, sem mensagens poluindo
        st.markdown("---")
        st.dataframe(df_final, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error("Erro ao processar o JSON. Certifique-se de que é o arquivo bruto do coletor.")
else:
    st.info("Aguardando o upload do arquivo JSON...")
