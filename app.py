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

    if eh_fiscal and not tag_qr_lido:
        st.warning("🔒 **Acesso via QR Code necessário:** Como Fiscal, você só pode consultar um equipamento específico lendo o QR Code dele. Não é permitido acessar outros equipamentos sem ler o QR Code correspondente.")
    else:
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

    if equip:
        st.subheader("📍 " + equip["ambiente"] + " (" + equip["tag"] + ")")
        st.markdown(renderizar_etiqueta_html(equip), unsafe_allow_html=True)
        st.write("**Equipamento:** " + formatar_equipamento_com_serie(equip) + " | **Carga Térmica:** " + str(equip["btus"]) + " BTUs")
        st.write("**Status de Instalação:** `" + equip["status"] + "`")

        hists = [h for h in st.session_state.historico if h.get("tag") == tag_codigo]

        if equip["status"] == "Previsto":
            st.info("🟡 Equipamento Previsto — Aguardando Instalação Física.")
        elif hists:
            ultima_manut = hists[-1]
            data_ult_str = ultima_manut.get("data", "")
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
            st.write("**Técnico Executor:** " + str(ultima_manut.get("tecnico", "")))
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
                    num_manut = str(len(hists) - idx)
                    titulo_manut = "#### Manutenção #" + num_manut + " — Data: " + str(h.get("data", "")) + " (" + freq_reg + ")"
                    st.markdown(titulo_manut)
                    st.write("**Técnico Executor:** " + str(h.get("tecnico", "")))

                    if h.get("checklist"):
                        st.write("**Itens Verificados (PMOC):**")
                        for item_nome, status_val in h["checklist"].items():
                            st.write("- " + ("✅" if status_val else "❌") + " " + str(item_nome))

                    if h.get("obs"):
                        st.write("**Observações:** " + str(h["obs"]))

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
        st.header("🛠️ Registro de Manutenção Preventiva")
        instalados = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
        tags = [e["tag"] + " - " + e["ambiente"] for e in instalados]

        if tags:
            tag_sel = st.selectbox("Selecione o Equipamento:", tags)
            tag_codigo = tag_sel.split(" - ")[0]
            hoje_formatado = datetime.date.today().strftime("%d/%m/%Y")

            periodicidade = st.selectbox(
                "Tipo de Manutenção / Periodicidade (Conforme PMOC):",
                ["Semestral (180 dias) — Completa (Engloba Trimestral)", "Trimestral (90 dias)"],
            )

            with st.form("form_manutencao", clear_on_submit=True):
                data_manut = st.text_input("Data da Manutenção (DD/MM/AAAA)", value=hoje_formatado)
                tecnico = st.text_input("Técnico Responsável", value="Antônio Sérgio Silva Gomes")

                st.markdown("---")
                st.subheader("📋 Atividades Obrigatórias do PMOC")

                if "Trimestral" in periodicidade:
                    st.info("📝 Checklist **TRIMESTRAL** (90 dias):")
                    itens_check = [
                        "4.1 - Limpeza dos filtros de ar",
                        "4.2 - Limpeza externa do gabinete",
                        "4.3 - Verificação de drenagem",
                        "4.6 - Higienização com bactericida",
                        "4.9 - Limpeza do ventilador/rotor",
                        "4.10 - Limpeza da bandeja de condensado",
                        "4.11 - Reaperto de terminais/conexões",
                    ]
                else:
                    st.info("📝 Checklist **SEMESTRAL** (180 dias) — *Ciclo Completo que engloba a rotina trimestral*:")
                    itens_check = [
                        "4.1 - Limpeza dos filtros de ar",
                        "4.2 - Limpeza externa do gabinete",
                        "4.3 - Verificação de drenagem",
                        "4.6 - Higienização com bactericida",
                        "4.8 - Limpeza química das serpentinas",
                        "4.9 - Limpeza do ventilador/rotor",
                        "4.10 - Limpeza e desinfecção da bandeja",
                        "4.12 - Verificação de corrente/tensão",
                        "4.13 - Limpeza do condensador",
                        "4.14 - Verificação dos compressores",
                    ]

                checklist_inputs = {item: st.checkbox(item, value=True) for item in itens_check}

                st.markdown("---")
                st.subheader("📸 Registros Fotográficos (Múltiplas Fotos) e Observações")
                st.caption("Selecione várias fotos de uma só vez nos campos abaixo.")
                obs = st.text_area("Observações Técnicas / Ocorrências")

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
        st.caption("Use esta tela para registrar dados de um equipamento novo ou atualizar/substituir o número de série de qualquer aparelho.")

        lista_todos = [e["tag"] + " - " + e["ambiente"] + " (" + e["status"] + ")" for e in st.session_state.equipamentos]
        tag_sel_ed = st.selectbox("Selecione o Equipamento para Editar ou Substituir:", lista_todos)
        tag_codigo_ed = tag_sel_ed.split(" - ")[0]
        equip_ed = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo_ed), None)

        if equip_ed:
            serie_atual = (equip_ed.get("numero_serie") or "").strip()
            if not serie_atual:
                m_s = re.search(r"s[eé]rie:\s*([^)]+)", equip_ed.get("equipamento", ""), flags=re.IGNORECASE)
                if m_s:
                    serie_atual = m_s.group(1).strip()

            with st.form("form_edicao_geral"):
                st.write("**Ambiente:** " + equip_ed["ambiente"] + " | **TAG:** " + equip_ed["tag"])
                novo_nome = st.text_input("Marca / Modelo do Equipamento", value=limpar_numero_serie(equip_ed["equipamento"]))
                novos_btus = st.text_input("Potência (BTUs)", value=equip_ed["btus"])
                novo_serie = st.text_input("Número de Série (Novo ou Substituído)", value=serie_atual, placeholder="Ex.: PQX150208")
                novo_status = st.selectbox("Status de Instalação", ["Instalado", "Previsto"], index=0 if equip_ed["status"] == "Instalado" else 1)

                if st.form_submit_button("✅ Salvar Alterações"):
                    equip_ed["equipamento"] = limpar_numero_serie(novo_nome)
                    equip_ed["btus"] = novos_btus.strip()
                    equip_ed["numero_serie"] = novo_serie.strip()
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
        selecionar_todos = st.checkbox("Selecionar todos os equipamentos cadastrados", value=True)
        equipamentos_selecionados = todas_tags if selecionar_todos else st.multiselect("Selecione os equipamentos:", todas_tags, default=todas_tags[:6])

        if st.button("🚀 Gerar PDF Oficial para Download"):
            if not equipamentos_selecionados:
                st.warning("Selecione pelo menos um equipamento.")
            else:
                with st.spinner("Gerando arquivo PDF..."):
                    try:
                        pdf_buffer = io.BytesIO()
                        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.0 * cm, bottomMargin=1.0 * cm)
                        story = []
                        celulas_pagina = []

                        estilo_header = ParagraphStyle("EtqHeader", fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=colors.whitesmoke, alignment=1)
                        estilo_texto = ParagraphStyle("EtqText", fontName="Helvetica", fontSize=6.0, leading=7.5, textColor=colors.black, alignment=0)
                        estilo_footer = ParagraphStyle("EtqFooter", fontName="Helvetica-Bold", fontSize=5.5, leading=7, textColor=colors.black, alignment=1)

                        style_hdr = TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.black), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)])
                        style_etq = TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("BOX", (0, 0), (-1, -1), 1, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2)])
                        style_pag = TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)])

                        for idx, item_sel in enumerate(equipamentos_selecionados):
                            eq_obj = next((e for e in st.session_state.equipamentos if e["tag"] == item_sel.split(" - ")[0]), None)
                            if eq_obj:
                                celulas_pagina.append(montar_etiqueta_pdf(eq_obj, estilo_header, estilo_texto, estilo_footer, style_hdr, style_etq))

                            if len(celulas_pagina) == 15 or idx == len(equipamentos_selecionados) - 1:
                                linhas_tabela = []
                                linha_atual = []
                                for cell in celulas_pagina:
                                    linha_atual.append(cell)
                                    if len(linha_atual) == 3:
                                        linhas_tabela.append(linha_atual)
                                        linha_atual = []
                                if linha_atual:
                                    linha_atual.extend([""] * (3 - len(linha_atual)))
                                    linhas_tabela.append(linha_atual)

                                t_pagina = Table(linhas_tabela, colWidths=[5.0 * cm, 5.0 * cm, 5.0 * cm], rowHeights=[5.0 * cm] * len(linhas_tabela))
                                t_pagina.setStyle(style_pag)
                                story.append(t_pagina)
                                if idx < len(equipamentos_selecionados) - 1:
                                    story.append(PageBreak())
                                celulas_pagina = []

                        doc.build(story)
                        pdf_buffer.seek(0)
                        st.success("✅ Arquivo PDF gerado com sucesso!")
                        st.download_button("📥 Baixar PDF Pronto para a Gráfica", data=pdf_buffer, file_name="etiquetas_pmoc_5x5cm_grafica.pdf", mime="application/pdf")
                    except Exception as e:
                        st.error("Erro ao gerar PDF: " + str(e))

elif opcao == "📊 Dashboard Geral":
    st.header("📊 Painel Geral de Climatização")
    total = len(st.session_state.equipamentos)
    instalados = len([e for e in st.session_state.equipamentos if e["status"] == "Instalado"])
    previstos = len([e for e in st.session_state.equipamentos if e["status"] == "Previsto"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Aparelhos", total)
    col2.metric("Instalados e Ativos", instalados)
    col3.metric("Previstos / Futuros", previstos)
    st.markdown("---")
    df_dash = pd.DataFrame(st.session_state.equipamentos)
    if eh_fiscal:
        st.caption("👁️ Visualização resumida para Fiscalização.")
        st.dataframe(df_dash[["tag", "ambiente", "equipamento", "btus", "status"]], use_container_width=True)
    else:
        st.dataframe(df_dash, use_container_width=True)

elif opcao == "📄 Relatório Fiscal A4":
    if not eh_admin:
        st.warning("🔒 O Relatório Fiscal A4 é exclusivo do Administrador.")
    else:
        st.header("📄 Relatório Fiscal Oficial A4 (Completo com Checklists e Todas as Fotos)")
        st.info("ℹ️ Este relatório consolida a relação de equipamentos, o histórico completo de manutenções com os itens verificados no checklist e **todas** as fotografias (Antes e Depois) anexadas em cada manutenção.")

        filtrar_periodo = st.checkbox("📅 Filtrar manutenções por período (Data Inicial e Data Final)", value=False)
        hoje_data = datetime.date.today()
        inicio_padrao = hoje_data - datetime.timedelta(days=180)
        data_inicio = inicio_padrao
        data_fim = hoje_data

        if filtrar_periodo:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                data_inicio = st.date_input("Data Inicial", value=inicio_padrao, format="DD/MM/YYYY")
            with col_d2:
                data_fim = st.date_input("Data Final", value=hoje_data, format="DD/MM/YYYY")
            if data_inicio > data_fim:
                st.warning("⚠️ A Data Inicial não pode ser maior que a Data Final.")

        def dentro_do_periodo(h_item):
            if not filtrar_periodo:
                return True
            try:
                d_reg = datetime.datetime.strptime(h_item.get("data", ""), "%d/%m/%Y").date()
                return data_inicio <= d_reg <= data_fim
            except Exception:
                return False

        periodo_valido = (not filtrar_periodo) or (data_inicio <= data_fim)

        if periodo_valido and st.button("🚀 Gerar PDF Oficial Completo do Relatório Fiscal"):
            with st.spinner("Compilando relatório fiscal completo com todas as fotos e checklists..."):
                try:
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
                    story = []

                    estilo_titulo = ParagraphStyle("RelTitulo", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#111111"), alignment=1)
                    estilo_sub = ParagraphStyle("RelSub", fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=colors.HexColor("#333333"), alignment=1)
                    estilo_info = ParagraphStyle("RelInfo", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#444444"))
                    estilo_secao = ParagraphStyle("RelSecao", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=colors.HexColor("#000000"), spaceBefore=12, spaceAfter=6)
                    estilo_texto = ParagraphStyle("RelTexto", fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#222222"))
                    estilo_check = ParagraphStyle("RelCheck", fontName="Helvetica", fontSize=7.5, leading=10, textColor=colors.HexColor("#333333"), leftIndent=10)

                    style_resumo = TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#000000")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ])
                    style_imgs = TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")])

                    story.append(Paragraph("<b>INSTITUTO SER CONSCIENTE LTDA</b>", estilo_titulo))
                    story.append(Paragraph("PLANO DE MANUTENÇÃO, OPERAÇÃO E CONTROLE - PMOC", estilo_sub))
                    story.append(Paragraph("Lei Federal nº 13.589/2018 | ART CREA-MG: MG20265436050", estilo_sub))
                    story.append(Spacer(1, 10))

                    texto_periodo = (
                        data_inicio.strftime("%d/%m/%Y") + " a " + data_fim.strftime("%d/%m/%Y")
                        if filtrar_periodo
                        else "Todo o histórico registrado"
                    )

                    story.append(Paragraph("<b>Data de Emissão:</b> " + hoje_data.strftime("%d/%m/%Y"), estilo_info))
                    story.append(Paragraph("<b>Período do Relatório:</b> " + texto_periodo, estilo_info))
                    story.append(Paragraph("<b>Responsável Técnico:</b> Eng. Alessandro Coelho (CREA-MG 238968-D)", estilo_info))
                    story.append(Paragraph("<b>Administrador / Gestor:</b> António Sérgio Silva Gomes", estilo_info))
                    story.append(Spacer(1, 10))

                    story.append(Paragraph("📑 Relação Resumida dos Equipamentos Instalados", estilo_secao))
                    instalados_df = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
                    dados_tabela = [["TAG", "Ambiente", "Equipamento", "BTUs", "Última Manutenção", "Próxima", "Frequência"]]

                    for eq in instalados_df:
                        hists_eq = [h for h in st.session_state.historico if h.get("tag") == eq["tag"] and dentro_do_periodo(h)]
                        if hists_eq:
                            ultima_manut = hists_eq[-1]
                            ultima_data = ultima_manut.get("data", "")
                            freq_ult = ultima_manut.get("periodicidade", "Semestral")
                            dias_vencimento = 90 if "Trimestral" in freq_ult else 180
                            try:
                                d_obj = datetime.datetime.strptime(ultima_data, "%d/%m/%Y").date()
                                prox_data_str = (d_obj + datetime.timedelta(days=dias_vencimento)).strftime("%d/%m/%Y")
                            except Exception:
                                prox_data_str = "A calcular"
                        else:
                            ultima_data, freq_ult, prox_data_str = "Sem registro", "-", "-"

                        dados_tabela.append([eq["tag"], eq["ambiente"], limpar_numero_serie(eq["equipamento"]), str(eq["btus"]), ultima_data, prox_data_str, freq_ult[:10]])

                    t_resumo = Table(dados_tabela, colWidths=[2.0 * cm, 3.2 * cm, 3.2 * cm, 1.6 * cm, 2.5 * cm, 2.2 * cm, 2.3 * cm])
                    t_resumo.setStyle(style_resumo)
                    story.append(t_resumo)
                    story.append(Spacer(1, 15))

                    story.append(Paragraph("📖 Detalhamento Completo, Checklists e Registros Fotográficos", estilo_secao))
                    for eq in instalados_df:
                        equip_sem_serie = limpar_numero_serie(eq["equipamento"])
                        story.append(Paragraph("<b>📍 Equipamento: " + eq["ambiente"] + " (TAG: " + eq["tag"] + ")</b> — " + equip_sem_serie + " (" + str(eq["btus"]) + " BTUs)", estilo_texto))
                        hists_eq = [h for h in st.session_state.historico if h.get("tag") == eq["tag"] and dentro_do_periodo(h)]

                        if hists_eq:
                            for h in hists_eq:
                                freq_reg = h.get("periodicidade", "Semestral")
                                story.append(Paragraph("• <b>Data:</b> " + str(h.get("data", "")) + " (" + freq_reg + ") | <b>Técnico:</b> " + str(h.get("tecnico", "")), estilo_texto))

                                if h.get("checklist"):
                                    story.append(Paragraph("  <b>Itens Verificados (PMOC):</b>", estilo_check))
                                    for item_nome, status_val in h["checklist"].items():
                                        simbolo = "✓" if status_val else "X"
                                        story.append(Paragraph("    [" + simbolo + "] " + str(item_nome), estilo_check))

                                if h.get("obs"):
                                    story.append(Paragraph("  <b>Observações:</b> " + str(h["obs"]), estilo_check))

                                f_antes = h.get("fotos_antes_bytes") or normalizar_lista_fotos(h, "fotos_antes_bytes", "foto_antes")
                                f_depois = h.get("fotos_depois_bytes") or normalizar_lista_fotos(h, "fotos_depois_bytes", "foto_depois")

                                adicionar_bloco_fotos_pdf(story, "  <b>Fotos - ANTES:</b>", f_antes, estilo_check, style_imgs)
                                adicionar_bloco_fotos_pdf(story, "  <b>Fotos - DEPOIS:</b>", f_depois, estilo_check, style_imgs)
                                story.append(Spacer(1, 6))
                        else:
                            msg_sem = "  <i>(Nenhuma manutenção registrada no período selecionado)</i>" if filtrar_periodo else "  <i>(Nenhuma manutenção registrada)</i>"
                            story.append(Paragraph(msg_sem, estilo_texto))
                        story.append(Spacer(1, 8))

                    doc.build(story)
                    pdf_buffer.seek(0)
                    nome_arq = (
                        "relatorio_fiscal_pmoc_" + data_inicio.strftime("%Y%m%d") + "_" + data_fim.strftime("%Y%m%d") + ".pdf"
                        if filtrar_periodo
                        else "relatorio_fiscal_pmoc_completo.pdf"
                    )
                    st.success("✅ Relatório Fiscal Completo em PDF gerado com sucesso!")
                    st.download_button("📥 Baixar Relatório Fiscal Oficial Completo (PDF)", data=pdf_buffer, file_name=nome_arq, mime="application/pdf")
                except Exception as e:
                    st.error("Erro ao compilar PDF fiscal completo: " + str(e))
