import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
import io
import re
import urllib.request

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    PageBreak,
    Paragraph,
    Image as RLImage,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

st.set_page_config(
    page_title="PMOC - Instituto Ser Consciente",
    layout="wide",
    page_icon="❄️",
)

ARQUIVO_DADOS = "pmoc_dados.json"
ARQUIVO_EQUIPAMENTOS = "pmoc_equipamentos.json"
BASE_URL = "https://sistema-ser-consciente-fexfnfuwjkntnzwdwhknso.streamlit.app"


def obter_credenciais():
    senha_admin = "admin"
    senha_visa = "visa"
    try:
        if "SENHA_ADMIN" in st.secrets and str(st.secrets["SENHA_ADMIN"]).strip():
            senha_admin = str(st.secrets["SENHA_ADMIN"]).strip()
        if "SENHA_VISA" in st.secrets and str(st.secrets["SENHA_VISA"]).strip():
            senha_visa = str(st.secrets["SENHA_VISA"]).strip()
    except Exception:
        pass
    return senha_admin, senha_visa


SENHA_ADMIN, SENHA_VISA = obter_credenciais()
CREDENCIAIS_VALIDAS = [SENHA_ADMIN, SENHA_VISA]


def limpar_numero_serie(texto):
    if not texto:
        return ""
    limpo = re.sub(r"\s*\([^)]*s[eé]rie[^)]*\)", "", str(texto), flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", limpo).strip()


def formatar_equipamento_com_serie(equip):
    base = limpar_numero_serie(equip.get("equipamento", ""))
    serie = (equip.get("numero_serie") or "").strip()
    if serie:
        return base + " (Série: " + serie + ")" if base else "(Série: " + serie + ")"
    return base


def decodificar_foto_segura(item):
    if isinstance(item, bytes):
        return item
    if isinstance(item, str) and item.strip():
        try:
            return base64.b64decode(item)
        except Exception:
            return None
    return None


def normalizar_lista_fotos(h, chave_lista, chave_antiga):
    origem = []
    if chave_lista in h and isinstance(h[chave_lista], list) and h[chave_lista]:
        origem = h[chave_lista]
    elif h.get(chave_antiga):
        origem = [h[chave_antiga]]

    resultado = []
    for item in origem:
        b = decodificar_foto_segura(item)
        if b:
            resultado.append(b)
    return resultado


def serializar_lista_fotos(lista_bytes):
    if not lista_bytes:
        return []
    saida = []
    for b in lista_bytes:
        if isinstance(b, bytes):
            saida.append(base64.b64encode(b).decode("utf-8"))
        elif isinstance(b, str) and b.strip():
            saida.append(b)
    return saida


def carregar_dados_disco():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados if isinstance(dados, list) else []
        except Exception:
            return []
    return []


def salvar_dados_disco(historico):
    dados_para_salvar = []
    for h in historico:
        h_copy = h.copy()
        antes_raw = h_copy.pop("foto_antes_bytes", None)
        depois_raw = h_copy.pop("foto_depois_bytes", None)

        antes_lista = h_copy.get("fotos_antes_bytes") or ([antes_raw] if antes_raw else [])
        depois_lista = h_copy.get("fotos_depois_bytes") or ([depois_raw] if depois_raw else [])

        h_copy["fotos_antes_bytes"] = serializar_lista_fotos(antes_lista)
        h_copy["fotos_depois_bytes"] = serializar_lista_fotos(depois_lista)
        dados_para_salvar.append(h_copy)

    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)


def salvar_equipamentos_disco(equipamentos):
    with open(ARQUIVO_EQUIPAMENTOS, "w", encoding="utf-8") as f:
        json.dump(equipamentos, f, ensure_ascii=False, indent=4)


@st.cache_resource
def carregar_logo():
    if os.path.exists("logo.png"):
        try:
            from PIL import Image
            img = Image.open("logo.png")
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[3])
                return bg
            return img.convert("RGB")
        except Exception:
            return None
    return None


logo_img = carregar_logo()

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


def carregar_equipamentos_iniciais():
    if os.path.exists(ARQUIVO_EQUIPAMENTOS):
        try:
            with open(ARQUIVO_EQUIPAMENTOS, "r", encoding="utf-8") as f:
                salvos = json.load(f)
                if isinstance(salvos, list) and salvos:
                    return salvos
        except Exception:
            pass

    dados = [
        ("CONS001", "Consultório 01", "Split Philco", "9000", "Instalado", ""),
        ("CONS002", "Consultório 02", "Split Philco", "9000", "Instalado", ""),
        ("CONS003", "Consultório 03", "Split Agratto", "9000", "Instalado", ""),
        ("CONS004", "Consultório 04", "Split Britania", "9000", "Instalado", ""),
        ("CONS005", "Consultório 05", "Split Agratto", "9000", "Instalado", ""),
        ("CONS006", "Consultório 06", "Split Britania", "9000", "Instalado", ""),
        ("CONS007", "Consultório 07", "Sem instalação", "9000", "Previsto", ""),
        ("CONS008", "Consultório 08", "Split Agratto", "9000", "Instalado", ""),
        ("CONS009", "Consultório 09", "Split Agratto", "9000", "Instalado", ""),
        ("CONS010", "Consultório 10", "Split Agratto", "9000", "Instalado", ""),
        ("CONS011", "Consultório 11", "Split Philco", "9000", "Instalado", ""),
        ("CONS012", "Consultório 12", "Sem instalação", "9000", "Previsto", ""),
        ("CONS013", "Consultório 13", "Split Agratto", "9000", "Instalado", ""),
        ("CONS014", "Consultório 14", "Sem instalação", "9000", "Previsto", ""),
        ("CONS015", "Consultório 15", "Split Agratto", "9000", "Instalado", ""),
        ("CONS016", "Consultório 16", "Sem instalação", "9000", "Previsto", ""),
        ("CONS017", "Consultório 17", "Split Agratto", "9000", "Instalado", ""),
        ("CONS018", "Consultório 18", "Split Agratto", "9000", "Instalado", ""),
        ("CONS019", "Consultório 19", "Split Electrolux", "9000", "Instalado", ""),
        ("CONS020", "Consultório 20", "Split Agratto", "9000", "Instalado", ""),
        ("CONS021", "Consultório 21", "Sem instalação", "9000", "Previsto", ""),
        ("CONS022", "Consultório 22", "Split Agratto", "9000", "Instalado", "PQX147229"),
        ("CONS023", "Consultório 23", "Split Agratto", "9000", "Instalado", "PQX147221"),
        ("CONS024", "Consultório 24", "Split Agratto", "9000", "Instalado", ""),
        ("CONS025", "Consultório 25", "Split Agratto", "9000", "Instalado", ""),
        ("CONS026", "Consultório 26", "Split Agratto", "9000", "Instalado", "PQX150208"),
        ("RECP001", "Recepção 01", "Cassete Philco", "48000", "Instalado", ""),
        ("RECP002", "Recepção 02", "Split Electrolux", "22000", "Instalado", ""),
        ("COPA001", "Copa", "Split Agratto", "9000", "Instalado", ""),
        ("MULTI001", "Espaço Multiatividades", "Sem instalação", "34000", "Previsto", ""),
        ("FRALD01", "Fraldário", "Sem instalação", "9000", "Previsto", ""),
        ("ADM0001", "Administração", "Split Agratto", "9000", "Instalado", ""),
    ]

    lista_eq = []
    for t, a, e, b, s, ns in dados:
        match_serie = re.search(r"s[eé]rie:\s*([^)]+)", e, flags=re.IGNORECASE)
        serie_final = ns or (match_serie.group(1).strip() if match_serie else "")
        lista_eq.append({
            "tag": t,
            "ambiente": a,
            "equipamento": limpar_numero_serie(e),
            "btus": b,
            "status": s,
            "numero_serie": serie_final,
        })
    return lista_eq


if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_equipamentos_iniciais()

if "historico" not in st.session_state:
    historico_convertido = []
    for h in carregar_dados_disco():
        if not isinstance(h, dict):
            continue
        h_conv = h.copy()
        h_conv["fotos_antes_bytes"] = normalizar_lista_fotos(h_conv, "fotos_antes_bytes", "foto_antes_bytes")
        h_conv["fotos_depois_bytes"] = normalizar_lista_fotos(h_conv, "fotos_depois_bytes", "foto_depois_bytes")
        h_conv.pop("foto_antes_bytes", None)
        h_conv.pop("foto_depois_bytes", None)
        historico_convertido.append(h_conv)
    st.session_state.historico = historico_convertido

try:
    tag_url = st.query_params.get("tag", None)
except Exception:
    tag_url = None

tag_qr_lido = tag_url.strip().upper() if tag_url else None
