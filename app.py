import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
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

query_params = st.query_params
tag_url = query_params.get("tag", None)

st.sidebar.title("❄️ PMOC Digital")
st.sidebar.subheader("Instituto Ser Consciente Ltda")
opcao = st.sidebar.radio("Navegação", [
    "📋 Informações do Equipamento", 
    "🛠️ Registrar Manutenção", 
    "✏️ Editar Previstos", 
    "🖨️ Gerar QR Codes", 
    "📊 Dashboard Geral",
    "📄 Relatório Fiscal A4"
])

# -----------------------------------------------------------------------------
# 1. INFORMAÇÕES DO EQUIPAMENTO (PÚBLICO / RESTRITO)
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
        st.markdown("### 🔐 Área Restrita / Fiscalização (Acesso Protegido)")
        senha = st.text_input("Digite a senha master/fiscal para ver histórico e fotos:", type="password", key="senha_fiscal")
        
        if senha == "visa":
            st.success("Acesso liberado com sucesso!")
            st.subheader("📋 Histórico Acumulado de Manutenções")
            
            if hists:
                for idx, h in enumerate(reversed(hists)):
                    st.markdown(f"#### Manutenção #{len(hists)-idx} — Data: {h['data']}")
                    st.write(f"**Técnico Executor:** {h['tecnico']}")
                    st.write(f"**Checklist:** Filtros: {'Sim' if h['filtros'] else 'Não'} | Dreno: {'Sim' if h['dreno'] else 'Não'} | Serpentina: {'Sim' if h['serpentina'] else 'Não'}")
                    st.write(f"**Serviços Adicionais:** Peças: {'Sim' if h.get('pecas') else 'Não'} | Isolamento: {'Sim' if h.get('isolamento') else 'Não'} | Carga de Gás: {'Sim' if h.get('gas') else 'Não'}")
                    if h["obs"]:
                        st.write(f"**Observações:** {h['obs']}")
                    
                    col1, col2 = st.columns(2)
                    if h["foto_antes"]:
                        col1.image(h["foto_antes"], caption="Foto Antes", use_container_width=True)
                    if h["foto_depois"]:
                        col2.image(h["foto_depois"], caption="Foto Depois", use_container_width=True)
                    
                    if st.button(f"🗑️ Deletar este registro ({h['data']})", key=f"del_{tag_codigo}_{idx}"):
                        st.session_state.historico = [item for item in st.session_state.historico if not (item["tag"] == tag_codigo and item["data"] == h["data"] and item["tecnico"] == h["tecnico"])]
                        st.success("Registro deletado com sucesso! Atualize a página.")
                        st.rerun()

                    st.markdown("---")
            else:
                st.info("Nenhum histórico cadastrado para este aparelho.")
        elif senha != "":
            st.error("Senha incorreta. Curiosos e visitantes não possuem acesso ao detalhamento.")

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
                img_antes = Image.open(foto_antes) if foto_antes else None
                img_depois = Image.open(foto_depois) if foto_depois else None
                
                st.session_state.historico.append({
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
                    "foto_antes": img_antes,
                    "foto_depois": img_depois
                })
                st.success(f"Manutenção do equipamento {tag_codigo} acumulada com sucesso!")
    else:
        st.info("Não há equipamentos instalados no momento.")

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
# 4. GERAR QR CODES COM TAG IMPRESSA NA ETIQUETA
# -----------------------------------------------------------------------------
elif opcao == "🖨️ Gerar QR Codes":
    st.header("🖨️ Gerador de QR Codes para Etiquetas")
    st.write("A etiqueta gerada inclui o QR code e a TAG impressa claramente para validação do fiscal.")
    
    base_url = st.text_input("URL base do seu sistema no Streamlit:", value="https://sistema-ser-consciente-fexfnfuwjkntnzwdwhknso.streamlit.app")
    tag_sel = st.selectbox("Selecione o Equipamento:", [e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos])
    
    equip_selecionado = next((e for e in st.session_state.equipamentos if e["tag"] in tag_sel), None)
    tag_codigo = equip_selecionado["tag"]
    ambiente_nome = equip_selecionado["ambiente"]
    
    link_qr = f"{base_url}/?tag={tag_codigo}"
    
    # Gerar imagem do QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(link_qr)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    # Criar uma etiqueta maior em branco para acomodar o texto da TAG e do Ambiente
    largura_qr, altura_qr = img_qr.size
    altura_banner = 120
    etiqueta = Image.new('RGB', (largura_qr, altura_qr + altura_banner), 'white')
    etiqueta.paste(img_qr, (0, 0))
    
    draw = ImageDraw.Draw(etiqueta)
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    # Desenhar textos informativos na etiqueta
    draw.text((20, altura_qr + 15), f"PMOC - SER CONSCIENTE", fill="black", font=font)
    draw.text((20, altura_qr + 45), f"TAG: {tag_codigo}", fill="black", font=font)
    draw.text((20, altura_qr + 75), f"Ambiente: {ambiente_nome}", fill="black", font=font)
    
    buf = BytesIO()
    etiqueta.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.image(etiqueta, caption=f"Etiqueta Oficial com TAG para Impressão: {tag_codigo}", width=300)
    st.download_button(
        label=f"⬇️ Baixar Etiqueta Completa ({tag_codigo}) para Vinil",
        data=byte_im,
        file_name=f"etiqueta_{tag_codigo}.png",
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
    col1.metric("Total", total)
    col2.metric("Instalados", instalados)
    col3.metric("Previstos", previstos)
    
    st.markdown("---")
    st.subheader("📋 Tabela de Ativos")
    df = pd.DataFrame(st.session_state.equipamentos)
    st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. RELATÓRIO FISCAL A4 (RETRATO)
# -----------------------------------------------------------------------------
elif opcao == "📄 Relatório Fiscal A4":
    st.header("📄 Relatório Consolidado para Fiscalização (A4 Retrato)")
    st.write("Este relatório resume a conformidade PMOC de todos os aparelhos instalados no Instituto Ser Consciente para apresentação imediata ao fiscal.")
    
    senha_rel = st.text_input("Digite a senha master para gerar o relatório fiscal:", type="password", key="senha_rel")
    
    if senha_rel == "visa":
        st.success("Senha validada. Relatório pronto para impressão:")
        st.markdown("---")
        
        st.markdown("<h2 style='text-align: center;'>INSTITUTO SER CONSCIENTE LTDA</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>PLANO DE MANUTENÇÃO, OPERAÇÃO E CONTROLE - PMOC (Lei 13.589/2018)</h4>", unsafe_allow_html=True)
        st.markdown(f"**Data de Emissão:** {datetime.date.today().strftime('%d/%m/%Y')}")
        st.markdown(f"**Responsável Técnico / Administrador:** Antônio Sérgio Silva Gomes")
        st.markdown("---")
        
        st.subheader("Resumo Geral dos Equipamentos Instalados")
        instalados_df = [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
        
        dados_relatorio = []
        for eq in instalados_df:
            hists_eq = [h for h in st.session_state.historico if h["tag"] == eq["tag"]]
            ultima_data = hists_eq[-1]["data"] if hists_eq else "Sem registro"
            dados_relatorio.append({
                "TAG": eq["tag"],
                "Ambiente": eq["ambiente"],
                "Equipamento": eq["equipamento"],
                "BTUs": eq["btus"],
                "Ultima Manut.": ultima_data,
                "Qtd Manutenções": len(hists_eq)
            })
            
        df_rel = pd.DataFrame(dados_relatorio)
        st.dataframe(df_rel, use_container_width=True)
        
        st.markdown("---")
        st.write("Dica de Impressão: Pressione **Ctrl + P** no seu navegador e selecione o formato **Retrato (Portrait)** com margens padrão para exportar ou imprimir diretamente em papel A4.")
    elif senha_rel != "":
        st.error("Senha incorreta.")
