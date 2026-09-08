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
CHAVE_PIX_INSTITUTO = "pix@institutoserconsciente.com.br" 
NOME_BENEFICIARIO = "Instituto Ser Consciente Ltda"
CIDADE_BENEFICIARIO = "Contagem"

# --- SIMULAÇÃO DE BANCO DE DADOS NA NUVEM ---
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = [
        {"username": "recepcao", "nome": "Recepção Central", "senha": "Senha@123", "perfil": "recepcao", "primeiro_acesso": True},
        {"username": "admin", "nome": "Administração (Antônio / Direção)", "senha": "Admin@123", "perfil": "admin", "primeiro_acesso": False},
    ]

if 'parceiros_lista' not in st.session_state:
    st.session_state.parceiros_lista = [
        {"id": 1, "nome": "Ana Carolina Ribeiro", "regra": "Percentual (30% Clínica / 70% Profissional)", "status": "Ativo"},
        {"id": 2, "nome": "Anderson Psicólogo", "regra": "Bloco de Horas (6h - R$ 250,00)", "status": "Ativo"},
    ]

if 'atendimentos' not in st.session_state:
    st.session_state.atendimentos = [
        {
            "id": 1, "data": str(datetime.today().date()), "hora": "08:00", 
            "paciente": "Rafael Oliveira", "id_parceiro": 2, "profissional": "Anderson Psicólogo", 
            "valor": 250.0, "pagamento": "Pix", "status": "Pendente"
        },
    ]

if 'contratos_fixos' not in st.session_state:
    st.session_state.contratos_fixos = [
        {"id": 1, "mes": "Março/2026", "profissional": "Dr. Matheus (Sala Fixa)", "valor": 2500.0, "status": "Pendente"}
    ]

# Função para validar força da senha
def validar_forca_senha(senha):
    tamanho = len(senha) >= 8
    tem_maiuscula = bool(re.search(r'[A-Z]', senha))
    tem_minuscula = bool(re.search(r'[a-z]', senha))
    tem_numero = bool(re.search(r'[0-9]', senha))
    tem_especial = bool(re.search(r'[@$!%*?&._-]', senha))
    return tamanho, tem_maiuscula, tem_minuscula, tem_numero, tem_especial

# Função para gerar QR Code Pix
def gerar_qrcode_pix(chave, nome, cidade, valor):
    def campo(id_campo, valor_campo):
        tamanho = f"{len(valor_campo):02d}"
        return f"{id_campo}{tamanho}{valor_campo}"

    gui = campo("00", "br.gov.bcb.pix")
    chave_pix_campo = campo("01", chave)
    merchant_account_info = campo("26", gui + chave_pix_campo)
    
    merchant_category_code = campo("52", "0000")
    transaction_currency = campo("53", "986") 
    valor_str = f"{valor:.2f}"
    transaction_amount = campo("54", valor_str)
    country_code = campo("58", "BR")
    merchant_name = campo("59", nome[:25])
    merchant_city = campo("60", cidade[:15])
    additional_data = campo("62", campo("05", "***"))
    
    payload_sem_crc = (
        campo("00", "01") + merchant_account_info + merchant_category_code +
        transaction_currency + transaction_amount + country_code +
        merchant_name + merchant_city + additional_data + "6304"
    )
    
    def calcula_crc16(payload):
        crc = 0xFFFF
        for char in payload:
            crc = crc ^ (ord(char) << 8)
            for _ in range(8):
                if (crc & 0x8000):
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = ((crc << 1) & 0xFFFF)
        return f"{crc:04X}"

    payload_pix = payload_sem_crc + calcula_crc16(payload_sem_crc)

    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(payload_pix)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# --- CONTROLE DE AUTENTICAÇÃO ---
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

def tela_login():
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=220)
        st.title("Instituto Ser Consciente")
        st.markdown("### 🏥 Sistema de Gestão e Faturamento")
        st.markdown("---")
        
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar no Sistema", type="primary", use_container_width=True):
            usuario_encontrado = next((u for u in st.session_state.usuarios if u["username"] == username and u["senha"] == senha), None)
            if usuario_encontrado:
                st.session_state.usuario_logado = usuario_encontrado
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

def tela_primeiro_acesso():
    user = st.session_state.usuario_logado
    st.title("🔒 Segurança Obrigatória - Primeiro Acesso")
    st.info(f"Olá, **{user['nome']}**. Por segurança da clínica, cadastre uma nova senha forte.")
    
    with st.form("form_nova_senha"):
        nova_senha = st.text_input("Nova Senha", type="password")
        confirma_senha = st.text_input("Confirme a Nova Senha", type="password")
        
        if nova_senha:
            t, mai, min_l, num, esp = validar_forca_senha(nova_senha)
            st.markdown("**Requisitos de Segurança:**")
            st.markdown(f"{'✅' if t else '❌'} Mínimo de 8 caracteres")
            st.markdown(f"{'✅' if mai else '❌'} Letra maiúscula")
            st.markdown(f"{'✅' if min_l else '❌'} Letra minúscula")
            st.markdown(f"{'✅' if num else '❌'} Número")
            st.markdown(f"{'✅' if esp else '❌'} Caractere especial (@, #, $, !)")
        
        if st.form_submit_button("Atualizar Senha e Entrar", type="primary"):
            t, mai, min_l, num, esp = validar_forca_senha(nova_senha)
            if not (t and mai and min_l and num and esp):
                st.error("A senha não atende aos requisitos mínimos exigidos.")
            elif nova_senha != confirma_senha:
                st.error("As senhas não coincidem.")
            else:
                for u in st.session_state.usuarios:
                    if u["username"] == user["username"]:
                        u["senha"] = nova_senha
                        u["primeiro_acesso"] = False
                st.session_state.usuario_logado = user
                st.success("Senha atualizada com sucesso!")
                st.rerun()

def app_principal():
    user = st.session_state.usuario_logado
    
    # Exibir logomarca na barra lateral
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_column_width=True)
    
    st.sidebar.title(f"Logado: {user['nome']}")
    st.sidebar.markdown(f"**Perfil:** `{user['perfil'].upper()}`")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.rerun()
        
    st.sidebar.markdown("---")

    if user['perfil'] == 'recepcao':
        st.header("📝 Recepção - Atendimentos e Fechamento de Caixa")
        aba_lancar, aba_fechar = st.tabs(["➕ Lançar Atendimento", "🧾 Fechamento, Fatura e Baixa de Pagamento"])
        profissionais_ativos = [p for p in st.session_state.parceiros_lista if p['status'] == 'Ativo']
        
        with aba_lancar:
            with st.form("form_lancamento", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data = st.date_input("Data do Atendimento", value=datetime.today())
                    hora = st.time_input("Hora")
                    paciente = st.text_input("Nome do Paciente")
                with col2:
                    profissional_escolhido = st.selectbox("Profissional / Parceiro Ativo", options=profissionais_ativos, format_func=lambda x: f"{x['nome']} ({x['regra']})")
                    valor = st.number_input("Valor da Consulta/Sessão (R$)", min_value=0.0, format="%.2f")
                    pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Convênio"])
                    
                if st.form_submit_button("Salvar Lançamento", type="primary"):
                    if paciente.strip() == "":
                        st.error("Preencha o nome do paciente.")
                    else:
                        st.session_state.atendimentos.append({
                            "id": len(st.session_state.atendimentos) + 1, "data": str(data), "hora": str(hora)[:5],
                            "paciente": paciente, "id_parceiro": profissional_escolhido['id'],
                            "profissional": profissional_escolhido['nome'], "valor": valor, 
                            "pagamento": pagamento, "status": "Pendente"
                        })
                        st.success(f"Atendimento de {paciente} lançado com sucesso!")

        with aba_fechar:
            st.subheader("Fechamento Diário e Emissão de Fatura")
            if profissionais_ativos:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    prof_filtro = st.selectbox("Selecione o Profissional", options=profissionais_ativos, format_func=lambda x: x['nome'], key="filtro_prof")
                with col_f2:
                    data_filtro = st.date_input("Selecione a Data", value=datetime.today(), key="filtro_data")
                    
                dados_filtrados = [
                    a for a in st.session_state.atendimentos 
                    if a['id_parceiro'] == prof_filtro['id'] and a['data'] == str(data_filtro)
                ]
                
                if dados_filtrados:
                    df_fechamento = pd.DataFrame(dados_filtrados)[['id', 'hora', 'paciente', 'valor', 'pagamento', 'status']]
                    st.dataframe(df_fechamento, use_container_width=True)
                    total_dia = sum(item['valor'] for item in dados_filtrados)
                    st.metric(label=f"Total Produzido por {prof_filtro['nome']}", value=f"R$ {total_dia:,.2f}")
                    
                    st.markdown("---")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("🧾 Gerar Fatura Oficial com Logo, QR Code e Chave", type="primary"):
                            st.success("Fatura gerada com sucesso!")
                            st.markdown("---")
                            
                            # LOGOMARCA NA FATURA
                            if os.path.exists("logo.png"):
                                col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
                                with col_logo2:
                                    st.image("logo.png", width=140)
                            
                            st.markdown("<h2 style='text-align: center;'>INSTITUTO SER CONSCIENTE LTDA</h2>", unsafe_allow_html=True)
                            st.markdown("<p style='text-align: center; color: gray;'>Em busca da saúde integral</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align: center;'><b>Fatura de Repasse — Regra: {prof_filtro['regra']}</b></p>", unsafe_allow_html=True)
                            st.markdown("---")
                            
                            st.markdown(f"**Data de Referência:** {data_filtro.strftime('%d/%m/%Y')} | **Profissional:** {prof_filtro['nome']}")
                            st.markdown("#### Detalhamento dos Atendimentos:")
                            for item in dados_filtrados:
                                st.text(f"• Às {item['hora']} | Paciente: {item['paciente']} | Valor: R$ {item['valor']:,.2f} ({item['pagamento']})")
                            
                            st.markdown("---")
                            col_q1, col_q2 = st.columns([2, 1])
                            with col_q1:
                                st.markdown(f"### **TOTAL A PAGAR:** R$ {total_dia:,.2f}")
                                st.markdown("#### 💳 Dados para Pagamento via Pix:")
                                st.markdown(f"• **Chave Pix (E-mail):** `{CHAVE_PIX_INSTITUTO}`")
                                st.markdown(f"• **Favorecido:** {NOME_BENEFICIARIO}")
                                st.markdown("*(Caso não consiga escanear o QR Code, copie e cole a chave acima no aplicativo do seu banco)*")
                            with col_q2:
                                st.markdown("**Escaneie o QR Code:**")
                                qr_bytes = gerar_qrcode_pix(CHAVE_PIX_INSTITUTO, NOME_BENEFICIARIO, CIDADE_BENEFICIARIO, total_dia)
                                st.image(qr_bytes, width=150)
                            st.markdown("---")

                    with col_b2:
                        st.markdown("### 📥 Baixa de Pagamento")
                        id_para_baixar = st.selectbox("Selecione o ID do atendimento para dar baixa", options=[item['id'] for item in dados_filtrados])
                        if st.button("Confirmar Recebimento (Baixar)"):
                            for item in st.session_state.atendimentos:
                                if item['id'] == id_para_baixar:
                                    item['status'] = 'Pago ✅'
                            st.success(f"Atendimento ID {id_para_baixar} marcado como PAGO!")
                            st.rerun()
                else:
                    st.info("Nenhum atendimento registrado para este profissional nesta data.")

    elif user['perfil'] == 'admin':
        st.header("📊 Painel Gerencial - Administração e Configurações")
        aba_geral, aba_parceiros, aba_usuarios, aba_fixos = st.tabs(["📈 Visão Geral", "👥 Gestão de Parceiros", "🔐 Gestão de Usuários & Senhas", "🏢 Contratos Fixos"])
        
        with aba_geral:
            df_geral = pd.DataFrame(st.session_state.atendimentos)
            if not df_geral.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Faturamento Atendimentos", f"R$ {df_geral['valor'].sum():,.2f}")
                with col2:
                    total_recebido = df_geral[df_geral['status'] == 'Pago ✅']['valor'].sum()
                    st.metric("Recebido / Baixado", f"R$ {total_recebido:,.2f}")
                with col3:
                    total_pendente = df_geral[df_gl['status'] != 'Pago ✅']['valor'].sum() if 'df_gl' in locals() else df_geral[df_geral['status'] != 'Pago ✅']['valor'].sum()
                    st.metric("Pendente", f"R$ {total_pendente:,.2f}")
                st.markdown("---")
                st.dataframe(df_geral, use_container_width=True)
            else:
                st.info("Nenhum atendimento registrado.")

        with aba_parceiros:
            st.subheader("Cadastro, Regras e Controle de Ativos/Inativos")
            st.dataframe(pd.DataFrame(st.session_state.parceiros_lista), use_container_width=True)
            with st.form("novo_parceiro_form", clear_on_submit=True):
                nome_novo = st.text_input("Nome do Profissional / Especialidade")
                regra_nova = st.selectbox("Regra de Pagamento", ["Percentual (30% Clínica / 70% Profissional)", "Bloco de Horas (6h - R$ 250,00)", "Por Hora (R$ 50,00/h)"])
                if st.form_submit_button("Cadastrar Profissional"):
                    if nome_novo.strip():
                        st.session_state.parceiros_lista.append({"id": len(st.session_state.parceiros_lista) + 1, "nome": nome_novo, "regra": regra_nova, "status": "Ativo"})
                        st.success(f"Profissional {nome_novo} cadastrado!")
                        st.rerun()

        with aba_usuarios:
            st.subheader("🔐 Controle de Acessos, Demissões e Reset de Senha")
            st.dataframe(pd.DataFrame(st.session_state.usuarios)[['username', 'nome', 'perfil', 'primeiro_acesso']], use_container_width=True)
            
            st.markdown("---")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                user_alvo = st.selectbox("Selecione o Usuário", options=[u['username'] for u in st.session_state.usuarios])
                if st.button("🔑 Resetar Senha para Padrão (Mudar@123)"):
                    for u in st.session_state.usuarios:
                        if u['username'] == user_alvo:
                            u['senha'] = "Mudar@123"
                            u['primeiro_acesso'] = True
                    st.success(f"Senha do usuário '{user_alvo}' resetada para 'Mudar@123'.")
                    st.rerun()
            with col_u2:
                if st.button("🚫 Remover / Inativar Usuário"):
                    st.session_state.usuarios = [u for u in st.session_state.usuarios if u['username'] != user_alvo or u['username'] == 'admin']
                    st.success(f"Usuário '{user_alvo}' removido com sucesso.")
                    st.rerun()

        with aba_fixos:
            st.subheader("🏢 Gestão de Contratos Fixos Mensais")
            st.dataframe(pd.DataFrame(st.session_state.contratos_fixos), use_container_width=True)
            with st.form("form_contrato_fixo", clear_on_submit=True):
                c_mes = st.text_input("Mês de Referência (Ex: Abril/2026)")
                c_prof = st.text_input("Profissional / Sala")
                c_valor = st.number_input("Valor Mensal (R$)", min_value=0.0, format="%.2f")
                if st.form_submit_button("Adicionar Contrato Fixo"):
                    st.session_state.contratos_fixos.append({"id": len(st.session_state.contratos_fixos) + 1, "mes": c_mes, "profissional": c_prof, "valor": c_valor, "status": "Pendente"})
                    st.success("Contrato fixo adicionado!")
                    st.rerun()

# --- CONTROLE DE FLUXO DA TELA ---
if st.session_state.usuario_logado is None:
    tela_login()
elif st.session_state.usuario_logado.get("primeiro_acesso", False):
    tela_primeiro_acesso()
else:
    app_principal()
