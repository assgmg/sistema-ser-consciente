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


def normalizar_lista_fotos(h, chave_lista, chave_antiga):
    if chave_lista in h and h[chave_lista]:
        return [
            base64.b64decode(b) if isinstance(b, str) else b
            for b in h[chave_lista]
        ]
    if h.get(chave_antiga):
        b = h[chave_antiga]
        return [base64.b64decode(b) if isinstance(b, str) else b]
    return []


def serializar_lista_fotos(lista_bytes):
    if not lista_bytes:
        return []
    return [
        base64.b64encode(b).decode("utf-8") if isinstance(b, bytes) else b
        for b in lista_bytes
    ]


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
    fotos_antes = h.get("fotos_antes_bytes") or ([h["foto_antes"]] if h.get("foto_antes") else [])
    fotos_depois = h.get("fotos_depois_bytes") or ([h["foto_depois"]] if h.get("foto_depois") else [])

    if fotos_antes or fotos_depois:
        col1, col2 = st.columns(2)
        with col1:
            if fotos_antes:
                st.markdown("**📷 Fotos ANTES:**")
                for i, img_data in enumerate(fotos_antes):
                    st.image(img_data, caption="Antes #" + str(i + 1) + " - " + str(h["data"]), use_container_width=True)
        with col2:
            if fotos_depois:
                st.markdown("**📷 Fotos DEPOIS:**")
                for i, img_data in enumerate(fotos_depois):
                    st.image(img_data, caption="Depois #" + str(i + 1) + " - " + str(h["data"]), use_container_width=True)


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
        'Eng. Alessandro Coelho (CREA-MG 238968-D)<br>ART: MG20265436050</div></div>'
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
    txt_rodape = Paragraph("Eng. Alessandro Coelho (CREA-MG 238968-D)<br/><b>ART:</b> MG20265436050", estilo_footer)

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
st.sidebar.caption("Resp. Técnico: Eng. Alessandro Coelho (CREA-MG 238968-D)")
st.sidebar.caption("ART: MG20265436050")
st.sidebar.markdown("---")

if "senha_salva" not in st.session_state:
    st.session_state.senha_salva = ""

if st.session_state.senha_salva not in ["admin", "visa"]:
    st.sidebar.markdown("### 🔐 Acesso Restrito")
    senha_input = st.sidebar.text_input("Credencial de acesso:", type="password")
    if senha_input in ["admin", "visa"]:
        st.session_state.senha_salva = senha_input
        st.rerun()
    senha_input_ativo = senha_input
else:
    senha_input_ativo = st.session_state.senha_salva
    st.sidebar.success("✅ Modo Administrador" if senha_input_ativo == "admin" else "👁️ Modo Fiscalização (Apenas Consulta)")
    if st.sidebar.button("🚪 Sair / Desconectar"):
        st.session_state.senha_salva = ""
        st.session_state.qr_liberado_tags = []
        st.rerun()

st.sidebar.markdown("---")

eh_admin = senha_input_ativo == "admin"
eh_fiscal = senha_input_ativo == "visa"

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
elif eh_fiscal:
    opcoes_menu = [
        "📋 Informações do Equipamento",
        "📊 Dashboard Geral",
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

    if eh_fiscal and not tag_qr_lido:
        st.warning("🔒 **Acesso via QR Code necessário:** Como Fiscal, você só pode consultar um equipamento específico lendo o QR Code dele. Não é permitido acessar outros equipamentos sem ler o QR Code correspondente.")
        st.stop()

    if tag_qr_lido:
        tag_codigo = tag_qr_lido
        st.info("📱 QR Code lido — Equipamento específico: **" + tag_codigo + "**")
    else:
        tags_lista = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
        tag_selecionada = st.selectbox("Selecione a TAG do Equipamento:", tags_lista)
        tag_codigo = tag_selecionada.split(" - ")[0]

    equip = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo), None)

    if not equip:
        st.error("❌ Equipamento não encontrado para a TAG informada.")
        st.stop()

    st.subheader("📍 " + equip["ambiente"] + " (" + equip["tag"] + ")")
    st.markdown(renderizar_etiqueta_html(equip), unsafe_allow_html=True)
    st.write("**Equipamento:** " + formatar_equipamento_com_serie(equip) + " | **Carga Térmica:** " + str(equip["btus"]) + " BTUs")
    st.write("**Status de Instalação:** `" + equip["status"] + "`")

    hists = [h for h in st.session_state.historico if h["tag"] == tag_codigo]

    if equip["status"] == "Previsto":
        st.info("🟡 Equipamento Previsto — Aguardando Instalação Física.")
    elif hists:
        ultima_manut = hists[-1]
        data_ult_str = ultima_manut["data"]
        tipo_freq = ultima_manut.get("periodicidade", "Semestral (180 dias)")
        dias_vencimento = 90 if "Trimestral" in tipo_freq else 180

        try:
            d_obj = datetime.datetime.strptime(data_ult_str, "%d/%m/%Y").date()
            d_prox = d_obj + datetime.timedelta(days=dias_vencimento)
            d_prox_str = d_prox.strftime("%d/%m/%Y")
            if datetime.date.today() <= d_prox:
                st.success("🟢 STATUS DA MANUTENÇÃO: EM DIA (" + tipo_freq + ")")
            else:
                st.error("🔴 STATUS DA MANUTENÇÃO: PENDENTE / VENCIDA (" + tipo_freq + ")")
        except Exception:
            d_prox_str = "A calcular"
            st.success("🟢 STATUS DA MANUTENÇÃO: REGISTRADA")

        st.write("**Última Manutenção Realizada:** " + data_ult_str + " — *" + tipo_freq + "*")
        st.write("**Próxima Manutenção Programada:** " + d_prox_str)
        st.write("**Técnico Executor:** " + ultima_manut["tecnico"])
    else:
        st.warning("⚪ Nenhuma manutenção registrada ainda para este equipamento.")

    st.markdown("---")

    tag_ja_liberada_qr = tag_codigo in st.session_state.qr_liberado_tags
    pode_ver_historico = eh_admin or (eh_fiscal and tag_ja_liberada_qr)

    if not pode_ver_historico:
        st.warning("🔒 **Histórico e Fotos Restritos:** Digite a senha de acesso para visualizar o histórico acumulado e todas as fotos deste equipamento (" + tag_codigo + ").")
        with st.form("form_senha_equipamento_" + tag_codigo):
            senha_equip_input = st.text_input("Digite a senha de acesso:", type="password")
            if st.form_submit_button("🔓 Liberar Histórico e Fotos"):
                if senha_equip_input in ["admin", "visa"]:
                    st.session_state.senha_salva = senha_equip_input
                    if tag_codigo not in st.session_state.qr_liberado_tags:
                        st.session_state.qr_liberado_tags.append(tag_codigo)
                    st.success("✅ Histórico liberado para " + tag_codigo + "!")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta. Tente novamente.")

    if pode_ver_historico:
        st.subheader("📋 Histórico Acumulado do Equipamento (" + tag_codigo + ")")
        if eh_fiscal:
            st.caption("👁️ Modo Fiscalização: apenas consulta do histórico e fotos deste equipamento.")

        if hists:
            for idx, h in enumerate(reversed(hists)):
                indice_real = st.session_state.historico.index(h)
                freq_reg = h.get("periodicidade", "Semestral")
                st.markdown("#### Manutenção #" + str(len(hists) - idx) + " — Data: " + str
