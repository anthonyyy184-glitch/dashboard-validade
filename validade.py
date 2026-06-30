import pandas as pd
import json

# 1. Carregar o arquivo JSON enviado pelo usuário
# (Substitua 'seu_arquivo.json' pelo caminho correto ou pelo componente do Streamlit)
with open('seu_arquivo.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# 2. Transformar a lista de produtos em um DataFrame do Pandas
df_bruto = pd.DataFrame(dados['products'])

# 3. Mágica do agrupamento: Contar quantas vezes cada código de barras aparece
# Isso vai gerar a quantidade real baseada em quantas vezes você bipou o item!
df_contagem = df_bruto.groupby('barcode').size().reset_index(name='Quantidade')

# 4. Pegar os nomes dos produtos (removendo as duplicatas para não repetir)
df_nomes = df_bruto[['barcode', 'name']].drop_duplicates(subset=['barcode'])

# 5. Juntar o nome do produto com a quantidade certa que contamos
df_final = pd.merge(df_nomes, df_contagem, on='barcode')

# 6. Renomear as colunas para o padrão que você já usa no Excel
df_final = df_final.rename(columns={
    'name': 'Produto',
    'barcode': 'Código de Barras'
})

# 7. Adicionar a coluna de Data de Validade (como o app não gera, deixamos para o Passo 2)
df_final['Data de Validade'] = ''

# Reorganizar as colunas na ordem correta
df_final = df_final[['Produto', 'Código de Barras', 'Data de Validade', 'Quantidade']]

# Agora o seu df_final terá as quantidades reais (ex: 3, 5, 12, etc.)!
