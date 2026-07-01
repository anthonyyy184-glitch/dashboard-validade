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
    st.markdown("Suba o JSON do coletor aqui. Se um produto tiver quantidade **7**, o sistema vai criar **7 linhas** dele no Excel.")
    
    json_bruto = st.file_uploader("Arraste o arquivo JSON do coletor aqui", type=["json"], key="uploader_json")
    
    if json_bruto is not None:
        try:
            dados = json.load(json_bruto)
            lista_produtos = dados.get('products', dados) if isinstance(dados, dict) else dados
            
            linhas_explodidas = []
            
            for item in lista_produtos:
                nome = str(item.get('name', 'S/ NOME')).strip()
                codigo = str(item.get('barcode', 'S/ CÓDIGO')).strip()
                
                # 🛠️ AJUSTE DA SUA LÓGICA: Conversão ultra segura para garantir o loop correto
                try:
                    qtd_original = int(float(item.get('quantity', 1)))
                except:
                    qtd_original = 1
                
                # REPETIÇÃO FORÇADA: Roda o loop exatamente o número de vezes da quantidade
                for _ in range(qtd_original):
                    linhas_explodidas.append({
                        'Produto': nome,
                        'Código de Barras': codigo,
                        'Data de Validade': '' # Em branco para preencher no Excel
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
    st.markdown("Suba o arquivo Excel editado aqui. O sistema vai agrupar os produtos repetidos e fazer a soma automática de todas as linhas.")
    
    excel_para_somar = st.file_uploader("Suba o arquivo Excel (.xlsx) aqui", type=["xlsx"], key="uploader_excel")
    
    if excel_para_somar is not None:
        try:
            df_para_agrupar = pd.read_excel(excel_para_somar)
            
            # Limpeza padrão de segurança
            df_para_agrupar['Código de Barras'] = df_para_agrupar['Código de Barras'].astype(str).str.strip()
            df_para_agrupar['Produto'] = df_para_agrupar['Produto'].astype(str).str.strip()
            
            if 'Data de Validade' not in df_para_agrupar.columns:
                df_para_agrupar['Data de Validade'] = ''
            else:
                df_para_agrupar['Data de Validade'] = df_para_agrupar['Data de Validade'].fillna('').astype(str).str.strip()

            # MOTOR DE SOMA DEFINITIVO:
            # Agrupa por Código e Validade, e conta quantas linhas repetidas existem no Excel (fazendo a soma)
            df_consolidado = df_para_agrupar.groupby(['Código de Barras', 'Data de Validade']).agg({
                'Produto': 'first', 
                'Código de Barras': 'size' # Conta a quantidade de linhas físicas idênticas
            }).rename(columns={'Código de Barras': 'Quantidade'}).reset_index()
            
            df_final = df_consolidado[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]
            
            st.success(f"🧮 Estoque unificado! As linhas duplicadas foram somadas e geraram {len(df_final)} produtos únicos.")
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            def gerar_excel_final(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Estoque_Somado')
                return output.getvalue()
                
            excel_final_bin = gerar_excel_final(df_final)
            
            st.download_button(
                label="📥 Baixar Planilha de Estoque Final Somado (.xlsx)",
                data=excel_final_bin,
                file_name=f"relatorio_estoque_final_{datetime.now().strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Erro ao consolidar as somas do Excel: {e}")
