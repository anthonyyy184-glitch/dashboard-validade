import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

st.set_page_config(page_title="Conversor Reverso de Validades", layout="wide")

st.title("🔄 Conversor Reverso de Estoque & Validades")
st.markdown("Interface dividida em duas etapas independentes para garantir a precisão total dos dados.")

# Criando as duas abas na tela principal
aba_explosao, aba_consolidacao = st.tabs(["💥 Passo 1: Explodir JSON", "🧮 Passo 2: Consolidar & Somar"])

# ==========================================
#        ABA 1: EXPLODIR O JSON BRUTO
# ==========================================
with aba_explosao:
    st.header("1️⃣ Gerar Excel Desagregado (Linha por Linha)")
    st.markdown("Suba o JSON do coletor aqui. Se um produto tiver quantidade **16**, o sistema vai criar **16 linhas** dele no Excel.")
    
    json_bruto = st.file_uploader("Arraste o arquivo JSON do coletor aqui", type=["json"], key="uploader_json")
    
    if json_bruto is not None:
        try:
            dados = json.load(json_bruto)
            lista_produtos = dados.get('products', dados) if isinstance(dados, dict) else dados
            
            linhas_explodidas = []
            
            for item in lista_produtos:
                nome = str(item.get('name', 'S/ NOME')).strip()
                codigo = str(item.get('barcode', 'S/ CÓDIGO')).strip()
                # Pega a quantidade que está no arquivo (ex: 16)
                qtd_original = int(item.get('quantity', 1))
                
                # REPETIÇÃO FORÇADA: Roda um loop para criar X linhas físicas na planilha
                for _ in range(qtd_original):
                    linhas_explodidas.append({
                        'Produto': nome,
                        'Código de Barras': codigo,
                        'Data de Validade': '' # Deixa em branco para preencher no Excel se quiser
                    })
            
            df_explodido = pd.DataFrame(linhas_explodidas)
            
            st.success(f"🎉 Sucesso! O arquivo JSON foi transformado em uma planilha com {len(df_explodido)} linhas totais.")
            st.dataframe(df_explodido, use_container_width=True, hide_index=True)
            
            # Função para converter para Excel real (.xlsx)
            def gerar_excel_bruto(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Itens_Explodidos')
                return output.getvalue()
            
            excel_bruto_bin = gerar_excel_bruto(df_explodido)
            
            st.download_button(
                label="📥 Baixar Excel Bruto Explodido (.xlsx)",
                data=excel_bruto_bin,
                file_name=f"base_bruta_explodida_{datetime.now().strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Erro ao explodir o JSON: {e}")

# ==========================================
#        ABA 2: CONSOLIDAR E SOMAR
# ==========================================
with aba_consolidacao:
    st.header("2️⃣ Somar e Unificar o Excel")
    st.markdown("Suba o arquivo Excel (pode ser o que você baixou no Passo 1, mesmo que tenha preenchido as validades nele). O sistema vai agrupar os repetidos e fazer a soma final.")
    
    excel_para_somar = st.file_uploader("Suba o arquivo Excel (.xlsx) aqui", type=["xlsx"], key="uploader_excel")
    
    if excel_para_somar is not None:
        try:
            # Lê o Excel que tem as linhas repetidas
            df_para_agrupar = pd.read_excel(excel_para_somar)
            
            # Limpeza padrão de segurança
            df_para_agrupar['Código de Barras'] = df_para_agrupar['Código de Barras'].astype(str).str.strip()
            df_para_agrupar['Produto'] = df_para_agrupar['Produto'].astype(str).str.strip()
            
            # Se a coluna Data de Validade não existir, cria ela vazia
            if 'Data de Validade' not in df_para_agrupar.columns:
                df_para_agrupar['Data de Validade'] = ''
            else:
                df_para_agrupar['Data de Validade'] = df_para_agrupar['Data de Validade'].fillna('').astype(str).str.strip()

            # MOTOR DE SOMA DEFINITIVO:
            # Agrupa por Código de Barras E Data de Validade (assim se o mesmo pão tiver duas validades, ele gera duas linhas com as somas separadas de cada lote!)
            df_consolidado = df_para_agrupar.groupby(['Código de Barras', 'Data de Validade']).agg({
                'Produto': 'first', # Mantém o nome
                'Código de Barras': 'size' # Conta quantas linhas repetidas existem (Soma 1+1+1...)
            }).rename(columns={'Código de Barras': 'Quantidade'}).reset_index()
            
            # Organiza a ordem das colunas pro formato que você gosta
            df_final = df_consolidado[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]
            
            st.success(f"🧮 Estoque unificado! As linhas duplicadas foram somadas e geraram {len(df_final)} produtos únicos.")
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            # Função para exportar o arquivo final somado
            def gerar_excel_final(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Estoque_Somado')
                return output.getvalue()
                
            excel_final_bin = gerar_excel_final(df_final)
            
            st.download_button(
                label="📥 Baixar Relatório de Estoque Final Somado (.xlsx)",
                data=excel_final_bin,
                file_name=f"relatorio_estoque_final_{datetime.now().strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Erro ao consolidar as somas do Excel: {e}")
