import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

st.set_page_config(page_title="Dashboard de Validades", layout="wide")

st.title("📊 Dashboard Inteligente de Validades")
st.markdown("Faça o upload do JSON do coletor. O sistema soma os repetidos e gera os indicadores automaticamente.")

# ==========================================
#        UPLOAD DO ARQUIVO
# ==========================================
arquivo_json = st.file_uploader("📥 Suba o arquivo JSON do coletor aqui", type=["json"])

if arquivo_json is not None:
    try:
        dados = json.load(arquivo_json)
        
        # 1. RASTREIO E AUTODETECÇÃO DOS DADOS
        lista_produtos = []
        lista_itens = []
        
        if isinstance(dados, dict):
            for chave, valor in dados.items():
                if isinstance(valor, list) and len(valor) > 0:
                    amostra = valor[0]
                    if isinstance(amostra, dict):
                        if 'name' in amostra:
                            lista_produtos.extend(valor)
                        if 'quantity' in amostra or 'expiryDate' in amostra:
                            lista_itens.extend(valor)
        elif isinstance(dados, list):
            lista_produtos = dados
            lista_itens = dados
            
        if not lista_itens and lista_produtos:
            lista_itens = lista_produtos

        # Mapa para achar o Nome do produto pelo Código
        mapa_nomes = {}
        for p in lista_produtos:
            cb = str(p.get('barcode', '')).strip()
            if cb:
                mapa_nomes[cb] = str(p.get('name', 'S/ NOME')).strip()
        
        # 2. PROCESSAMENTO E CÁLCULO DE DATAS
        linhas = []
        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for item in lista_itens:
            codigo = str(item.get('barcode', '')).strip()
            if not codigo or codigo == "None":
                continue
                
            nome = mapa_nomes.get(codigo, str(item.get('name', f"Produto ({codigo})")).strip())
            
            try:
                qtd = int(float(item.get('quantity', 1)))
            except:
                qtd = 1
                
            # Lógica de cálculo de validade e Status (KPIs)
            data_original = item.get('expiryDate', '')
            data_formatada = ""
            status = "⚪ Sem Data"
            dias_vencimento = 9999 # Valor alto para itens sem data irem pro final da fila
            
            if data_original and str(data_original) != "None":
                try:
                    data_limpa = data_original.split('T')[0]
                    dt = datetime.strptime(data_limpa, '%Y-%m-%d')
                    data_formatada = dt.strftime('%d/%m/%Y')
                    
                    # Calcula a diferença de dias
                    diferenca = (dt - hoje).days
                    dias_vencimento = diferenca
                    
                    # Classificação Inteligente
                    if diferenca < 0:
                        status = "🔴 Vencido"
                    elif diferenca <= 15:
                        status = "🟠 Vence em ≤ 15 dias"
                    elif diferenca <= 30:
                        status = "🟡 Vence em ≤ 30 dias"
                    else:
                        status = "🟢 No Prazo"
                except:
                    data_formatada = str(data_original)
            
            linhas.append({
                'Produto': nome,
                'Código de Barras': codigo,
                'Data de Validade': data_formatada,
                'Quantidade': qtd,
                'Status': status,
                '_dias_ordenacao': dias_vencimento # Oculto, usado só para organizar a tabela
            })
            
        df_bruto = pd.DataFrame(linhas)
        
        if not df_bruto.empty:
            # 3. MOTOR DE SOMA E CONSOLIDAÇÃO INTERNA (O fim do passo 1 e passo 2 separados!)
            df_consolidado = df_bruto.groupby(
                ['Código de Barras', 'Produto', 'Data de Validade', 'Status', '_dias_ordenacao'], dropna=False
            )['Quantidade'].sum().reset_index()
            
            # Ordena a tabela para mostrar o que vence primeiro no topo
            df_consolidado = df_consolidado.sort_values(by=['_dias_ordenacao', 'Produto'])
            
            # Tabela final pronta para exibição (sem a coluna de lógica oculta)
            df_exibicao = df_consolidado.drop(columns=['_dias_ordenacao'])
            df_exibicao = df_exibicao[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade', 'Status']]

            # ==========================================
            #        KPIs (INDICADORES NA TELA)
            # ==========================================
            st.markdown("---")
            st.markdown("### 📈 Raio-X do Estoque")
            
            total_itens = df_consolidado['Quantidade'].sum()
            qtd_vencidos = df_consolidado[df_consolidado['Status'] == '🔴 Vencido']['Quantidade'].sum()
            qtd_alerta = df_consolidado[df_consolidado['Status'] == '🟠 Vence em ≤ 15 dias']['Quantidade'].sum()
            qtd_sem_data = df_consolidado[df_consolidado['Status'] == '⚪ Sem Data']['Quantidade'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Total de Produtos Físicos", f"{total_itens}")
            col2.metric("🔴 Produtos Vencidos", f"{qtd_vencidos}")
            col3.metric("🟠 Vencem em 15 dias", f"{qtd_alerta}")
            col4.metric("⚪ Sem Data (Auditar)", f"{qtd_sem_data}")
            
            st.markdown("---")

            # ==========================================
            #        VISÕES DO DASHBOARD (ABAS)
            # ==========================================
            aba_critica, aba_geral = st.tabs(["🚨 Alertas (Queima de Estoque)", "📋 Estoque Completo Consolidado"])
            
            with aba_critica:
                st.markdown("#### Produtos que exigem ação imediata (Vencidos ou Vencendo logo)")
                # Filtra apenas os problemáticos
                df_critico = df_exibicao[df_exibicao['Status'].isin(['🔴 Vencido', '🟠 Vence em ≤ 15 dias'])]
                
                if not df_critico.empty:
                    st.dataframe(df_critico, use_container_width=True, hide_index=True)
                else:
                    st.success("🎉 Sensacional! Você não tem nenhum produto vencido ou perto do vencimento.")
                    
            with aba_geral:
                st.markdown("#### Todos os produtos unificados com soma de quantidades perfeitas")
                # Exibe a tabela onde tudo já foi somado pelo Python internamente
                st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

            # ==========================================
            #        BOTÃO DE DOWNLOAD ÚNICO
            # ==========================================
            st.markdown("---")
            st.subheader("💾 Baixar Relatório Final")
            st.markdown("Se precisar guardar ou imprimir, baixe a planilha com tudo consolidado e somado.")
            
            def gerar_excel_final(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Validades_Dashboard')
                return output.getvalue()
                
            excel_final_bin = gerar_excel_final(df_exibicao)
            
            st.download_button(
                label="📥 Baixar Excel Consolidado (.xlsx)",
                data=excel_final_bin,
                file_name=f"dashboard_validades_{datetime.now().strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.error("Nenhum produto com quantidade válida foi encontrado.")
            
    except Exception as e:
        st.error(f"Erro ao processar o Dashboard: {e}")
