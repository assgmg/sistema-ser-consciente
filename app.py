import streamlit as str_lib
import pandas as pd
import datetime
import os
import json
import base64

str_lib.set_page_config(page_title="PMOC - Instituto Ser Consciente", layout="wide", page_icon="❄️")

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
@str_lib.cache_resource
def carregar_logo():
    if os.path.exists("Borboleta.png"):
        from PIL import Image
        return Image.open("Borboleta.png")
    return None

logo_img = carregar_logo()

# -----------------------------------------------------------------------------
# ESTILO CSS PARA IMPRESSÃO LIMPA E MASCARA DE ETIQUETA 5x5 cm
# -----------------------------------------------------------------------------
str_lib.markdown("""
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
@str_lib.cache_data
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

if "equipamentos" not in str_lib.session_state:
    str_lib.session_state.equipamentos = carregar_equipamentos_iniciais()

if "historico" not in str_lib.session_state:
    raw_hist = carregar_dados_disco()
    historico_convertido = []
    for h in raw_hist:
        h_conv = h.copy()
        if h_conv.get("foto_antes_bytes"):
            h_conv["foto_antes_bytes"] = base64.b64decode(h_conv["foto_antes_bytes"])
        if h_conv.get("foto_depois_bytes"):
            h_conv["foto_depois_bytes"] = base64.b64decode(h_conv["foto_depois_bytes"])
        historico_convertido.append(h_conv)
    str_lib.session_state.historico = historico_convertido

try:
    tag_url = str_lib.query_params.get("tag", None)
except:
    tag_url = None

# -----------------------------------------------------------------------------
# MENU LATERAL
# -----------------------------------------------------------------------------
if logo_img:
    str_lib.sidebar.image(logo_img, width=120)

str_lib.sidebar.title("❄️ PMOC Digital")
str_lib.sidebar.subheader("Instituto Ser Consciente Ltda")
str_lib.sidebar.caption("Resp. Técnico: Eng. Alessandro Coelho (CREA-MG 238968-D)")
str_lib.sidebar.caption("ART: MG20265436050")

str_lib.sidebar.markdown("---")
str_lib.sidebar.markdown("### 🔐 Acesso Restrito")
senha_input = str_lib.sidebar.text_input("Credencial de acesso:", type="password")

if senha_input == "admin":
    str_lib.sidebar.success("✅ Modo Administrador")
    opcoes_menu = [
        "📋 Informações do Equipamento", 
        "🛠️ Registrar Manutenção", 
        "✏️ Editar Previstos", 
        "🖨️ Etiquetas 5x5 cm (Gráfica)", 
        "📊 Dashboard Geral",
        "📄 Relatório Fiscal A4"
    ]
elif senha_input == "visa":
    str_lib.sidebar.info("👁️ Modo Fiscalização")
    opcoes_menu = [
        "📋 Informações do Equipamento", 
        "📄 Relatório Fiscal A4"
    ]
else:
    opcoes_menu = [
        "📋 Informações do Equipamento"
    ]

opcao = str_lib.sidebar.radio("Navegação", opcoes_menu)

# -----------------------------------------------------------------------------
# 1. INFORMAÇÕES DO EQUIPAMENTO
# -----------------------------------------------------------------------------
if opcao == "📋 Informações do Equipamento":
    str_lib.header("📋 Informações do Equipamento - PMOC Oficial")
    str_lib.info("ℹ️ Projeto validado pela Vineyard Engenharia | ART CREA-MG nº MG20265436050")
    
    tags_lista = [e["tag"] + " - " + e["ambiente"] for e in str_lib.session_state.equipamentos]
    indice_inicial = 0
    
    if tag_url:
        for i, t in enumerate(tags_lista):
            if tag_url in t:
                indice_inicial = i
                break

    tag_selecionada = str_lib.selectbox("Selecione a TAG do Equipamento:", tags_lista, index=indice_inicial)
    tag_codigo = tag_selecionada.split(" - ")[0]
    
    equip = next((e for e in str_lib.session_state.equipamentos if e["tag"] == tag_codigo), None)
    
    if equip:
        str_lib.subheader(f"📍 {equip['ambiente']} ({equip['tag']})")
        str_lib.write(f"**Equipamento:** {equip['equipamento']} | **Carga Térmica:** {equip['btus']} BTUs")
        str_lib.write(f"**Status de Instalação:** `{equip['status']}`")
        
        hists = [h for h in str_lib.session_state.historico if h["tag"] == tag_codigo]
        
        if equip["status"] == "Previsto":
            str_lib.info("🟡 Equipamento Previsto — Aguardando Instalação Física.")
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
                    str_lib.success(f"🟢 STATUS DA MANUTENÇÃO: EM DIA ({tipo_freq})")
                else:
                    str_lib.error(f"🔴 STATUS DA MANUTENÇÃO: PENDENTE / VENCIDA ({tipo_freq})")
            except:
                d_prox_str = "A calcular"
                str_lib.success("🟢 STATUS DA MANUTENÇÃO: REGISTRADA")

            str_lib.write(f"**Última Manutenção Realizada:** {data_ult_str} — *{tipo_freq}*")
            str_lib.write(f"**Próxima Manutenção Programada:** {d_prox_str}")
            str_lib.write(f"**Técnico Executor:** {ultima_manut['tecnico']}")
        else:
            str_lib.warning("⚪ Nenhuma manutenção registrada ainda para este equipamento.")
            
        str_lib.markdown("---")
        str_lib.subheader("📋 Histórico Acumulado e Gerenciamento de Registros")
        
        if hists:
            for idx, h in enumerate(reversed(hists)):
                indice_real = len(str_lib.session_state.historico) - 1 - idx
                freq_reg = h.get('periodicidade', 'Semestral')
                
                str_lib.markdown(f"#### Manutenção #{len(hists)-idx} — Data: {h['data']} ({freq_reg})")
                str_lib.write(f"**Técnico Executor:** {h['tecnico']}")
                
                if "checklist" in h and h["checklist"]:
                    str_lib.write("**Itens Verificados (PMOC):**")
                    for item_nome, status_val in h["checklist"].items():
                        check_icon = "✅" if status_val else "❌"
                        str_lib.write(f"- {check_icon} {item_nome}")
                
                if h.get("obs"):
                    str_lib.write(f"**Observações:** {h['obs']}")
                
                col1, col2 = str_lib.columns(2)
                if h.get("foto_antes_bytes"):
                    col1.image(h["foto_antes_bytes"], caption=f"Foto Antes - {h['data']}", use_container_width=True)
                elif h.get("foto_antes"):
                    col1.image(h["foto_antes"], caption=f"Foto Antes - {h['data']}", use_container_width=True)
                    
                if h.get("foto_depois_bytes"):
                    col2.image(h["foto_depois_bytes"], caption=f"Foto Depois - {h['data']}", use_container_width=True)
                elif h.get("foto_depois"):
                    col2.image(h["foto_depois"], caption=f"Foto Depois - {h['data']}", use_container_width=True)
                
                if senha_input == "admin":
                    if str_lib.button("Excluir este Registro Incorreto", key=f"btn_del_{tag_codigo}_{idx}"):
                        del str_lib.session_state.historico[indice_real]
                        salvar_dados_disco(str_lib.session_state.historico)
                        str_lib.cache_data.clear()
                        str_lib.success("Registro excluído com sucesso! Atualizando...")
                        str_lib.rerun()

                str_lib.markdown("---")
        else:
            str_lib.info("Nenhum histórico cadastrado para este aparelho.")

# -----------------------------------------------------------------------------
# 2. REGISTRAR MANUTENÇÃO
# -----------------------------------------------------------------------------
elif opcao == "🛠️ Registrar Manutenção" and senha_input == "admin":
    str_lib.header("🛠️ Registro de Manutenção Preventiva")
    instalados = [e for e in str_lib.session_state.equipamentos if e["status"] == "Instalado"]
    tags = [e["tag"] + " - " + e["ambiente"] for e in instalados]
    
    if tags:
        tag_sel = str_lib.selectbox("Selecione o Equipamento:", tags)
        tag_codigo = tag_sel.split(" - ")[0]
        hoje_formatado = datetime.date.today().strftime("%d/%m/%Y")
        
        periodicidade = str_lib.selectbox(
            "Tipo de Manutenção / Periodicidade (Conforme PMOC):", 
            ["Semestral (180 dias)",
