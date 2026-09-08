import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import qrcode
from io import BytesIO
import base64

# Configuração da Página
st.set_page_config(page_title="Instituto Ser Consciente - Gestão", layout="wide", page_icon="🦋")

# --- CONFIGURAÇÕES BANCÁRIAS DO INSTITUTO ---
CHAVE_PIX_INSTITUTO = "pix@institutoserconsciente.com.br"
NOME_BENEFICIARIO = "Instituto Ser Consciente Ltda"
CIDADE_BENEFICIARIO = "Contagem"

# --- SIMULAÇÃO DE BANCO DE DADOS NA NUVEM ---
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = [
        {"username": "recepcao", "nome": "Recepção Central", "senha": "Senha@123", "perfil": "recepcao", "primeiro_acesso": True},
        {"username": "admin", "nome": "Administração (Antônio / Direção)", "senha": "Admin@123", "perfil": "admin", "primeiro_acesso": False}
    ]

if 'parceiros_df' not in st.session_state:
    st.session_state.parceiros_df = pd.DataFrame([
        {"id": 1, "nome": "Ana Carolina Ribeiro", "regra": "Percentual (70% Profissional / 30% Clínica)", "status": "Ativo"},
        {"id": 2, "nome": "Anderson Psicólogo", "regra": "Bloco de Horas (6h)", "status": "Ativo"}
    ])

if 'atendimentos' not in st.session_state:
    st.session_state.atendimentos = []

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

if 'ultima_fatura' not in st.session_state:
    st.session_state.ultima_fatura = None

# --- REGRAS OFICIAIS DO INSTITUTO ---
REGRAS_CLINICA = [
    "Percentual (70% Profissional / 30% Clínica)",
    "Percentual (80% Profissional / 20% Clínica)",
    "Bloco de Horas (6h)",
    "Locação por Hora (R$ 50,00/h)",
    "Locação por Hora (R$ 42,00/h)"
]

# --- FUNÇÃO GERADORA DE QR CODE PIX ---
def gerar_qrcode_pix(valor, identificador):
    payload = f"00020126580014BR.GOV.BCB.PIX0136{CHAVE_PIX_INSTITUTO}5204000053039865802BR5925{NOME_BENEFICIARIO}6009{CIDADE_BENEFICIARIO}62070503***6304"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- TELA DE LOGIN ---
def tela_login():
    st.markdown("<h2 style='text-align: center;'>🏥 Sistema de Gestão e Faturamento</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Instituto Ser Consciente</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit:
                user_encontrado = next((u for u in st.session_state.usuarios if u["username"] == usuario and u["senha"] == senha), None)
                if user_encontrado:
                    st.session_state.usuario_logado = user_encontrado
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# --- GESTÃO DE PARCEIROS ---
def gerenciar_parceiros():
    st.markdown("### 👥 Cadastro, Regras e Controle de Parceiros")
    
    df = st.session_state.parceiros_df
    st.dataframe(df, use_container_width=True)
    
    col_cad, col_edit = st.columns(2)
    
    with col_cad:
        st.markdown("#### ➕ Cadastrar Novo Profissional")
        with st.form(key="form_novo_parceiro"):
            novo_cad_nome = st.text_input("Nome do Profissional / Especialidade", key="cad_nome")
            novo_cad_regra = st.selectbox("Regra de Pagamento / Parceria", REGRAS_CLINICA, key="cad_regra")
            btn_cadastrar = st.form_submit_button("Cadastrar Profissional", use_container_width=True)
            
            if btn_cadastrar:
                if novo_cad_nome.strip():
                    novo_id = int(df['id'].max() + 1) if not df.empty else 1
                    novo_registro = pd.DataFrame([{"id": novo_id, "nome": novo_cad_nome, "regra": novo_cad_regra, "status": "Ativo"}])
                    st.session_state.parceiros_df = pd.concat([df, novo_registro], ignore_index=True)
                    st.success(f"Profissional '{novo_cad_nome}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe o nome do profissional.")

    with col_edit:
        st.markdown("#### ⚙️ Editar / Inativar Profissional")
        if not df.empty:
            opcoes_parceiros = df['nome'].tolist()
            parceiro_selecionado = st.selectbox("Selecione o profissional:", opcoes_parceiros)
            dados_atuais = df[df['nome'] == parceiro_selecionado].iloc[0]
            
            with st.form(key="form_edicao_parceiro"):
                novo_nome = st.text_input("Nome", value=dados_atuais['nome'])
                regra_atual_idx = REGRAS_CLINICA.index(dados_atuais['regra']) if dados_atuais['regra'] in REGRAS_CLINICA else 0
                nova_regra = st.selectbox("Regra", REGRAS_CLINICA, index=regra_atual_idx)
                status_disponiveis = ["Ativo", "Inativo"]
                status_atual_idx = status_disponiveis.index(dados_atuais['status']) if dados_atuais['status'] in status_disponiveis else 0
                novo_status = st.selectbox("Status", status_disponiveis, index=status_atual_idx)
                
                col_b1, col_b2 = st.columns(2)
                btn_salvar = col_b1.form_submit_button("💾 Salvar", use_container_width=True)
                btn_excluir = col_b2.form_submit_button("🗑️ Excluir", use_container_width=True)
                
                if btn_salvar:
                    df.loc[df['nome'] == parceiro_selecionado, 'nome'] = novo_nome
                    df.loc[df['nome'] == novo_nome, 'regra'] = nova_regra
                    df.loc[df['nome'] == novo_nome, 'status'] = novo_status
                    st.session_state.parceiros_df = df
                    st.success("Atualizado com sucesso!")
                    st.rerun()
                if btn_excluir:
                    st.session_state.parceiros_df = df[df['nome'] != parceiro_selecionado].reset_index(drop=True)
                    st.warning("Excluído com sucesso!")
                    st.rerun()

# --- MÓDULO VISUAL DE LANÇAMENTOS E FATURAS ---
def modulo_lancamentos():
    st.subheader("📝 Lançamento Rápido e Emissão de Faturas / Recibos")
    
    parceiros_ativos = st.session_state.parceiros_df[st.session_state.parceiros_df['status'] == 'Ativo']
    
    if parceiros_ativos.empty:
        st.warning("Não há profissionais ativos cadastrados.")
        return

    # Layout mais compacto em colunas para evitar rolagem excessiva
    with st.form("form_novo_atendimento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            data_atendimento = st.date_input("Data", value=datetime.today())
        with col2:
            profissional_escolhido = st.selectbox("Profissional / Parceiro", parceiros_ativos['nome'].tolist())
        with col3:
            nome_paciente_cliente = st.text_input("Paciente / Cliente")
            
        regra_prof = parceiros_ativos[parceiros_ativos['nome'] == profissional_escolhido]['regra'].values[0]
        st.caption(f"📌 Regra ativa para este profissional: **{regra_prof}**")
        
        # Parâmetros dinâmicos divididos em colunas limpas
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        
        valor_consulta = 0.0
        qtd_blocos = 1
        hora_chegada = time(8, 0)
        hora_devolucao = time(9, 0)
        forma_pagto = "Pix"
        
        with col_p1:
            if "Percentual" in regra_prof:
                valor_consulta = st.number_input("Valor da Consulta (R$)", min_value=0.0, value=150.0, step=10.0)
            elif "Bloco de Horas" in regra_prof:
                qtd_blocos = st.number_input("Qtd Blocos (6h) no mês", min_value=1, value=1, step=1)
            elif "Locação por Hora" in regra_prof:
                hora_chegada = st.time_input("Início (Chave)", value=time(8, 0))
                
        with col_p2:
            if "Locação por Hora" in regra_prof:
                hora_devolucao = st.time_input("Devolução (Chave)", value=time(9, 0))
            else:
                forma_pagto = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Dinheiro", "Transferência", "Boleto"])
                
        with col_p3:
            if "Locação por Hora" in regra_prof:
                forma_pagto = st.selectbox("Pagamento", ["Pix", "Dinheiro", "Transferência"])

        btn_lancar = st.form_submit_button("⚡ Calcular e Gerar Fatura / Recibo", use_container_width=True)
        
        if btn_lancar:
            if nome_paciente_cliente.strip():
                taxa_clinica = 0.0
                repasse_prof = 0.0
                detalhes_calculo = ""
                
                if regra_prof == "Percentual (70% Profissional / 30% Clínica)":
                    repasse_prof = valor_consulta * 0.70
                    taxa_clinica = valor_consulta * 0.30
                    detalhes_calculo = "70% Profissional / 30% Clínica"
                elif regra_prof == "Percentual (80% Profissional / 20% Clínica)":
                    repasse_prof = valor_consulta * 0.80
                    taxa_clinica = valor_consulta * 0.20
                    detalhes_calculo = "80% Profissional / 20% Clínica"
                elif "Bloco de Horas" in regra_prof:
                    if qtd_blocos == 1:
                        taxa_clinica = 300.0 * qtd_blocos
                        detalhes_calculo = f"1 Bloco único (R$ 300,00)"
                    else:
                        taxa_clinica = 250.0 * qtd_blocos
                        detalhes_calculo = f"{qtd_blocos} Blocos (R$ 250,00 cada)"
                    repasse_prof = 0.0
                elif "Locação por Hora" in regra_prof:
                    valor_hora_base = 50.0 if "50,00" in regra_prof else 42.0
                    dt_ini = datetime.combine(datetime.today(), hora_chegada)
                    dt_fim = datetime.combine(datetime.today(), hora_devolucao)
                    if dt_fim < dt_ini:
                        dt_fim += timedelta(days=1)
                    diff_minutos = (dt_fim - dt_ini).total_seconds() / 60.0
                    
                    horas_cobradas = 0
                    if diff_minutos > 0:
                        horas_inteiras = int(diff_minutos // 60)
                        minutos_restantes = diff_minutos % 60
                        if minutos_restantes > 5:
                            horas_cobradas = horas_inteiras + 1
                        else:
                            horas_cobradas = max(1, horas_inteiras) if horas_inteiras > 0 else 1
                            
                    taxa_clinica = horas_cobradas * valor_hora_base
                    repasse_prof = 0.0
                    detalhes_calculo = f"{horas_cobradas}h cobradas (R$ {valor_hora_base}/h) | {hora_chedaq_str if 'hora_chedaq_str' in locals() else hora_chegada.strftime('%H:%M')} às {hora_devolucao.strftime('%H:%M')}"

                valor_total_fatura = taxa_clinica + repasse_prof if "Percentual" in regra_prof else taxa_clinica

                novo_id = len(st.session_state.atendimentos) + 1
                novo_atend = {
                    "id": novo_id,
                    "data": str(data_atendimento),
                    "cliente_paciente": nome_paciente_cliente,
                    "profissional": profissional_escolhido,
                    "regra_aplicada": regra_prof,
                    "detalhes": detalhes_calculo,
                    "valor_total_envolvido": valor_total_fatura,
                    "taxa_clinica": taxa_clinica,
                    "repasse_profissional": repasse_prof,
                    "pagamento": forma_pagto,
                    "status": "Pendente"
                }
                st.session_state.atendimentos.append(novo_atend)
                st.session_state.ultima_fatura = novo_atend
                st.success("Lançamento efetuado e Fatura gerada com sucesso!")
                st.rerun()
            else:
                st.error("Informe o nome do paciente ou cliente.")

    # --- SEÇÃO VISUAL DA FATURA / RECIBO GERADO ---
    if st.session_state.ultima_fatura:
        fat = st.session_state.ultima_fatura
        st.markdown("---")
        st.markdown("### 📄 Fatura / Recibo de Pagamento Gerado")
        
        col_f1, col_f2 = st.columns([2, 1])
        
        with col_f1:
            st.info(f"""
            **INSTITUTO SER CONSCIENTE LTDA**  
            CNPJ: 04.000.917/0001-47 | Contagem - MG  
            --------------------------------------------------  
            **Fatura Nº:** {fat['id']} | **Data:** {fat['data']}  
            **Profissional:** {fat['profissional']}  
            **Paciente/Cliente:** {fat['cliente_paciente']}  
            **Modalidade / Regra:** {fat['regra_aplicada']}  
            **Detalhamento:** {fat['detalhes']}  
            --------------------------------------------------  
            💵 **Valor a Pagar / Repassar:** **R$ {fat['valor_total_envolvido']:,.2f}**  
            💳 **Forma de Pagamento:** {fat['pagamento']}  
            📌 **Status:** {fat['status']}  
            """)
            
        with col_f2:
            st.markdown("#### 📱 Pagamento via Pix")
            qr_b64 = gerar_qrcode_pix(fat['valor_total_envolvido'], fat['id'])
            st.markdown(f'<img src="data:image/png;base64,{qr_b64}" width="180">', unsafe_allow_html=True)
            st.code(CHAVE_PIX_INSTITUTO, language="text")

    st.markdown("---")
    st.markdown("#### 📋 Histórico de Lançamentos")
    df_atend = pd.DataFrame(st.session_state.atendimentos)
    if not df_atend.empty:
        st.dataframe(df_atend, use_container_width=True)
    else:
        st.info("Nenhum lançamento registrado ainda.")

# --- GESTÃO DE USUÁRIOS ---
def gerenciar_usuarios():
    st.subheader("🔐 Controle de Acessos")
    usuarios_df = pd.DataFrame(st.session_state.usuarios)
    st.dataframe(usuarios_df[['username', 'nome', 'perfil']], use_container_width=True)
    
    with st.form("form_novo_usuario"):
        st.markdown("#### ➕ Criar Novo Usuário")
        col_u1, col_u2, col_u3 = st.columns(3)
        with col_u1:
            novo_user = st.text_input("Usuário (Login)")
        with col_u2:
            novo_nome_completo = st.text_input("Nome / Função")
        with col_u3:
            nova_senha = st.text_input("Senha", type="password")
        novo_perfil = st.selectbox("Perfil", ["recepcao", "admin"])
        
        btn_criar_user = st.form_submit_button("Criar Usuário")
        if btn_criar_user:
            if novo_user and nova_senha:
                st.session_state.usuarios.append({"username": novo_user, "nome": novo_nome_completo, "senha": nova_senha, "perfil": novo_perfil, "primeiro_acesso": True})
                st.success("Usuário criado!")
                st.rerun()
            else:
                st.error("Preencha usuário e senha.")

# --- APLICATIVO PRINCIPAL ---
def app_principal():
    user = st.session_state.usuario_logado
    st.sidebar.markdown(f"**Logado:** {user['nome']}")
    st.sidebar.markdown(f"**Perfil:** {user['perfil'].upper()}")
    
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.session_state.ultima_fatura = None
        st.rerun()
        
    if user['perfil'] == 'admin':
        st.header("📊 Painel Gerencial - Instituto Ser Consciente")
        aba_geral, aba_lancamentos, aba_parceiros, aba_usuarios = st.tabs(["📈 Visão Geral", "📝 Lançamentos & Faturas", "👥 Gestão de Parceiros", "🔐 Acessos"])
        
        with aba_geral:
            df_geral = pd.DataFrame(st.session_state.atendimentos)
            if not df_geral.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Volume Total", f"R$ {df_geral['valor_total_envolvido'].sum():,.2f}")
                with col2:
                    st.metric("Receita Clínica", f"R$ {df_geral['taxa_clinica'].sum():,.2f}")
                with col3:
                    st.metric("Repasses Profissionais", f"R$ {df_geral['repasse_profissional'].sum():,.2f}")
                st.dataframe(df_geral, use_container_width=True)
            else:
                st.info("Nenhum dado registrado.")
        with aba_lancamentos:
            modulo_lancamentos()
        with aba_parceiros:
            gerenciar_parceiros()
        with aba_usuarios:
            gerenciar_usuarios()
    else:
        st.header("🗂️ Módulo de Atendimento e Recepção")
        modulo_lancamentos()

# --- CONTROLE DE FLUXO ---
if st.session_state.usuario_logado is None:
    tela_login()
else:
    app_principal()
