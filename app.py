import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import json
import base64

# Importações para o PDF em Grade A4 para a Gráfica
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate

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
        return Image.open("Borboleta.png")
    return None

logo_img = carregar_logo()

# -----------------------------------------------------------------------------
# ESTILO CSS PARA IMPRESSÃO LIMPA
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
        "🖨️ Gerar QR Codes (5x5 cm)", 
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
# FUNÇÃO PARA GERAR A IMAGEM INDIVIDUAL DA ETIQUETA (5x5 cm)
# -----------------------------------------------------------------------------
def gerar_imagem_etiqueta_5x5(tag_codigo, ambiente_nome, base_url):
    tamanho = 600  # Alta resolução 300 DPI proporcional
    etiqueta = Image.new('RGB', (tamanho, tamanho), 'white')
    draw = ImageDraw.Draw(etiqueta)
    
    link_qr = f"{base_url}/?tag={tag_codigo}"
    
    # 1. Cabeçalho Superior Preto
    draw.rectangle([(0, 0), (tamanho, 55)], fill="black")
    draw.text((20, 16), "PMOC - INST. SER CONSCIENTE LTDA", fill="white")
    
    # 2. Identificação TAG e Ambiente
    draw.text((20, 75), f"TAG: {tag_codigo}", fill="black")
    draw.text((20, 110), f"Amb: {ambiente_nome}", fill="black")
    
    # 3. Box com Dados do RT e ART
    draw.rectangle([(20, 145), (310, 245)], outline="black", width=2)
    draw.text((30, 155), "RESPONSÁVEL TÉCNICO:", fill="darkblue")
    draw.text((30, 175), "Eng. Alessandro Coelho", fill="black")
    draw.text((30, 195), "CREA-MG: 238968-D", fill="black")
    draw.text((30, 215), "ART: MG20265436050", fill="black")
    
    # 4. QR Code à Direita
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(link_qr)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").resize((240, 240))
    etiqueta.paste(img_qr, (330, 70))
    
    # 5. Rodapé Informativo
    draw.rectangle([(0, 535), (tamanho, tamanho)], fill="#f0f2f6")
    draw.text((20, 555), "Lei Fed. 13.589/2018 | Aponte para ver o Histórico", fill="dimgray")
    
    return etiqueta

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
        st.markdown("### 🔐 Acesso ao Histórico Detalhado e Fotos")
        senha_tela = st.text_input("Digite a senha de acesso para liberar o relatório completo:", type="password", key=f"senha_tela_{tag_codigo}")
        
        senha_ativa = senha_input if senha_input in ["visa", "admin"] else senha_tela
        
        if senha_ativa in ["visa", "admin"]:
            st.success("Acesso autorizado ao relatório completo do equipamento.")
            st.subheader("📋 Histórico Acumulado de Manutenções e Registros")
            
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
                    
                    if senha_input == "admin" or senha_tela == "admin":
                        if st.button(f"🗑️ Excluir Definitivamente este Registro", key=f"btn_del_{tag_codigo}_{idx}"):
                            del st.session_state.historico[indice_real]
                            salvar_dados_disco(st.session_state.historico)
                            st.cache_data.clear()
                            st.success("Registro apagado com sucesso! Atualizando...")
                            st.rerun()

                    st.markdown("---")
            else:
                st.info("Nenhum histórico cadastrado para este aparelho.")
        else:
            st.info("🔒 Insira a senha autorizada acima para visualizar o histórico detalhado, checklist completo e registros fotográficos deste equipamento.")

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
# 3. EDITAR PREVISTOS
# -----------------------------------------------------------------------------
elif opcao == "✏️ Editar Previstos" and senha_input == "admin":
    st.header("✏️ Atualizar Equipamentos Previstos")
    tags_previstas = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos if e["status"] == "Previsto"]
    
    if tags_previstas:
        tag_sel = st.selectbox("Selecione o Equipamento Previsto:", tags_previstas)
        tag_codigo = tag_sel.split(" - ")[0]
        equip = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo), None)
        
        if equip:
            with st.form("form_edicao"):
                st.write(f"**Ambiente:** {equip['ambiente']}")
                novo_nome = st.text_input("Marca / Modelo do Equipamento Instalado", value="Split Agratto")
                novos_btus = st.text_input("Potência (BTUs)", value=equip["btus"])
                confirmar = st.form_submit_button("✅ Confirmar Instalação")
                
                if confirmar:
                    equip["equipamento"] = novo_nome
                    equip["btus"] = novos_btus
                    equip["status"] = "Instalado"
                    st.cache_data.clear()
                    st.success(f"O equipamento {tag_codigo} agora está instalado!")
                    st.rerun()
    else:
        st.info("Todos os equipamentos já estão instalados!")

# -----------------------------------------------------------------------------
# 4. GERAR QR CODES & FOLHA A4 PARA GRÁFICA (GUILHOTINA 5x5 cm)
# -----------------------------------------------------------------------------
elif opcao == "🖨️ Gerar QR Codes (5x5 cm)" and senha_input == "admin":
    st.header("🖨️ Gerador de Etiquetas 5x5 cm e Folha A4 para Gráfica")
    st.write("Baixe a etiqueta individual ou gere o arquivo completo em PDF em grade A4 com marcas de corte para a guilhotina.")
    
    base_url = st.text_input("URL base do seu sistema no Streamlit:", value="https://sistema-ser-consciente-fexfnfuwjkntnzwdwhknso.streamlit.app")
    
    tab_ind, tab_lote = st.tabs(["📥 Etiqueta Individual (5x5 cm)", "📄 Arquivo A4 Completo para Gráfica"])
    
    with tab_ind:
        lista_eq_qr = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
        if lista_eq_qr:
            tag_sel_qr = st.selectbox("Selecione o Equipamento:", lista_eq_qr, key="select_qr_eq")
            if tag_sel_qr:
                tag_codigo = tag_sel_qr.split(" - ")[0]
                equip_sel = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo), None)
                if equip_sel:
                    img_etq = gerar_imagem_etiqueta_5x5(tag_codigo, equip_sel["ambiente"], base_url)
                    st.image(img_etq, caption=f"Prévia da Etiqueta 5x5 cm - {tag_codigo}", width=320)
                    
                    buf = BytesIO()
                    img_etq.save(buf, format="PNG")
                    st.download_button(
                        label=f"⬇️ Baixar Imagem 5x5 ({tag_codigo})",
                        data=buf.getvalue(),
                        file_name=f"etiqueta_5x5_{tag_codigo}.png",
                        mime="image/png"
                    )
        else:
            st.warning("Nenhum equipamento cadastrado.")
            
    with tab_lote:
        st.markdown("### 🖨️ Gerar PDF em Grade A4 para Corte em Guilhotina")
        st.info("Este arquivo organiza **20 etiquetas por página (grade 4x5)** no tamanho exato de 5x5 cm, com margens de segurança e **marcas de corte (cruz de registro)** para a guilhotina da gráfica.")
        
        if st.button("🚀 Gerar PDF A4 de Etiquetas para a Gráfica"):
            instalados = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
            
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=28, rightMargin=28, topMargin=28, bottomMargin=28)
            
            # Dimensões da Página A4 em pontos (1 ponto = 1/72 polegada)
            # A4 = 595.27 x 841.89 pontos
            # Margem útil = largura 539 pt, altura 785 pt
            # Tamanho da etiqueta 5x5 cm = 141.73 pontos x 141.73 pontos
            
            larg_etq = 5 * 28.3465  # 5 cm em pt (~141.7 pt)
            alt_etq = 5 * 28.3465   # 5 cm em pt
            cols = 4
            rows = 5
            
            # Espaçamentos para centralizar na folha A4
            margem_x = (595.27 - (cols * larg_etq)) / 2
            margem_y = (841.89 - (rows * alt_etq)) / 2
            
            story = []
            
            def desenhar_grade_a4(canvas_obj, doc_obj):
                canvas_obj.saveState()
                # Desenhar marcas de corte para a guilhotina nas posições da grade
                for r in range(rows + 1):
                    y = 841.89 - margem_y - (r * alt_etq)
                    for c in range(cols + 1):
                        x = margem_x + (c * larg_etq)
                        # Pequenas marcas de corte em cruz / canto
                        canvas_obj.setStrokeColor(colors.gray)
                        canvas_obj.setLineWidth(0.5)
                        # Cruz externa de corte
                        canvas_obj.line(x - 10, y, x - 3, y)
                        canvas_obj.line(x + 3, y, x + 10, y)
                        canvas_obj.line(x, y - 10, x, y - 3)
                        canvas_obj.line(x, y + 3, x, y + 10)
                canvas_obj.restoreState()

            # Vamos gerar imagens temporárias em PNG de cada etiqueta e inseri-las no canvas do ReportLab
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            
            etq_idx = 0
            for eq in instalados:
                col = etq_idx % cols
                row = (etq_idx // cols) % rows
                
                if etq_idx > 0 and etq_idx % (cols * rows) == 0:
                    c.showPage()
                    etq_idx = 0
                    col = 0
                    row = 0
                
                x = margem_x + (col * larg_etq)
                y = 841.89 - margem_y - ((row + 1) * alt_etq)
                
                # Gerar imagem PIL da etiqueta
                img_etq = gerar_imagem_etiqueta_5x5(eq["tag"], eq["ambiente"], base_url)
                img_io = BytesIO()
                img_etq.save(img_io, format="PNG")
                img_io.seek(0)
                
                # Inserir no PDF
                c.drawImage(img_io, x, y, width=larg_etq, height=alt_etq)
                
                # Desenhar borda fina de contorno para guiar o corte
                c.setStrokeColor(colors.lightgrey)
                c.setLineWidth(0.5)
                c.rect(x, y, larg_etq, alt_etq)
                
                etq_idx += 1
            
            c.save()
            pdf_buffer.seek(0)
            
            st.success("✅ Arquivo PDF A4 gerado com sucesso para a gráfica!")
            st.download_button(
                label="⬇️ Baixar PDF A4 de Etiquetas para Impressão Gráfica",
                data=pdf_buffer.getvalue(),
                file_name="etiquetas_pmoc_5x5_grafica.pdf",
                mime="application/pdf"
            )

# -----------------------------------------------------------------------------
# 5. DASHBOARD GERAL
# -----------------------------------------------------------------------------
elif opcao == "📊 Dashboard Geral" and senha_input == "admin":
    st.header("📊 Painel Geral de Climatização")
    total = len(st.session_state.equipamentos)
    instalados = len([e for e in st.session_state.equipamentos if e["status"] == "Instalado"])
    previstos = len([e for e in st.session_state.equipamentos if e["status"] == "Previsto"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", total)
    col2.metric("Instalados", instalados)
    col3.metric("Previstos", previstos)
    
    st.markdown("---")
    st.subheader("📋 Tabela de Ativos")
    df = pd.DataFrame(st.session_state.equipamentos)
    st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. RELATÓRIO FISCAL A4 COMPLETO
# -----------------------------------------------------------------------------
elif opcao == "📄 Relatório Fiscal A4" and senha_input in ["visa", "admin"]:
    
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if logo_img:
            st.image(logo_img, width=100)
    with col_titulo:
        st.markdown("<h2>INSTITUTO SER CONSCIENTE LTDA</h2>", unsafe_allow_html=True)
        st.markdown("<h4>PLANO DE MANUTENÇÃO, OPERAÇÃO E CONTROLE - PMOC</h4>", unsafe_allow_html=True)
        st.markdown("<b>Lei Federal nº 13.589/2018 | ART CREA-MG: MG20265436050</b>", unsafe_allow_html=True)

    data_hoje_str = datetime.date.today().strftime('%d/%m/%Y')
    st.markdown(f"**Data de Emissão:** {data_hoje_str}")
    st.markdown(f"**Responsável Técnico:** Eng. Alessandro Ribeiro Coelho (CREA-MG 238968-D)")
    st.markdown(f"**Administrador / Gestor:** Antônio Sérgio Silva Gomes")
    st.markdown("---")
    
    st.markdown("### 📑 Relação Resumida dos Equipamentos Instalados")
    instalados_df = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
    
    dados_resumo = []
    for eq in instalados_df:
        hists_eq = [h for h in st.session_state.historico if h["tag"] == eq["tag"]]
        ultima_data = hists_eq[-1]["data"] if hists_eq else "Sem registro"
        freq_ult = hists_eq[-1].get("periodicidade", "Semestral") if h
