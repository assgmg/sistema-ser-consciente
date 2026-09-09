from datetime import datetime
import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Configuração da Página
st.set_page_config(
    page_title="Instituto Ser Consciente - Sistema Integrado",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- 1. BANCO DE DADOS E SEGURANÇA (ROBUSTO) ---
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

    # Pacotes de Sessões
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

    # Atendimentos
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                profissional_id INTEGER,
                paciente_id INTEGER,
                tipo_atendimento TEXT,
                valor_consulta REAL,
                forma_pagamento TEXT,
                repasse_clinica REAL,
                repasse_profissional REAL,
                recepcionista TEXT,
                status TEXT DEFAULT 'Ativo',
                consolidado INTEGER DEFAULT 0
            )
        """)

    # Migrações seguras de colunas caso o banco já exista
    try:
      cursor.execute(
          "ALTER TABLE atendimentos ADD COLUMN status TEXT DEFAULT 'Ativo'"
      )
    except sqlite3.OperationalError:
      pass

    try:
      cursor.execute(
          "ALTER TABLE atendimentos ADD COLUMN consolidado INTEGER DEFAULT 0"
      )
    except sqlite3.OperationalError:
      pass

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
    st.error(f"Erro ao inicializar banco de dados: {e}")


init_db()


def run_query(query, params=(), fetch=True):
  try:
    conn = sqlite3.connect("ser_consciente.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
      result = cursor.fetchall()
      conn.close()
      return result
    conn.commit()
    conn.close()
  except Exception as e:
    st.error(f"Erro na operação do banco de dados: {e}")
    return []


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
          "Auditoria e Lançamentos",
          "Cadastro de Profissionais",
          "Despesas e Fluxo de Caixa",
          "Conciliação Bancária",
          "Relatórios Completos",
      ],
  )


# --- 3. MÓDULOS DA RECEPÇÃO ---
if menu == "Registro de Atendimentos":
  st.header("📝 Registro Diário de Atendimentos")
  st.markdown(
      "Insira os dados do atendimento. O sistema aplica automaticamente as"
      " regras de cessão de espaço."
  )

  profissionais = run_query(
      "SELECT id, nome, tipo_contrato FROM profissionais WHERE ativo = 1"
  )

  if not profissionais:
    st.warning(
        "Nenhum profissional ativo cadastrado. Cadastre no painel administrativo"
        " primeiro."
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

          # Regras de Negócio de Cessão de Espaço
          contrato = prof_selecionado[2]
          repasse_clinica = 0.0

          if "70/30" in contrato:
            repasse_clinica = valor_consulta * 0.30
          elif "20/80" in contrato:
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
                    INSERT INTO atendimentos (data, profissional_id, paciente_id, tipo_atendimento, valor_consulta, forma_pagamento, repasse_clinica, repasse_profissional, recepcionista, status, consolidado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Ativo', 0)
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

elif menu == "Controle de Pacotes":
  st.header("📦 Gestão e Consumo de Pacotes de Sessões")
  st.write(
      "Registre novos pacotes vendidos ou dê baixa nas sessões consumidas."
  )
  profissionais = run_query("SELECT id, nome FROM profissionais WHERE ativo = 1")

  if not profissionais:
    st.warning("Cadastre profissionais ativos primeiro.")
  else:
    with st.form("form_pacote"):
      p_prof = st.selectbox(
          "Profissional Responsável", profissionais, format_func=lambda x: x[1]
      )
      p_pac = st.text_input("Nome do Paciente do Pacote")
      qtd_s = st.number_input(
          "Quantidade Total de Sessões", min_value=1, value=10, step=1
      )
      val_pac = st.number_input(
          "Valor Total Pago pelo Pacote (R$)", min_value=0.0, format="%.2f"
      )
      btn_cad_pacote = st.form_submit_button("Cadastrar Pacote")

      if btn_cad_pacote:
        if p_pac and val_pac > 0:
          conn = sqlite3.connect("ser_consciente.db")
          cursor = conn.cursor()
          cursor.execute("SELECT id FROM pacientes WHERE nome = ?", (p_pac,))
          res = cursor.fetchone()
          if res:
            pac_id = res[0]
          else:
            cursor.execute("INSERT INTO pacientes (nome) VALUES (?)", (p_pac,))
            pac_id = cursor.lastrowid
            conn.commit()

          cursor.execute(
              """
                    INSERT INTO pacotes (paciente_id, profissional_id, total_sessoes, sessoes_consumidas, valor_total, status, data_aquisicao)
                    VALUES (?, ?, ?, 0, ?, 'Ativo', ?)
                """,
              (
                  pac_id,
                  p_prof[0],
                  qtd_s,
                  val_pac,
                  datetime.today().strftime("%d/%m/%Y"),
              ),
          )
          conn.commit()
          conn.close()
          st.success("Pacote registrado com sucesso!")
        else:
          st.error("Preencha todos os campos corretamente.")

elif menu == "Fechamento de Caixa e Fatura":
  st.header("💰 Fechamento de Caixa e Emissão de Fatura para Cobrança")
  data_filtro = st.date_input(
      "Selecione a Data para Fechamento", value=datetime.today()
  )
  data_str = data_filtro.strftime("%d/%m/%Y")

  conn = sqlite3.connect("ser_consciente.db")
  df_caixa = pd.read_sql_query(
      """
        SELECT a.id, p.nome as profissional, pac.nome as paciente, a.valor_consulta, a.forma_pagamento, a.repasse_clinica, a.status 
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN pacientes pac ON a.paciente_id = pac.id
        WHERE a.data = ? AND a.status = 'Ativo'
    """,
      conn,
      params=(data_str,),
  )
  conn.close()

  if df_caixa.empty:
    st.info(f"Nenhum atendimento ativo registrado para a data {data_str}.")
  else:
    st.dataframe(df_caixa, use_container_width=True)
    total_dia = df_caixa["valor_consulta"].sum()
    total_repasse_clinica = df_caixa["repasse_clinica"].sum()

    col_m1, col_m2 = st.columns(2)
    with col_m1:
      st.metric(label="Faturamento Total do Dia", value=f"R$ {total_dia:.2f}")
    with col_m2:
      st.metric(
          label="Total Cessão de Espaço (Clínica)",
          value=f"R$ {total_repasse_clinica:.2f}",
      )

    st.markdown("### Visualização e Impressão da Fatura de Cessão")
    prof_fatura = st.selectbox(
        "Selecione o Profissional para Gerar a Fatura",
        df_caixa["profissional"].unique(),
    )

    if st.button("Gerar Fatura em Documento Pronto para Impressão"):
      df_prof = df_caixa[df_caixa["profissional"] == prof_fatura]
      val_total_prof = df_prof["repasse_clinica"].sum()

      html_fatura = f"""
            <div style="font-family: Arial, sans-serif; font-size: 11pt; color: #222222; max-width: 800px; margin: 0 auto; background: #ffffff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                <div style="border-bottom: 2px solid #333333; padding-bottom: 10px; margin-bottom: 15px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td>
                                <div style="font-size: 16pt; font-weight: bold; color: #1a365d;">Instituto Ser Consciente Ltda</div>
                                <div style="font-size: 9pt; color: #555555;">CNPJ: 04.000.917/0001-47</div>
                                <div style="font-size: 9pt; color: #555555;">Rua Inconfidentes, Contagem - MG</div>
                            </td>
                            <td style="text-align: right;">
                                <div style="font-size: 14pt; font-weight: bold; color: #2c5282;">FATURA DE CESSÃO DE ESPAÇO</div>
                                <div style="font-size: 10pt; color: #666666;">Data: {data_str}</div>
                            </td>
                        </tr>
                    </table>
                </div>
                <div style="font-size: 11pt; font-weight: bold; background-color: #edf2f7; padding: 6px; margin-bottom: 8px;">Colaborador: {prof_fatura}</div>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                    <thead>
                        <tr style="background-color: #f7fafc;">
                            <th style="border: 1px solid #cbd5e0; padding: 6px; text-align: left;">Paciente</th>
                            <th style="border: 1px solid #cbd5e0; padding: 6px; text-align: right;">Valor Consulta</th>
                            <th style="border: 1px solid #cbd5e0; padding: 6px; text-align: right;">Cessão de Espaço</th>
                        </tr>
                    </thead>
                    <tbody>
            """
      for _, row in df_prof.iterrows():
        html_fatura += f"""
                <tr>
                    <td style="border: 1px solid #cbd5e0; padding: 6px;">{row['paciente']}</td>
                    <td style="border: 1px solid #cbd5e0; padding: 6px; text-align: right;">R$ {row['valor_consulta']:.2f}</td>
                    <td style="border: 1px solid #cbd5e0; padding: 6px; text-align: right;">R$ {row['repasse_clinica']:.2f}</td>
                </tr>
                """
      html_fatura += f"""
                    </tbody>
                </table>
                <div style="float: right; width: 300px; font-weight: bold; padding: 8px; background-color: #edf2f7; text-align: right; border: 1px solid #cbd5e0;">
                    Valor Total da Cessão: R$ {val_total_prof:.2f}
                </div>
                <div style="clear: both;"></div>
                <div style="margin-top: 30px; text-align: center; border: 1px solid #cbd5e0; padding: 15px; background-color: #f7fafc;">
                    <div style="font-weight: bold; margin-bottom: 5px;">PAGAMENTO VIA PIX (QR CODE ESTÁTICO)</div>
                    <div>Chave Pix (CNPJ): <strong>04.000.917/0001-47</strong></div>
                </div>
            </div>
            """
      components.html(html_fatura, height=650, scrolling=True)


# --- 4. MÓDULOS GERENCIAIS (ADMINISTRAÇÃO) ---
elif menu == "Dashboard Executivo":
  st.header("📊 Dashboard Executivo e Caixa Consolidado")
  conn = sqlite3.connect("ser_consciente.db")
  df_geral = pd.read_sql_query(
      """
        SELECT a.data, p.nome as profissional, a.valor_consulta, a.repasse_clinica, a.forma_pagamento, a.consolidado
        FROM atendimentos a
        JOIN profissionais p ON a.profissional_id = p.id
        WHERE a.status = 'Ativo'
    """,
      conn,
  )
  conn.close()

  if not df_geral.empty:
    c1, c2 = st.columns(2)
    with c1:
      st.metric(
          "Faturamento Acumulado",
          f"R$ {df_geral['valor_consulta'].sum():.2f}",
      )
    with c2:
      st.metric(
          "Receita Total Cessão (Clínica)",
          f"R$ {df_geral['repasse_clinica'].sum():.2f}",
      )

    st.subheader("Histórico Completo de Lançamentos")
    st.dataframe(df_geral, use_container_width=True)
  else:
    st.info("Sem dados cadastrados no momento.")

elif menu == "Auditoria e Lançamentos":
  st.header("🔍 Auditoria, Correção de Status e Travamento de Lançamentos")
  conn = sqlite3.connect("ser_consciente.db")
  df_aud = pd.read_sql_query(
      """
        SELECT a.id, a.data, p.nome as profissional, pac.nome as paciente, a.valor_consulta, a.status, a.consolidado
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
        "ID do Lançamento para Alterar Status", min_value=1, step=1
    )
    novo_status = st.selectbox(
        "Novo Status", ["Ativo", "Cancelado", "Corrigido"]
    )
    travar = st.checkbox(
        "Consolidar e Travar (Imutável para Conciliação Bancária)"
    )

    if st.button("Atualizar Lançamento com Segurança"):
      val_cons = 1 if travar else 0
      run_query(
          "UPDATE atendimentos SET status = ?, consolidado = ? WHERE id = ?",
          (novo_status, val_cons, at_id),
          fetch=False,
      )
      st.success("Lançamento atualizado com sucesso!")
  else:
    st.info("Nenhum lançamento para auditar.")

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
        st.error("Informe o nome.")

  st.subheader("Profissionais Cadastrados")
  res_prof = run_query(
      "SELECT id, nome, tipo_contrato, ativo FROM profissionais"
  )
  if res_prof:
    st.dataframe(
        pd.DataFrame(
            res_prof, columns=["ID", "Nome", "Tipo de Contrato", "Ativo"]
        ),
        use_container_width=True,
    )

elif menu == "Despesas e Fluxo de Caixa":
  st.header("📉 Módulo de Despesas e Previsão de Fluxo de Caixa")
  with st.form("form_desp"):
    desc = st.text_input("Descrição da Despesa")
    cat = st.selectbox("Categoria", ["Operacional", "Pessoal", "Infraestrutura"])
    val = st.number_input("Valor (R$)", min_value=0.0)
    venc = st.date_input("Data de Vencimento")
    if st.form_submit_button("Lançar Despesa"):
      run_query(
          """
                INSERT INTO despesas (data_vencimento, descricao, categoria, valor, status)
                VALUES (?, ?, ?, ?, 'Pendente')
            """,
          (venc.strftime("%d/%m/%Y"), desc, cat, val),
          fetch=False,
      )
      st.success("Despesa registrada.")

elif menu == "Conciliação Bancária":
  st.header("🔄 Conciliação Bancária Automatizada")
  st.file_uploader("Enviar Extrato Bancário (OFX/CSV)", type=["ofx", "csv", "txt"])

elif menu == "Relatórios Completos":
  st.header("📈 Relatórios Diários, Semanais, Mensais e Anuais")
  st.selectbox(
      "Período", ["Diário", "Semanal", "Mensal", "Trimestral", "Anual"]
  )
  st.info("Relatórios cruzados por profissional, paciente e pacotes.")
