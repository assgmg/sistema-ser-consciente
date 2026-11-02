import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
import datetime

st.set_page_config(page_title="PMOC - Instituto Ser Consciente", layout="wide", page_icon="❄️")

# -----------------------------------------------------------------------------
# BASE DE DADOS INICIAL COM OS 32 EQUIPAMENTOS DO INSTITUTO SER CONSCIENTE
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
        {"tag": "CONS022", "ambiente": "Consultório 22", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS023", "ambiente": "Consultório 23", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS024", "ambiente": "Consultório 24", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS025", "ambiente": "Consultório 25", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "CONS026", "ambiente": "Consultório 26", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "RECP001", "ambiente": "Recepção 01", "equipamento": "Cassete Philco", "btus": "48000", "status": "Instalado"},
        {"tag": "RECP002", "ambiente": "Recepção 02", "equipamento": "Split Electrolux", "btus": "22000", "status": "Instalado"},
        {"tag": "COPA001", "ambiente": "Copa", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"},
        {"tag": "MULTI001", "ambiente": "Espaço Multiatividades", "equipamento": "Sem instalação", "btus": "34000", "status": "Previsto"},
        {"tag": "FRALD01", "ambiente": "Fraldário", "equipamento": "Sem instalação", "btus": "9000", "status": "Previsto"},
        {"tag": "ADM0001", "ambiente": "Administração", "equipamento": "Split Agratto", "btus": "9000", "status": "Instalado"}
    ]

# INICIALIZAÇÃO DA SESSÃO
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_equipamentos_iniciais()

if "historico" not in st.session_state:
    st.session_state.historico = []

# MENU LATERAL
st.sidebar.title("❄️ PMOC Digital")
st.sidebar.subheader("Instituto Ser Consciente Ltda")
opcao = st.sidebar.radio("Navegação", ["🔍 Consulta QR Code", "🛠️ Registrar Manutenção", "✏️ Editar Previstos", "🖨️ Gerar QR Codes", "📊 Dashboard Geral"])

# -----------------------------------------------------------------------------
# 1. CONSULTA PÚBLICA / FISCAL (QR CODE)
# -----------------------------------------------------------------------------
if opcao == "🔍 Consulta QR Code":
    st.header("🔍 Consulta de Conformidade PMOC")
    
    tags = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
    tag_selecionada = st.selectbox("Selecione a TAG do Equipamento (Simulação do QR Code):", tags)
    tag_codigo = tag_selecionada.split(" - ")[0]
    
    equip = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo), None)
    
    if equip:
        st.subheader(f"📍 {equip['ambiente']} ({equip['tag']})")
        st.write(f"**Equipamento:** {equip['equipamento']} | **Carga Térmica:** {equip['btus']} BTUs")
        st.write(f"**Status de Instalação:** `{equip['status']}`")
        
        # Filtra histórico do equipamento
        hists = [h for h in st.session_state.historico if h["tag"] == tag_codigo]
        
        if equip["status"] == "Previsto":
            st.info("🟡 Equipamento Previsto — Aguardando Instalação Física.")
        elif hists:
            ultima_manut = hists[-1]
            data_str = ultima_manut["data"]
            
            st.success("🟢 STATUS DA MANUTENÇÃO: REGISTRADA")
            st.write(f"**Última Manutenção:** {data_str}")
        else:
            st.warning("⚪ Nenhuma manutenção registrada ainda para este equipamento.")
            
        st.markdown("---")
        # ÁREA DE AUTENTICAÇÃO DO FISCAL
        with st.expander("🔐 Área Restrita / Fiscalização"):
            senha = st.text_input("Digite a senha do fiscal:", type="password")
            if senha == "visa":
                st.success("Autenticação realizada com sucesso!")
                st.subheader("📋 Histórico Completo de Manutenções")
                
                if hists:
                    for idx, h in enumerate(reversed(hists)):
                        st.markdown(f"### Manutenção em {h['data']}")
                        st.write(f"**Técnico:** {h['tecnico']}")
                        st.write(f"**Filtros Limpos:** {'Sim' if h['filtros'] else 'Não'} | **Dreno Verificado:** {'Sim' if h['dreno'] else 'Não'} | **Serpentina Limpa:** {'Sim' if h['serpentina'] else 'Não'}")
                        if h["obs"]:
                            st.write(f"**Observações:** {h['obs']}")
                        
                        col1, col2 = st.columns(2)
                        if h["foto_antes"]:
                            col1.image(h["foto_antes"], caption="Foto Antes", use_container_width=True)
                        if h["foto_depois"]:
                            col2.image(h["foto_depois"], caption="Foto Depois", use_container_width=True)
                        st.markdown("---")
                else:
