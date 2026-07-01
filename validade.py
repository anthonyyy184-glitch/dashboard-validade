import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Configuração da página profissional e larga
st.set_page_config(page_title="Auditor de Validades", layout="wide")

st.title("🛡️ Auditor & Controlador de Validades Inteligente")
st.markdown("Suba o JSON do coletor, compare com o histórico e gerencie seu estoque por categorias.")

# 1. Inicializa os bancos de dados na memória do navegador
if 'estoque_atual' not in st.session_state:
    st.session_state.estoque_atual = None

# ==========================================
#          BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("📂 1. Base Histórica (Excel)")
    arquivo_excel = st.file_uploader("Suba o Excel salvo do mês/semana anterior (Opcional)", type=["xlsx", "csv"])
    
    st.header("📲 2. Coleta Nova (JSON)")
    arquivo_json = st.file_uploader("Arraste o arquivo JSON atual do coletor aqui", type=["json"])
    
    st.markdown("---")
    if st.button("🗑️ Resetar Painel / Novo Inventário"):
        st.session_state.estoque_atual = None
        st.rerun()

# ==========================================
#        LÓGICA DE PROCESSAMENTO & COMPARAÇÃO
# ==========================================
if arquivo_json is not None and st.session_state.estoque_atual is None:
    try:
        # Carrega o JSON novo do coletor
        dados = json.load(arquivo_json)
        lista_produtos = dados.get('products', dados) if isinstance(dados, dict) else dados
        
        novos_itens = []
        for item in lista_produtos:
            novos_itens.append({
                'Produto': str(item.get('name', 'S/ NOME')).strip(),
                'Código de Barras': str(item.get('barcode', 'S/ CÓDIGO')).strip(),
                'Data de Validade': '',
                'Quantidade': int(item.get('quantity', 1)),
                'Status': 'Novo no Coletor'  # Status padrão inicial
            })
        df_novo = pd.DataFrame(novos_itens)

        # Se ela subiu um Excel antigo para comparar...
        if arquivo_excel is not None:
            try:
                if arquivo_excel.name.endswith('.xlsx'):
                    df_antigo = pd.read_excel(arquivo_excel)
                else:
                    df_antigo = pd.read_csv(arquivo_excel)
                
                # Garante que a chave de busca seja texto limpo
                df_antigo['Código de Barras'] = df_antigo['Código de Barras'].astype(str).str.strip()
                
                # Mapeia as validades antigas para os produtos novos não virem em branco
                mapeamento_validade = dict(zip(df_antigo['Código de Barras'], df_antigo['Data de Validade']))
                mapeamento_qtd = dict(zip(df_antigo['Código de Barras'], df_antigo['Quantidade']))
                
                for idx, row in df_novo.iterrows():
                    cb = row['Código de Barras']
                    if cb in mapeamento_validade:
                        df_novo.at[idx, 'Data de Validade'] = mapeamento_validade[cb]
                        df_novo.at[idx, 'Quantidade'] = mapeamento_qtd[cb]
                        df_novo.at[idx, 'Status'] = 'Já Existia'
            except Exception as e:
                st.warning(f"Não consegui ler o Excel antigo para comparar, mostrando apenas o JSON. Erro: {e}")

        st.session_state.estoque_atual = df_novo

    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {e}")

# ==========================================
#          PAINEL PRINCIPAL (INTERFACES E ABAS)
# ==========================================
if st.session_state.estoque_atual is not None:
    df_trabalho = st.session_state.estoque_atual.copy()

    # --- FUNÇÃO DE SEPARAÇÃO POR CATEGORIAS (Sua ideia de organização) ---
    def definir_categoria(nome):
        nome_lower = nome.lower()
        if any(x in nome_lower for x in ['iogurte', 'iog', 'leite', 'danone', 'carolina', 'unibaby', 'batavo', 'requeijao', 'nata']):
            return '🥛 Laticínios & Iogurtes'
        elif any(x in nome_lower for x in ['pao', 'pão', 'bisnag', 'torrada', 'brioche', 'forma', 'seven boys', 'wickbold', 'pullman']):
            return '🍞 Panificação & Pães'
        else:
            return '📦 Outros Produtos'

    df_trabalho['Categoria'] = df_trabalho['Produto'].apply(definir_categoria)

    # --- FUNÇÃO DE CORES (Sua ideia visual de legibilidade + Alerta) ---
    def estilizar_tabela(row):
        estilos = [''] * len(row)
        # Se for um item novo detectado pelo comparador -> Fundo Verde Claro
        if row['Status'] == 'Novo no Coletor':
            return ['background-color: #d4edda; color: #155724; font-weight: bold'] * len(row)
        
        # Alerta Extra: Se tiver validade preenchida e estiver vencendo (Exemplo fictício de lógica)
        val = str(row['Data de Validade']).strip()
        if val and ('/06/' in val or '/2026' in val):  # Filtro simples para o exemplo
            return ['background-color: #f8d7da; color: #721c24;'] * len(row)
            
        return estilos

    # Criando as abas dinâmicas na tela
    categorias_unicas = sorted(df_trabalho['Categoria'].unique())
    abas = st.tabs(categorias_unicas)

    for i, cat in enumerate(categorias_unicas):
        with abas[i]:
            st.markdown(f"### Gerenciamento de {cat}")
            df_filtrado = df_trabalho[df_trabalho['Categoria'] == cat].drop(columns=['Categoria'])
            
            # Excel interativo na tela
            dados_editados = st.data_editor(
                df_filtrado,
                use_container_width=True,
                hide_index=True,
                key=f"editor_{cat}"
            )
            
            # Atualiza o banco principal com o que ela digitou na aba específica
            for idx, row in dados_editados.iterrows():
                cb = row['Código de Barras']
                st.session_state.estoque_atual.loc[st.session_state.estoque_atual['Código de Barras'] == cb, 'Data de Validade'] = row['Data de Validade']
                st.session_state.estoque_atual.loc[st.session_state.estoque_atual['Código de Barras'] == cb, 'Quantidade'] = row['Quantidade']

    # --- BOTÃO DE SALVAMENTO (Baixar o Excel Atualizado) ---
    st.markdown("---")
    st.subheader("💾 3. Salvar Trabalho")
    st.markdown("Clique no botão abaixo para exportar a planilha corrigida. Guarde esse arquivo para usar como comparação no próximo inventário!")
    
    # Converte o dataframe atualizado para formato Excel na memória para download rápido
    @st.cache_data
    def converter_para_excel(df):
        return df.to_csv(index=False).encode('utf-8')
        
    csv_final = converter_para_excel(st.session_state.estoque_atual)
    
    st.download_button(
        label="📥 Baixar Planilha de Validades Corrigida (.CSV / Excel)",
        data=csv_final,
        file_name=f"inventario_validades_{datetime.now().strftime('%d-%m-%Y')}.csv",
        mime="text/csv"
    )

else:
    st.info("💡 Como usar: Vá na barra lateral esquerda, insira o JSON do seu coletor (e o Excel do inventário passado se tiver). O sistema montará o painel automaticamente!")
