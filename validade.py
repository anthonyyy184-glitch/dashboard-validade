import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Painel de Validades", layout="wide")

st.title("📦 Conversor de Estoque (Modo Foto Estática)")
st.markdown("Este código usa a sua lógica: processa tudo escondido e exibe uma tabela fixa que não reseta.")

with st.sidebar:
    st.header("📂 Importação")
    arquivo_subido = st.file_uploader("Arraste seu arquivo JSON aqui", type=["json"])

if arquivo_subido is not None:
    try:
        # === 1. O MECANISMO ESCONDIDO (Python Puro) ===
        dados = json.load(arquivo_subido)
        lista_produtos = dados.get('products', dados) if isinstance(dados, dict) else dados

        # Dicionário escondido na memória para fazer a contagem sem o Streamlit ver
        contagem_escondida = {}

        for item in lista_produtos:
            codigo = str(item.get('barcode', '')).strip()
            nome = str(item.get('name', 'Produto Sem Nome')).strip()
            
            if codigo and codigo != "None":
                # Se o produto já passou por aqui, soma +1 no papelzinho escondido
                if codigo in contagem_escondida:
                    contagem_escondida[codigo]['Quantidade'] += 1
                else:
                    # Se é a primeira vez, registra com 1
                    contagem_escondida[codigo] = {
                        'Produto': nome,
                        'Código de Barras': codigo,
                        'Quantidade': 1
                    }

        # Transforma o papelzinho de contagem na tabela final
        df_foto = pd.DataFrame(contagem_escondida.values())
        
        # Cria a coluna de validade vazia
        df_foto['Data de Validade'] = '👉 Preencher no Excel'
        df_foto = df_foto[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]


        # === 2. MOSTRAR A "FOTO" NA TELA ===
        st.subheader("📋 Tabela Consolidada (Pronta para Cópia/Download)")
        st.success(f"Sucesso! O mecanismo processou {len(df_foto)} produtos únicos.")
        
        # st.table funciona como uma foto fixa. Não dá bug de reset porque ela não é editável na tela!
        st.table(df_foto)

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
else:
    st.info("Aguardando o arquivo JSON para acionar o mecanismo...")
