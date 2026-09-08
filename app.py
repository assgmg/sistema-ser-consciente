import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import qrcode
from io import BytesIO
import base64
import json
import os

# Configuração da Página
st.set_page_config(page_title="Instituto Ser Consciente - Gestão", layout="wide", page_icon="🦋")

# --- CONFIGURAÇÕES BANCÁRIAS DO INSTITUTO ---
CHAVE_PIX_INSTITUTO = "pix@institutoserconsciente.com.br"
NOME_BENEFICIARIO = "Instituto Ser Consciente Ltda"
CIDADE_BENEFICIARIO = "Contagem"

# --- ARQUIVO DE PERSISTÊNCIA HISTÓRICA (JSON) ---
ARQUIVO_DADOS = "dados_instituto.json"

def carregar_dados_persistencia():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def salvar_dados_persistencia():
    dados = {
        "usuarios": st.session_state.usuarios,
        "parceiros": st.session_state.parceiros_df.to_dict(orient="records"),
        "atendimentos": st.session_state.atendimentos
    }
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO DE ESTADO COM HISTÓRICO ACUMULATIVO ---
dados_salvos = carregar_dados_persistencia()

if 'usuarios' not in st.session_state:
    if dados_salvos and "usuarios" in dados_salvos:
        st.session_state.usuarios = dados_salvos["usuarios"]
    else:
        st.session_state.usuarios = [
            {"username": "recepcao", "nome": "Recepção Central", "senha": "Senha@123", "perfil": "recepcao", "primeiro_acesso": True},
            {"username": "admin", "nome": "Administração (Antônio / Direção)", "senha": "Admin@123", "perfil": "admin", "primeiro_acesso": False}
        ]

if 'parceiros_df' not in st.session_state:
    if dados_salvos and "parceiros" in dados_salvos:
        st.session_state.parceiros_df = pd.DataFrame(dados_salvos["parceiros"])
    else:
        st.session_state.parceiros_df = pd.DataFrame([
            {"id": 1, "nome": "Ana Carolina Ribeiro", "regra": "Percentual (70% Profissional / 30% Clínica)", "status": "Ativo"},
            {"id": 2, "nome": "Anderson Psicólogo", "regra": "Bloco de Horas (6h)", "status": "Ativo"}
        ])

if 'atendimentos' not in st.session_state:
    if dados_salvos and "atendimentos" in dados_salvos:
        st.session_state.atendimentos = dados_salvos["atendimentos"]
    else:
        st.session_state.atendimentos = []

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

# --- REGRAS OFICIAIS DO INSTITUTO ---
REGRAS_CLINICA = [
    "Percentual (70% Profissional / 30% Clínica)",
    "Percentual (80% Profissional / 20% Clínica)",
    "Bloco de Horas (6h)",
    "Locação por Hora (R$ 50,00/h)",
    "Locação por Hora (R$ 42,00/h)"
]

# --- FUNÇÃO GERADORA DE QR CODE PIX ---
def gerar_qrcode_pix(valor):
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
                    salvar_dados_persistencia()
                    st.success(f"Profissional '{novo_cad_nome}' cadastrado!")
                    st.rerun()
                else:
                    st.error("Informe o nome.")

    with col_edit:
        st.markdown("#### ⚙️ Editar / Inativar Profissional")
        if not df.empty:
            opcoes_parceiros = df['nome'].tolist()
            parceiro_selecionado = st.selectbox("Selecione:", opcoes_parceiros)
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
                    salvar_dados_persistencia()
                    st.success("Atualizado!")
                    st.rerun()
                if btn_excluir:
                    st.session_state.parceiros_df = df[df['nome'] != parceiro_selecionado].reset_index(drop=True)
                    salvar_dados_persistencia()
                    st.warning("Excluído!")
                    st.rerun()

# --- MÓDULO DE LANÇAMENTOS E HISTÓRICO COM ALTERAÇÃO DE STATUS ---
def modulo_lancamentos():
    st.subheader("📝 Lançamento de Atendimentos e Locações (Histórico Acumulado)")
    parceiros_ativos = st.session_state.parceiros_df[st.session_state.parceiros_df['status'] == 'Ativo']
    
    if parceiros_ativos.empty:
        st.warning("Não há profissionais ativos cadastrados.")
        return

    with st.form("form_novo_atendimento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            data_atendimento = st.date_input("Data", value=datetime.today())
        with col2:
            profissional_escolhido = st.selectbox("Profissional / Parceiro", parceiros_ativos['nome'].tolist())
        with col3:
            nome_paciente_cliente = st.text_input("Paciente / Cliente")
            
        regra_prof = parceiros_ativos[parceiros_ativos['nome'] == profissional_escolhido]['regra'].values[0]
        st.caption(f"📌 Regra ativa: **{regra_prof}**")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        valor_consulta, qtd_blocos = 0.0, 1
        hora_chegada, hora_devolucao = time(8, 0), time(9, 0)
        forma_pagto = "Pix"
        
        with col_p1:
            if "Percentual" in regra_prof:
                valor_consulta = st.number_input("Valor da Consulta (R$)", min_value=0.0, value=150.0, step=10.0)
            elif "Bloco de Horas" in regra_prof:
                qtd_blocos = st.number_input("Qtd Blocos (6h)", min_value=1, value=1, step=1)
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

        btn_lancar = st.form_submit_button("⚡ Salvar Lançamento no Histórico", use_container_width=True)
        
        if btn_lancar:
            if nome_paciente_cliente.strip():
                taxa_clinica, repasse_prof, detalhes_calculo = 0.0, 0.0, ""
                
                if regra_prof == "Percentual (70% Profissional / 30% Clínica)":
                    repasse_prof, taxa_clinica = valor_consulta * 0.70, valor_consulta * 0.30
                    detalhes_calculo = "70% Profissional / 30% Clínica"
                elif regra_prof == "Percentual (80% Profissional / 20% Clínica)":
                    repasse_prof, taxa_clinica = valor_consulta * 0.80, valor_consulta * 0.20
                    detalhes_calculo = "80% Profissional / 20% Clínica"
                elif "Bloco de Horas" in regra_prof:
                    taxa_clinica = (300.0 if qtd_blocos == 1 else 250.0) * qtd_blocos
                    detalhes_calculo = "1 Bloco (R$ 300)" if qtd_blocos == 1 else f"{qtd_blocos} Blocos (R$ 250/cada)"
                    repasse_prof = 0.0
                elif "Locação por Hora" in regra_prof:
                    valor_hora_base = 50.0 if "50,00" in regra_prof else 42.0
                    dt_ini = datetime.combine(datetime.today(), hora_chegada)
                    dt_fim = datetime.combine(datetime.today(), hora_devolucao)
                    if dt_fim < dt_ini: dt_fim += timedelta(days=1)
                    diff_minutos = (dt_fim - dt_ini).total_seconds() / 60.0
                    
                    horas_cobradas = 0
                    if diff_minutos > 0:
                        h_int, m_rest = int(diff_minutos // 60), diff_minutos % 60
                        horas_cobradas = (h_int + 1) if m_rest > 5 else max(1, h_int)
                    taxa_clinica = horas_cobradas * valor_hora_base
                    repasse_prof = 0.0
                    detalhes_calculo = f"{horas_cobradas}h cobradas (R$ {valor_hora_base}/h)"

                novo_id = len(st.session_state.atendimentos) + 1
                st.session_state.atendimentos.append({
                    "id": novo_id, "data": str(data_atendimento), "cliente_paciente": nome_paciente_cliente,
                    "profissional": profissional_escolhido, "regra_aplicada": regra_prof, "detalhes": detalhes_calculo,
                    "valor_total_envolvido": (taxa_clinica + repasse_prof) if "Percentual" in regra_prof else taxa_clinica,
                    "taxa_clinica": taxa_clinica, "repasse_profissional": repasse_prof, "pagamento": forma_pagto, "status": "Pendente"
                })
                salvar_dados_persistencia()
                st.success("Lançamento salvo e acumulado no histórico com sucesso!")
                st.rerun()
            else:
                st.error("Informe o nome do paciente/cliente.")

    st.markdown("---")
    st.markdown("#### 📋 Histórico Geral Acumulado (Gerenciamento de Status)")
    if st.session_state.atendimentos:
        df_atend = pd.DataFrame(st.session_state.atendimentos)
        
        for idx, row in df_atend.iterrows():
            col_t1, col_t2, col_t3, col_t4 = st.columns([2, 2, 2, 1])
            with col_t1:
                st.text(f"{row['data']} | {row['profissional']}")
            with col_t2:
                st.text(f"Cliente: {row['cliente_paciente']} ({row['detalhes']})")
            with col_t3:
                st.text(f"R$ {row['valor_total_envolvido']:,.2f} [{row['status']}]")
            with col_t4:
                novo_status_btn = "✅ Pagar" if row['status'] == "Pendente" else "🔄 Pendente"
                if st.button(novo_status_btn, key=f"btn_st_{row['id']}"):
                    st.session_state.atendimentos[idx]['status'] = "Pago" if row['status'] == "Pendente" else "Pendente"
                    salvar_dados_persistencia()
                    st.rerun()
    else:
        st.info("Nenhum lançamento registrado no histórico.")

# --- MÓDULO DE RELATÓRIOS E FATURAS CONSOLIDADAS ---
def modulo_relatorios():
    st.subheader("📊 Central de Relatórios e Extratos Históricos Acumulados")
    
    if not st.session_state.atendimentos:
        st.info("Nenhum dado disponível no histórico para relatórios.")
        return
        
    df = pd.DataFrame(st.session_state.atendimentos)
    df['data_dt'] = pd.to_datetime(df['data'])
    
    tipo_rel = st.selectbox("Selecione o Tipo de Relatório:", ["Relatório Diário", "Extrato Consolidado por Profissional", "Relatório Periódico (Mensal/Trimestral/Anual)"])
    
    if tipo_rel == "Relatório Diário":
        st.markdown("#### 📅 Fechamento de Caixa Diário")
        data_escolhida = st.date_input("Escolha a Data:", value=datetime.today())
        df_dia = df[df['data_dt'].dt.date == data_escolhida]
        
        if not df_dia.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Volume do Dia", f"R$ {df_dia['valor_total_envolvido'].sum():,.2f}")
            c2.metric("Receita Clínica", f"R$ {df_dia['taxa_clinica'].sum():,.2f}")
            c3.metric("Repasses", f"R$ {df_dia['repasse_profissional'].sum():,.2f}")
            st.dataframe(df_dia[['id', 'profissional', 'cliente_paciente', 'detalhes', 'valor_total_envolvido', 'status']], use_container_width=True)
        else:
            st.info("Nenhum atendimento registrado nesta data.")
            
    elif tipo_rel == "Extrato Consolidado por Profissional":
        st.markdown("#### 📄 Extrato Mensal Acumulado para Prestação de Contas")
        profissionais = df['profissional'].unique().tolist()
        prof_sel = st.selectbox("Selecione o Profissional:", profissionais)
        
        df_prof = df[df['profissional'] == prof_sel]
        total_envolvido = df_prof['valor_total_envolvido'].sum()
        total_clinica = df_prof['taxa_clinica'].sum()
        total_repasse = df_prof['repasse_profissional'].sum()
        
        col_e1, col_e2 = st.columns([2, 1])
        with col_e1:
            st.info(f"""
            **INSTITUTO SER CONSCIENTE LTDA**  
            CNPJ: 04.000.917/0001-47 | Contagem - MG  
            --------------------------------------------------  
            **Profissional:** {prof_sel}  
            **Total Histórico de Atendimentos:** {len(df_prof)} registros  
            **Valor Total Acumulado:** R$ {total_envolvido:,.2f}  
            **Taxa da Clínica / Locação:** R$ {total_clinica:,.2f}  
            **Repasse Devido ao Profissional:** R$ {total_repasse:,.2f}  
            --------------------------------------------------  
            """)
            st.dataframe(df_prof[['data', 'cliente_paciente', 'detalhes', 'valor_total_envolvido', 'status']], use_container_width=True)
            
        with col_e2:
            st.markdown("#### 📱 Pagamento / Pix Único")
            qr_b64 = gerar_qrcode_pix(total_envolvido)
            st.markdown(f'<img src="data:image/png;base64,{qr_b64}" width="180">', unsafe_allow_html=True)
            st.code(CHAVE_PIX_INSTITUTO, language="text")
            
    elif tipo_rel == "Relatório Periódico (Mensal/Trimestral/Anual)":
        st.markdown("#### 📈 Balanço Financeiro Histórico por Período")
        periodo = st.selectbox("Período:", ["Mensal", "Trimestral", "Semestral", "Anual"])
        ano = st.number_input("Ano de Referência:", min_value=2024, max_value=2030, value=datetime.today().year)
        
        if periodo == "Mensal":
            mes = st.selectbox("Mês:", list(range(1, 13)), format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
            df_p = df[(df['data_dt'].dt.year == ano) & (df['data_dt'].dt.month == mes)]
        elif periodo == "Trimestral":
            trimestre = st.selectbox("Trimestre:", [1, 2, 3, 4])
            meses_tri = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}[trimestre]
            df_p = df[(df['data_dt'].dt.year == ano) & (df['data_dt'].dt.month.isin(meses_tri))]
        elif periodo == "Semestral":
            semestre = st.selectbox("Semestre:", [1, 2])
            meses_sem = {1: [1,2,3,4,5,6], 2: [7,8,9,10,11,12]}[semestre]
            df_p = df[(df['data_dt'].dt.year == ano) & (df['data_dt'].dt.month.isin(meses_sem))]
        else:
            df_p = df[df['data_dt'].dt.year == ano]
            
        if not df_p.empty:
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Faturamento Acumulado", f"R$ {df_p['valor_total_envolvido'].sum():,.2f}")
            kpi2.metric("Receita da Clínica", f"R$ {df_p['taxa_clinica'].sum():,.2f}")
            kpi3.metric("Total Repasses", f"R$ {df_p['repasse_profissional'].sum():,.2f}")
            st.dataframe(df_p, use_container_width=True)
        else:
            st.info("Nenhum lançamento encontrado para o período selecionado.")

# --- GESTÃO DE USUÁRIOS ---
def gerenciar_usuarios():
    st.subheader("🔐 Controle de Acessos")
    st.dataframe(pd.DataFrame(st.session_state.usuarios)[['username', 'nome', 'perfil']], use_container_width=True)
    with st.form("form_novo_usuario"):
        st.markdown("#### ➕ Criar Novo Usuário")
        c1, c2, c3 = st.columns(3)
        with c1: novo_user = st.text_input("Usuário")
        with c2: novo_nome_completo = st.text_input("Nome / Função")
        with c3: nova_senha = st.text_input("Senha", type="password")
        novo_perfil = st.selectbox("Perfil", ["recepcao", "admin"])
        if st.form_submit_button("Criar Usuário"):
            if novo_user and nova_senha:
                st.session_state.usuarios.append({"username": novo_user, "nome": novo_nome_completo, "senha": nova_senha, "perfil": novo_perfil, "primeiro_acesso": True})
                salvar_dados_persistencia()
                st.success("Criado com sucesso!")
                st.rerun()
            else:
                st.error("Preencha todos os campos.")

# --- APLICATIVO PRINCIPAL ---
def app_principal():
    user = st.session_state.usuario_logado
    st.sidebar.markdown(f"**Logado:** {user['nome']}")
    st.sidebar.markdown(f"**Perfil:** {user['perfil'].upper()}")
    
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.rerun()
        
    if user['perfil'] == 'admin':
        st.header("📊 Painel Gerencial - Instituto Ser Consciente")
        aba_lancamentos, aba_relatorios, aba_parceiros, aba_usuarios = st.tabs(["📝 Lançamentos", "📈 Relatórios & Extratos", "👥 Parceiros", "🔐 Acessos"])
        with aba_lancamentos: modulo_lancamentos()
        with aba_relatorios: modulo_relatorios()
        with aba_parceiros: gerenciar_parceiros()
        with aba_usuarios: gerenciar_usuarios()
    else:
        st.header("🗂️ Módulo de Atendimento e Recepção")
        modulo_lancamentos()

# --- CONTROLE DE FLUXO ---
if st.session_state.usuario_logado is None:
    tela_login()
else:
    app_principal()
