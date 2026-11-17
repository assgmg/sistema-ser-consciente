import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
import io

# Importações do ReportLab para Geração de PDF Profissional para Gráfica
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="PMOC - Instituto Ser Consciente", layout="wide", page_icon="❄️")

# -----------------------------------------------------------------------------
# PERSISTÊNCIA (JSON) - COM SUPORTE A MÚLTIPLAS FOTOS ANTES E DEPOIS
# -----------------------------------------------------------------------------
ARQUIVO_DADOS = "pmoc_dados.json"

def carregar_dados_disco():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_dados_disco(historico):
    dados_para_salvar = []
    for h in historico:
        h_copy = h.copy()
        
        # Compatibilidade com formato antigo (1 foto) e novo formato (lista de fotos)
        if "fotos_antes_bytes" in h_copy and h_copy["fotos_antes_bytes"]:
            h_copy["fotos_antes_bytes"] = [
                base64.b64encode(b).decode("utf-8") if isinstance(b, bytes) else b 
                for b in h_copy["fotos_antes_bytes"]
            ]
        elif h_copy.get("foto_antes_bytes"):
            b = h_copy["foto_antes_bytes"]
            h_copy["fotos_antes_bytes"] = [base64.b64encode(b).decode("utf-8") if isinstance(b, bytes) else b]
            h_copy.pop("foto_antes_bytes", None)
            
        if "fotos_depois_bytes" in h_copy and h_copy["fotos_depois_bytes"]:
            h_copy["fotos_depois_bytes"] = [
                base64.b64encode(b).decode("utf-8") if isinstance(b, bytes) else b 
                for b in h_copy["fotos_depois_bytes"]
            ]
        elif h_copy.get("foto_depois_bytes"):
            b = h_copy["foto_depois_bytes"]
            h_copy["fotos_depois_bytes"] = [base64.b64encode(b).decode("utf-8") if isinstance(b, bytes) else b]
            h_copy.pop("foto_depois_bytes", None)
            
        dados_para_salvar.append(h_copy)
        
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

# -----------------------------------------------------------------------------
# LOGOMARCA
# -----------------------------------------------------------------------------
@st.cache_resource
def carregar_logo():
    if os.path.exists("Borboleta.png"):
        from PIL import Image
        return Image.open("Borboleta.png")
    return None

logo_img = carregar_logo()

# -----------------------------------------------------------------------------
# ESTILO CSS PARA O SISTEMA WEB
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    @media print {
        [data-testid="stSidebar"] {display: none;}
        header {visibility: hidden;}
        .stButton {display: none;}
        .stTextInput {display: none;}
        .streamlit-expanderHeader {display: none;}
        .stAlert {display: none;}
        body {margin: 0; padding: 0; background: #fff;}
    }
    .etiqueta-box {
        border: 2px dashed #000;
        border-radius: 4px;
        padding: 8px;
        background-color: #ffffff;
        color: #000000;
        width: 5cm;
        height: 5cm;
        box-sizing: border-box;
        font-family: Arial, sans-serif;
        display: inline-flex;
        flex-direction: column;
        justify-content: space-between;
        margin: 5px;
        overflow: hidden;
        vertical-align: top;
    }
    .etiqueta-header {
        background-color: #000;
        color: #fff;
        padding: 2px 4px;
        font-weight: bold;
        font-size: 9px;
        text-align: center;
        border-radius: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BASE DE DADOS OFICIAL CONFORME PMOC / ART (ENG. ALESSANDRO COELHO)
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_equipamentos_iniciais():
    return [
        {"tag": "CONS001", "ambiente": "Consultório 01", "equipamento": "Split Philco", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS002", "ambiente": "Consultório 02", "equipamento": "Split Philco", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS003", "ambiente": "Consultório 03", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS004", "ambiente": "Consultório 04", "equipamento": "Split Britania", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS005", "ambiente": "Consultório 05", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS006", "ambiente": "Consultório 06", "equipamento": "Split Britania", "btus": "9000", "status": "
