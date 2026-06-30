import streamlit as st
import pandas as pd

st.title("Painel de Validades")

# Cria o campo de upload aceitando o CSV exportado
arquivo_subido = st.file_uploader("Arraste ou selecione seu arquivo CSV aqui", type=["csv"])

if arquivo_subido is not None:
    try:
        # Lê o CSV garantindo que ele entenda a formatação padrão do Pandas/Streamlit
        df_bruto = pd.read_csv(arquivo_subido)
        
        # Correção crucial: Remove a primeira coluna se ela for o índice sem nome exportado pelo Streamlit
        if df_bruto.columns[0] == "" or "Unnamed" in str(df_bruto.columns[0]):
            df_bruto = df_bruto.drop(columns=[df_bruto.columns[0]])

        # Garante que todas as colunas necessárias existam (mesmo se vierem vazias)
        colunas_obrigatorias = ['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']
        for col in colunas_obrigatorias:
            if col not in df_bruto.columns:
                df_bruto[col] = ""

        # Limpa valores nulos para não aparecer "NaN" na tela
        df_bruto['Data de Validade'] = df_bruto['Data de Validade'].fillna('')
        df_bruto['Quantidade'] = df_bruto['Quantidade'].fillna(1)

        # Organiza na ordem certa
        df_final = df_bruto[colunas_obrigatorias]

        # Mostra o resultado final na tela
        st.write("### Dados Carregados com Sucesso!")
        st.dataframe(df_final)
        
        st.success(f"Total de {len(df_final)} itens carregados prontos para validação.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo exportado: {e}")
    
else:
    st.info("Aguardando o upload do arquivo de exportação para começar...")
