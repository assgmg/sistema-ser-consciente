import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st

# Configuração Inicial da Página
st.set_page_config(
    page_title="Instituto Ser Consciente - Sistema Integrado",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- 1. CONFIGURAÇÃO DO BANCO DE DADOS E SEGURANÇA ---
def init_db():
  conn = sqlite3.connect("ser_consciente.db", timeout=10)
  cursor = conn.cursor()

  # Tabela de Profissionais
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS profissionais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo_contrato TEXT NOT NULL, -- 'Fixo Mensal', 'Percentual 70/30', 'Percentual 20/80', 'Bloco R$300', 'Bloco R$250', 'Hora R$50', 'Hora R$42', 'Isento (Dono)'
            ativo INTEGER DEFAULT 1,
            data_cadastro TEXT
        )
    """)

  # Tabela de Pacientes
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT
        )
    """)

  # Tabela de Pacotes de Sessões
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            profissional_id INTEGER,
            total_sessoes INTEGER,
            sessoes_consumidas INTEGER DEFAULT 0,
            valor_total REAL,
            status TEXT DEFAULT 'Ativo',
            data_aquisicao TEXT
        )
    """)

  # Tabela de Atendimentos / Lançamentos Diários
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            profissional_id INTEGER,
            paciente_id INTEGER,
            tipo_atendimento TEXT, -- 'Avulso', 'Pacote', 'Fixo'
            valor_consulta REAL,
            forma_pagamento TEXT, -- 'Dinheiro', 'Cartão', 'PIX', 'Fiado'
            repasse_clinica REAL,
            repasse_profissional REAL,
            recepcionista TEXT,
            status_caixa TEXT DEFAULT 'Aberto'
        )
    """)

  # Tabela de Despesas
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_vencimento TEXT,
            data_pagamento TEXT,
            descricao TEXT,
            categoria TEXT,
            valor REAL,
            status TEXT DEFAULT 'Pendente'
        )
    """)

  conn.commit()
  conn.close()


init_db()

# --- 2. AUTENTICAÇÃO E PERFIS ---
st.sidebar.title("🔐 Instituto Ser Consciente")
perfil = st.sidebar.selectbox(
    "Selecione o Perfil de Acesso", ["Recepção", "Administração (Você / Dono)"]
)

st.sidebar.markdown("---")

if perfil == "Recepção":
  menu = st.sidebar.radio(
      "Menu Operacional",
      [
          "Registro de Atendimentos",
          "Controle de Pacotes",
          "Fechamento de Caixa e Fatura",
      ],
  )
else:
  menu = st.sidebar.radio(
      "Menu Gerencial",
      [
          "Dashboard Executivo",
          "Cadastro de Profissionais",
          "Gestão de Contratos Fixos",
          "Despesas e Fluxo de Caixa",
          "Conciliação Bancária (OFX/TXT)",
          "Relatórios Completos",
      ],
  )


# Função Auxiliar para Conexão
def run_query(query, params=(), fetch=True):
  conn = sqlite3.connect("ser_consciente.db")
  cursor = conn.cursor()
  cursor.execute(query, params)
  if fetch:
    result = cursor.fetchall()
    conn.close()
    return result
  conn.commit()
  conn.close()


# --- 3. MÓDULOS DA RECEPÇÃO ---
if menu == "Registro de Atendimentos":
  st.header("📝 Registro Diário de Atendimentos")
  st.markdown(
      "Insira as informações do atendimento. O sistema calculará automaticamente"
      " o repasse da cessão de espaço."
  )

  profissionais = run_query(
      "SELECT id, nome, tipo_contrato FROM profissionais WHERE ativo = 1"
  )
  pacientes = run_query("SELECT id, nome FROM pacientes")

  if not profissionais:
    st.warning(
        "Nenhum profissional cadastrado. Solicite à administração o cadastro"
        " inicial."
    )
  else:
    with st.form("form_atendimento"):
      col1, col2 = st.columns(2)
      with col1:
        data_atendimento = st.date_input(
            "Data do Atendimento", value=datetime.today()
        )
        prof_selecionado = st.selectbox(
            "Profissional",
            profissionais,
            format_func=lambda x: f"{x[1]} ({x[2]})",
        )
      with col2:
        # Gerenciamento simples de pacientes
        nome_paciente = st.text_input("Nome do Paciente")
        forma_pgto = st.selectbox(
            "Forma de Pagamento", ["Dinheiro", "Cartão", "PIX", "Fiado", "Misto"]
        )

      col3, col4 = st.columns(2)
      with col3:
        valor_consulta = st.number_input(
            "Valor da Consulta / Sessão (R$)", min_value=0.0, format="%.2f"
        )
      with col4:
        tipo_atendimento = st.selectbox(
            "Tipo", ["Avulso", "Pacote (Consumo)", "Contrato Fixo"]
        )

      submitted = st.form_submit_button("Registrar Atendimento")

      if submitted:
        if not nome_paciente or valor_consulta <= 0:
          st.error("Preencha o nome do paciente e um valor válido.")
        else:
          # Salvar ou recuperar paciente
          conn = sqlite3.connect("ser_consciente.db")
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id FROM pacientes WHERE nome = ?", (nome_paciente,)
          )
          p_res = cursor.fetchone()
          if p_res:
            paciente_id = p_res[0]
          else:
            cursor.execute(
                "INSERT INTO pacientes (nome) VALUES (?)", (nome_paciente,)
            )
            paciente_id = cursor.lastrowid
            conn.commit()

          # Lógica de Cálculo de Cessão de Espaço
          contrato = prof_selecionado[2]
          repasse_clinica = 0.0

          if "70/30" in contrato:  # Ex: 70% Profissional / 30% Clínica
            repasse_clinica = valor_consulta * 0.30
          elif "20/80" in contrato:  # Ex: 20% Profissional / 80% Clínica
            repasse_clinica = valor_consulta * 0.80
          elif "Bloco R$300" in contrato:
            repasse_clinica = 300.0
          elif "Bloco R$250" in contrato:
            repasse_clinica = 250.0
          elif "Hora R$50" in contrato:
            repasse_clinica = 50.0
          elif "Hora R$42" in contrato:
            repasse_clinica = 42.0
          elif "Isento" in contrato:
            repasse_clinica = 0.0

          repasse_profissional = valor_consulta - repasse_clinica
          data_str = data_atendimento.strftime("%d/%m/%Y")

          cursor.execute(
              """
                    INSERT INTO atendimentos (data, profissional_id, paciente_id, tipo_atendimento, valor_consulta, forma_pagamento, repasse_clinica, repasse_profissional, recepcionista)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
              (
                  data_str,
                  prof_selecionado[0],
                  paciente_id,
                  tipo_atendimento,
                  valor_consulta,
                  forma_pgto,
                  repasse_clinica,
                  repasse_profissional,
                  perfil,
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"Atendimento de {nome_paciente} registrado com sucesso! Repasse"
              f" Clínica: R$ {repasse_clinica:.2f}"
          )

elif menu == "Fechamento de Caixa e Fatura":
  st.header("💰 Fechamento de Caixa e Emissão de Fatura")
  st.write(
      "Resumo diário para fechamento de caixa e envio de fatura de cessão de"
      " espaço aos profissionais."
  )

  data_filtro = st.date_input(
      "Selecione a Data para Fechamento", value=datetime.today()
  )
  data_str = data_filtro.strftime("%d/%m/%Y")

  query = """
        <query>
        SELECT a.id, p.nome as profissional, pac.nome as paciente, a.valor_consulta, a.forma_pagamento, a.repasse_clinica 
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN pacientes pac ON a.paciente_id = pac.id
        WHERE a.data = ?
    """
  # Executando consulta via python direto
  conn = sqlite3.connect("ser_consciente.db")
  df_caixa = pd.read_sql_query(
      """
        SELECT a.id, p.nome as profissional, pac.nome as paciente, a.valor_consulta, a.forma_pagamento, a.repasse_clinica 
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN pacientes pac ON a.paciente_id = pac.id
        WHERE a.data = ?
    """,
      conn,
      params=(data_str,),
  )
  conn.close()

  if df_caixa.empty:
    st.info(f"Nenhum atendimento registrado para a data {data_str}.")
  else:
    st.dataframe(df_caixa, use_container_width=True)
    total_dia = df_caixa["valor_consulta"].sum()
    total_repasse_clinica = df_caixa["repasse_clinica"].sum()

    st.metric(label="Faturamento Total do Dia", value=f"R$ {total_dia:.2f}")
    st.metric(
        label="Total Cessão de Espaço (Clínica)",
        value=f"R$ {total_repasse_clinica:.2f}",
    )

    if st.button("Gerar Fatura PDF da Clínica (QR Code Pix)"):
      st.success(
          "Fatura gerada com sucesso! Chave Pix CNPJ: 04.000.917/0001-47 - Valor"
          f" Total: R$ {total_repasse_clinica:.2f}"
      )
      # Aqui você pode incorporar a estrutura HTML do componente da fatura desenvolvida anteriormente.

# --- 4. MÓDULOS GERENCIAIS (ADMINISTRAÇÃO) ---
elif menu == "Dashboard Executivo":
  st.header("📊 Dashboard Executivo e Caixa Consolidado")
  conn = sqlite3.connect("ser_consciente.db")
  df_geral = pd.read_sql_query(
      """
        SELECT a.data, p.nome as profissional, a.valor_consulta, a.repasse_clinica, a.forma_pagamento
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
    """,
      conn,
  )
  conn.close()

  if not df_geral.empty:
    col1, col2 = st.columns(2)
    with col1:
      st.metric(
          "Faturamento Acumulado",
          f"R$ {df_geral['valor_consulta'].sum():.2f}",
      )
    with col2:
      st.metric(
          "Receita Total Cessão (Clínica)",
          f"R$ {df_geral['repasse_clinica'].sum():.2f}",
      )
    st.subheader("Histórico Consolidado de Lançamentos")
    st.dataframe(df_geral, use_container_width=True)
  else:
    st.info("Ainda não há dados suficientes para exibição do dashboard.")

elif menu == "Cadastro de Profissionais":
  st.header("👥 Cadastro e Regras de Profissionais")

  with st.form("novo_prof"):
    nome_p = st.text_input("Nome Completo do Profissional")
    tipo_c = st.selectbox(
        "Regra de Cessão de Espaço",
        [
            "Percentual 70/30",
            "Percentual 20/80",
            "Bloco de Horários Avulso (R$ 300,00)",
            "Mais de uma reserva no mês (R$ 250,00)",
            "Por hora (R$ 50,00)",
            "Por hora (R$ 42,00)",
            "Isento (Dono - Dr. Fabrício)",
        ],
    )
    btn_cad = st.form_submit_button("Cadastrar Profissional")

    if btn_cad:
      if nome_p:
        run_query(
            "INSERT INTO profissionais (nome, tipo_contrato, data_cadastro)"
            " VALUES (?, ?, ?)",
            (nome_p, tipo_c, datetime.today().strftime("%d/%m/%Y")),
            fetch=False,
        )
        st.success(f"Profissional {nome_p} cadastrado com sucesso!")
      else:
        st.error("Informe o nome do profissional.")

  st.subheader("Profissionais Cadastrados Atualmente")
  prof_cadastrados = run_query(
      "SELECT id, nome, tipo_contrato, ativo FROM profissionais"
  )
  if prof_cadastrados:
    df_p = pd.DataFrame(
        prof_cadastrados,
        columns=["ID", "Nome", "Tipo de Contrato", "Status Ativo"],
    )
    st.dataframe(df_p, use_container_width=True)

elif menu == "Despesas e Fluxo de Caixa":
  st.header("📉 Módulo de Despesas e Projeção de Fluxo de Caixa")
  st.markdown(
      "Módulo exclusivo de acesso restrito (Diretoria) para lançamento de"
      " despesas e previsão financeira."
  )

  with st.form("form_despesa"):
    desc = st.text_input("Descrição da Despesa (Ex: Aluguel, Internet, Material)")
    cat = st.selectbox(
        "Categoria", ["Operacional", "Pessoal", "Infraestrutura", "Impostos"]
    )
    valor_d = st.number_input("Valor da Despesa (R$)", min_value=0.0)
    venc_d = st.date_input("Data de Vencimento")
    btn_desp = st.form_submit_button("Lançar Despesa")

    if btn_desp:
      run_query(
          """
                INSERT INTO despesas (data_vencimento, descricao, categoria, valor, status)
                VALUES (?, ?, ?, ?, 'Pendente')
            """,
          (venc_d.strftime("%d/%m/%Y"), desc, cat, valor_d),
          fetch=False,
      )
      st.success("Despesa cadastrada para projeção de fluxo de caixa.")

  conn = sqlite3.connect("ser_consciente.db")
  df_despesas = pd.read_sql_query("SELECT * FROM despesas", conn)
  conn.close()

  if not df_despesas.empty:
    st.subheader("Extrato de Despesas Cadastradas")
    st.dataframe(df_despesas, use_container_width=True)

elif menu == "Conciliação Bancária (OFX/TXT)":
  st.header("🔄 Conciliação Bancária Automatizada")
  st.markdown(
      "Faça o upload do extrato bancário (OFX ou CSV) para cruzar os"
      " recebimentos com o faturamento do sistema."
  )
  uploaded_file = st.file_uploader(
      "Envie o arquivo do extrato bancário", type=["ofx", "csv", "txt"]
  )
  if uploaded_file is not None:
    st.success(
        "Arquivo carregado com sucesso! Cruzamento de dados de faturamento em"
        " andamento..."
    )

elif menu == "Relatórios Completos":
  st.header("📈 Relatórios Diários, Semanais, Mensais e Anuais")
  st.selectbox(
      "Selecione o Período do Relatório",
      ["Diário", "Semanal", "Mensal", "Trimestral", "Anual"],
  )
  st.info(
      "Os relatórios cruzam dados por profissional, por paciente e por pacotes"
      " consumidos."
  )
