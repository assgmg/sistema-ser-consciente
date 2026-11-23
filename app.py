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

CHECKLIST_PMOC_OFICIAL = [
    "4.1 - Efetuar a limpeza dos filtros de ar e/ou substituir por novos, caso necessário (M/T/S)",
    "4.2 - Efetuar a limpeza externa do gabinete do evaporador (M/T/S)",
    "4.3 - Verificar operação de drenagem e corrigir caso necessário (M/T/S)",
    "4.4 - Verificar e corrigir ruídos e vibrações anormais (M/T/S)",
    "4.5 - Verificar a operação dos termostatos, controles e sensores de temperatura (M/T/S)",
    "4.6 - Higienizar evaporadores com aplicação de bactericida (M/T/S)",
    "4.7 - Verificar e eliminar odores desagradáveis nos ambientes climatizados (M/T/S)",
    "4.8 - Efetuar a limpeza das serpentinas do evaporador (T/S)",
    "4.9 - Efetuar a limpeza do ventilador/rotor do evaporador (T/S)",
    "4.10 - Efetuar a limpeza da bandeja de condensado (T/S)",
    "4.11 - Verificar e corrigir reaperto de terminais/conexões elétricas (T/S)",
    "4.12 - Verificar corrente/pressão/tensão (S)",
    "4.13 - Efetuar a limpeza do condensador (S)",
    "4.14 - Verificar estado dos compressores (S)",
    "4.15 - Verificar lubrificação geral do equipamento (S)",
    "4.16 - Verificar estado dos suportes/coxins e corrigir caso necessário (S)",
    "4.17 - Verificar e corrigir focos de corrosão nos equipamentos/acessórios (S)",
    "4.18 - Verificar e corrigir isolantes térmicos das linhas de cobre/alumínio (S)",
]

OPCOES_CICLO_MANUTENCAO = [
    "Semestral (180 dias) — Ciclo Completo (Itens 4.1 a 4.18)",
    "Trimestral (90 dias) — Rotina Trimestral (Itens 4.1 a 4.11)",
    "Corretiva / Ocorrência Extraordinária",
]

ITENS_PADRAO_TRIMESTRAL = set(CHECKLIST_PMOC_OFICIAL[0:11])
ITENS_PADRAO_SEMESTRAL = set(CHECKLIST_PMOC_OFICIAL[0:18])


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
    limpo = re.sub(r"\s*\([^)]*\)", "", str(texto), flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", limpo).strip()


def formatar_equipamento_com_serie(equip):
    return limpar_numero_serie(equip.get("equipamento", ""))


def rotulo_ciclo_curto(periodicidade_str):
    texto = str(periodicidade_str or "")
    if "Trimestral" in texto:
        return "Trimestral"
    if "Semestral" in texto or "Completa" in texto:
        return "Semestral"
    if "Corretiva" in texto or "Ocorrência" in texto:
        return "Corretiva"
    return texto[:12] if texto else "-"


def indice_ciclo_existente(periodicidade_str):
    texto = str(periodicidade_str or "")
    if "Trimestral" in texto:
        return 1
    if "Corretiva" in texto or "Ocorrência" in texto:
        return 2
    return 0


def proximo_ciclo_esperado(hists_eq):
    if not hists_eq:
        return "Semestral"
    ultima_per = str(hists_eq[-1].get("periodicidade", ""))
    if "Trimestral" in ultima_per:
        return "Semestral"
    if "Semestral" in ultima_per or "Completa" in ultima_per:
        return "Trimestral"
    return "Semestral"


def calcular_proxima_manutencao(hists_eq):
    if not hists_eq:
        return "-", "-", None, "", ""
    ultima = hists_eq[-1]
    data_ult_str = str(ultima.get("data", "-"))
    tipo_freq = str(ultima.get("periodicidade", "Semestral"))
    prox_tipo = proximo_ciclo_esperado(hists_eq)

    trimestrais_apos_semestral = 0
    for h in reversed(hists_eq):
        p = str(h.get("periodicidade", ""))
        if "Trimestral" in p:
            trimestrais_apos_semestral += 1
        elif "Semestral" in p or "Completa" in p:
            break

    try:
        d_obj = datetime.datetime.strptime(data_ult_str.strip(), "%d/%m/%Y").date()
        if "Semestral" in tipo_freq or "Completa" in tipo_freq:
            d_prox = d_obj + datetime.timedelta(days=90)
        elif "Trimestral" in tipo_freq and trimestrais_apos_semestral >= 2:
            d_prox = d_obj + datetime.timedelta(days=180)
        else:
            d_prox = d_obj + datetime.timedelta(days=90)
        d_prox_str = d_prox.strftime("%d/%m/%Y")
    except Exception:
        d_prox = None
        d_prox_str = "A calcular"

    return data_ult_str, d_prox_str, d_prox, tipo_freq, prox_tipo


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
                    for item in salvos:
                        if isinstance(item, dict):
                            item["equipamento"] = limpar_numero_serie(item.get("equipamento", ""))
                            item["numero_serie"] = ""
                    return salvos
        except Exception:
            pass

    dados = [
        ("CONS001", "Consultório 01", "Split Philco", "9000", "Instalado", "", "7,21", "1"),
        ("CONS002", "Consultório 02", "Split Philco", "9000", "Instalado", "", "11,24", "2"),
        ("CONS003", "Consultório 03", "Split Agratto", "9000", "Instalado", "", "7,02", "1"),
        ("CONS004", "Consultório 04", "Split Britania", "9000", "Instalado", "", "9,36", "2"),
        ("CONS005", "Consultório 05", "Split Agratto", "9000", "Instalado", "", "7,21", "1"),
        ("CONS006", "Consultório 06", "Split Britania", "9000", "Instalado", "", "13,60", "2"),
        ("CONS007", "Consultório 07", "Sem instalação", "9000", "Previsto", "", "", ""),
        ("CONS008", "Consultório 08", "Split Agratto", "9000", "Instalado", "", "11,84", "2"),
        ("CONS009", "Consultório 09", "Split Agratto", "9000", "Instalado", "", "14,75", "2"),
        ("CONS010", "Consultório 10", "Split Agratto", "9000", "Instalado", "", "11,84", "2"),
        ("CONS011", "Consultório 11", "Split Philco", "9000", "Instalado", "", "12,06", "2"),
        ("CONS012", "Consultório 12", "Sem instalação", "9000", "Previsto", "", "", ""),
        ("CONS013", "Consultório 13", "Split Agratto", "9000", "Instalado", "", "12,01", "2"),
        ("CONS014", "Consultório 14", "Sem instalação", "9000", "Previsto", "", "", ""),
        ("CONS015", "Consultório 15", "Split Agratto", "9000", "Instalado", "", "13,81", "2"),
        ("CONS016", "Consultório 16", "Sem instalação", "9000", "Previsto", "", "", ""),
        ("CONS017", "Consultório 17", "Split Agratto", "9000", "Instalado", "", "7,95", "2"),
        ("CONS018", "Consultório 18", "Split Agratto", "9000", "Instalado", "", "8,85", "2"),
        ("CONS019", "Consultório 19", "Split Electrolux", "9000", "Instalado", "", "8,50", "2"),
        ("CONS020", "Consultório 20", "Split Agratto", "9000", "Instalado", "", "7,57", "1"),
        ("CONS021", "Consultório 21", "Sem instalação", "9000", "Previsto", "", "", ""),
        ("CONS022", "Consultório 22", "Split Agratto", "9000", "Instalado", "", "17,01", "2"),
        ("CONS023", "Consultório 23", "Split Agratto", "9000", "Instalado", "", "10,70", "2"),
        ("CONS024", "Consultório 24", "Split Agratto", "9000", "Instalado", "", "12,74", "2"),
        ("CONS025", "Consultório 25", "Split Agratto", "9000", "Instalado", "", "12,91", "2"),
        ("CONS026", "Consultório 26", "Split Agratto", "9000", "Instalado", "", "14,93", "2"),
        ("RECP001", "Recepção 01", "Cassete Philco", "48000", "Instalado", "", "34,87", "10"),
        ("RECP002", "Recepção 02", "Split Electrolux", "22000", "Instalado", "", "21,76", "6"),
        ("COPA001", "Copa", "Split Agratto", "9000", "Instalado", "", "25,00", "2"),
        ("MULTI001", "Espaço Multiatividades", "Sem instalação", "34000", "Previsto", "", "", ""),
        ("FRALD01", "Fraldário", "Sem instalação", "9000", "Previsto", "", "", ""),
        ("ADM0001", "Administração", "Split Agratto", "9000", "Instalado", "", "18,02", "2"),
    ]

    lista_eq = []
    for t, a, e, b, s, ns, area, ocup in dados:
        lista_eq.append({
            "tag": t,
            "ambiente": a,
            "equipamento": limpar_numero_serie(e),
            "btus": b,
            "status": s,
            "numero_serie": "",
            "area_m2": area,
            "ocupantes_max": ocup,
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

if "qr_liberado_tags" not in st.session_state:
    st.session_state.qr_liberado_tags = []


def exibir_fotos_registro(h):
    fotos_antes = h.get("fotos_antes_bytes") or normalizar_lista_fotos(h, "fotos_antes_bytes", "foto_antes")
    fotos_depois = h.get("fotos_depois_bytes") or normalizar_lista_fotos(h, "fotos_depois_bytes", "foto_depois")

    if fotos_antes or fotos_depois:
        col1, col2 = st.columns(2)
        with col1:
            if fotos_antes:
                st.markdown("**📷 Fotos ANTES:**")
                for i, img_data in enumerate(fotos_antes):
                    st.image(img_data, caption="Antes #" + str(i + 1) + " - " + str(h.get("data", "")), use_container_width=True)
        with col2:
            if fotos_depois:
                st.markdown("**📷 Fotos DEPOIS:**")
                for i, img_data in enumerate(fotos_depois):
                    st.image(img_data, caption="Depois #" + str(i + 1) + " - " + str(h.get("data", "")), use_container_width=True)


def renderizar_etiqueta_html(eq_sel):
    link_equip = BASE_URL + "/?tag=" + eq_sel["tag"]
    api_qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=" + link_equip
    return (
        '<div class="etiqueta-box">'
        '<div class="etiqueta-header">PMOC - SER CONSCIENTE</div>'
        '<div style="font-size: 8px; line-height: 1.1;">'
        '<b>TAG:</b> ' + eq_sel["tag"] + '<br>'
        '<b>Amb:</b> ' + eq_sel["ambiente"] + '<br>'
        '<b>Equip:</b> ' + formatar_equipamento_com_serie(eq_sel) + '<br>'
        '<b>Carga:</b> ' + str(eq_sel["btus"]) + ' BTUs</div>'
        '<div style="text-align: center; margin: 1px 0;">'
        '<img src="' + api_qr_url + '" width="65" height="65" style="border: 1px solid #ddd; padding: 1px; background: #fff;"></div>'
        '<div style="text-align: center; font-size: 6px; color: #000; font-weight: bold; line-height: 1;">'
        'Eng. Alessandro Coelho (CREA-MG 238468-D)<br>ART: MG20265436050</div></div>'
    )


def adicionar_bloco_fotos_pdf(story, titulo_bloco, lista_bytes, estilo_check, style_imgs):
    if not lista_bytes:
        return
    story.append(Paragraph(titulo_bloco, estilo_check))
    linha_imgs = []
    for img_bytes in lista_bytes:
        try:
            linha_imgs.append(RLImage(io.BytesIO(img_bytes), width=4.0 * cm, height=3.0 * cm))
            if len(linha_imgs) == 2:
                t_imgs = Table([linha_imgs], colWidths=[4.5 * cm, 4.5 * cm])
                t_imgs.setStyle(style_imgs)
                story.append(Spacer(1, 3))
                story.append(t_imgs)
                linha_imgs = []
        except Exception:
            pass
    if linha_imgs:
        while len(linha_imgs) < 2:
            linha_imgs.append("")
        t_imgs = Table([linha_imgs], colWidths=[4.5 * cm, 4.5 * cm])
        t_imgs.setStyle(style_imgs)
        story.append(Spacer(1, 3))
        story.append(t_imgs)


def montar_etiqueta_pdf(eq_obj, estilo_header, estilo_texto, estilo_footer, style_hdr, style_etq):
    link_eq = BASE_URL + "/?tag=" + eq_obj["tag"]
    qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + link_eq
    qr_img_obj = None
    try:
        qr_bytes = urllib.request.urlopen(qr_url, timeout=3).read()
        qr_img_obj = RLImage(io.BytesIO(qr_bytes), width=1.6 * cm, height=1.6 * cm)
    except Exception:
        pass

    t_header = Table([[Paragraph("<b>PMOC - SER CONSCIENTE</b>", estilo_header)]], colWidths=[4.6 * cm])
    t_header.setStyle(style_hdr)

    txt_dados = Paragraph(
        "<b>TAG:</b> " + str(eq_obj["tag"]) + "<br/>"
        + "<b>Amb:</b> " + str(eq_obj["ambiente"]) + "<br/>"
        + "<b>Equip:</b> " + formatar_equipamento_com_serie(eq_obj) + "<br/>"
        + "<b>Carga:</b> " + str(eq_obj["btus"]) + " BTUs",
        estilo_texto,
    )
    txt_rodape = Paragraph("Eng. Alessandro Coelho (CREA-MG 238468-D)<br/><b>ART:</b> MG20265436050", estilo_footer)

    conteudo = [t_header, Spacer(1, 1), txt_dados, Spacer(1, 0.5)]
    if qr_img_obj:
        conteudo.append(qr_img_obj)
    conteudo.append(Spacer(1, 0.5))
    conteudo.append(txt_rodape)

    t_etiqueta = Table([[conteudo]], colWidths=[5.0 * cm], rowHeights=[5.0 * cm])
    t_etiqueta.setStyle(style_etq)
    return t_etiqueta


if logo_img is not None:
    try:
        st.sidebar.image(logo_img, use_container_width=True)
    except Exception:
        pass

st.sidebar.title("❄️ PMOC Digital")
st.sidebar.subheader("Instituto Ser Consciente Ltda")
st.sidebar.caption("Resp. Técnico: Eng. Alessandro Coelho (CREA-MG 238468-D)")
st.sidebar.caption("ART: MG20265436050")
st.sidebar.markdown("---")

if "senha_salva" not in st.session_state:
    st.session_state.senha_salva = ""

if st.session_state.senha_salva not in CREDENCIAIS_VALIDAS:
    st.sidebar.markdown("### 🔐 Acesso Restrito")
    senha_input = st.sidebar.text_input("Credencial de acesso:", type="password")
    if senha_input in CREDENCIAIS_VALIDAS:
        st.session_state.senha_salva = senha_input
        st.rerun()
    senha_input_
