import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import qrcode
from io import BytesIO
import re
import os

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

# --- REGRAS OFICIAIS DO INSTITUTO ---
REGRAS_CLINICA = [
    "Percentual (70% Profissional / 30% Clínica)",
    "Percentual (80% Profissional / 20% Clínica)",
    "Bloco de Horas (6h)",
    "Locação por Hora (R$ 50,00/h)",
    "Locação por Hora (R$ 42,00/h)"
]

# --- FUNÇÃO DE LOGIN ---
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
    st.markdown("### Cadastro, Regras e Controle de Ativos/Inativos")
    
    df = st.session_state.parceiros_df
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### ⚙️ Gerenciar / Editar Profissional Selecionado")
    
    if not df.empty:
        opcoes_parceiros = df['nome'].tolist()
        parceiro_selecionado = st.selectbox("Selecione o profissional para gerenciar:", opcoes_parceiros)
        
        dados_atuais = df[df['nome'] == parceiro_selecionado].iloc[0]
        
        with st.form(key="form_edicao_parceiro"):
            novo_nome = st.text_input("Nome do Profissional / Especialidade", value=dados_atuais['nome'])
            
            regra_atual_idx = REGRAS_CLINICA.index(dados_atuais['regra']) if dados_atuais['regra'] in REGRAS_CLINICA else 0
            nova_regra = st.selectbox("Regra de Pagamento / Parceria", REGRAS_CLINICA, index=regra_atual_idx)
            
            status_disponiveis = ["Ativo", "Inativo"]
            status_atual_idx = status_disponiveis.index(dados_atuais['status']) if dados_atuais['status'] in status_disponiveis else 0
            novo_status = st.selectbox("Status", status_disponiveis, index=status_atual_idx)
            
            col_b1, col_b2 = st.columns(2)
            btn_salvar = col_b1.form_submit_button("💾 Salvar Alterações")
            btn_excluir = col_b2.form_submit_button("🗑️ Excluir Profissional")
            
            if btn_salvar:
                df.loc[df['nome'] == parceiro_selecionado, 'nome'] = novo_nome
                df.loc[df['nome'] == novo_nome, 'regra'] = nova_regra
                df.loc[df['nome'] == novo_nome, 'status'] = novo_status
                st.session_state.parceiros_df = df
                st.success(f"Profissional '{novo_nome}' atualizado com sucesso!")
                st.rerun()
                
            if btn_excluir:
                st.session_state.parceiros_df = df[df['nome'] != parceiro_selecionado].reset_index(drop=True)
                st.warning(f"Profissional '{parceiro_selecionado}' excluído com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum profissional cadastrado no momento.")

    st.markdown("---")
    st.markdown("#### ➕ Cadastrar Novo Profissional")
    with st.form(key="form_novo_parceiro"):
        novo_cad_nome = st.text_input("Nome do Profissional / Especialidade", key="cad_nome")
        novo_cad_regra = st.selectbox("Regra de Pagamento / Parceria", REGRAS_CLINICA, key="cad_regra")
        
        btn_cadastrar = st.form_submit_button("Cadastrar Profissional")
        
        if btn_cadastrar:
            if novo_cad_nome.strip():
                novo_id = int(df['id'].max() + 1) if not df.empty else 1
                novo_registro = pd.DataFrame([{"id": novo_id, "nome": novo_cad_nome, "regra": novo_cad_regra, "status": "Ativo"}])
                st.session_state.parceiros_df = pd.concat([df, novo_registro], ignore_index=True)
                st.success(f"Profissional '{novo_cad_nome}' cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, informe o nome do profissional.")

# --- MÓDULO DE LANÇAMENTO E CÁLCULO DE REPASSE ---
def modulo_lancamentos():
    st.subheader("📝 Lançamento de Atendimentos, Locações e Cálculo de Repasse")
    
    parceiros_ativos = st.session_state.parceiros_df[st.session_state.parceiros_df['status'] == 'Ativo']
    
    if parceiros_ativos.empty:
        st.warning("Não há profissionais ativos cadastrados. Cadastre um parceiro na aba de gestão primeiro.")
        return

    with st.form("form_novo_atendimento"):
        col1, col2 = st.columns(2)
        with col1:
            data_atendimento = st.date_input("Data da Ocorrência", value=datetime.today())
        with col2:
            nome_paciente_cliente = st.text_input("Nome do Paciente ou Cliente da Locação")
            
        profissional_escolhido = st.selectbox("Profissional / Parceiro Responsável", parceiros_ativos['nome'].tolist())
        
        regra_prof = parceiros_ativos[parceiros_ativos['nome'] == profissional_escolhido]['regra'].values[0]
        st.info(f"Regra vigente cadastrada para este profissional: **{regra_prof}**")
        
        # Parâmetros Dinâmicos conforme a Regra
        valor_consulta = 0.0
        qtd_blocos = 1
        hora_chegada = time(8, 0)
        hora_devolucao = time(9, 0)
        forma_pagto = "Pix"
        
        if "Percentual" in regra_prof:
            col3, col4 = st.columns(2)
            with col3:
                valor_consulta = st.number_input("Valor Cobrado do Paciente (R$)", min_value=0.0, value=150.0, step=10.0)
            with col4:
                forma_pagto = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Dinheiro", "Transferência"])
                
        elif "Bloco de Horas" in regra_prof:
            qtd_blocos = st.number_input("Quantidade de Blocos de 6h contratados no mês", min_value=1, value=1, step=1)
            forma_pagto = st.selectbox("Forma de Pagamento", ["Pix", "Boleto", "Transferência", "Dinheiro"])
            
        elif "Locação por Hora" in regra_prof:
            st.markdown("##### ⏱️ Controle de Chave e Permanência (Tolerância de 5 min)")
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                hora_chegada = st.time_input("Horário de Chegada (Retirada da Chave)", value=time(8, 0))
            with col_h2:
                hora_devolucao = st.time_input("Horário de Devolução da Chave", value=time(9, 0))
            forma_pagto = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Transferência"])

        btn_lancar = st.form_submit_button("💾 Salvar e Calcular Valores")
        
        if btn_lancar:
            if nome_paciente_cliente.strip():
                taxa_clinica = 0.0
                repasse_prof = 0.0
                detalhes_calculo = ""
                
                # 1. Regra Percentual 70/30
                if regra_prof == "Percentual (70% Profissional / 30% Clínica)":
                    repasse_prof = valor_consulta * 0.70
                    taxa_clinica = valor_consulta * 0.30
                    detalhes_calculo = "70% Profissional / 30% Clínica"
                
                # 2. Regra Percentual 80/20
                elif regra_prof == "Percentual (80% Profissional / 20% Clínica)":
                    repasse_prof = valor_consulta * 0.80
                    taxa_clinica = valor_consulta * 0.20
                    detalhes_calculo = "80% Profissional / 20% Clínica"
                
                # 3. Regra Bloco de 6 horas (R$300 un / R$250 se 2 ou mais)
                elif "Bloco de Horas" in regra_prof:
                    if qtd_blocos == 1:
                        taxa_clinica = 300.0 * qtd_blocos
                        detalhes_calculo = f"1 Bloco único (R$ 300,00)"
                    else:
                        taxa_clinica = 250.0 * qtd_blocos
                        detalhes_calculo = f"{qtd_blocos} Blocos (R$ 250,00 cada)"
                    repasse_prof = 0.0
                
                # 4. Regra Locação por Hora (Com tolerância de 5 minutos)
                elif "Locação por Hora" in regra_prof:
                    # Definir valor da hora com base na regra do profissional
                    valor_hora_base = 50.0 if "50,00" in regra_prof else 42.0
                    
                    # Converter horários para datetime dummy para calcular diferença exata
                    dt_ini = datetime.combine(datetime.today(), hora_chegada)
                    dt_fim = datetime.combine(datetime.today(), hora_devolucao)
                    
                    if dt_fim < dt_ini:
                        dt_fim += timedelta(days=1) # Caso passe da meia-noite
                        
                    diff_minutos = (dt_fim - dt_ini).total_seconds() / 60.0
                    
                    # Aplicar regra de tolerância de 5 minutos para cobrar hora adicional
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
                    detalhes_calculo = f"Total: {horas_cobradas}h cobradas (R$ {valor_hora_base}/h) | Período: {hora_chegada.strftime('%H:%M')} às {hora_devolucao.strftime('%H:%M')}"

                novo_id = len(st.session_state.atendimentos) + 1
                novo_atend = {
                    "id": novo_id,
                    "data": str(data_atendimento),
                    "cliente_paciente": nome_paciente_cliente,
                    "profissional": profissional_escolhido,
                    "regra_aplicada": regra_prof,
                    "detalhes": detalhes_calculo,
                    "valor_total_envolvido": taxa_clinica + repasse_prof if "Percentual" in regra_prof else taxa_clinica,
                    "taxa_clinica": taxa_clinica,
                    "repasse_profissional": repasse_prof,
                    "pagamento": forma_pagto,
                    "status": "Pendente"
                }
                st.session_state.atendimentos.append(novo_atend)
                st.success(f"Lançamento efetuado com sucesso! Receita da Clínica: R$ {taxa_clinica:,.2f}")
                st.rerun()
            else:
                st.error("Informe o nome do paciente ou cliente.")

    st.markdown("---")
    st.markdown("#### 📋 Registros e Lançamentos Realizados")
    df_atend = pd.DataFrame(st.session_state.atendimentos)
    if not df_atend.empty:
        st.dataframe(df_atend, use_container_width=True)
    else:
        st.info("Nenhum lançamento registrado ainda.")

# --- GESTÃO DE USUÁRIOS E ACESSOS ---
def gerenciar_usuarios():
    st.subheader("🔐 Controle de Acessos e Senhas")
    
    usuarios_df = pd.DataFrame(st.session_state.usuarios)
    st.dataframe(usuarios_df[['username', 'nome', 'perfil']], use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### ➕ Criar Novo Usuário de Acesso")
    with st.form("form_novo_usuario"):
        novo_user = st.text_input("Nome de Usuário (Login)")
        novo_nome_completo = st.text_input("Nome Completo / Função")
        nova_senha = st.text_input("Senha Inicial", type="password")
        novo_perfil = st.selectbox("Perfil de Acesso", ["recepcao", "admin"])
        
        btn_criar_user = st.form_submit_button("Criar Usuário")
        if btn_criar_user:
            if novo_user and nova_senha:
                st.session_state.usuarios.append({
                    "username": novo_user,
                    "nome": novo_nome_completo,
                    "senha": nova_senha,
                    "perfil": novo_perfil,
                    "primeiro_acesso": True
                })
                st.success(f"Usuário '{novo_user}' criado com sucesso!")
                st.rerun()
            else:
                st.error("Preencha usuário e senha.")

# --- APLICATIVO PRINCIPAL ---
def app_principal():
    user = st.session_state.usuario_logado
    
    # Menu Lateral
    st.sidebar.markdown(f"**Logado:** {user['nome']}")
    st.sidebar.markdown(f"**Perfil:** {user['perfil'].upper()}")
    
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.rerun()
        
    if user['perfil'] == 'admin':
        st.header("📊 Painel Gerencial - Administração e Configurações")
        aba_geral, aba_lancamentos, aba_parceiros, aba_usuarios = st.tabs(["📈 Visão Geral", "📝 Lançamentos & Repasses", "👥 Gestão de Parceiros", "🔐 Gestão de Usuários"])
        
        with aba_geral:
            df_geral = pd.DataFrame(st.session_state.atendimentos)
            if not df_geral.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Volume Financeiro Total", f"R$ {df_geral['valor_total_envolvido'].sum():,.2f}")
                with col2:
                    total_taxas = df_geral['taxa_clinica'].sum()
                    st.metric("Receita Clínica", f"R$ {total_taxas:,.2f}")
                with col3:
                    total_repasse = df_geral['repasse_profissional'].sum()
                    st.metric("Repasses aos Profissionais", f"R$ {total_repasse:,.2f}")
                
                st.dataframe(df_geral, use_container_width=True)
            else:
                st.info("Nenhum lançamento registrado no momento.")
                
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
