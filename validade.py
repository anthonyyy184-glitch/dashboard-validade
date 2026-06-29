import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Configuração da página para o padrão Dark Premium
st.set_page_config(page_title="Central de Validades", layout="wide")

# Estilização CSS para o modo escuro e cards chamativos
st.markdown("""
    <style>
    .metric-card {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #EF4444;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .metric-title {
        color: #9CA3AF;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: bold;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: #FFFFFF; font-family: Arial, sans-serif; font-weight: 700; margin-bottom: 5px;'>🛡️ Central de Prevenção de Perdas e Validades</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #9CA3AF; margin-bottom: 25px;'>Monitore lotes vencendo e evite prejuízos no caixa</p>", unsafe_allow_html=True)

# --- REPOSITÓRIO E UPLOAD DE DADOS ---
st.sidebar.markdown("<h2 style='color: #FFFFFF;'>🔄 Carga de Dados</h2>", unsafe_allow_html=True)
arquivo_subido = st.sidebar.file_uploader("📥 Upload do JSON do App de Validade", type=["json"])

dados_carregados = None

if arquivo_subido is not None:
    try:
        dados_carregados = json.load(arquivo_subido)
        st.sidebar.success("✅ App de Validade atualizado!")
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao ler o arquivo: {e}")

# Se não subirem nada, tenta ler o arquivo padrão de backup que você tem
if dados_carregados is None:
    try:
        with open("backup_controle_validade_1782571355318.json", 'r', encoding='utf-8') as f:
            dados_carregados = json.load(f)
    except:
        st.warning("⚠️ Aguardando o upload do arquivo JSON para iniciar o monitoramento.")

if dados_carregados and 'products' in dados_carregados:
    # Transformando em DataFrame do Pandas
    df = pd.DataFrame(dados_carregados['products'])
    
    # Tratando as datas de validade
    df['expiryDate'] = pd.to_datetime(df['expiryDate'])
    
    # Calculando quantos dias faltam com base na data de hoje
    hoje = pd.to_datetime(datetime.now().date())
    df['Dias_Para_Vencer'] = (df['expiryDate'] - hoje).dt.days
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)

    # ---- 1. MÉTRICAS DE ALERTA RÁPIDO ----
    col1, col2, col3, col4 = st.columns(4)
    
    vencidos = df[df['Dias_Para_Vencer'] < 0]['quantity'].sum()
    critico = df[(df['Dias_Para_Vencer'] >= 0) & (df['Dias_Para_Vencer'] <= 7)]['quantity'].sum()
    atencao = df[(df['Dias_Para_Vencer'] > 7) & (df['Dias_Para_Vencer'] <= 30)]['quantity'].sum()
    total_lotes = len(df)
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">🚨 Já Vencidos</div><div class="metric-value">{vencidos} itens</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card" style="border-left-color: #F59E0B;"><div class="metric-title">⚠️ Urgente (Até 7 dias)</div><div class="metric-value">{critico} itens</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card" style="border-left-color: #10B981;"><div class="metric-title">📅 Atenção (Até 30 dias)</div><div class="metric-value">{atencao} itens</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card" style="border-left-color: #3B82F6;"><div class="metric-title">📦 Total de Lotes</div><div class="metric-value">{total_lotes} cadastros</div></div>', unsafe_allow_html=True)

    st.write("---")

    # ---- 2. FILTROS INTERATIVOS ----
    st.sidebar.markdown("---")
    status_filtro = st.sidebar.selectbox(
        "Filtrar por Status de Risco:",
        ["Todos", "Já Vencidos", "Crítico (Até 7 dias)", "Atenção (7 a 30 dias)", "Seguro (Mais de 30 dias)"]
    )
    
    if status_filtro == "Já Vencidos":
        df_filtrado = df[df['Dias_Para_Vencer'] < 0]
    elif status_filtro == "Crítico (Até 7 dias)":
        df_filtrado = df[(df['Dias_Para_Vencer'] >= 0) & (df['Dias_Para_Vencer'] <= 7)]
    elif status_filtro == "Atenção (7 a 30 dias)":
        df_filtrado = df[(df['Dias_Para_Vencer'] > 7) & (df['Dias_Para_Vencer'] <= 30)]
    elif status_filtro == "Seguro (Mais de 30 dias)":
        df_filtrado = df[df['Dias_Para_Vencer'] > 30]
    else:
        df_filtrado = df

    # ---- 3. EXIBIÇÃO EM TABELA INTELIGENTE ----
    st.markdown("### 📋 Relatório Detalhado de Lotes")
    
    df_visual = df_filtrado.copy()
    df_visual['Data de Validade'] = df_visual['expiryDate'].dt.strftime('%d/%m/%Y')
    df_visual = df_visual.sort_values(by='Dias_Para_Vencer')
    
    # Organiza colunas para exibição limpa
    df_visual = df_visual[['name', 'barcode', 'Data de Validade', 'quantity', 'Dias_Para_Vencer']]
    df_visual.columns = ['Produto', 'Código de Barras', 'Data de Validade', 'Qtd no Estoque', 'Dias Restantes']
    
    st.dataframe(df_visual, use_container_width=True, hide_index=True)

    # ---- 4. AÇÃO COMERCIAL RECOMENDADA ----
    st.write("---")
    st.markdown("### 💡 Ação Comercial Recomendada (Queima de Estoque)")
    
    df_promocao = df[(df['Dias_Para_Vencer'] >= 0) & (df['Dias_Para_Vencer'] <= 15)]
    if not df_promocao.empty:
        st.info(f"💡 Dica de Gestão: Existem {df_promocao['quantity'].sum()} itens vencendo nos próximos 15 dias. Aplique um desconto agressivo na frente de caixa para recuperar o custo antes do vencimento.")
        df_promocao_vis = df_promocao[['name', 'quantity', 'Dias_Para_Vencer']].rename(columns={'name':'Produto', 'quantity':'Quantidade', 'Dias_Para_Vencer':'Dias Restantes'})
        st.dataframe(df_promocao_vis.sort_values('Dias Restantes'), use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Nenhum produto crítico vencendo nos próximos 15 dias!")

else:
    st.info("Por favor, faça o upload do arquivo JSON na barra lateral para gerar os relatórios.")
