import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Configuração da página para o padrão Dark Premium
st.set_page_config(page_title="Central de Validades", layout="wide")

# Forçar o tema escuro direto no código para evitar textos invisíveis
st.markdown("""
    <style>
    /* Muda o fundo geral do app para escuro */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    /* Garante que todos os textos e títulos fiquem brancos/claros */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
    }
    /* Estilização dos cards de métricas */
    .metric-card {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #EF4444;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .metric-title {
        color: #9CA3AF !important;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .metric-value {
        color: #FFFFFF !important;
        font-size: 28px;
        font-weight: bold;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Títulos usando as funções nativas do Streamlit (mais seguro para temas)
st.title("🛡️ Central de Prevenção de Perdas e Validades")
st.caption("Monitore lotes vencendo e evite prejuízos no caixa")
st.write("---")

# --- REPOSITÓRIO E UPLOAD DE DADOS ---
st.sidebar.markdown("## 🔄 Carga de Dados")
arquivo_subido = st.sidebar.file_uploader("📥 Upload do JSON do App de Validade", type=["json"])

dados_carregados = None

if arquivo_subido is not None:
    try:
        dados_carregados = json.load(arquivo_subido)
        st.sidebar.success("✅ App de Validade carregado com sucesso!")
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao ler o arquivo: {e}")

# Se não subirem nada, tenta ler o arquivo padrão de backup (se existir)
if dados_carregados is None:
    try:
        with open("backup_controle_validade_1782571355318.json", 'r', encoding='utf-8') as f:
            dados_carregados = json.load(f)
    except:
        st.info("👋 Olá! Por favor, faça o upload do seu arquivo de backup do aplicativo (.json) na barra lateral para gerar o painel de monitoramento.")

# Processamento dos dados se o JSON estiver carregado
if dados_carregados and 'products' in dados_carregados:
    df_cru = pd.DataFrame(dados_carregados['products'])
    
    # DataFrame limpo para padronizar as colunas e evitar KeyError
    df = pd.DataFrame()
    
    # Mapeamento flexível de colunas (ignora maiúsculas/minúsculas e variações)
    for col in df_cru.columns:
        col_lower = col.lower()
        if 'name' in col_lower or 'produto' in col_lower:
            df['name'] = df_cru[col].astype(str).str.strip()
        elif 'bar' in col_lower or 'cod' in col_lower:
            df['barcode'] = df_cru[col].astype(str).str.strip()
        elif 'exp' in col_lower or 'val' in col_lower or 'dat' in col_lower:
            df['expiryDate'] = pd.to_datetime(df_cru[col], errors='coerce')
        elif 'qua' in col_lower or 'qtd' in col_lower:
            df['quantity'] = pd.to_numeric(df_cru[col], errors='coerce').fillna(0).astype(int)

    # Garantindo colunas padrão caso o JSON falte com algum campo
    if 'name' not in df.columns: df['name'] = "Produto Sem Nome"
    if 'barcode' not in df.columns: df['barcode'] = "Sem Código"
    if 'quantity' not in df.columns: df['quantity'] = 0
    if 'expiryDate' not in df.columns: df['expiryDate'] = pd.to_datetime(datetime.now().date())

    # Calculando quantos dias faltam
