import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

st.set_page_config(page_title="Conversor Reverso de Validades", layout="wide")

st.title("🔄 Conversor Reverso de Estoque & Validades")
st.markdown("Interface calibrada com **Autodetecção Inteligente** para ler qualquer formato do seu coletor.")

# Criando as duas abas na tela principal
aba_explosao, aba_consolidacao = st.tabs(["💥 Passo 1: Explodir JSON", "🧮 Passo 2: Consolidar & Somar"])

# ==========================================
#        ABA 1: EXPLODIR O JSON BRUTO
# ==========================================
with aba_explosao:
    st.header("1️⃣ Gerar Excel Desagregado (Linha por Linha)")
    st.markdown("Suba o JSON do coletor aqui. O sistema vai rastrear as quantidades e multiplicar as linhas.")
    
    json_bruto = st.file_uploader("Arraste o arquivo JSON do coletor aqui", type=["json"], key="uploader_json")
    
    if json_bruto is not None:
        try:
            dados = json.load(json_bruto)
            
            # 🛠️ A SOLUÇÃO DEFINITIVA: AUTODETECÇÃO DE TABELAS
            # O Python vai caçar os dados pelo que eles são, não pelo nome da chave!
            lista_produtos = []
            lista_itens = []
            
            if isinstance(dados, dict):
                for chave, valor in dados.items():
                    if isinstance(valor, list) and len(valor) > 0:
                        amostra = valor[0]
                        if isinstance(amostra, dict):
                            # Se tem 'name', guarda na base de produtos
                            if 'name' in amostra:
                                lista_produtos.extend(valor)
                            # Se tem 'quantity' ou 'expiryDate', guarda na base de lotes/quantidades reais
                            if 'quantity' in amostra or 'expiryDate' in amostra or 'storeId' in amostra:
                                lista_itens.extend(valor)
            elif isinstance(dados, list):
                lista_produtos = dados
                lista_itens = dados
            
            # Fallback de segurança
            if not lista_itens and lista_produtos:
                lista_itens = lista_produtos

            # Mapa ultra-rápido para cruzar o código de barras com o nome correto
            mapa_nomes = {}
            for p in lista_produtos:
                cb = str(p.get('barcode', '')).strip()
                if cb:
                    mapa_nomes[cb] = str(p.get('name', 'S/ NOME')).strip()
            
            linhas_explodidas = []
            
            # Varre os itens rastreados
            for item in lista_itens:
                codigo = str(item.get('barcode', '')).strip()
                if not codigo or codigo == "None":
                    continue
                    
                nome = mapa_nomes.get(codigo, str(item.get('name', f"Produto ({codigo})")).strip())
                
                # Tratamento Inteligente de Data: Se o app manda 2026-07-16, vira 16/07/2026
                data_original = item.get('expiryDate', '')
                data_formatada = ''
                if data_original and str(data_original) != "None":
                    try:
                        data_limpa = data_original.split('T')[0]
                        dt = datetime.strptime(data_limpa, '%Y-%m-%d')
                        data_formatada = dt.strftime('%d/%m/%Y')
                    except:
                        data_formatada = str(data_original)

                # Tratamento da Quantidade (para não travar e explodir a quantia certa)
                try:
                    qtd_original = int(float(item.get('quantity', 1)))
                except:
                    qtd_original = 1
                
                # 🔥 O MOTOR DE EXPLOSÃO: O Danone tá com 7? Ele gera 7 linhas idênticas!
                for _ in range(qtd_original):
                    linhas_explodidas.append({
                        'Produto': nome,
                        'Código de Barras': codigo,
                        'Data de Validade': data_formatada
                    })
            
            df_explodido = pd.DataFrame(linhas_explodidas)
            
            if not df_explodido.empty:
                st.success(f"🎉 SUCESSO ABSOLUTO! O sistema rastreou os dados e gerou {len(df_explodido)} linhas.")
                st.dataframe(df_explodido, use_container_width=True, hide_index=True)
                
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
            else:
                st.error("O arquivo foi lido, mas não encontramos produtos com código de barras válido.")
            
        except Exception as e:
            st.error(f"Erro ao processar o JSON: {e}")

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
            
            df_para_agrupar['Código de Barras'] = df_para_agrupar['Código de Barras'].astype(str).str.strip()
            df_para_agrupar['Produto'] = df_para_agrupar['Produto'].astype(str).str.strip()
            
            if 'Data de Validade' not in df_para_agrupar.columns:
                df_para_agrupar['Data de Validade'] = ''
            else:
                df_para_agrupar['Data de Validade'] = df_para_agrupar['Data de Validade'].fillna('').astype(str).str.strip()

            # MOTOR DE SOMA: Agrupa os códigos e datas e soma
            df_consolidado = df_para_agrupar.groupby(['Código de Barras', 'Data de Validade']).agg({
                'Produto': 'first', 
                'Código de Barras': 'size' 
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
                label="📥 Baixar Planilha de Estoque Final Somada (.xlsx)",
                data=excel_final_bin,
                file_name=f"relatorio_estoque_final_{datetime.now().strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Erro ao consolidar as somas do Excel: {e}")
