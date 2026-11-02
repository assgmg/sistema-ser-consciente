import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
import datetime

st.set_page_config(page_title="PMOC - Instituto Ser Consciente", layout="wide", page_icon="❄️")

# -----------------------------------------------------------------------------
# BASE DE DADOS INICIAL COM OS 32 EQUIPAMENTOS
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
    st.session_state.historico = []

# SUPORTE A PARÂMETRO VIA URL (LEITURA DO QR CODE)
query_params = st.query_params
tag_url = query_params.get("tag", None)

st.sidebar.title("❄️ PMOC Digital")
st.sidebar.subheader("Instituto Ser Consciente Ltda")
opcao = st.sidebar.radio("Navegação", ["🔍 Consulta QR Code", "🛠️ Registrar Manutenção", "✏️ Editar Previstos", "🖨️ Gerar QR Codes", "📊 Dashboard Geral"])

# -----------------------------------------------------------------------------
# 1. CONSULTA PÚBLICA / FISCAL (QR CODE)
# -----------------------------------------------------------------------------
if opcao == "🔍 Consulta QR Code":
    st.header("🔍 Consulta de Conformidade PMOC")
    
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
        with st.expander("🔐 Área Restrita / Fiscalização (Senha: visa)"):
            senha = st.text_input("Digite a senha do fiscal:", type="password", key="senha_fiscal")
            if senha == "visa":
                st.success("Autenticação realizada com sucesso!")
                st.subheader("📋 Histórico Completo de Manutenções")
                if hists:
                    for h in reversed(hists):
                        st.markdown(f"### Manutenção em {h['data']}")
                        st.write(f"**Técnico Executor:** {h['tecnico']}")
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
                    st.info("Sem histórico de manutenções cadastradas.")
            elif senha != "":
                st.error("Senha incorreta.")

# -----------------------------------------------------------------------------
# 2. REGISTRAR MANUTENÇÃO
# -----------------------------------------------------------------------------
elif opcao == "🛠️ Registrar Manutenção":
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
            
            st.write("**Checklist de Limpeza:**")
            filtros = st.checkbox("Filtros de Ar Limpos", value=True)
            dreno = st.checkbox("Bandeja e Dreno Desobstruídos", value=True)
            serpentina = st.checkbox("Serpentina Higienizada", value=True)
            
            obs = st.text_area("Observações Técnicas")
            foto_antes = st.file_uploader("Tirar foto do ANTES", type=["png", "jpg", "jpeg"])
            foto_depois = st.file_uploader("Tirar foto do DEPOIS", type=["png", "jpg", "jpeg"])
            
            salvar = st.form_submit_button("💾 Salvar Registro de Manutenção")
            
            if salvar:
                img_antes = Image.open(foto_antes) if foto_antes else None
                img_depois = Image.open(foto_depois) if foto_depois else None
                
                st.session_state.historico.append({
                    "tag": tag_codigo,
                    "data": data_manut,
                    "tecnico": tecnico,
                    "filtros": filtros,
                    "dreno": dreno,
                    "serpentina": serpentina,
                    "obs": obs,
                    "foto_antes": img_antes,
                    "foto_depois": img_depois
                })
                st.success(f"Manutenção do equipamento {tag_codigo} registrada com sucesso por {tecnico}!")
    else:
        st.info("Não há equipamentos instalados no momento para registrar manutenção.")

# -----------------------------------------------------------------------------
# 3. EDITAR PREVISTOS
# -----------------------------------------------------------------------------
elif opcao == "✏️ Editar Previstos":
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
                    st.success(f"O equipamento {tag_codigo} agora está instalado!")
                    st.rerun()
    else:
        st.info("Todos os equipamentos já estão instalados!")

# -----------------------------------------------------------------------------
# 4. GERAR QR CODES
# -----------------------------------------------------------------------------
elif opcao == "🖨️ Gerar QR Codes":
    st.header("🖨️ Gerador de QR Codes para Etiquetas")
    st.write("Gere e baixe os QR codes que direcionam diretamente para a consulta do aparelho.")
    
    base_url = st.text_input("URL base do seu sistema no Streamlit:", value="https://sistema-ser-consciente-fexfnfuwjkntnzwdwhknso.streamlit.app")
    tag_sel = st.selectbox("Selecione o Equipamento para Gerar Etiqueta:", [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos])
    tag_codigo = tag_sel.split(" - ")[0]
    
    link_qr = f"{base_url}/?tag={tag_codigo}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(link_qr)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img_qr.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.image(byte_im, caption=f"QR Code do Equipamento: {tag_codigo} ({link_qr})", width=250)
    st.download_button(
        label=f"⬇️ Baixar QR Code ({tag_codigo}) para Impressão em Vinil",
        data=byte_im,
        file_name=f"qrcode_{tag_codigo}.png",
        mime="image/png"
    )

# -----------------------------------------------------------------------------
# 5. DASHBOARD GERAL
# -----------------------------------------------------------------------------
elif opcao == "📊 Dashboard Geral":
    st.header("📊 Painel Geral de Climatização")
    total = len(st.session_state.equipamentos)
    instalados = len([e for e in st.session_state.equipamentos if e["status"] == "Instalado"])
    previstos = len([e for e in st.session_state.equipamentos if e["status"] == "Previsto"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Ambientes", total)
    col2.metric("Aparelhos Instalados", instalados)
    col3.metric("Aparelhos Previstos", previstos)
    
    st.markdown("---")
    st.subheader("📋 Tabela de Ativos do Instituto")
    df = pd.DataFrame(st.session_state.equipamentos)
    st.dataframe(df, use_container_width=True)
