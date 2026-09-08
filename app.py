import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
import re
import os

# Configuração da Página
st.set_page_config(page_title="Instituto Ser Consciente - Gestão", layout="wide", page_icon="🦋")

# --- CONFIGURAÇÕES BANCÁRIAS DO INSTITUTO ---
CHAVE_PIX_INSTITUITO = "pix@institutoserconsciente.com.br"
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
        {"id": 1, "nome": "Ana Carolina Ribeiro", "regra": "Percentual (30% Clínica / 70% Profissional)", "status": "Ativo"},
        {"id": 2, "nome": "Anderson Psicólogo", "regra": "Bloco de Horas (6h - R$ 300,00)", "status": "Ativo"}
    ])

if 'atendimentos' not in st.session_state:
    st.session_state.atendimentos = [
        {"id": 1, "data": "2026-09-08", "hora": "08:00", "paciente": "Rafael Oliveira", "id_parceiro": 2, "profissional": "Anderson Psicólogo", "valor": 250, "pagamento": "Pix", "status": "Pendente"}
    ]

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

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

# --- GESTÃO DE PARCEIROS (COM BOTÕES DE EDITAR, EXCLUIR E STATUS) ---
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
            
            regras_disponiveis = [
                "Percentual (30% Clínica / 70% Profissional)",
                "Bloco de Horas (6h - R$ 300,00)"
            ]
            regra_atual_idx = regras_disponiveis.index(dados_atuais['regra']) if dados_atuais['regra'] in regras_disponiveis else 0
            nova_regra = st.selectbox("Regra de Pagamento", regras_disponiveis, index=regra_atual_idx)
            
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
        novo_cad_regra = st.selectbox("Regra de Pagamento", [
            "Percentual (30% Clínica / 70% Profissional)",
            "Bloco de Horas (6h - R$ 300,00)"
        ], key="cad_regra")
        
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

# --- GESTÃO DE USUÁRIOS E ACESSOS ---
def gerenciar_usuarios():
    st.subheader("🔐 Controle de Acessos, Demissões e Reset de Senha")
    
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
    st.sidebar.image("logo.png", use_container_width=True)
    st.sidebar.markdown(f"**Logado:** {user['nome']}")
    st.sidebar.markdown(f"**Perfil:** {user['perfil'].upper()}")
    
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.rerun()
        
    if user['perfil'] == 'admin':
        st.header("📊 Painel Gerencial - Administração e Configurações")
        aba_geral, aba_parceiros, aba_usuarios = st.tabs(["📈 Visão Geral", "👥 Gestão de Parceiros", "🔐 Gestão de Usuários & Senhas"])
        
        with aba_geral:
            df_geral = pd.DataFrame(st.session_state.atendimentos)
            if not df_geral.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Faturamento Atendimentos", f"R$ {df_geral['valor'].sum():,.2f}")
                with col2:
                    total_recebido = df_geral[df_geral['status'] == 'Pago 💰']['valor'].sum()
                    st.metric("Recebido / Baixado", f"R$ {total_recebido:,.2f}")
                with col3:
                    total_pendente = df_geral[df_geral['status'] != 'Pago 💰']['valor'].sum()
                    st.metric("Pendente", f"R$ {total_pendente:,.2f}")
                
                st.dataframe(df_geral, use_container_width=True)
            else:
                st.info("Nenhum atendimento registrado no momento.")
                
        with aba_parceiros:
            gerenciar_parceiros()
            
        with aba_usuarios:
            gerenciar_usuarios()
            
    else:
        st.header("🗂️ Módulo de Atendimento e Recepção")
        st.info("Painel operacional da recepção pronto para novos lançamentos.")

# --- CONTROLE DE FLUXO ---
if st.session_state.usuario_logado is None:
    tela_login()
else:
    app_principal()
