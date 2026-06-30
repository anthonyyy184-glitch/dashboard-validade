import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

# Configuração da página para o padrão Dark Premium
st.set_page_config(page_title="Central de Validades Premium", layout="wide")

# FORÇAR MODO ESCURO COMPLETO E CORRIGIR SETINHA DO CELULAR
st.markdown("""
<style>
/* 1. Muda o fundo geral do app para escuro */
.stApp { 
    background-color: #0E1117; 
    color: #FFFFFF; 
}

/* 2. Força a barra lateral a ficar escura */
[data-testid="stSidebar"] { 
    background-color: #111827 !important; 
}

/* 3. CORREÇÃO DA SETINHA DO CELULAR */
[data-testid="stSidebarCollapseButton"] button {
    background-color: #1F2937 !important;
    color: #FFFFFF !important;
    border: 1px solid #4B5563 !important;
    border-radius: 50% !important;
}

[data-testid="stSidebarCollapseButton"] svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
}

h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { 
    color: #FFFFFF !important; 
}

small, [data-testid="stWidgetMarkdownHint"] p { 
    color: #9CA3AF !important; 
}

[data-testid="stFileUploaderDropzone"] { 
    background-color: #1F2937 !important; 
    border: 2px dashed #4B5563 !important; 
}
[data-testid="stFileUploaderDropzone"] div { 
    color: #FFFFFF !important; 
}
[data-testid="stFileUploaderDropzone"] button { 
    background-color: #374151 !important; 
    color: #FFFFFF !important; 
}

.stButton>button {
    background-color: #10B981 !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 10px 20px !important;
}

.metric-card {
    background-color: #1F2937;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #EF4444;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
.metric-title { color: #9CA3AF !important; font-size: 14px; font-weight: bold; text-transform: uppercase; }
.metric-value { color: #FFFFFF !important; font-size: 28px; font-weight: bold; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Central de Validades e Estoque")
st.caption("Gerenciamento dinâmico e monitoramento de lotes via planilha")
st.write("---")

aba_selecionada = st.sidebar.radio("📂 Navegação do Sistema", ["📊 Dashboard de Visão Geral", "✏️ Gerenciador / Editor de Dados"])

# --- PASSO 1: CONVERSOR DE JSON PARA EXCEL ---
st.markdown("### 🔄 Passo 1: Converter JSON do Aplicativo para Excel")
arquivo_json = st.file_uploader("📥 Envie o arquivo .json do seu aplicativo aqui", type=["json"], key="json_uploader")

if arquivo_json is not None:
    try:
        dados = json.load(arquivo_json)
        if 'products' in dados:
            lista_produtos = dados['products']
            linhas = []
            
            for p in lista_produtos:
                nome = str(p.get('name', 'Produto Sem Nome')).strip()
                codigo = str(p.get('barcode', 'Sem Código')).strip()
                
                validade_crua = p.get('expiryDate', '')
                if not validade_crua:
                    validade_crua = datetime.now().strftime('%Y-%m-%d')
                else:
                    if 'T' in str(validade_crua):
                        validade_crua = str(validade_crua).split('T')[0]
                
                # MAPEAMENTO DA QUANTIDADE: Tenta encontrar qualquer variação de nome de chave usada no Flutter
                qtd = 1
                for chave_possivel in ['quantity', 'qtd', 'amount', 'count', 'quantidade', 'stock']:
                    if chave_possivel in p and p[chave_possivel] is not None:
                        try:
                            valor_capturado = int(float(p[chave_possivel]))
                            if valor_capturado > 0:
                                qtd = valor_capturado
                                break
                        except:
                            pass
                
                linhas.append({
                    'Produto': nome,
                    'Código de Barras': codigo,
                    'Data de Validade': validade_crua,
                    'Quantidade': qtd
                })
            
            df_converte = pd.DataFrame(linhas)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_converte.to_excel(writer, index=False, sheet_name='Validades')
            
            st.success("✅ JSON processado com sucesso!")
            st.download_button(
                label="📥 Baixar Banco de Dados em formato Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name="tabela_validade_convertida.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Erro ao processar o JSON: {e}")

st.write("---")

# --- PASSO 2: UPLOAD DA TABELA CERTINHA E EXIBIÇÃO ---
st.markdown("### 📊 Passo 2: Carregar a Tabela Excel (.xlsx) no Sistema")
arquivo_excel = st.file_uploader("📥 Envie a tabela Excel convertida (.xlsx) para liberar os KPIs", type=["xlsx"], key="excel_uploader")

if arquivo_excel is not None:
    try:
        df_excel = pd.read_excel(arquivo_excel)
        
        # Garante a formatação sem destruir os dados reais gerados no passo anterior
        df_excel['Quantidade'] = pd.to_numeric(df_excel['Quantidade'], errors='coerce').fillna(1).astype(int)
        df_excel['Data de Validade'] = pd.to_datetime(df_excel['Data de Validade'], errors='coerce')

        if aba_selecionada == "📊 Dashboard de Visão Geral":
            df_calculo = df_excel.copy()
            hoje = pd.to_datetime(datetime.now().date())
            df_calculo['Dias_Para_Vencer'] = (df_calculo['Data de Validade'] - hoje).dt.days

            col1, col2, col3, col4 = st.columns(4)
            
            vencidos = int(df_calculo[df_calculo['Dias_Para_Vencer'] < 0]['Quantidade'].sum())
            critico = int(df_calculo[(df_calculo['Dias_Para_Vencer'] >= 0) & (df_calculo['Dias_Para_Vencer'] <= 7)]['Quantidade'].sum())
            atencao = int(df_calculo[(df_calculo['Dias_Para_Vencer'] > 7) & (df_calculo['Dias_Para_Vencer'] <= 30)]['Quantidade'].sum())
            total_lotes = len(df_calculo)

            with col1: st.markdown(f'<div class="metric-card"><div class="metric-title">🚨 Já Vencidos</div><div class="metric-value">{vencidos} itens</div></div>', unsafe_allow_html=True)
            with col2: st.markdown(f'<div class="metric-card" style="border-left-color: #F59E0B;"><div class="metric-title">⚠️ Urgente (7 dias)</div><div class="metric-value">{critico} itens</div></div>', unsafe_allow_html=True)
            with col3: st.markdown(f'<div class="metric-card" style="border-left-color: #10B981;"><div class="metric-title">📅 Atenção (30 dias)</div><div class="metric-value">{atencao} itens</div></div>', unsafe_allow_html=True)
            with col4: st.markdown(f'<div class="metric-card" style="border-left-color: #3B82F6;"><div class="metric-title">📦 Total de Lotes</div><div class="metric-value">{total_lotes} cadastros</div></div>', unsafe_allow_html=True)

            st.markdown("### 📋 Lista Geral de Monitoramento")
            df_visual = df_calculo.copy()
            df_visual['Data Formatada'] = df_visual['Data de Validade'].dt.strftime('%d/%m/%Y')
            df_visual = df_visual.sort_values(by='Dias_Para_Vencer')[['Produto', 'Código de Barras', 'Data Formatada', 'Quantidade', 'Dias_Para_Vencer']]
            df_visual.columns = ['Produto', 'Código de Barras', 'Data de Validade', 'Qtd no Estoque', 'Dias Restantes']
            st.dataframe(df_visual, use_container_width=True, hide_index=True)

        elif aba_selecionada == "✏️ Gerenciador / Editor de Dados":
            st.subheader("✏️ Edição Dinâmica da Planilha")
            
            df_edit_view = df_excel.copy()
            df_edit_view['Data de Validade'] = df_edit_view['Data de Validade'].dt.strftime('%Y-%m-%d')

            df_editado = st.data_editor(
                df_edit_view,
                column_config={
                    "Produto": st.column_config.TextColumn("Nome do Produto", required=True, width="medium"),
                    "Código de Barras": st.column_config.TextColumn("Código de Barras", required=True),
                    "Data de Validade": st.column_config.TextColumn("Validade (AAAA-MM-DD)", required=True),
                    "Quantidade": st.column_config.NumberColumn("Quantidade", min_value=1, default=1, step=1)
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True
            )

            st.write("---")
            st.subheader("💾 Salvar Planilha Atualizada")
            
            buffer_salvar = io.BytesIO()
            with pd.ExcelWriter(buffer_salvar, engine='openpyxl') as writer:
                df_editado.to_excel(writer, index=False, sheet_name='Validades')
                
            st.download_button(
                label="📥 Baixar Planilha Excel Modificada",
                data=buffer_salvar.getvalue(),
                file_name="tabela_validade_atualizada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Erro ao ler a tabela Excel: {e}")
else:
    st.info("👋 Aguardando o upload da tabela Excel (.xlsx) no Passo 2.")
