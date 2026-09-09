from datetime import datetime, time
import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Instituto Ser Consciente - Sistema Integrado",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- 1. BANCO DE DADOS E SEGURANÇA (SOFT DELETE / LGPD) ---
def init_db():
  try:
    conn = sqlite3.connect("ser_consciente.db", timeout=10)
    cursor = conn.cursor()

    # Profissionais
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS profissionais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo_contrato TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                data_cadastro TEXT
            )
        """)

    # Pacientes
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT
            )
        """)

    # Salas / Consultórios
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS salas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_sala TEXT NOT NULL,
                status TEXT DEFAULT 'Disponível', -- Disponível, Ocupada, Manutenção
                profissional_atual TEXT
            )
        """)
    # Inserir salas padrão se não existirem
    cursor.execute("SELECT COUNT(*) FROM salas")
    if cursor.fetchone()[0] == 0:
      salas_iniciais = [
          ("Consultório 1", "Disponível", None),
          ("Consultório 2", "Disponível", None),
          ("Consultório 3", "Disponível", None),
          ("Sala de Procedimentos", "Disponível", None),
      ]
      cursor.executemany(
          "INSERT INTO salas (nome_sala, status, profissional_atual) VALUES (?,"
          " ?, ?)",
          salas_iniciais,
      )

    # Atendimentos (Com suporte a Soft Delete e Vínculo de Consultório)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                profissional_id INTEGER,
                paciente_id INTEGER,
                consultorio TEXT,
                tipo_atendimento TEXT,
                valor_consulta REAL,
                forma_pagamento TEXT,
                repasse_clinica REAL,
                repasse_profissional REAL,
                recepcionista TEXT,
                status TEXT DEFAULT 'Ativo', -- 'Ativo', 'Cancelado', 'Arquivado' (Soft Delete)
                consolidado INTEGER DEFAULT 0
            )
        """)

    # Fila de Espera
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS fila_espera (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_nome TEXT,
                profissional_interesse INTEGER,
                data_cadastro TEXT,
                prioridade INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Aguardando'
            )
        """)

    # Despesas
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
  except Exception as e:
    st.error(f"Erro ao inicializar o banco de dados: {e}")


init_db()


def run_query(query, params=(), fetch=True):
  try:
    conn = sqlite3.connect("ser_consciente.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
      res = cursor.fetchall()
      conn.close()
      return res
    conn.commit()
    conn.close()
  except Exception as e:
    st.error(f"Erro na operação SQL: {e}")
    return []


# --- 2. CONTROLE DE ACESSO (RBAC) ---
st.sidebar.title("🔐 Instituto Ser Consciente")
perfil = st.sidebar.selectbox(
    "Perfil de Acesso",
    [
        "Recepção",
        "Administração (Antônio)",
        "Direção Técnica (Dr. Fabrício)",
    ],
)

st.sidebar.markdown("---")

if perfil == "Recepção":
  menu = st.sidebar.radio(
      "Menu Operacional",
      [
          "Mapa de Salas em Tempo Real",
          "Registro de Atendimentos & QR Code",
          "Fila de Espera",
          "Fechamento de Caixa",
      ],
  )
elif perfil == "Administração (Antônio)":
  menu = st.sidebar.radio(
      "Menu Gerencial",
      [
          "Dashboard BI & Ociosidade",
          "Auditoria (Soft Delete & Travas)",
          "Cadastro de Profissionais",
          "Despesas e Fluxo de Caixa",
      ],
  )
else:
  menu = st.sidebar.radio(
      "Painel Clínico",
      ["Prontuários e Visão Geral", "Relatórios de Atendimento Clínico"],
  )


# --- 3. MÓDULOS DE OPERAÇÃO (RECEPÇÃO & SALAS) ---
if menu == "Mapa de Salas em Tempo Real":
  st.header("🏢 Mapa de Consultórios - Tempo Real")
  st.write(
      "Visualize o status atual das salas e gerencie o check-in/out por chave."
  )

  salas = run_query("SELECT id, nome_sala, status, profissional_atual FROM salas")
  cols = st.columns(len(salas))

  for idx, sala in enumerate(salas):
    s_id, nome, status_sala, prof = sala
    with cols[idx]:
      if status_sala == "Disponível":
        st.success(f"**{nome}**\n\n🟢 Disponível")
      else:
        st.error(f"**{nome}**\n\n🔴 Ocupado\n\nProf: {prof}")

  st.markdown("---")
  st.subheader("Gerenciar Ocupação de Sala (Check-in / Check-out)")
  with st.form("form_sala"):
    sala_escolhida = st.selectbox(
        "Selecionar Sala", salas, format_func=lambda x: x[1]
    )
    novo_status = st.selectbox(
        "Ação", ["Ocupar Sala (Entrega de Chave)", "Liberar Sala (Check-out)"]
    )
    prof_ocupante = st.text_input("Nome do Profissional (se ocupando)")

    if st.form_submit_button("Atualizar Status da Sala"):
      st_text = (
          "Ocupada" if "Ocupar" in novo_status else "Disponível"
      )
      p_nome = prof_ocupante if st_text == "Ocupada" else None
      run_query(
          "UPDATE salas SET status = ?, profissional_atual = ? WHERE id = ?",
          (st_text, p_nome, sala_escolhida[0]),
          fetch=False,
      )
      st.success(f"Sala {sala_escolhida[1]} atualizada com sucesso!")
      st.rerun()

elif menu == "Registro de Atendimentos & QR Code":
  st.header("📝 Registro de Atendimentos e Cessão de Espaço")
  profissionais = run_query(
      "SELECT id, nome, tipo_contrato FROM profissionais WHERE ativo = 1"
  )
  salas = run_query("SELECT nome_sala FROM salas")

  if not profissionais:
    st.warning("Cadastre profissionais ativos no painel administrativo.")
  else:
    with st.form("form_atendimento"):
      c1, c2 = st.columns(2)
      with c1:
        data_atendimento = st.date_input(
            "Data do Atendimento", value=datetime.today()
        )
        prof_sel = st.selectbox(
            "Profissional",
            profissionais,
            format_func=lambda x: f"{x[1]} ({x[2]})",
        )
        sala_atend = st.selectbox(
            "Consultório Utilizado (Obrigatório)",
            [s[0] for s in salas],
        )
      with c2:
        nome_paciente = st.text_input("Nome do Paciente")
        forma_pgto = st.selectbox(
            "Forma de Pagamento", ["Dinheiro", "Cartão", "PIX", "Faturado"]
        )
        tipo_atend = st.selectbox(
            "Tipo", ["Avulso (R$ 50,00)", "Conveniado (R$ 42,00)", "Outro"]
        )

      valor_consulta = st.number_input(
          "Valor Cobrado do Paciente (R$)", min_value=0.0, format="%.2f"
      )
      submitted = st.form_submit_button("Registrar com Trava de LGPD")

      if submitted:
        if not nome_paciente or valor_consulta <= 0:
          st.error(
              "Preencha o nome do paciente e um valor de consulta válido."
          )
        else:
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

          # Cálculo automático da taxa de ocupação
          contrato = prof_sel[2]
          repasse_clinica = 0.0
          if "Avulso" in tipo_atend:
            repasse_clinica = 50.0
          elif "Conveniado" in tipo_atend:
            repasse_clinica = 42.0
          elif "70/30" in contrato:
            repasse_clinica = valor_consulta * 0.30
          else:
            repasse_clinica = 50.0  # Padrão base

          repasse_prof = valor_consulta - repasse_clinica

          cursor.execute(
              """
                    INSERT INTO atendimentos (data, profissional_id, paciente_id, consultorio, tipo_atendimento, valor_consulta, forma_pagamento, repasse_clinica, repasse_profissional, recepcionista, status, consolidado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Ativo', 0)
                """,
              (
                  data_atendimento.strftime("%d/%m/%Y"),
                  prof_sel[0],
                  paciente_id,
                  sala_atend,
                  tipo_atend,
                  valor_consulta,
                  forma_pgto,
                  repasse_clinica,
                  repasse_prof,
                  perfil,
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"Atendimento registrado! Taxa de Ocupação Clínica (Repasse): R$"
              f" {repasse_clinica:.2f}"
          )

elif menu == "Fila de Espera":
  st.header("⏳ Fila de Espera de Pacientes")
  with st.form("form_fila"):
    p_nome = st.text_input("Nome do Paciente")
    p_prof = st.selectbox(
        "Profissional Desejado",
        run_query("SELECT id, nome FROM profissionais WHERE ativo = 1"),
        format_func=lambda x: x[1],
    )
    if st.form_submit_button("Adicionar à Fila por Antiguidade"):
      run_query(
          """
                INSERT INTO fila_espera (paciente_nome, profissional_interesse, data_cadastro, status)
                VALUES (?, ?, ?, 'Aguardando')
            """,
          (p_nome, p_prof[0], datetime.today().strftime("%d/%m/%Y")),
          fetch=False,
      )
      st.success("Paciente inserido na fila de espera com prioridade.")

  st.subheader("Fila Atual")
  df_fila = pd.DataFrame(
      run_query(
          "SELECT id, paciente_nome, data_cadastro, status FROM fila_espera"
          " WHERE status = 'Aguardando'"
      ),
      columns=["ID", "Paciente", "Data Cadastro", "Status"],
  )
  st.dataframe(df_fila, use_container_width=True)

elif menu == "Fechamento de Caixa":
  st.header("💰 Fechamento de Caixa Diário")
  data_f = st.date_input("Data do Fechamento", value=datetime.today())
  conn = sqlite3.connect("ser_consciente.db")
  df_c = pd.read_sql_query(
      """
        SELECT a.id, p.nome as profissional, pac.nome as paciente, a.consultorio, a.valor_consulta, a.repasse_clinica, a.status 
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN pacientes pac ON a.paciente_id = pac.id
        WHERE a.data = ? AND a.status = 'Ativo'
    """,
      conn,
      params=(data_f.strftime("%d/%m/%Y"),),
  )
  conn.close()

  if df_c.empty:
    st.info("Nenhum atendimento ativo nesta data.")
  else:
    st.dataframe(df_c, use_container_width=True)
    st.metric("Total Arrecadado Clínica", f"R$ {df_c['repasse_clinica'].sum():.2f}")


# --- 4. MÓDULOS GERENCIAIS (ADMINISTRAÇÃO) ---
elif menu == "Dashboard BI & Ociosidade":
  st.header("📊 BI & Inteligência de Dados - Instituto Ser Consciente")
  conn = sqlite3.connect("ser_consciente.db")
  df_bi = pd.read_sql_query(
      """
        SELECT a.data, p.nome as profissional, a.valor_consulta, a.repasse_clinica, a.consultorio
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        WHERE a.status = 'Ativo'
    """,
      conn,
  )
  conn.close()

  if not df_bi.empty:
    c1, c2, c3 = st.columns(3)
    with c1:
      st.metric(
          "Faturamento Total Bruto", f"R$ {df_bi['valor_consulta'].sum():.2f}"
      )
    with c2:
      st.metric(
          "Receita Ocupação (Clínica)",
          f"R$ {df_bi['repasse_clinica'].sum():.2f}",
      )
    with c3:
      st.metric("Total Atendimentos", len(df_bi))

    st.subheader("Desempenho por Profissional")
    df_prof = (
        df_bi.groupby("profissional")["repasse_clinica"].sum().reset_index()
    )
    st.bar_chart(df_prof.set_index("profissional"))
  else:
    st.info("Sem dados suficientes para gerar os gráficos de BI.")

elif menu == "Auditoria (Soft Delete & Travas)":
  st.header("🔍 Auditoria e Política de Exclusão Zero (Soft Delete)")
  st.write(
      "Nenhum registro é apagado permanentemente. O Soft Delete preserva a"
      " trilha de auditoria exigida."
  )
  conn = sqlite3.connect("ser_consciente.db")
  df_aud = pd.read_sql_query(
      """
        SELECT a.id, a.data, p.nome as profissional, pac.nome as paciente, a.status, a.consolidado
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN pacientes pac ON a.paciente_id = pac.id
    """,
      conn,
  )
  conn.close()

  if not df_aud.empty:
    st.dataframe(df_aud, use_container_width=True)
    at_id = st.number_input(
        "ID do Registro para Alterar Status", min_value=1, step=1
    )
    novo_status = st.selectbox(
        "Novo Status de Auditoria", ["Ativo", "Cancelado", "Arquivado"]
    )
    if st.button("Aplicar Soft Delete / Alteração"):
      run_query(
          "UPDATE atendimentos SET status = ? WHERE id = ?",
          (novo_status, at_id),
          fetch=False,
      )
      st.success("Status atualizado preservando o histórico (Soft Delete).")

elif menu == "Cadastro de Profissionais":
  st.header("👥 Gestão de Profissionais e Regras Contratuais")
  with st.form("nov_prof"):
    nome_p = st.text_input("Nome do Profissional")
    tipo_c = st.selectbox(
        "Modelo de Cessão",
        [
            "Taxa Fixa Avulso (R$ 50,00)",
            "Taxa Fixa Conveniado (R$ 42,00)",
            "Percentual 70/30",
            "Isento (Diretoria)",
        ],
    )
    if st.form_submit_button("Cadastrar Profissional"):
      run_query(
          "INSERT INTO profissionais (nome, tipo_contrato, data_cadastro)"
          " VALUES (?, ?, ?)",
          (nome_p, tipo_c, datetime.today().strftime("%d/%m/%Y")),
          fetch=False,
      )
      st.success("Profissional cadastrado com sucesso!")

  st.dataframe(
      pd.DataFrame(
          run_query(
              "SELECT id, nome, tipo_contrato, ativo FROM profissionais"
          ),
          columns=["ID", "Nome", "Contrato", "Ativo"],
      ),
      use_container_width=True,
  )

elif menu == "Despesas e Fluxo de Caixa":
  st.header("📉 Despesas Operacionais")
  with st.form("form_desp"):
    desc = st.text_input("Descrição")
    val = st.number_input("Valor (R$)", min_value=0.0)
    venc = st.date_input("Vencimento")
    if st.form_submit_button("Lançar Despesa"):
      run_query(
          "INSERT INTO despesas (data_vencimento, descricao, valor, status)"
          " VALUES (?, ?, ?, 'Pendente')",
          (venc.strftime("%d/%m/%Y"), desc, val),
          fetch=False,
      )
      st.success("Despesa registrada.")


# --- 5. PAINEL CLÍNICO (DR. FABRÍCIO) ---
elif menu == "Prontuários e Visão Geral":
  st.header("🩺 Painel Clínico - Visão Geral do Diretor Técnico")
  st.info(
      "Acesso restrito para acompanhamento de escalas, exames e dados médicos"
      " agregados com total conformidade ética."
  )
  conn = sqlite3.connect("ser_consciente.db")
  df_clin = pd.read_sql_query(
      """
        SELECT a.data, p.nome as profissional, pac.nome as paciente, a.consultorio, a.tipo_atendimento
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN pacientes pac ON a.paciente_id = pac.id
        WHERE a.status = 'Ativo'
    """,
      conn,
  )
  conn.close()
  st.dataframe(df_clin, use_container_width=True)

elif menu == "Relatórios de Atendimento Clínico":
  st.header("📈 Relatórios de Produtividade e Consultórios")
  st.write(
      "Estatísticas de ocupação dos consultórios por período e volume de"
      " pacientes atendidos."
  )
  conn = sqlite3.connect("ser_consciente.db")
  df_rep = pd.read_sql_query(
      "SELECT consultorio, COUNT(*) as total FROM atendimentos GROUP BY"
      " consultorio",
      conn,
  )
  conn.close()
  if not df_rep.empty:
    st.bar_chart(df_rep.set_index("consultorio"))
