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
        border: 2px solid #000;
        border-radius: 6px;
        padding: 10px;
        background-color: #ffffff;
        color: #000000;
        width: 100%;
        max-width: 300px;
        font-family: Arial, sans-serif;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        box-sizing: border-box;
    }
    .etiqueta-header {
        background-color: #000;
        color: #fff;
        padding: 4px 6px;
        font-weight: bold;
        font-size: 11px;
        text-align: center;
        border-radius: 3px;
        margin-bottom: 6px;
    }
    .folha-a4-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        background: white;
        padding: 20px;
        border: 1px dashed #999;
        justify-content: flex-start;
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
senha_input = st.sidebar.text_input("Credencial de acesso:", type="password")

if senha_input == "admin":
    st.sidebar.success("✅ Modo Administrador")
    opcoes_menu = [
        "📋 Informações do Equipamento", 
        "🛠️ Registrar Manutenção", 
        "✏️ Editar Previstos", 
        "🖨️ Etiquetas 5x5 cm (Individual)", 
        "📑 Lote A4 para Gráfica (Guilhotina)",
        "📊 Dashboard Geral",
        "📄 Relatório Fiscal A4"
    ]
elif senha_input == "visa":
    st.sidebar.info("👁️ Modo Fiscalização")
    opcoes_menu = [
        "📋 Informações do Equipamento", 
        "📄 Relatório Fiscal A4"
    ]
else:
    opcoes_menu = [
        "📋 Informações do Equipamento"
    ]

opcao = st.sidebar.radio("Navegação", opcoes_menu)

# -----------------------------------------------------------------------------
# 1. INFORMAÇÕES DO EQUIPAMENTO
# -----------------------------------------------------------------------------
if opcao == "📋 Informações do Equipamento":
    st.header("📋 Informações do Equipamento - PMOC Oficial")
    st.info("ℹ️ Projeto validado pela Vineyard Engenharia | ART CREA-MG nº MG20265436050")
    
    tags_lista = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
    indice_inicial = 0
    
    if tag_url:
        for i, t in enumerate(tags_lista):
            if tag_url in t:
                indice_inicial = i
                break

    tag_selecionada = st.selectbox("Selecione a TAG do Equipamento:", tags_lista, index=indice_inicial)
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
            except:
                d_prox_str = "A calcular"
                st.success("🟢 STATUS DA MANUTENÇÃO: REGISTRADA")

            st.write(f"**Última Manutenção Realizada:** {data_ult_str} — *{tipo_freq}*")
            st.write(f"**Próxima Manutenção Programada:** {d_prox_str}")
            st.write(f"**Técnico Executor:** {ultima_manut['tecnico']}")
        else:
            st.warning("⚪ Nenhuma manutenção registrada ainda para este equipamento.")
            
        st.markdown("---")
        st.subheader("📋 Histórico Acumulado e Gerenciamento de Registros")
        
        if hists:
            for idx, h in enumerate(reversed(hists)):
                indice_real = len(st.session_state.historico) - 1 - idx
                freq_reg = h.get('periodicidade', 'Semestral')
                
                st.markdown(f"#### Manutenção #{len(hists)-idx} — Data: {h['data']} ({freq_reg})")
                st.write(f"**Técnico Executor:** {h['tecnico']}")
                
                if "checklist" in h and h["checklist"]:
                    st.write("**Itens Verificados (PMOC):**")
                    for item_nome, status_val in h["checklist"].items():
                        check_icon = "✅" if status_val else "❌"
                        st.write(f"- {check_icon} {item_nome}")
                
                if h.get("obs"):
                    st.write(f"**Observações:** {h['obs']}")
                
                col1, col2 = st.columns(2)
                if h.get("foto_antes_bytes"):
                    col1.image(h["foto_antes_bytes"], caption=f"Foto Antes - {h['data']}", use_container_width=True)
                elif h.get("foto_antes"):
                    col1.image(h["foto_antes"], caption=f"Foto Antes - {h['data']}", use_container_width=True)
                    
                if h.get("foto_depois_bytes"):
                    col2.image(h["foto_depois_bytes"], caption=f"Foto Depois - {h['data']}", use_container_width=True)
                elif h.get("foto_depois"):
                    col2.image(h["foto_depois"], caption=f"Foto Depois - {h['data']}", use_container_width=True)
                
                if senha_input == "admin":
                    if st.button("Excluir este Registro Incorreto", key=f"btn_del_{tag_codigo}_{idx}"):
                        del st.session_state.historico[indice_real]
                        salvar_dados_disco(st.session_state.historico)
                        st.cache_data.clear()
                        st.success("Registro excluído com sucesso! Atualizando...")
                        st.rerun()

                st.markdown("---")
        else:
            st.info("Nenhum histórico cadastrado para este aparelho.")

# -----------------------------------------------------------------------------
# 2. REGISTRAR MANUTENÇÃO
# -----------------------------------------------------------------------------
elif opcao == "🛠️ Registrar Manutenção" and senha_input == "admin":
    st.header("🛠️ Registro de Manutenção Preventiva")
    instalados = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
    tags = [e["tag"] + " - " + e["ambiente"] for e in instalados]
    
    if tags:
        tag_sel = st.selectbox("Selecione o Equipamento:", tags)
        tag_codigo = tag_sel.split(" - ")[0]
        hoje_formatado = datetime.date.today().strftime("%d/%m/%Y")
        
        periodicidade = st.selectbox(
            "Tipo de Manutenção / Periodicidade (Conforme PMOC):", 
            ["Semestral (180 dias)", "Trimestral (90 dias)"]
        )
        
        with st.form("form_manutencao"):
            data_manut = st.text_input("Data da Manutenção (DD/MM/AAAA)", value=hoje_formatado)
            tecnico = st.text_input("Técnico Responsável", value="Antônio Sérgio Silva Gomes")
            
            st.markdown("---")
            st.subheader("📋 Atividades Obrigatórias do PMOC")
            
            checklist_inputs = {}
            if "Trimestral" in periodicidade:
                st.info("📝 Checklist **TRIMESTRAL**:")
                checklist_inputs["4.1 - Limpeza dos filtros de ar"] = st.checkbox("4.1 - Limpeza dos filtros de ar", value=True)
                checklist_inputs["4.2 - Limpeza externa do gabinete"] = st.checkbox("4.2 - Limpeza externa do gabinete", value=True)
                checklist_inputs["4.3 - Verificação de drenagem"] = st.checkbox("4.3 - Verificação de drenagem", value=True)
                checklist_inputs["4.6 - Higienização com bactericida"] = st.checkbox("4.6 - Higienização com bactericida", value=True)
                checklist_inputs["4.9 - Limpeza do ventilador/rotor"] = st.checkbox("4.9 - Limpeza do ventilador/rotor", value=True)
                checklist_inputs["4.10 - Limpeza da bandeja de condensado"] = st.checkbox("4.10 - Limpeza da bandeja de condensado", value=True)
                checklist_inputs["4.11 - Reaperto de terminais/conexões"] = st.checkbox("4.11 - Reaperto de terminais/conexões", value=True)
            else:
                st.info("📝 Checklist **SEMESTRAL** Completo:")
                checklist_inputs["4.1 - Limpeza dos filtros de ar"] = st.checkbox("4.1 - Limpeza dos filtros de ar", value=True)
                checklist_inputs["4.2 - Limpeza externa do gabinete"] = st.checkbox("4.2 - Limpeza externa do gabinete", value=True)
                checklist_inputs["4.3 - Verificação de drenagem"] = st.checkbox("4.3 - Verificação de drenagem", value=True)
                checklist_inputs["4.6 - Higienização com bactericida"] = st.checkbox("4.6 - Higienização com bactericida", value=True)
                checklist_inputs["4.8 - Limpeza química das serpentinas"] = st.checkbox("4.8 - Limpeza química das serpentinas", value=True)
                checklist_inputs["4.9 - Limpeza do ventilador/rotor"] = st.checkbox("4.9 - Limpeza do ventilador/rotor", value=True)
                checklist_inputs["4.10 - Limpeza e desinfecção da bandeja"] = st.checkbox("4.10 - Limpeza e desinfecção da bandeja", value=True)
                checklist_inputs["4.12 - Verificação de corrente/tensão"] = st.checkbox("4.12 - Verificação de corrente/tensão", value=True)
                checklist_inputs["4.13 - Limpeza do condensador"] = st.checkbox("4.13 - Limpeza do condensador", value=True)
                checklist_inputs["4.14 - Verificação dos compressores"] = st.checkbox("4.14 - Verificação dos compressores", value=True)

            st.markdown("---")
            st.subheader("📸 Registros e Observações")
            obs = st.text_area("Observações Técnicas / Ocorrências")
            foto_antes = st.file_uploader("Tirar foto do ANTES", type=["png", "jpg", "jpeg"])
            foto_depois = st.file_uploader("Tirar foto do DEPOIS", type=["png", "jpg", "jpeg"])
            
            salvar = st.form_submit_button("💾 Salvar Registro de Manutenção")
            
            if salvar:
                img_antes_bytes = foto_antes.getvalue() if foto_antes else None
                img_depois_bytes = foto_depois.getvalue() if foto_depois else None
                
                novo_registro = {
                    "tag": tag_codigo,
                    "data": data_manut,
                    "periodicidade": periodicidade,
                    "tecnico": tecnico,
                    "checklist": checklist_inputs,
                    "obs": obs,
                    "foto_antes_bytes": img_antes_bytes,
                    "foto_depois_bytes": img_depois_bytes
                }
                
                st.session_state.historico.append(novo_registro)
                salvar_dados_disco(st.session_state.historico)
                st.cache_data.clear()
                st.success(f"Manutenção {periodicidade} do equipamento {tag_codigo} registrada com sucesso!")
    else:
        st.info("Não há equipamentos instalados no momento.")

# -----------------------------------------------------------------------------
# 3. EDITAR PREVISTOS / GERENCIAR EQUIPAMENTOS
# -----------------------------------------------------------------------------
elif opcao == "✏️ Editar Previstos" and senha_input == "admin":
    st.header("✏️ Gerenciar e Atualizar Equipamentos")
    
    lista_todos = [e["tag"] + " - " + e["ambiente"] + f" ({e['status']})" for e in st.session_state.equipamentos]
    
    if lista_todos:
        tag_sel_ed = st.selectbox("Selecione o Equipamento para Editar:", lista_todos)
        tag_codigo_ed = tag_sel_ed.split(" - ")[0]
        equip_ed = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo_ed), None)
        
        if equip_ed:
            with st.form("
