import streamlit as st
import pandas as pd
import json

# Configuração visual (Interface limpa e larga)
st.set_page_config(page_title="Validades", layout="wide")

st.title("📦 Conversor de Estoque por Etapas")
st.markdown("Siga os passos abaixo para unificar o seu inventário.")

# --- ETAPA 1: CARREGAMENTO DOS DADOS ---
st.markdown("### 1️⃣ Carregar Arquivo")
arquivo_subido = st.file_uploader("Arraste o arquivo JSON bruto do seu coletor aqui", type=["json"])

if arquivo_subido is not None:
    try:
        # Carrega os dados originais sem mexer em nada
        dados = json.load(arquivo_subido)
        df_bruto = pd.DataFrame(dados['products'])
        
        # Garante que as colunas críticas estão limpas e sem espaços invisíveis
        df_bruto['barcode'] = df_bruto['barcode'].astype(str).str.strip()
        df_bruto['name'] = df_bruto['name'].astype(str).str.strip()
        
        # Define a quantidade base como 1 para cada linha caso não exista
        if 'quantity' in df_bruto.columns:
            df_bruto['quantity'] = pd.to_numeric(df_bruto['quantity'], errors='coerce').fillna(1)
        else:
            df_bruto['quantity'] = 1

        # Mostra os dados brutos exatamente como vieram do coletor
        st.info(f"✔ Arquivo carregado com sucesso! Encontradas {len(df_bruto)} linhas brutas no coletor.")
        
        with st.expander("Visualizar dados originais do coletor"):
            st.dataframe(df_bruto[['name', 'barcode']], use_container_width=True)

        st.markdown("---")

        # --- ETAPA 2: PROCESSAMENTO E SOMA ---
        st.markdown("### 2️⃣ Consolidação de Estoque")
        st.markdown("Clique no botão abaixo para juntar os produtos repetidos e somar as quantidades.")

        # O botão força a execução da soma apenas quando você clica
        if st.button("🔄 Unificar e Somar Produtos", type="primary"):
            
            # Executa o agrupamento somando as quantidades de itens idênticos
            df_unificado = df_bruto.groupby('barcode').agg({
                'name': 'first',       # Pega o nome do produto
                'quantity': 'sum'      # Soma todas as linhas iguais (1 + 1 + 1...)
            }).reset_index()

            # Renomeia para o padrão visual do seu dashboard antigo
            df_final = df_unificado.rename(columns={
                'name': 'Produto',
                'barcode': 'Código de Barras',
                'quantity': 'Quantidade'
            })

            # Adiciona a coluna de validade vazia para preenchimento posterior
            df_final['Data de Validade'] = ''
            
            # Organiza a ordem final das colunas
            df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

            # Resultado final na tela
            st.success(f"🎉 Sucesso! Os produtos foram unificados em {len(df_final)} itens únicos com estoques somados.")
            st.dataframe(df_final, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo. Verifique o formato do JSON. Detalhes: {e}")
else:
    st.info("Aguardando o upload do arquivo JSON para iniciar a Etapa 1.")
