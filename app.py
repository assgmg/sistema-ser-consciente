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


def proximo_ciclo_esperado(hists_eq):
    if not hists_eq:
        return "Semestral"
    # Varre do mais recente para o mais antigo para identificar o ciclo vigente
    for h in reversed(hists_eq):
        per = str(h.get("periodicidade", ""))
        if "Trimestral" in per:
            return "Semestral"
        if "Semestral" in per or "Completa" in per:
            return "Trimestral"
    return "Semestral"


def calcular_proxima_manutencao(hists_eq):
    if not hists_eq:
        return "-", "-", "-"
    ultima = hists_eq[-1]
    data_ult_str = str(ultima.get("data", "-"))
    tipo_freq = str(ultima.get("periodicidade", "Semestral"))
    prox_tipo = proximo_ciclo_esperado(hists_eq)
    try:
        d_obj = datetime.datetime.strptime(data_ult_str.strip(), "%d/%m/%Y").date()
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

    # (tag, ambiente, equipamento, btus, status, numero_serie, area_m2, ocupantes_max)
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
    senha_input_ativo = senha_input
else:
    senha_input_ativo = st.session_state.senha_salva
    st.sidebar.success("✅ Modo Administrador" if senha_input_ativo == SENHA_ADMIN else "👁️ Modo Fiscalização")
    if st.sidebar.button("🚪 Sair / Desconectar"):
        st.session_state.senha_salva = ""
        st.session_state.qr_liberado_tags = []
        st.rerun()

st.sidebar.markdown("---")

eh_admin = senha_input_ativo == SENHA_ADMIN
eh_fiscal = senha_input_ativo == SENHA_VISA

if eh_admin:
    opcoes_menu = [
        "📋 Informações do Equipamento",
        "🛠️ Registrar Manutenção",
        "✏️ Editar Previstos",
        "🖨️ Etiquetas 5x5 cm (Individual)",
        "📑 Lote A4 para Gráfica (Guilhotina)",
        "📊 Dashboard Geral",
        "📄 Relatório Fiscal A4",
    ]
else:
    opcoes_menu = [
        "📋 Informações do Equipamento",
        "📊 Dashboard Geral",
    ]

opcao = st.sidebar.radio("Navegação", opcoes_menu)

if opcao == "📋 Informações do Equipamento":
    st.header("📋 Informações do Equipamento - PMOC Oficial")
    st.info("ℹ️ Projeto validado pela Vineyard Engenharia | ART CREA-MG nº MG20265436050")

    equip = None
    tag_codigo = ""

    if tag_qr_lido:
        tag_codigo = tag_qr_lido
        st.info("📱 QR Code lido — Equipamento: **" + tag_codigo + "**")
        equip = next((e for e in st.session_state.equipamentos if e.get("tag") == tag_codigo), None)
        if not equip:
            st.error("❌ Equipamento não encontrado para a TAG informada.")
    else:
        tags_lista = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
        tag_selecionada = st.selectbox("Selecione a TAG do Equipamento:", tags_lista)
        tag_codigo = tag_selecionada.split(" - ")[0]
        equip = next((e for e in st.session_state.equipamentos if e.get("tag") == tag_codigo), None)
        if not equip:
            st.error("❌ Equipamento não encontrado para a TAG informada.")

    if equip:
        hists = [h for h in st.session_state.historico if h.get("tag") == tag_codigo]

        data_ult_str = "-"
        d_prox_str = "-"
        tipo_freq = ""
        prox_tipo_str = ""

        if equip["status"] == "Previsto":
            status_exibicao = "🟡 Previsto (Aguardando Instalação)"
        elif hists:
            data_ult_str, d_prox_str, d_prox_obj, tipo_freq, prox_tipo_str = calcular_proxima_manutencao(hists)
            if d_prox_obj is not None:
                if datetime.date.today() <= d_prox_obj:
                    status_exibicao = "🟢 Em dia"
                else:
                    status_exibicao = "🔴 Em atraso"
            else:
                status_exibicao = "🟢 Em dia"
        else:
            status_exibicao = "⚪ Sem registro"

        tag_ja_liberada = tag_codigo in st.session_state.qr_liberado_tags
        senha_digitada_ok = eh_admin or eh_fiscal or tag_ja_liberada

        if tag_qr_lido and not senha_digitada_ok:
            st.subheader("📍 " + equip["ambiente"] + " (" + equip["tag"] + ")")
            st.write("**Data da última manutenção:** " + data_ult_str)
            st.write("**Data da próxima manutenção:** " + d_prox_str + (" — *" + prox_tipo_str + "*" if prox_tipo_str else ""))
            if "Em dia" in status_exibicao:
                st.success("**Status:** " + status_exibicao)
            elif "Em atraso" in status_exibicao:
                st.error("**Status:** " + status_exibicao)
            else:
                st.info("**Status:** " + status_exibicao)

            st.markdown("---")
            st.write("🔐 Digite a senha para ver a informação completa do equipamento:")
            with st.form("form_senha_qr_" + tag_codigo):
                senha_qr_input = st.text_input("Senha:", type="password")
                if st.form_submit_button("🔓 Ver Informação Completa"):
                    if senha_qr_input in CREDENCIAIS_VALIDAS:
                        st.session_state.senha_salva = senha_qr_input
                        if tag_codigo not in st.session_state.qr_liberado_tags:
                            st.session_state.qr_liberado_tags.append(tag_codigo)
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta.")
        else:
            area_txt = str(equip.get("area_m2") or "").strip()
            ocup_txt = str(equip.get("ocupantes_max") or "").strip()
            detalhes_amb = []
            if area_txt:
                detalhes_amb.append("**Área Climatizada:** " + area_txt + " m²")
            if ocup_txt:
                detalhes_amb.append("**Ocupantes Máx.:** " + ocup_txt)

            st.subheader("📍 " + equip["ambiente"] + " (" + equip["tag"] + ")")
            st.write("**Equipamento:** " + formatar_equipamento_com_serie(equip) + " | **Carga Térmica:** " + str(equip["btus"]) + " BTUs")
            if detalhes_amb:
                st.write(" | ".join(detalhes_amb))
            st.write("**Status de Instalação:** `" + equip["status"] + "`")
            st.write("**Data da última manutenção:** " + data_ult_str + (" — *" + rotulo_ciclo_curto(tipo_freq) + "*" if tipo_freq else ""))
            st.write("**Data da próxima manutenção:** " + d_prox_str + (" — *" + prox_tipo_str + "*" if prox_tipo_str else ""))

            if "Em dia" in status_exibicao:
                st.success("**Status:** " + status_exibicao)
            elif "Em atraso" in status_exibicao:
                st.error("**Status:** " + status_exibicao)
            else:
                st.info("**Status:** " + status_exibicao)

            if hists and equip["status"] != "Previsto":
                st.write("**Técnico Executor:** " + str(hists[-1].get("tecnico", "")))
                if hists[-1].get("visto"):
                    st.write("**Visto / Validação:** " + str(hists[-1].get("visto", "")))

            st.markdown("---")
            st.subheader("📋 Histórico Acumulado e Gerenciamento de Registros")

            if hists:
                for idx, h in enumerate(reversed(hists)):
                    indice_real = st.session_state.historico.index(h)
                    freq_reg = h.get("periodicidade", "Semestral")
                    num_manut = str(len(hists) - idx)
                    titulo_manut = "#### Manutenção #" + num_manut + " — Data: " + str(h.get("data", "")) + " (" + freq_reg + ")"
                    st.markdown(titulo_manut)
                    st.write("**Técnico Executor:** " + str(h.get("tecnico", "")))
                    if h.get("visto"):
                        st.write("**Visto / Validação:** " + str(h.get("visto", "")))

                    if h.get("checklist"):
                        st.write("**Itens Verificados (PMOC - Itens 4.1 a 4.18):**")
                        for item_nome, status_val in h["checklist"].items():
                            st.write("- " + ("✅" if status_val else "❌") + " " + str(item_nome))

                    if h.get("obs"):
                        st.write("**Observações / Ocorrências:** " + str(h["obs"]))

                    exibir_fotos_registro(h)

                    if eh_admin:
                        with st.expander("➕ Adicionar mais fotos a esta manutenção (" + str(h.get("data", "")) + ")"):
                            novas_antes = st.file_uploader("Selecionar fotos adicionais do ANTES", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="add_antes_" + tag_codigo + "_" + str(idx))
                            novas_depois = st.file_uploader("Selecionar fotos adicionais do DEPOIS", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="add_depois_" + tag_codigo + "_" + str(idx))
                            if st.button("💾 Anexar Novas Fotos ao Registro", key="btn_add_fotos_" + tag_codigo + "_" + str(idx)):
                                if novas_antes or novas_depois:
                                    reg = st.session_state.historico[indice_real]
                                    reg.setdefault("fotos_antes_bytes", [])
                                    reg.setdefault("fotos_depois_bytes", [])
                                    reg["fotos_antes_bytes"].extend([f.getvalue() for f in novas_antes])
                                    reg["fotos_depois_bytes"].extend([f.getvalue() for f in novas_depois])
                                    salvar_dados_disco(st.session_state.historico)
                                    st.success("Fotos adicionadas com sucesso!")
                                    st.rerun()
                                else:
                                    st.warning("Selecione pelo menos uma foto para anexar.")

                        if st.button("🗑️ Excluir este Registro Incorreto", key="btn_del_" + tag_codigo + "_" + str(idx)):
                            del st.session_state.historico[indice_real]
                            salvar_dados_disco(st.session_state.historico)
                            st.cache_data.clear()
                            st.success("Registro excluído com sucesso! Atualizando...")
                            st.rerun()

                    st.markdown("---")
            else:
                st.info("Nenhum histórico cadastrado para este aparelho.")

elif opcao == "🛠️ Registrar Manutenção":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("🛠️ Registro de Manutenção Preventiva e Ocorrências (PMOC)")
        instalados = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
        tags = [e["tag"] + " - " + e["ambiente"] for e in instalados]

        if tags:
            tag_sel = st.selectbox("Selecione o Equipamento:", tags)
            tag_codigo = tag_sel.split(" - ")[0]
            hists_eq_atual = [h for h in st.session_state.historico if h.get("tag") == tag_codigo]
            prox_sugerido = proximo_ciclo_esperado(hists_eq_atual)
            opcoes_ciclo = [
                "Semestral (90 dias) — Ciclo Completo (Itens 4.1 a 4.18)",
                "Trimestral (90 dias) — Rotina Trimestral (Itens 4.1 a 4.11)",
                "Corretiva / Ocorrência Extraordinária",
            ]
            idx_ciclo = 1 if prox_sugerido == "Trimestral" else 0
            hoje_formatado = datetime.date.today().strftime("%d/%m/%Y")

            periodicidade = st.selectbox(
                "Tipo de Manutenção / Periodicidade (Conforme PMOC):",
                opcoes_ciclo,
                index=idx_ciclo,
            )

            itens_padrao = (
                ITENS_PADRAO_TRIMESTRAL
                if "Trimestral" in periodicidade
                else (set() if "Corretiva" in periodicidade else ITENS_PADRAO_SEMESTRAL)
            )

            with st.form("form_manutencao", clear_on_submit=True):
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    data_manut = st.text_input("Data da Manutenção (DD/MM/AAAA)", value=hoje_formatado)
                with col_d2:
                    tecnico = st.text_input("Técnico Responsável", value="Antônio Sérgio Silva Gomes")
                with col_d3:
                    visto = st.text_input("Visto / Responsável Conferência", value="")

                st.markdown("---")
                st.subheader("📋 Checklist Oficial do PMOC (Itens 4.1 a 4.18)")
                st.caption("M = Mensal | T = Trimestral | S = Semestral. Os itens padrão do ciclo selecionado já vêm marcados, e você pode alterar qualquer um.")

                checklist_inputs = {}
                for item in CHECKLIST_PMOC_OFICIAL:
                    checklist_inputs[item] = st.checkbox(item, value=(item in itens_padrao), key="chk_" + item[:4])

                st.markdown("---")
                st.subheader("📸 Registros Fotográficos (Múltiplas Fotos) e Ocorrências (Seção 6)")
                st.caption("Selecione várias fotos de uma só vez nos campos abaixo.")
                obs = st.text_area("Observações Técnicas / Registro de Ocorrências")

                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    fotos_antes = st.file_uploader("📷 Fotos do ANTES", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
                with col_f2:
                    fotos_depois = st.file_uploader("📷 Fotos do DEPOIS", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

                if st.form_submit_button("💾 Salvar Registro de Manutenção"):
                    st.session_state.historico.append({
                        "tag": tag_codigo,
                        "data": data_manut,
                        "periodicidade": periodicidade,
                        "tecnico": tecnico,
                        "visto": visto,
                        "checklist": checklist_inputs,
                        "obs": obs,
                        "fotos_antes_bytes": [f.getvalue() for f in fotos_antes] if fotos_antes else [],
                        "fotos_depois_bytes": [f.getvalue() for f in fotos_depois] if fotos_depois else [],
                    })
                    salvar_dados_disco(st.session_state.historico)
                    st.cache_data.clear()
                    st.success("✅ Manutenção registrada com sucesso!")
        else:
            st.info("Não há equipamentos instalados no momento.")

elif opcao == "✏️ Editar Previstos":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("✏️ Gerenciar, Cadastrar Novos e Substituir Equipamentos")
        st.caption("Use esta tela para registrar dados de um equipamento novo ou atualizar dados do ambiente.")

        lista_todos = [e["tag"] + " - " + e["ambiente"] + " (" + e["status"] + ")" for e in st.session_state.equipamentos]
        tag_sel_ed = st.selectbox("Selecione o Equipamento para Editar ou Substituir:", lista_todos)
        tag_codigo_ed = tag_sel_ed.split(" - ")[0]
        equip_ed = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo_ed), None)

        if equip_ed:
            with st.form("form_edicao_geral"):
                st.write("**Ambiente:** " + equip_ed["ambiente"] + " | **TAG:** " + equip_ed["tag"])
                novo_nome = st.text_input("Marca / Modelo do Equipamento", value=limpar_numero_serie(equip_ed["equipamento"]))
                novos_btus = st.text_input("Potência / Carga Térmica (BTUs)", value=equip_ed["btus"])
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    nova_area = st.text_input("Área Climatizada (m²)", value=str(equip_ed.get("area_m2") or ""), placeholder="Ex.: 12,50")
                with col_a2:
                    novo_ocup = st.text_input("Ocupantes Máximos", value=str(equip_ed.get("ocupantes_max") or ""), placeholder="Ex.: 2")
                novo_status = st.selectbox("Status de Instalação", ["Instalado", "Previsto"], index=0 if equip_ed["status"] == "Instalado" else 1)

                if st.form_submit_button("✅ Salvar Alterações"):
                    equip_ed["equipamento"] = limpar_numero_serie(novo_nome)
                    equip_ed["btus"] = novos_btus.strip()
                    equip_ed["numero_serie"] = ""
                    equip_ed["area_m2"] = nova_area.strip()
                    equip_ed["ocupantes_max"] = novo_ocup.strip()
                    equip_ed["status"] = novo_status
                    salvar_equipamentos_disco(st.session_state.equipamentos)
                    st.cache_data.clear()
                    st.success("Equipamento " + tag_codigo_ed + " atualizado e salvo com sucesso!")
                    st.rerun()

elif opcao == "🖨️ Etiquetas 5x5 cm (Individual)":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("🖨️ Pré-visualização de Etiqueta Individual 5x5 cm")
        lista_eq_qr = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
        tag_sel_qr = st.selectbox("Selecione o Equipamento:", lista_eq_qr)
        equip_sel = next((e for e in st.session_state.equipamentos if e["tag"] == tag_sel_qr.split(" - ")[0]), None)
        if equip_sel:
            st.markdown(renderizar_etiqueta_html(equip_sel), unsafe_allow_html=True)

elif opcao == "📑 Lote A4 para Gráfica (Guilhotina)":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("📑 Gerador de Arquivo PDF Pronto para Gráfica (5x5 cm)")
        todas_tags = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
        selecionar_todos = st.checkbox("
