import streamlit as st
import pandas as pd
import json
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
    
    /* 3. CORREÇÃO DA SETINHA DO CELULAR: Força o botão de abrir/fechar a barra lateral a ficar visível */
    [data-testid="stSidebarCollapseButton"] button {
        background-color: #1F2937 !important; /* Fundo cinza escuro para dar destaque */
        color: #FFFFFF !important;            /* Setinha branca dentro do botão escuro */
        border: 1px solid #4B5563 !important;  /* Bordinha cinza */
        border-radius: 50% !important;         /* Deixa o botão redondo */
    }
    
    /* Garante que o ícone da setinha dentro do botão mude de cor se necessário */
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    
    /* 4. Garante que todos os textos, títulos e etiquetas fiquem brancos/claros */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { 
        color: #FFFFFF !important; 
    }
    
    /* 5. Corrige a cor dos textos pequenos de ajuda do upload (ex: "200MB per file") */
    small, [data-testid="stWidgetMarkdownHint"] p { 
        color: #9CA3AF !important; 
    }
    
    /* 6. Força a caixinha de upload (File Uploader) a ficar escura */
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
        border: 1px solid #4B5563 !important; 
    }
    
    /* Customização dos botões de ação */
    .stButton>button {
        background-color: #10B981 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
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
    .metric-title { color: #9CA3AF !important; font-size: 14px; font-weight: bold; text-transform
