import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
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
# BASE DE DADOS INICIAL (32 EQUIPAMENTOS)
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 Acesso Restrito")
senha_input = st.sidebar.text_input("Credencial de acesso:", type="password")

if senha_input == "admin":
    st.sidebar.success("✅ Modo Administrador")
    opcoes_menu = [
        "📋 Informações do Equipamento", 
        "🛠️ Registrar Manutenção", 
        "✏️ Editar Previstos", 
        "🖨️ Gerar QR Codes", 
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
    st.header("📋 Informações do Equipamento - PMOC")
    
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
            try:
                d_obj = datetime.datetime.strptime(data_ult_str, "%d/%m/%Y").date()
                d_prox = d_obj + datetime.timedelta(days=30)
                d_prox_str = d_prox.strftime("%d/%m/%Y")
                hoje = datetime.date.today()
                
                if hoje <= d_prox:
                    st.success("🟢 STATUS DA MANUTENÇÃO: EM DIA")
                else:
                    st.error("🔴 STATUS DA MANUTENÇÃO: PENDENTE (Vencida)")
            except:
                d_prox_str = "A calcular"
                st.success("🟢 STATUS DA MANUTENÇÃO: REGISTRADA")

            st.write(f"**Última Manutenção:** {data_ult_str}")
            st.write(f"**Próxima Manutenção Preventiva:** {d_prox_str}")
            st.write(f"**Técnico Responsável:** {ultima_manut['tecnico']}")
        else:
            st.warning("⚪ Nenhuma manutenção registrada ainda para este equipamento.")
            
        st.markdown("---")
        st.markdown("### 🔐 Acesso ao Histórico Detalhado e Fotos")
        senha_tela = st.text_input("Digite a senha de acesso para liberar o relatório completo:", type="password", key=f"senha_tela_{tag_codigo}")
        
        senha_ativa = senha_input if senha_input in ["visa", "admin"] else senha_tela
        
        if senha_ativa in ["visa", "admin"]:
            st.success("Acesso autorizado ao relatório completo do equipamento.")
            st.subheader("📋 Histórico Acumulado de Manutenções e Registros Fotográficos")
            
            if hists:
                for idx, h in enumerate(reversed(hists)):
                    indice_real = len(st.session_state.historico) - 1 - idx
                    
                    txt_filtros = "Sim" if h['filtros'] else "Não"
                    txt_dreno = "Sim" if h['dreno'] else "Não"
                    txt_serpentina = "Sim" if h['serpentina'] else "Não"
                    
                    txt_pecas = "Sim" if h.get('pecas') else "Não"
                    txt_isolamento = "Sim" if h.get('isolamento') else "Não"
                    txt_gas = "Sim" if h.get('gas') else "Não"
                    
                    st.markdown(f"#### Manutenção #{len(hists)-idx} — Data: {h['data']}")
                    st.write(f"**Técnico Executor:** {h['tecnico']}")
                    st.write(f"**Checklist:** Filtros: {txt_filtros} | Dreno: {txt_dreno} | Serpentina: {txt_serpentina}")
                    st.write(f"**Serviços Adicionais:** Peças: {txt_pecas} | Isolamento: {txt_isolamento} | Carga de Gás: {txt_gas}")
                    if h["obs"]:
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
                        with st.expander(f"✏️ Editar ou 🗑️ Excluir este registro ({h['data']})"):
                            with st.form(f"form_edit_{tag_codigo}_{idx}"):
                                novo_data = st.text_input("Alterar Data (DD/MM/AAAA)", value=h['data'])
                                novo_tecnico = st.text_input("Alterar Técnico", value=h['tecnico'])
                                novo_obs = st.text_area("Alterar Observações", value=h['obs'])
                                
                                salvar_edicao = st.form_submit_button("💾 Salvar Alterações")
                                if salvar_edicao:
                                    st.session_state.historico[indice_real]["data"] = novo_data
                                    st.session_state.historico[indice_real]["tecnico"] = novo_tecnico
                                    st.session_state.historico[indice_real]["obs"] = novo_obs
                                    salvar_dados_disco(st.session_state.historico)
                                    st.cache_data.clear()
                                    st.success("Registro atualizado com sucesso! Atualize a página.")
                                    st.rerun()

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
        
        with st.form("form_manutencao"):
            data_manut = st.text_input("Data da Manutenção (DD/MM/AAAA)", value=hoje_formatado)
            tecnico = st.text_input("Técnico Responsável", value="Antônio Sérgio Silva Gomes")
            
            st.write("**Checklist Padrão de Limpeza:**")
            filtros = st.checkbox("Filtros de Ar Limpos", value=True)
            dreno = st.checkbox("Bandeja e Dreno Desobstruídos", value=True)
            serpentina = st.checkbox("Serpentina Higienizada", value=True)
            
            st.write("**Serviços Extras Realizados:**")
            pecas = st.checkbox("Substituição de peças")
            isolamento = st.checkbox("Substituição de isolamento térmico")
            gas = st.checkbox("Carga de gás")
            
            obs = st.text_area("Observações Técnicas")
            foto_antes = st.file_uploader("Tirar foto do ANTES", type=["png", "jpg", "jpeg"])
            foto_depois = st.file_uploader("Tirar foto do DEPOIS", type=["png", "jpg", "jpeg"])
            
            salvar = st.form_submit_button("💾 Salvar Registro de Manutenção")
            
            if salvar:
                img_antes_bytes = foto_antes.getvalue() if foto_antes else None
                img_depois_bytes = foto_depois.getvalue() if foto_depois else None
                
                novo_registro = {
                    "tag": tag_codigo,
                    "data": data_manut,
                    "tecnico": tecnico,
                    "filtros": filtros,
                    "dreno": dreno,
                    "serpentina": serpentina,
                    "pecas": pecas,
                    "isolamento": isolamento,
                    "gas": gas,
                    "obs": obs,
                    "foto_antes_bytes": img_antes_bytes,
                    "foto_depois_bytes": img_depois_bytes
                }
                
                st.session_state.historico.append(novo_registro)
                salvar_dados_disco(st.session_state.historico)
                st.cache_data.clear()
                st.success(f"Manutenção do equipamento {tag_codigo} registrada e salva permanentemente com sucesso!")
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
# 4. GERAR QR CODES (BLINDADO CONTRA TELA BRANCA)
# -----------------------------------------------------------------------------
elif opcao == "🖨️ Gerar QR Codes" and senha_input == "admin":
    st.header("🖨️ Gerador de QR Codes para Etiquetas")
    st.write("A etiqueta gerada inclui o QR code, o nome da clínica e a TAG impressa claramente para validação.")
    
    base_url = st.text_input("URL base do seu sistema no Streamlit:", value="https://sistema-ser-consciente-fexfnfuwjkntnzwdwhknso.streamlit.app")
    
    lista_eq_qr = [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos]
    
    if lista_eq_qr:
        tag_sel_qr = st.selectbox("Selecione o Equipamento para a Etiqueta:", lista_eq_qr, key="select_qr_eq")
        
        if tag_sel_qr:
            tag_codigo = tag_sel_qr.split(" - ")[0]
            equip_selecionado = next((e for e in st.session_state.equipamentos if e["tag"] == tag_codigo), None)
            
            if equip_selecionado:
                ambiente_nome = equip_selecionado["ambiente"]
                link_qr = f"{base_url}/?tag={tag_codigo}"
                
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(link_qr)
                qr.make(fit=True)
                img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                
                largura_qr, altura_qr = img_qr.size
                altura_banner = 140
                etiqueta = Image.new('RGB', (largura_qr, altura_qr + altura_banner), 'white')
                etiqueta.paste(img_qr, (0, 0))
                
                draw = ImageDraw.Draw(etiqueta)
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
                    
                draw.text((15, altura_qr + 10), "PMOC - Clínica Instituto Ser Consciente", fill="black", font=font)
                draw.text((15, altura_qr + 45), f"TAG: {tag_codigo}", fill="black", font=font)
                draw.text((15, altura_qr + 80), f"Ambiente: {ambiente_nome}", fill="black", font=font)
                
                buf = BytesIO()
                etiqueta.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.markdown("---")
                st.subheader(f"Etiqueta Gerada para: {tag_codigo}")
                st.image(etiqueta, caption=f"Etiqueta Oficial: {tag_codigo}", width=300)
                st.download_button(
                    label=f"⬇️ Baixar Etiqueta Completa ({tag_codigo}) para Vinil",
                    data=byte_im,
                    file_name=f"etiqueta_{tag_codigo}.png",
                    mime="image/png"
                )
    else:
        st.warning("Nenhum equipamento cadastrado para gerar QR Code.")

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
        st.markdown("<b>Lei Federal nº 13.589/2018</b>", unsafe_allow_html=True)

    data_hoje_str = datetime.date.today().strftime('%d/%m/%Y')
    st.markdown(f"**Data de Emissão:** {data_hoje_str}")
    st.markdown(f"**Responsável Técnico / Administrador:** Antônio Sérgio Silva Gomes")
    st.markdown("---")
    
    st.markdown("### 📑 Relação Resumida dos Equipamentos Instalados")
    instalados_df = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
    
    dados_resumo = []
    for eq in instalados_df:
        hists_eq = [h for h in st.session_state.historico if h["tag"] == eq["tag"]]
        ultima_data = hists_eq[-1]["data"] if hists_eq else "Sem registro"
        dados_resumo.append({
            "TAG": eq["tag"],
            "Ambiente": eq["ambiente"],
            "Equipamento": eq["equipamento"],
            "BTUs": eq["btus"],
            "Última Manutenção": ultima_data,
            "Qtd Registros": len(hists_eq)
        })
        
    df_resumo = pd.DataFrame(dados_resumo)
    st.table(df_resumo)
    
    st.markdown("---")
    st.markdown("### 📖 Detalhamento Completo e Histórico de Manutenções")
    
    for eq in instalados_df:
        st.markdown(f"#### 📍 Equipamento: {eq['ambiente']} (TAG: {eq['tag']})")
        st.write(f"**Modelo:** {eq['equipamento']} | **Carga Térmica:** {eq['btus']} BTUs")
        
        hists_eq = [h for h in st.session_state.historico if h["tag"] == eq["tag"]]
        if hists_eq:
            for h in hists_eq:
                txt_f = "Sim" if h['filtros'] else "Não"
                txt_d = "Sim" if h['dreno'] else "Não"
                txt_s = "Sim" if h['serpentina'] else "Não"
                txt_p = "Sim" if h.get('pecas') else "Não"
                txt_i = "Sim" if h.get('isolamento') else "Não"
                txt_g = "Sim" if h.get('gas') else "Não"

                st.write(f"- **Data da Manutenção:** {h['data']} | **Técnico:** {h['tecnico']}")
                st.write(f"  * Checklist: Filtros: {txt_f} | Dreno: {txt_d} | Serpentina: {txt_s}")
                st.write(f"  * Extras: Peças: {txt_p} | Isolamento: {txt_i} | Gás: {txt_g}")
                if h["obs"]:
                    st.write(f"  * Observações: {h['obs']}")
                
                c1, c2 = st.columns(2)
                if h.get("foto_antes_bytes"):
                    c1.image(h["foto_antes_bytes"], caption=f"Foto Antes - {h['data']}", width=250)
                elif h.get("foto_antes"):
                    c1.image(h["foto_antes"], caption=f"Foto Antes - {h['data']}", width=250)
                    
                if h.get("foto_depois_bytes"):
                    c2.image(h["foto_depois_bytes"], caption=f"Foto Depois - {h['data']}", width=250)
                elif h.get("foto_depois"):
                    c2.image(h["foto_depois"], caption=f"Foto Depois - {h['data']}", width=250)
        else:
            st.write("*(Nenhuma manutenção registrada para este equipamento)*")
        st.markdown("---")
