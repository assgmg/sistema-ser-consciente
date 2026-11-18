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

                for item in itens_check:
                    checklist_inputs[item] = st.checkbox(item, value=True)

                st.markdown("---")
                st.subheader("📸 Registros Fotográficos (Múltiplas Fotos) e Observações")
                st.caption("Selecione várias fotos de uma só vez nos campos abaixo.")

                obs = st.text_area("Observações Técnicas / Ocorrências")

                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    fotos_antes = st.file_uploader("📷 Fotos do ANTES", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
                with col_f2:
                    fotos_depois = st.file_uploader("📷 Fotos do DEPOIS", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

                salvar = st.form_submit_button("💾 Salvar Registro de Manutenção")

                if salvar:
                    lista_antes_bytes = [f.getvalue() for f in fotos_antes] if fotos_antes else []
                    lista_depois_bytes = [f.getvalue() for f in fotos_depois] if fotos_depois else []

                    novo_registro = {
                        "tag": tag_codigo,
                        "data": data_manut,
                        "periodicidade": periodicidade,
                        "tecnico": tecnico,
                        "checklist": checklist_inputs,
                        "obs": obs,
                        "fotos_antes_bytes": lista_antes_bytes,
                        "fotos_depois_bytes": lista_depois_bytes,
                    }

                    st.session_state.historico.append(novo_registro)
                    salvar_dados_disco(st.session_state.historico)
                    st.cache_data.clear()
                    st.success(f"✅ Manutenção registrada com sucesso!")
        else:
            st.info("Não há equipamentos instalados no momento.")

elif opcao == "✏️ Editar Previstos":
    if senha_input_ativo != "admin":
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("✏️ Gerenciar e Atualizar Equipamentos")
        lista_todos = [e["tag"] + " - " + e["ambiente"] + f" ({e['status']})" for e in st.session_state.equipamentos]

        if lista_todos:
            tag_sel_ed = st.selectbox("Selecione o Equipamento para Editar:", lista_todos)
            tag_codigo_ed = tag_sel_ed.split(" - ")[0]
            equip_ed = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo_ed), None)

            if equip_ed:
                with st.form("form_edicao_geral"):
                    st.write(f"**Ambiente:** {equip_ed['ambiente']} | **TAG:** {equip_ed['tag']}")
                    novo_nome = st.text_input("Marca / Modelo do Equipamento", value=equip_ed["equipamento"])
                    novos_btus = st.text_input("Potência (BTUs)", value=equip_ed["btus"])
                    novo_status = st.selectbox("Status de Instalação", ["Instalado", "Previsto"], index=0 if equip_ed["status"] == "Instalado" else 1)

                    confirmar = st.form_submit_button("✅ Salvar Alterações")

                    if confirmar:
                        equip_ed["equipamento"] = novo_nome
                        equip_ed["btus"] = novos_btus
                        equip_ed["status"] = novo_status
                        st.cache_data.clear()
                        st.success(f"Equipamento {tag_codigo_ed} atualizado com sucesso!")
                        st.rerun()

elif opcao == "🖨️ Etiquetas 5x5 cm (Individual)":
    st.header("🖨️ Pré-visualização de Etiqueta Individual 5x5 cm")
    base_url = "https://sistema-ser-consciente-fexfnfuwjkntnzwdwhknso.streamlit.app"
    lista_eq_qr = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
    if lista_eq_qr:
        tag_sel_qr = st.selectbox("Selecione o Equipamento:", lista_eq_qr)
        tag_codigo = tag_sel_qr.split(" - ")[0]
        equip_sel = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo), None)

        if equip_sel:
            link_equip = base_url + "/?tag=" + equip_sel["tag"]
            api_qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=" + link_equip

            html_etiqueta = f'<div class="etiqueta-box"><div class="etiqueta-header">PMOC - SER CONSCIENTE</div><div style="font-size: 8px; line-height: 1.1;"><b>TAG:</b> {equip_sel["tag"]}<br><b>Amb:</b> {equip_sel["ambiente"]}<br><b>Equip:</b> {equip_sel["equipamento"]}<br><b>Carga:</b> {equip_sel["btus"]} BTUs</div><div style="text-align: center; margin: 1px 0;"><img src="{api_qr_url}" width="65" height="65" style="border: 1px solid #ddd; padding: 1px; background: #fff;"></div><div style="text-align: center; font-size: 6px; color: #000; font-weight: bold; line-height: 1;">Eng. Alessandro Coelho (CREA-MG 238968-D)<br>ART: MG20265436050</div></div>'

            st.markdown(html_etiqueta, unsafe_allow_html=True)

elif opcao == "📑 Lote A4 para Gráfica (Guilhotina)":
    st.header("📑 Gerador de Arquivo PDF Pronto para Gráfica (5x5 cm)")
    todas_tags = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
    selecionar_todos = st.checkbox("Selecionar todos os equipamentos cadastrados", value=True)

    if selecionar_todos:
        equipamentos_selecionados = todas_tags
    else:
        equipamentos_selecionados = st.multiselect("Selecione os equipamentos:", todas_tags, default=todas_tags[:6])

    if st.button("🚀 Gerar PDF Oficial para Download"):
        if not equipamentos_selecionados:
            st.warning("Selecione pelo menos um equipamento.")
        else:
            with st.spinner("Gerando arquivo PDF..."):
                try:
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.0*cm, bottomMargin=1.0*cm)
                    story = []
                    base_url = "https://sistema-ser-consciente-fexfnfuwjkntnzwdwhknso.streamlit.app"
                    celulas_pagina = []

                    for idx, item_sel in enumerate(equipamentos_selecionados):
                        tag_cod = item_sel.split(" - ")[0]
                        eq_obj = next((e for e in st.session_state.equipamentos if e["tag"] == tag_cod), None)
                        if eq_obj:
                            link_eq = base_url + "/?tag=" + eq_obj["tag"]
                            qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + link_eq
                            qr_img_obj = None
                            try:
                                req = urllib.request.urlopen(qr_url, timeout=3)
                                qr_bytes = req.read()
                                qr_io = io.BytesIO(qr_bytes)
                                qr_img_obj = RLImage(qr_io, width=1.6*cm, height=1.6*cm)
                            except Exception:
                                pass

                            estilo_header = ParagraphStyle("EtqHeader", fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=colors.whitesmoke, alignment=1)
                            estilo_texto = ParagraphStyle("EtqText", fontName="Helvetica", fontSize=6.0, leading=7.5, textColor=colors.black, alignment=0)
                            estilo_footer = ParagraphStyle("EtqFooter", fontName="Helvetica-Bold", fontSize=5.5, leading=7, textColor=colors.black, alignment=1)

                            t_header = Table([[Paragraph("<b>PMOC - SER CONSCIENTE</b>", estilo_header)]], colWidths=[4.6*cm])
                            t_header.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.black), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))

                            txt_dados = Paragraph(f"<b>TAG:</b> {eq_obj['tag']}<br/><b>Amb:</b> {eq_obj['ambiente']}<br/><b>Equip:</b> {eq_obj['equipamento']}<br/><b>Carga:</b> {eq_obj['btus']} BTUs", estilo_texto)
                            txt_rodape = Paragraph("Eng. Alessandro Coelho (CREA-MG 238968-D)<br/><b>ART:</b> MG20265436050", estilo_footer)

                            conteudo_etiqueta = [t_header, Spacer(1, 1), txt_dados, Spacer(1, 0.5)]
                            if qr_img_obj:
                                conteudo_etiqueta.append(qr_img_obj)
                            conteudo_etiqueta.append(Spacer(1, 0.5))
                            conteudo_etiqueta.append(txt_rodape)

                            t_etiqueta = Table([[conteudo_etiqueta]], colWidths=[5.0*cm], rowHeights=[5.0*cm])
                            t_etiqueta.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("BOX", (0, 0), (-1, -1), 1, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))

                            celulas_pagina.append(t_etiqueta)

                            if len(celulas_pagina) == 15 or (idx == len(equipamentos_selecionados) - 1):
                                linhas_tabela = []
                                linha_atual = []
                                for cell in celulas_pagina:
                                    linha_atual.append(cell)
                                    if len(linha_atual) == 3:
                                        linhas_tabela.append(linha_atual)
                                        linha_atual = []
                                if linha_atual:
                                    while len(linha_atual) < 3:
                                        linha_atual.append("")
                                    linhas_tabela.append(linha_atual)

                                t_pagina = Table(linhas_tabela, colWidths=[5.0*cm, 5.0*cm, 5.0*cm], rowHeights=[5.0*cm] * len(linhas_tabela))
                                t_pagina.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
                                story.append(t_pagina)
                                if idx < len(equipamentos_selecionados) - 1:
                                    story.append(PageBreak())
                                celulas_pagina = []

                    doc.build(story)
                    pdf_buffer.seek(0)
                    st.success("✅ Arquivo PDF gerado com sucesso!")
                    st.download_button(label="📥 Baixar PDF Pronto para a Gráfica", data=pdf_buffer, file_name="etiquetas_pmoc_5x5cm_grafica.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

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
    df = pd.DataFrame(st.session_state.equipamentos)
    st.dataframe(df, use_container_width=True)

elif opcao == "📄 Relatório Fiscal A4":
    st.header("📄 Relatório Fiscal Oficial A4 (Completo com Checklists e Fotos)")
    st.info("ℹ️ Este relatório consolida a relação de equipamentos, o histórico completo de manutenções com os itens verificados no checklist e os registros fotográficos (Antes e Depois) em um formato PDF executivo pronto para fiscalização.")

    if st.button("🚀 Gerar PDF Oficial Completo do Relatório Fiscal"):
        with st.spinner("Compilando relatório fiscal completo com fotos e checklists..."):
            try:
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
                story = []

                estilo_titulo = ParagraphStyle("RelTitulo", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#111111"), alignment=1)
                estilo_sub = ParagraphStyle("RelSub", fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=colors.HexColor("#333333"), alignment=1)
                estilo_info = ParagraphStyle("RelInfo", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#444444"))
                estilo_secao = ParagraphStyle("RelSecao", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=colors.HexColor("#000000"), spaceBefore=12, spaceAfter=6)
                estilo_texto = ParagraphStyle("RelTexto", fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#222222"))
                estilo_check = ParagraphStyle("RelCheck", fontName="Helvetica", fontSize=7.5, leading=10, textColor=colors.HexColor("#333333"), leftIndent=10)

                # Cabeçalho
                story.append(Paragraph("<b>INSTITUTO SER CONSCIENTE LTDA</b>", estilo_titulo))
                story.append(Paragraph("PLANO DE MANUTENÇÃO, OPERAÇÃO E CONTROLE - PMOC", estilo_sub))
                story.append(Paragraph("Lei Federal nº 13.589/2018 | ART CREA-MG: MG20265436050", estilo_sub))
                story.append(Spacer(1, 10))

                data_hoje_str = datetime.date.today().strftime("%d/%m/%Y")
                story.append(Paragraph(f"<b>Data de Emissão:</b> {data_hoje_str}", estilo_info))
                story.append(Paragraph("<b>Responsável Técnico:</b> Eng. Alessandro Coelho (CREA-MG 238968-D)", estilo_info))
                story.append(Paragraph("<b>Administrador / Gestor:</b> Antônio Sérgio Silva Gomes", estilo_info))
                story.append(Spacer(1, 10))

                # Tabela Resumo
                story.append(Paragraph("📑 Relação Resumida dos Equipamentos Instalados", estilo_secao))
                instalados_df = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]

                dados_tabela = [["TAG", "Ambiente", "Equipamento", "BTUs", "Última Manutenção", "Próxima", "Frequência"]]
                for eq in instalados_df:
                    hists_eq = [h for h in st.session_state.historico if h["tag"] == eq["tag"]]
                    if hists_eq:
                        ultima_manut = hists_eq[-1]
                        ultima_data = ultima_manut["data"]
                        freq_ult = ultima_manut.get("periodicidade", "Semestral")
                        dias_vencimento = 90 if "Trimestral" in freq_ult else 180
                        try:
                            d_obj = datetime.datetime.strptime(ultima_data, "%d/%m/%Y").date()
                            d_prox = d_obj + datetime.timedelta(days=dias_vencimento)
                            prox_data_str = d_prox.strftime("%d/%m/%Y")
                        except Exception:
                            prox_data_str = "A calcular"
                    else:
                        ultima_data = "Sem registro"
                        freq_ult = "-"
                        prox_data_str = "-"

                    dados_tabela.append([eq["tag"], eq["ambiente"], eq["equipamento"], str(eq["btus"]), ultima_data, prox_data_str, freq_ult[:10]])

                t_resumo = Table(dados_tabela, colWidths=[2.0*cm, 3.2*cm, 3.2*cm, 1.6*cm, 2.5*cm, 2.2*cm, 2.3*cm])
                t_resumo.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#000000")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                story.append(t_resumo)
                story.append(Spacer(1, 15))

                # Histórico Completo com Checklists e Fotos
                story.append(Paragraph("📖 Detalhamento Completo, Checklists e Registros Fotográficos", estilo_secao))
                for eq in instalados_df:
                    story.append(Paragraph(f"<b>📍 Equipamento: {eq['ambiente']} (TAG: {eq['tag']})</b> — {eq['equipamento']} ({eq['btus']} BTUs)", estilo_texto))
                    hists_eq = [h for h in st.session_state.historico if h["tag"] == eq["tag"]]
                    if hists_eq:
                        for h in hists_eq:
                            freq_reg = h.get("periodicidade", "Semestral")
                            story.append(Paragraph(f"• <b>Data:</b> {h['data']} ({freq_reg}) | <b>Técnico:</b> {h['tecnico']}", estilo_texto))
                            
                            if "checklist" in h and h["checklist"]:
                                story.append(Paragraph("  <b>Itens Verificados (PMOC):</b>", estilo_check))
                                for k, v in h["checklist"].items():
                                    simbolo = "✓" if v else "X"
                                    story.append(Paragraph(f"    [{simbolo}] {k}", estilo_check))

                            if h.get("obs"):
                                story.append(Paragraph(f"  <b>Observações:</b> {h['obs']}", estilo_check))

                            # Adicionar Fotos ao PDF (Compactas)
                            f_antes = h.get("fotos_antes_bytes", [])
                            f_depois = h.get("fotos_depois_bytes", [])
                            
                            img_cells = []
                            if f_antes:
                                try:
                                    img_io = io.BytesIO(f_antes[0])
                                    img_cells.append(RLImage(img_io, width=4.0*cm, height=3.0*cm))
                                except Exception:
                                    pass
                            if f_depois:
                                try:
                                    img_io = io.BytesIO(f_depois[0])
                                    img_cells.append(RLImage(img_io, width=4.0*cm, height=3.0*cm))
                                except Exception:
                                    pass

                            if img_cells:
                                t_imgs = Table([img_cells], colWidths=[4.5*cm]*len(img_cells))
                                t_imgs.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
                                story.append(Spacer(1, 4))
                                story.append(t_imgs)
                                story.append(Spacer(1, 4))

                            story.append(Spacer(1, 4))
                    else:
                        story.append(Paragraph("  <i>(Nenhuma manutenção registrada)</i>", estilo_texto))
                    story.append(Spacer(1, 8))

                doc.build(story)
                pdf_buffer.seek(0)
                st.success("✅ Relatório Fiscal Completo em PDF gerado com sucesso!")
                st.download_button(
                    label="📥 Baixar Relatório Fiscal Oficial Completo (PDF)",
                    data=pdf_buffer,
                    file_name="relatorio_fiscal_pmoc_completo.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Erro ao compilar PDF fiscal completo: {e}")
