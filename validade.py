import streamlit as st
import pandas as pd

st.title("Painel de Validades")

# 1. Cria o campo de upload no Streamlit aceitando CSV ou Excel
arquivo_subido = st.file_uploader("Arraste ou selecione seu arquivo CSV aqui", type=["csv", "xlsx"])

if arquivo_subido is not None:
    try:
        # 2. Lê o arquivo carregado (como CSV)
        df_bruto = pd.read_csv(arquivo_subido)
        
        # Se o CSV vier com uma coluna de índice sem nome (ex: coluna 0, 1, 2...), removemos ela
        if df_bruto.columns[0] == "" or "Unnamed" in df_bruto.columns[0]:
            df_bruto = df_bruto.iloc[:, 1:]

        # 3. Garante que as colunas necessárias existem
        colunas_necessarias = ['Produto', 'Código de Barras', 'Quantidade']
        
        # Pequeno ajuste caso os nomes das colunas estejam ligeiramente diferentes
        # Mapeia colunas conhecidas para o padrão interno
        mapeamento = {
            'name': 'Produto',
            'barcode': 'Código de Barras',
            'quantity': 'Quantidade',
            'name ': 'Produto',
            'barcode ': 'Código de Barras'
        }
        df_bruto = df_bruto.rename(columns=mapeamento)

        # 4. Cria a coluna de Data de Validade se ela não existir ou estiver vazia
        if 'Data de Validade' not in df_bruto.columns:
            df_bruto['Data de Validade'] = ''
        else:
            # Preenche valores nulos com texto vazio para ficar limpo na tela
            df_bruto['Data de Validade'] = df_bruto['Data de Validade'].fillna('')

        # 5. Organiza a ordem das colunas para exibição
        df_final = df_bruto[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

        # 6. Mostra o resultado final na tela
        st.write("### Dados Carregados com Sucesso!")
        st.dataframe(df_final)
        
        st.success(f"Total de {len(df_final)} itens carregados prontos para validação.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
    
else:
    st.info("Aguardando o upload do arquivo de exportação para começar...")
