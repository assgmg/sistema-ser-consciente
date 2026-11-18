import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
import io

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
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
import urllib.request

st.set_page_config(
    page_title="PMOC - Instituto Ser Consciente",
    layout="wide",
    page_icon="❄️",
)

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

@st.cache_data
def carregar_equipamentos_iniciais():
    dados = [
        ("CONS001", "Consultório 01", "Split Philco", "9000", "Instalado"),
        ("CONS002", "Consultório 02", "Split Philco", "9000", "Instalado"),
        ("CONS003", "Consultório 03", "Split Agratto", "9000", "Instalado"),
        ("CONS004", "Consultório 04", "Split Britania", "9000", "Instalado"),
        ("CONS005", "Consultório 05", "Split Agratto", "9000", "Instalado"),
        ("CONS006", "Consultório 06", "Split Britania", "9000", "Instalado"),
        ("CONS007", "Consultório 07", "Sem instalação", "9000", "Previsto"),
        ("CONS008", "Consultório 08", "Split Agratto", "9000", "Instalado"),
        ("CONS009", "Consultório 09", "Split Agratto", "9000", "Instalado"),
        ("CONS010", "Consultório 10", "Split Agratto", "9000", "Instalado"),
        ("CONS011", "Consultório 11", "Split Philco", "9000", "Instalado"),
        ("CONS012", "Consultório 12", "Sem instalação", "9000", "Previsto"),
        ("CONS013", "Consultório 13", "Split Agratto", "9000", "Instalado"),
        ("CONS014", "Consultório 14", "Sem instalação", "9000", "Previsto"),
        ("CONS015", "Consultório 15", "Split Agratto", "9000", "Instalado"),
        ("CONS016", "Consultório 16", "Sem instalação", "9000", "Previsto"),
        ("CONS017", "Consultório 17", "Split Agratto", "9000", "Instalado"),
        ("CONS018", "Consultório 18", "Split Agratto", "9000", "Instalado"),
        ("CONS019", "Consultório 19", "Split Electrolux", "9000", "Instalado"),
        ("CONS020", "Consultório 20", "Split Agratto", "9000", "Instalado"),
        ("CONS021", "Consultório 21", "Sem instalação", "9000", "Previsto"),
        ("CONS022", "Consultório 22", "Split Agratto (Série: PQX147229)", "9000", "Instalado"),
        ("CONS023", "Consultório 23", "Split Agratto (Série: PQX147221)", "9000", "Instalado"),
        ("CONS024", "Consultório 24", "Split Agratto", "9000", "Instalado"),
        ("CONS025", "Consultório 25", "Split Agratto", "9000", "Instalado"),
        ("CONS026", "Consultório 26", "Split Agratto (Série: PQX150208)", "9000", "Instalado"),
        ("RECP001", "Recepção 01", "Cassete Philco", "48000", "Instalado"),
        ("RECP002", "Recepção 02", "Split Electrolux", "22000", "Instalado"),
        ("COPA001", "Copa", "Split Agratto", "9000", "Instalado"),
        ("MULTI001", "Espaço Multiatividades", "Sem instalação", "34000", "Previsto"),
        ("FRALD01", "Fraldário", "Sem instalação", "9000", "Previsto"),
        ("ADM0001", "Administração", "Split Agratto", "9000", "Instalado"),
    ]
    return [{"tag": t, "ambiente": a, "equipamento": e, "btus": b, "status": s} for t, a, e, b, s in dados]

if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_equipamentos_iniciais()

if "historico" not in st.session_state:
    raw_hist = carregar_dados_disco()
    historico_convertido = []
    for h in raw_hist:
        h_conv = h.copy()
        if "fotos_antes_bytes" in h_conv and h_conv["fotos_antes_bytes"]:
            h_conv["fotos_antes_bytes"] = [base64.b64decode(b) if isinstance(b, str) else b for b in h_conv["fotos_antes_bytes"]]
        elif h_conv.get("foto_antes_bytes"):
            b = h_conv.pop("foto_antes_bytes")
            h_conv["fotos_antes_bytes"] = [base64.b64decode(b) if isinstance(b, str) else b]
        else:
            h_conv["fotos_antes_bytes"] = []

        if "fotos_depois_bytes" in h_conv and h_conv["fotos_depois_bytes"]:
            h_conv["fotos_depois_bytes"] = [base64.b64decode(b) if isinstance(b, str) else b for b in h_conv["fotos_depois_bytes"]]
        elif h_conv.get("foto_depois_bytes"):
            b = h_conv.pop("foto_depois_bytes")
            h_conv["fotos_depois_bytes"] = [base64.b64decode(b) if isinstance(b, str) else b]
        else:
            h_conv["fotos_depois_bytes"] = []

        historico_convertido.append(h_conv)
    st.session_state.historico = historico_convertido

try:
    tag_url = st.query_params.get("tag", None)
except Exception:
    tag_url = None

if "qr_liberado" not in st.session_state:
    st.session_state.qr_liberado = False

def exibir_fotos_registro(h, largura_relatorio=None):
    fotos_antes = h.get("fotos_antes_bytes", [])
    if not fotos_antes and h.get("foto_antes"):
        fotos_antes = [h["foto_antes"]]

    fotos_depois = h.get("fotos_depois_bytes", [])
    if not fotos_depois and h.get("foto_depois"):
        fotos_depois = [h["foto_depois"]]

    if fotos_antes or fotos_depois:
        col1, col2 = st.columns(2)
        with col1:
            if fotos_antes:
                st.markdown("**📷 Fotos ANTES:**")
                for i, img_data in enumerate(fotos_antes):
                    legenda = f"Antes #{i+1} - {h['data']}"
                    if largura_relatorio:
                        st.image(img_data, caption=legenda, width=largura_relatorio)
                    else:
                        st.image(img_data, caption=legenda, use_container_width=True)
        with col2:
            if fotos_depois:
                st.markdown("**📷 Fotos DEPOIS:**")
                for i, img_data in enumerate(fotos_depois):
                    legenda = f"Depois #{i+1} - {h['data']}"
                    if largura_relatorio:
                        st.image(img_data, caption=legenda, width=largura_relatorio)
                    else:
                        st.image(img_data, caption=legenda, use_container_width=True)

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
    st.sidebar.success("✅ Modo Administrador" if senha_input_ativo == "admin" else "👁️ Modo Fiscalização")
    if st.sidebar.button("🚪 Sair / Desconectar"):
        st.session_state.senha_salva = ""
        st.session_state.qr_liberado = False
        st.rerun()

st.sidebar.markdown("---")

opcoes_menu = [
    "📋 Informações do Equipamento",
    "🛠️ Registrar Manutenção",
    "✏️ Editar Previstos",
    "🖨️ Etiquetas 5x5 cm (Individual)",
    "📑 Lote A4 para Gráfica (Guilhotina)",
    "📊 Dashboard Geral",
    "📄 Relatório Fiscal A4",
]

opcao = st.sidebar.radio("Navegação", opcoes_menu)

if opcao == "📋 Informações do Equipamento":
    st.header("📋 Informações do Equipamento - PMOC Oficial")
    st.info("ℹ️ Projeto validado pela Vineyard Engenharia | ART CREA-MG nº MG20265436050")

    if tag_url:
        tag_codigo = tag_url.strip().upper()
        st.info(f"📱 Acesso via QR Code — Equipamento identificado: **{tag_codigo}**")
    else:
        tags_lista = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
        tag_selecionada = st.selectbox("Selecione a TAG do Equipamento:", tags_lista)
        tag_codigo = tag_selecionada.split(" - ")[0]

    equip = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo), None)

    if equip:
        st.subheader(f"📍 {equip['ambiente']} ({equip['tag']})")
        st.write(f"**Equipamento:** {equip['equipamento']} | **Carga Térmica:** {equip['btus']} BTUs")
        st.write(f"**Status de Instalação:** `{equip['status']}`")

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
                hoje = datetime.date.today()

                if hoje <= d_prox:
                    st.success(f"🟢 STATUS DA MANUTENÇÃO: EM DIA ({tipo_freq})")
                else:
                    st.error(f"🔴 STATUS DA MANUTENÇÃO: PENDENTE / VENCIDA ({tipo_freq})")
            except Exception:
                d_prox_str = "A calcular"
                st.success("🟢 STATUS DA MANUTENÇÃO: REGISTRADA")

            st.write(f"**Última Manutenção Realizada:** {data_ult_str} — *{tipo_freq}*")
            st.write(f"**Próxima Manutenção Programada:** {d_prox_str}")
            st.write(f"**Técnico Executor:** {ultima_manut['tecnico']}")
        else:
            st.warning("⚪ Nenhuma manutenção registrada ainda para este equipamento.")

        st.markdown("---")

        pode_ver_historico = True
        if tag_url and not st.session_state.qr_liberado and senha_input_ativo not in ["admin", "visa"]:
            pode_ver_historico = False
            st.warning("🔒 **Área Restrita / Fiscalização:** O histórico detalhado e os registros fotográficos deste equipamento exigem a senha de liberação.")
            
            with st.form("form_senha_qr"):
                senha_fiscal_input = st.text_input("Digite a senha de acesso (Fiscalização/Admin):", type="password")
                btn_enviar_senha = st.form_submit_button("🔓 Liberar Histórico")
                
                if btn_enviar_senha:
                    if senha_fiscal_input in ["admin", "visa"]:
                        st.session_state.qr_liberado = True
                        st.session_state.senha_salva = senha_fiscal_input
                        st.success("✅ Acesso liberado com sucesso! Atualizando...")
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta. Tente novamente.")

        if pode_ver_historico:
            st.subheader("📋 Histórico Acumulado e Gerenciamento de Registros")

            if hists:
                for idx, h in enumerate(reversed(hists)):
                    indice_real = st.session_state.historico.index(h)
                    freq_reg = h.get("periodicidade", "Semestral")

                    st.markdown(f"#### Manutenção #{len(hists)-idx} — Data: {h['data']} ({freq_reg})")
                    st.write(f"**Técnico Executor:** {h['tecnico']}")

                    if "checklist" in h and h["checklist"]:
                        st.write("**Itens Verificados (PMOC):**")
                        for item_nome, status_val in h["checklist"].items():
                            check_icon = "✅" if status_val else "❌"
                            st.write(f"- {check_icon} {item_nome}")

                    if h.get("obs"):
                        st.write(f"**Observações:** {h['obs']}")

                    exibir_fotos_registro(h)

                    if senha_input_ativo == "admin":
                        with st.expander(f"➕ Adicionar mais fotos a esta manutenção ({h['data']})"):
                            novas_antes = st.file_uploader(
                                "Selecionar fotos adicionais do ANTES",
                                type=["png", "jpg", "jpeg"],
                                accept_multiple_files=True,
                                key=f"add_antes_{tag_codigo}_{idx}"
                            )
                            novas_depois = st.file_uploader(
                                "Selecionar fotos adicionais do DEPOIS",
                                type=["png", "jpg", "jpeg"],
                                accept_multiple_files=True,
                                key=f"add_depois_{tag_codigo}_{idx}"
                            )
                            if st.button("💾 Anexar Novas Fotos ao Registro", key=f"btn_add_fotos_{tag_codigo}_{idx}"):
                                if novas_antes or novas_depois:
                                    if "fotos_antes_bytes" not in st.session_state.historico[indice_real]:
                                        st.session_state.historico[indice_real]["fotos_antes_bytes"] = []
                                    if "fotos_depois_bytes" not in st.session_state.historico[indice_real]:
                                        st.session_state.historico[indice_real]["fotos_depois_bytes"] = []

                                    for f in novas_antes:
                                        st.session_state.historico[indice_real]["fotos_antes_bytes"].append(f.getvalue())
                                    for f in novas_depois:
                                        st.session_state.historico[indice_real]["fotos_depois_bytes"].append(f.getvalue())

                                    salvar_dados_disco(st.session_state.historico)
                                    st.success("Fotos adicionadas com sucesso!")
                                    st.rerun()
                                else:
                                    st.warning("Selecione pelo menos uma foto para anexar.")

                        if st.button("🗑️ Excluir este Registro Incorreto", key=f"btn_del_{tag_codigo}_{idx}"):
                            del st.session_state.historico[indice_real]
                            salvar_dados_disco(st.session_state.historico)
                            st.cache_data.clear()
                            st.success("Registro excluído com sucesso! Atualizando...")
                            st.rerun()

                    st.markdown("---")
            else:
                st.info("Nenhum histórico cadastrado para este aparelho.")

elif opcao == "🛠️ Registrar Manutenção":
    if senha_input_ativo != "admin":
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
                ["Semestral (180 dias) — Completa (Engloba Trimestral)", "Trimestral (90 dias)"]
            )

            with st.form("form_manutencao", clear_on_submit=True):
                data_manut = st.text_input("Data da Manutenção (DD/MM/AAAA)", value=hoje_formatado)
                tecnico = st.text_input("Técnico Responsável", value="Antônio Sérgio Silva Gomes")

                st.markdown("---")
                st.subheader("📋 Atividades Obrigatórias do PMOC")

                checklist_inputs = {}
                if "Trimestral" in periodicidade:
                    st.info("📝 Checklist **TRIMESTRAL** (90 dias):")
                    itens_check =
