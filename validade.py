import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Configuração da página para o padrão Dark Premium
st.set_page_config(page_title="Central de Validades Premium", layout="wide")

# FORÇAR MODO ESCURO COMPLETO (FUNDO PRINCIPAL + BARRA LATERAL + COMPONENTES)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #111827 !important; }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { color: #FFFFFF !important; }
    small, [data-testid="stWidgetMarkdownHint"] p { color: #9CA3AF !important; }
    [data-testid="stFileUploaderDropzone"] { background-color: #1F2937 !important; border: 2px dashed #4B5563 !important; }
    [data-testid="stFileUploaderDropzone"] div { color: #FFFFFF !important; }
    [data-testid="stFileUploaderDropzone"] button { background-color: #374151 !important; color: #FFFFFF !important; border: 1px solid #4B5563 !important; }
    
    /* Customização dos botões de ação */
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

st.title("🛡️ Sistema de Gestão de Validades e Perdas")
st.caption("Visualize, edite, adicione ou exclua lotes de produtos em tempo real")
st.write("---")

# --- NAVEGAÇÃO ENTRE ABAS ---
aba_selecionada = st.sidebar.radio("📂 Navegação do Sistema", ["📊 Dashboard de Visão Geral", "✏️ Gerenciador / Editor de Dados"])
st.sidebar.write("---")

# --- CARGA DE DADOS NA BARRA LATERAL ---
st.sidebar.markdown("## 🔄 Carga de Dados")
arquivo_subido = st.sidebar.file_uploader("📥 Upload do JSON do App de Validade", type=["json"])

# Inicializa os dados na sessão se um arquivo for carregado
if arquivo_subido is not None and 'df_produtos' not in st.session_state:
    try:
        dados = json.load(arquivo_subido)
        if 'products' in dados:
            df_cru = pd.DataFrame(dados['products'])
            df_limpo = pd.DataFrame()
            
            # Mapeamento flexível de colunas
            for col in df_cru.columns:
                col_lower = col.lower()
                if 'name' in col_lower or 'produto' in col_lower:
                    df_limpo['name'] = df_cru[col].astype(str).str.strip()
                elif 'bar' in col_lower or 'cod' in col_lower:
                    df_limpo['barcode'] = df_cru[col].astype(str).str.strip()
                elif 'exp' in col_lower or 'val' in col_lower or 'dat' in col_lower:
                    # Salva como string ISO para manter compatibilidade no editor
                    df_limpo['expiryDate'] = pd.to_datetime(df_cru[col], errors='coerce').dt.strftime('%Y-%m-%dT00:00:00.000')
                elif 'qua' in col_lower or 'qtd' in col_lower:
                    df_limpo['quantity'] = pd.to_numeric(df_cru[col], errors='coerce').fillna(0).astype(int)
            
            # Preenche colunas obrigatórias vazias
            if 'name' not in df_limpo.columns: df_limpo['name'] = "Produto Sem Nome"
            if 'barcode' not in df_limpo.columns: df_limpo['barcode'] = "Sem Código"
            if 'quantity' not in df_limpo.columns: df_limpo['quantity'] = 0
            if 'expiryDate' not in df_limpo.columns: df_limpo['expiryDate'] = datetime.now().strftime('%Y-%m-%dT00:00:00.000')
            
            st.session_state['df_produtos'] = df_limpo
            st.sidebar.success("✅ Arquivo carregado!")
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao ler arquivo: {e}")

# Se o usuário limpou o uploader, limpa a sessão para pedir novo arquivo
if arquivo_subido is None and 'df_produtos' in st.session_state:
    del st.session_state['df_produtos']

# --- CONTEÚDO PRINCIPAL ---
if 'df_produtos' in st.session_state:
    df_atual = st.session_state['df_produtos']

    # ABA 1: VISUALIZAÇÃO E ESTATÍSTICAS
    if aba_selecionada == "📊 Dashboard de Visão Geral":
        # Converte datas temporariamente para cálculo de dias
        df_calculo = df_atual.copy()
        df_calculo['expiryDate'] = pd.to_datetime(df_calculo['expiryDate'])
        hoje = pd.to_datetime(datetime.now().date())
        df_calculo['Dias_Para_Vencer'] = (df_calculo['expiryDate'] - hoje).dt.days

        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        vencidos = df_calculo[df_calculo['Dias_Para_Vencer'] < 0]['quantity'].sum()
        critico = df_calculo[(df_calculo['Dias_Para_Vencer'] >= 0) & (df_calculo['Dias_Para_Vencer'] <= 7)]['quantity'].sum()
        atencao = df_calculo[(df_calculo['Dias_Para_Vencer'] > 7) & (df_calculo['Dias_Para_Vencer'] <= 30)]['quantity'].sum()
        total_lotes = len(df_calculo)

        with col1: st.markdown(f'<div class="metric-card"><div class="metric-title">🚨 Já Vencidos</div><div class="metric-value">{vencidos} itens</div></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="metric-card" style="border-left-color: #F59E0B;"><div class="metric-title">⚠️ Urgente (7 dias)</div><div class="metric-value">{critico} itens</div></div>', unsafe_allow_html=True)
        with col3: st.markdown(f'<div class="metric-card" style="border-left-color: #10B981;"><div class="metric-title">📅 Atenção (30 dias)</div><div class="metric-value">{atencao} itens</div></div>', unsafe_allow_html=True)
        with col4: st.markdown(f'<div class="metric-card" style="border-left-color: #3B82F6;"><div class="metric-title">📦 Total de Lotes</div><div class="metric-value">{total_lotes} cadastros</div></div>', unsafe_allow_html=True)

        st.markdown("### 📋 Lista Geral de Monitoramento")
        df_visual = df_calculo.copy()
        df_visual['Data de Validade'] = df_visual['expiryDate'].dt.strftime('%d/%m/%Y')
        df_visual = df_visual.sort_values(by='Dias_Para_Vencer')[['name', 'barcode', 'Data de Validade', 'quantity', 'Dias_Para_Vencer']]
        df_visual.columns = ['Produto', 'Código de Barras', 'Data de Validade', 'Qtd no Estoque', 'Dias Restantes']
        st.dataframe(df_visual, use_container_width=True, hide_index=True)

    # ABA 2: EDITOR E EXPORTADOR DE DADOS
    elif aba_selecionada == "✏️ Gerenciador / Editor de Dados":
        st.subheader("✏️ Edição Dinâmica do Banco de Dados")
        st.info("💡 Como usar: Dê duplo clique em qualquer célula para alterar o texto/quantidade. Para deletar uma linha, selecione-a e aperte 'Delete' no seu teclado. Use a última linha vazia para ADICIONAR novos produtos.")
        
        # O st.data_editor cria a planilha interativa mágica que permite adicionar, deletar e editar linhas
        df_editado = st.data_editor(
            df_atual,
            column_config={
                "name": st.column_config.TextColumn("Nome do Produto", required=True, width="medium"),
                "barcode": st.column_config.TextColumn("Código de Barras", required=True),
                "expiryDate": st.column_config.TextColumn("Data de Validade (AAAA-MM-DD)", required=True),
                "quantity": st.column_config.NumberColumn("Quantidade", min_value=0, default=0, step=1)
            },
            num_rows="dynamic", # Ativa botões de adicionar/remover linhas automaticamente
            use_container_width=True,
            hide_index=True
        )

        # Atualiza o estado da sessão com os novos valores digitados
        st.session_state['df_produtos'] = df_editado

        st.write("---")
        st.subheader("💾 Exportar e Salvar Novo Arquivo")
        
        # Botão para preparar o download do novo JSON formatado exatamente igual ao app deles
        if st.button("🔄 Estruturar e Gerar Novo JSON"):
            lista_produtos = df_editado.to_dict(orient='records')
            json_final = {"products": lista_produtos}
            json_string = json.dumps(json_final, indent=2, ensure_ascii=False)
            
            # Cria o botão de download nativo do navegador
            st.download_button(
                label="📥 Baixar Novo Arquivo JSON Atualizado",
                data=json_string,
                file_name=f"backup_validade_atualizado_{datetime.now().strftime('%d%m%Y_%H%M')}.json",
                mime="application/json"
            )
            st.success("🎉 JSON gerado! Clique no botão acima para fazer o download para o seu computador/celular.")

else:
    st.info("👋 Olá! Por favor, faça o upload do seu arquivo de backup do aplicativo (.json) na barra lateral para liberar as telas de monitoramento e edição.")
