import streamlit as st
import pandas as pd
import json

st.title("Conversor de JSON para Estoque")

# 1. Cria o campo para você arrastar o seu arquivo JSON
arquivo_subido = st.file_uploader("Arraste ou selecione seu arquivo JSON aqui", type=["json"])

if arquivo_subido is not None:
    try:
        # 2. Carrega os dados direto do JSON que você subiu
        dados = json.load(arquivo_subido)

        # 3. Transforma a lista de produtos em um DataFrame do Pandas
        df_bruto = pd.DataFrame(dados['products'])

        # 4. Agrupa e conta quantas vezes cada código de barras aparece
        df_contagem = df_bruto.groupby('barcode').size().reset_index(name='Quantidade')

        # 5. Pega os nomes dos produtos removendo duplicados
        df_nomes = df_bruto[['barcode', 'name']].drop_duplicates(subset=['barcode'])

        # 6. Junta o nome com a quantidade certa
        df_final = pd.merge(df_nomes, df_contagem, on='barcode')

        # 7. Renomeia as colunas para o seu padrão
        df_final = df_final.rename(columns={
            'name': 'Produto',
            'barcode': 'Código de Barras'
        })

        # 8. Adiciona a coluna de validade vazia
        df_final['Data de Validade'] = ''
        
        # Organiza a ordem das colunas
        df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

        # Mostra o resultado na tela do Streamlit
        st.write("### Dados Convertidos com Sucesso!")
        st.dataframe(df_final)
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo JSON: {e}")
    
else:
    st.info("Aguardando o upload do arquivo JSON para começar...")
