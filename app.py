import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64

st.set_page_config(page_title="PMOC - Instituto Ser Consciente", layout="wide", page_icon="❄️")

# -----------------------------------------------------------------------------
# PERSISTÊNCIA (JSON)
# -----------------------------------------------------------------------------
ARQUIVO_DADOS = "pmoc_dados.json"

def carregar_dados_disco():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_dados_disco(historico):
    dados_para_salvar = []
    for h in historico:
        h_copy = h.copy()
        if h_copy.get("foto_antes_bytes"):
            h_copy["foto_antes_bytes"] = base64.b64encode(h_copy["foto_antes_bytes"]).decode("utf-8")
        if h_copy.get("foto_depois_bytes"):
            h_copy["foto_depois_bytes"] = base64.b64encode(h_copy["foto_depois_bytes"]).decode("utf-8")
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
# ESTILO CSS PARA IMPRESSÃO LIMPA E MASCARA DE ETIQUETA 5x5 cm
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
        body {margin: 0; padding: 0;}
    }
    .etiqueta-box {
        border: 3px solid #000;
        border-radius: 8px;
        padding: 15px;
        background-color: #ffffff;
        color: #000000;
        width: 100%;
        max-width: 480px;
        font-family: Arial, sans-serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .etiqueta-header {
        background-color: #000;
        color: #fff;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        border-radius: 4px;
        margin-bottom: 10px;
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
        {"tag": "CONS006", "ambiente": "Consultório 06", "equipamento": "Split Britania", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS007", "ambiente": "Consultório 07", "equipamento": "Sem instalação", "btus": "9000", "status": "Previsto"},
        {"tag": "CONS008", "ambiente": "Consultório 08", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS009", "ambiente": "Consultório 09", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS010", "ambiente": "Consultório 10", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS011", "ambiente": "Consultório 11", "equipamento": "Split Philco", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS012", "ambiente": "Consultório 12", "equipamento": "Sem instalação", "btus": "9000", "status": "Previsto"},
        {"tag": "CONS013", "ambiente": "Consultório 13", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS014", "ambiente": "Consultório 14", "equipamento": "Sem instalação", "btus": "9000", "status": "Previsto"},
        {"tag": "CONS015", "ambiente": "Consultório 15", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS016", "ambiente": "Consultório 16", "equipamento": "Sem instalação", "btus": "9000", "status": "Previsto"},
        {"tag": "CONS017", "ambiente": "Consultório 17", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS018", "ambiente": "Consultório 18", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS019", "ambiente": "Consultório 19", "equipamento": "Split Electrolux", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS020", "ambiente": "Consultório 20", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS021", "ambiente": "Consultório 21", "equipamento": "Sem instalação", "btus": "9000", "status": "Previsto"},
        {"tag": "CONS022", "ambiente": "Consultório 22", "equipamento": "Split Agratto (Série: PQX147229)", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS023", "ambiente": "Consultório 23", "equipamento": "Split Agratto (Série: PQX147221)", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS024", "ambiente": "Consultório 24", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS025", "ambiente": "Consultório 25", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS026", "ambiente": "Consultório 26", "equipamento": "Split Agratto (Série: PQX150208)", "btus": "9000", "status": "Instalado"},
        {"tag": "RECP001", "ambiente": "Recepção 01", "equipamento": "Cassete Philco", "btus": "48000", "status": "Instalado"},
        {"tag": "RECP002", "ambiente": "Recepção 02", "equipamento": "Split Electrolux", "btus": "22000", "status": "Instalado"},
        {"tag": "COPA001", "ambiente": "Copa", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "MULTI001", "ambiente": "Espaço Multiatividades", "equipamento": "Sem instalação", "btus": "34000", "status": "Previsto"},
        {"tag": "FRALD01", "ambiente": "Fraldário", "equipamento": "Sem instalação", "btus": "9000", "status": "Previsto"},
        {"tag": "ADM0001", "ambiente": "Administração", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"}
    ]

if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_equipamentos_iniciais()

if "historico" not in st.session_state:
    raw_hist = carregar_dados_disco()
    historico_convertido = []
    for h in raw_hist:
        h_conv = h.copy()
        if h_conv.get("foto_antes_bytes"):
            h_conv["foto_antes_bytes"] = base64.b64decode(h_conv["foto_antes_bytes"])
        if h_conv.get("foto_depois_bytes"):
            h_conv["foto_depois_bytes"] = base64.b64decode(h_conv["foto_depois_bytes"])
        historico_convertido.append(h_conv)
    st.session_state.historico = historico_convertido

try:
    tag_url = st.query_params.get("tag", None)
except:
    tag_url = None

# -----------------------------------------------------------------------------
# MENU LATERAL
# -----------------------------------------------------------------------------
if logo_img:
    st.sidebar.image(logo_img, width=120)

st.sidebar.title("❄️ PMOC Digital")
st.sidebar.subheader("Instituto Ser Consciente Ltda")
st.sidebar.caption("Resp. Técnico: Eng. Alessandro Coelho (CREA-MG 238968-D)")
st.sidebar.caption("ART: MG20265436050")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 Acesso Restrito")
senha_input =
