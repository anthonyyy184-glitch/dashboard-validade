import streamlit as st
import pandas as pd
import json

st.title("Conversor de JSON para Estoque")

# 1. Cria o campo de upload no Streamlit
arquivo_subido = st.file_uploader("Arraste ou selecione seu arquivo JSON aqui", type=["json"])

if arquivo_subido is not None:
    # 2. Carrega os dados diretamente do arquivo que você subiu na tela
    dados = json.load(arquivo_subido)

    # 3. Transforma a lista de produtos em um DataFrame do Pandas
    df_bruto = pd.DataFrame(dados['products'])

    # 4. Mágica do agrupamento: Contar quantas vezes cada código de barras aparece
    df_contagem = df_bruto.groupby('barcode').size().reset_index(name='Quantidade')

    # 5. Pegar os nomes dos produtos (removendo as duplicatas para não repetir)
    df_nomes = df_bruto[['barcode', 'name']].drop_duplicates(subset=['barcode'])

    # 6. Juntar o nome do produto com a quantidade certa que contamos
    df_final = pd.merge(df_nomes, df_contagem, on='barcode')

    # 7. Renomear as colunas para o padrão
    df_final = df_final.rename(columns={
        'name': 'Produto',
        'barcode': 'Código de Barras'
    })

    # 8. Adiciona a coluna de validade vazia e organiza
    df_final['Data de Validade'] = ''
    df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

    # Mostra o resultado na tela do Streamlit para você ver se deu certo!
    st.write("### Dados Convertidos com Sucesso!")
    st.dataframe(df_final)
    
else:
    st.info("Aguardando o upload do arquivo JSON para começar...")
