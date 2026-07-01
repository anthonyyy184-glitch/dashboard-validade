import streamlit as st
import pandas as pd
import json

# Configuração da página antiga: limpa e larga
st.set_page_config(page_title="Painel de Validades", layout="wide")

st.title("📦 Painel de Validades & Estoque")
st.markdown("Faça o upload do arquivo JSON na barra lateral para gerar e editar a tabela de validades.")

# ==========================================
#          BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("📂 Importação de Dados")
    
    # Botão de Upload do arquivo JSON original do seu coletor
    arquivo_subido = st.file_uploader("Arraste seu arquivo JSON aqui", type=["json"])
    
    st.markdown("---")
    st.markdown("🤖 *Dashboard de Validades v2.0*")

# ==========================================
#        PROCESSAMENTO E TELA PRINCIPAL
# ==========================================
if arquivo_subido is not None:
    try:
        # 1. Carrega o JSON bruto vindo do uploader da barra lateral
        dados = json.load(arquivo_subido)
        df_bruto = pd.DataFrame(dados['products'])

        # 2. Limpeza dos dados de códigos e nomes para evitar falhas
        df_bruto['barcode'] = df_bruto['barcode'].astype(str).str.strip()
        df_bruto['name'] = df_bruto['name'].astype(str).str.strip()

        # 3. Garante que a quantidade seja lida como número e soma de forma real
        if 'quantity' in df_bruto.columns:
            df_bruto['quantity'] = pd.to_numeric(df_bruto['quantity'], errors='coerce').fillna(1)
        else:
            df_bruto['quantity'] = 1

        # 4. Agrupa e unifica o estoque pelo código de barras
        df_unificado = df_bruto.groupby('barcode').agg({
            'name': 'first',       # Mantém o nome do produto
            'quantity': 'sum'      # Soma todas as linhas/bipes repetidos
        }).reset_index()

        # 5. Formata a tabela para o padrão visual do seu dashboard
        df_final = df_unificado.rename(columns={
            'name': 'Produto',
            'barcode': 'Código de Barras',
            'quantity': 'Quantidade'
        })
        
        # Cria a coluna de validade vazia pronta para preenchimento
        df_final['Data de Validade'] = ''
        
        # Organiza a ordem oficial das colunas na tela
        df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

        # 6. Exibe a tabela interativa e editável na tela principal
        st.subheader("📋 Dados Carregados do Coletor")
        st.markdown("💡 *Dica: Você pode dar um duplo clique em 'Data de Validade' ou na 'Quantidade' para ajustar as informações na tela.*")
        
        estoque_editado = st.data_editor(
            df_final,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo JSON. Detalhes: {e}")
        
else:
    # Mensagem limpa enquanto aguarda o arquivo ser colocado na barra lateral
    st.info("Aguardando o upload do arquivo JSON na barra lateral para carregar a tabela...")
