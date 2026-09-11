import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão Clínica - Instituto Ser Consciente",
    page_icon="🏥",
    layout="wide",
)

# Inicialização do Banco de Dados em Memória (Session State) com Chaves Globalizadas de Pacientes
if "perfil_usuario" not in st.session_state:
  st.session_state.perfil_usuario = "Administrador"

if "audit_log" not in st.session_state:
  st.session_state.audit_log = pd.DataFrame(columns=[
      "Timestamp",
      "Usuario",
      "Modulo",
      "Acao",
      "Detalhes",
  ])

if "usuarios_sistema" not in st.session_state:
  st.session_state.usuarios_sistema = pd.DataFrame([
      {
          "ID_Usuario": "USER-001",
          "Nome": "Antônio Sérgio",
          "Email": "antonio@institutoserconsciente.com.br",
          "Perfil": "Administrador",
          "Status": "Ativo",
          "Ultima_Modificacao": "2026-09-11 08:00:00",
      },
      {
          "ID_Usuario": "USER-002",
          "Nome": "Nathália",
          "Email": "recepcao@institutoserconsciente.com.br",
          "Perfil": "Recepcionista",
          "Status": "Ativo",
          "Ultima_Modificacao": "2026-09-11 08:00:00",
      },
  ])

if "profissionais" not in st.session_state:
  st.session_state.profissionais = pd.DataFrame([
      {
          "ID": 1,
          "Nome": "Dr. Fabrício",
          "Especialidade": "Psiquiatria",
          "Tipo_Atendimento": "Consulta",
          "Modalidade": "Produtividade Variável",
          "Percentual_Clinica": 30.0,
          "Status": "Ativo",
      },
      {
          "ID": 2,
          "Nome": "Mariana Terapeuta",
          "Especialidade": "Psicologia",
          "Tipo_Atendimento": "Sessão",
          "Modalidade": "Produtividade Variável",
          "Percentual_Clinica": 20.0,
          "Status": "Ativo",
      },
  ])

# Base Mestra de Pacientes com ID Único (Resolve ambiguidade de múltiplos profissionais)
if "base_pacientes" not in st.session_state:
  st.session_state.base_pacientes = pd.DataFrame([
      {
          "ID_Paciente": "PAC-0001",
          "Nome_Completo": "João da Silva",
          "Telefone": "(31) 99999-1111",
          "Email": "joao@email.com",
          "Data_Cadastro": "2026-01-15",
      },
      {
          "ID_Paciente": "PAC-0002",
          "Nome_Completo": "Maria Oliveira",
          "Telefone": "(31) 98888-2222",
          "Email": "maria@email.com",
          "Data_Cadastro": "2026-02-10",
      },
  ])

# Base de Opções/Modelos de Pacotes por Profissional
if "modelos_pacotes_profissional" not in st.session_state:
  st.session_state.modelos_pacotes_profissional = pd.DataFrame([
      {
          "ID_Modelo": 1,
          "Profissional": "Dr. Fabrício",
          "Descricao_Opcao": "Pacote 4 Sessões (Tabela Antiga)",
          "Total_Sessoes": 4,
          "Valor_Sugerido": 500.0,
      },
      {
          "ID_Modelo": 2,
          "Profissional": "Dr. Fabrício",
          "Descricao_Opcao": "Pacote 4 Sessões (Tabela Atualizada)",
          "Total_Sessoes": 4,
          "Valor_Sugerido": 580.0,
      },
      {
          "ID_Modelo": 3,
          "Profissional": "Mariana Terapeuta",
          "Descricao_Opcao": "Pacote 5 Sessões (Padrão)",
          "Total_Sessoes": 5,
          "Valor_Sugerido": 750.0,
      },
  ])

# Base de Pacotes Cadastrados (Vinculados por ID_Paciente)
if "pacotes_atendimento" not in st.session_state:
  st.session_state.pacotes_atendimento = pd.DataFrame(columns=[
      "ID_Pacote",
      "Profissional",
      "ID_Paciente",
      "Nome_Paciente",
      "Categoria_Opcao",
      "Total_Sessoes",
      "Valor_Total_Pacote",
      "Percentual_Clinica",
      "Valor_Repasse_Total",
      "Status_Pacote",
      "Data_Cadastro",
  ])

# Base de Atendimentos por Produtividade & Avulsos (Vinculados por ID_Paciente)
if "atendimentos_produtividade" not in st.session_state:
  st.session_state.atendimentos_produtividade = pd.DataFrame(columns=[
      "ID_Atendimento",
      "Data",
      "Hora",
      "Profissional",
      "Tipo_Atendimento",
      "ID_Paciente",
      "Nome_Paciente",
      "Tipo_Cobranca",
      "ID_Pacote",
      "Sessao_Atual",
      "Valor_Total_Paciente",
      "Percentual_Clinica",
      "Valor_Repasse_Clinica",
      "Status_Pagamento",
      "Data_Baixa",
      "Plano_Contas",
      "Registrado_Por",
  ])


def registrar_auditoria(modulo, acao, detalhes):
  novo_log = pd.DataFrame([{
      "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "Usuario": st.session_state.get("perfil_usuario", "Desconhecido"),
      "Modulo": modulo,
      "Acao": acao,
      "Detalhes": detalhes,
  }])
  st.session_state.audit_log = pd.concat(
      [st.session_state.audit_log, novo_log], ignore_index=True
  )


# ---------------------------------------------------------
# BARRA LATERAL DE NAVEGAÇÃO E CONTROLE DE ACESSO
# ---------------------------------------------------------
st.sidebar.title("🏥 Painel de Gestão (Coworking)")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Identificação de Usuário Ativo")
usuarios_ativos_lista = st.session_state.usuarios_sistema[
    st.session_state.usuarios_sistema["Status"] == "Ativo"
]["Nome"].tolist()
if not usuarios_ativos_lista:
  usuarios_ativos_lista = ["Administrador"]

usuario_logado_sel = st.sidebar.selectbox(
    "Usuário Operando a Sessão", usuarios_ativos_lista
)
st.session_state.perfil_usuario = usuario_logado_sel

perfil_atual_cargo = st.session_state.usuarios_sistema.loc[
    st.session_state.usuarios_sistema["Nome"] == usuario_logado_sel, "Perfil"
].values
cargo_str = (
    perfil_atual_cargo[0] if len(perfil_atual_cargo) > 0 else "Administrador"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Módulos do Sistema")

if cargo_str == "Recepcionista":
  menu = st.sidebar.selectbox(
      "Escolha o Módulo",
      [
          "Lançamento de Produtividade & Conta Corrente",
          "Cadastro Mestre de Pacientes",
          "Cadastro & Gestão de Pacotes",
          "Agendamento & Salas",
          "Fechamento de Caixa Diário",
      ],
  )
  st.sidebar.info("ℹ️ Recepção com cadastro ágil e blindagem de pacotes.")
else:
  menu = st.sidebar.selectbox(
      "Escolha o Módulo",
      [
          "Dashboard Gerencial & Relatórios Completos",
          "Lançamento de Produtividade & Conta Corrente",
          "Cadastro Mestre de Pacientes",
          "Cadastro & Gestão de Pacotes",
          "Cadastro de Profissionais",
          "Conciliação e Fluxo de Caixa (Auditável)",
          "Gestão de Usuários e Permissões",
          "Auditoria do Sistema",
      ],
  )

# ---------------------------------------------------------
# 1. MÓDULO: CADASTRO MESTRE DE PACIENTES (ID ÚNICO)
# ---------------------------------------------------------
if menu == "Cadastro Mestre de Pacientes":
  st.title("👤 Cadastro Mestre de Pacientes (ID Único)")
  st.markdown(
      "Base unificada de pacientes da clínica. Cada paciente possui um ID"
      " exclusivo para evitar cruzamentos incorretos quando atendidos por"
      " múltiplos profissionais."
  )

  tab_pac1, tab_pac2 = st.tabs(
      ["📋 Pacientes Cadastrados", "➕ Novo Cadastro de Paciente"]
  )

  with tab_pac1:
    if not st.session_state.base_pacientes.empty:
      st.dataframe(
          st.session_state.base_pacientes, use_container_width=True
      )
    else:
      st.info("Nenhum paciente cadastrado.")

  with tab_pac2:
    with st.form("form_cad_paciente_mestre"):
      c1, c2 = st.columns(2)
      with c1:
        novo_nome_pac = st.text_input("Nome Completo do Paciente")
        tel_pac = st.text_input("Telefone / WhatsApp (Ex: 31 99999-9999)")
      with c2:
        email_pac = st.text_input("E-mail do Paciente")

      if st.form_submit_button("Salvar Paciente na Base Mestra"):
        if not novo_nome_pac.strip():
          st.error("O nome completo é obrigatório.")
        else:
          proximo_id_num = len(st.session_state.base_pacientes) + 1
          novo_id_str = f"PAC-{proximo_id_num:04d}"

          df_novo_p = pd.DataFrame([{
              "ID_Paciente": novo_id_str,
              "Nome_Completo": novo_nome_pac,
              "Telefone": tel_pac,
              "Email": email_pac,
              "Data_Cadastro": str(datetime.date.today()),
          }])
          st.session_state.base_pacientes = pd.concat(
              [st.session_state.base_pacientes, df_novo_p], ignore_index=True
          )
          registrar_auditoria(
              "Pacientes",
              "Cadastro Mestre",
              f"ID: {novo_id_str}, Nome: {novo_nome_pac}",
          )
          st.success(
              f"Paciente {novo_nome_pac} cadastrado com sucesso! ID gerado:"
              f" **{novo_id_str}**"
          )
          st.rerun()

# ---------------------------------------------------------
# 2. MÓDULO: DASHBOARD GERENCIAL & RELATÓRIOS COMPLETOS
# ---------------------------------------------------------
elif menu == "Dashboard Gerencial & Relatórios Completos":
  st.title("📊 Dashboard Executivo & Central de Relatórios Completos")
  st.markdown(
      "Visão consolidada do faturamento, repasses, pacotes e produtividade"
      " por profissional e paciente."
  )

  df_prod = st.session_state.atendimentos_produtividade
  df_pacs = st.session_state.pacotes_atendimento
  df_pats = st.session_state.base_pacientes

  # Métricas Principais
  col1, col2, col3, col4 = st.columns(4)
  total_recebido = (
      df_prod[df_prod["Status_Pagamento"] == "Pago (PIX para Clínica)"][
          "Valor_Repasse_Clinica"
      ].sum()
      if not df_prod.empty
      else 0.0
  )
  total_pendente_cc = (
      df_prod[df_prod["Status_Pagamento"] == "Pendente (Conta Corrente)"][
          "Valor_Repasse_Clinica"
      ].sum()
      if not df_prod.empty
      else 0.0
  )

  col1.metric("Repasses Efetivados (Caixa)", f"R$ {total_recebido:,.2f}")
  col2.metric(
      "Conta Corrente (Pendentes)", f"R$ {total_pendente_cc:,.2f}"
  )
  col3.metric(
      "Total de Pacientes Cadastrados",
      len(df_pats) if not df_pats.empty else 0,
  )
  col4.metric(
      "Atendimentos Realizados", len(df_prod) if not df_prod.empty else 0
  )

  st.markdown("---")
  st.subheader("📑 Central de Relatórios Analíticos")

  tipo_relatorio = st.selectbox(
      "Selecione o Relatório Desejado",
      [
          "1. Relatório Geral de Produtividade por Profissional",
          "2. Relatório de Extrato de Consumo de Pacotes (Por Paciente/ID)",
          "3. Relatório de Conta Corrente e Pendências Detalhadas",
          "4. Relatório de Faturamento Consolidado por Período / Plano de Contas",
          "5. Relatório de Pacientes Atendidos por Múltiplos Profissionais",
      ],
  )

  if tipo_relatorio.startswith("1."):
    st.markdown("### 👨‍⚕️ Produtividade Consolidada por Profissional")
    if not df_prod.empty:
      resumo_prof = (
          df_prod.groupby("Profissional")
          .agg(
              Total_Atendimentos=("ID_Atendimento", "count"),
              Repasse_Total_Gerado=("Valor_Repasse_Clinica", "sum"),
          )
          .reset_index()
      )
      st.dataframe(resumo_prof, use_container_width=True)
      fig = px.bar(
          resumo_prof,
          x="Profissional",
          y="Repasse_Total_Gerado",
          title="Repasse Total Gerado por Profissional (R$)",
      )
      st.plotly_chart(fig, use_container_width=True)
    else:
      st.info("Nenhum dado para exibir.")

  elif tipo_relatorio.startswith("2."):
    st.markdown("### 📦 Extrato e Status de Consumo de Pacotes")
    if not df_pacs.empty:
      df_pacs_rel = df_pacs.copy()
      consu_lista, rest_lista = [], []
      for _, row in df_pacs_rel.iterrows():
        id_p = row["ID_Pacote"]
        tot_s = int(row["Total_Sessoes"])
        usados = len(
            df_prod[df_prod["ID_Pacote"] == id_p]
        )
        consu_lista.append(usados)
        rest_lista.append(max(0, tot_s - usados))

      df_pacs_rel["Sessoes_Consumidas"] = consu_lista
      df_pacs_rel["Sessoes_Restantes"] = rest_lista
      st.dataframe(
          df_pacs_rel[
              [
                  "ID_Pacote",
                  "ID_Paciente",
                  "Nome_Paciente",
                  "Profissional",
                  "Categoria_Opcao",
                  "Total_Sessoes",
                  "Sessoes_Consumidas",
                  "Sessoes_Restantes",
                  "Status_Pacote",
              ]
          ],
          use_container_width=True,
      )
    else:
      st.info("Nenhum pacote cadastrado.")

  elif tipo_relatorio.startswith("3."):
    st.markdown("### 💳 Relatório Detalhado de Conta Corrente")
    if not df_prod.empty:
      df_cc = df_prod[
          df_prod["Status_Pagamento"] == "Pendente (Conta Corrente)"
      ]
      if not df_cc.empty:
        st.dataframe(
            df_cc[
                [
                    "Data",
                    "Profissional",
                    "ID_Paciente",
                    "Nome_Paciente",
                    "Tipo_Cobranca",
                    "Valor_Repasse_Clinica",
                ]
            ],
            use_container_width=True,
        )
      else:
        st.success("Não há pendências em aberto na conta corrente.")
    else:
      st.info("Nenhum registro.")

  elif tipo_relatorio.startswith("4."):
    st.markdown("### 💰 Faturamento Consolidado por Plano de Contas")
    if not df_prod.empty:
      df_fin = (
          df_prod.groupby("Plano_Contas")
          .agg(Valor_Total_Repasse=("Valor_Repasse_Clinica", "sum"))
          .reset_index()
      )
      st.dataframe(df_fin, use_container_width=True)
    else:
      st.info("Nenhum lançamento financeiro.")

  elif tipo_relatorio.startswith("5."):
    st.markdown(
        "### 👥 Relatório de Pacientes Atendidos por Múltiplos Profissionais"
    )
    if not df_prod.empty:
      cruzamento = (
          df_prod.groupby(["ID_Paciente", "Nome_Paciente"])["Profissional"]
          .unique()
          .reset_index()
      )
      cruzamento["Quantidade_Profissionais"] = cruzamento["Profissional"].apply(
          len
      )
      cruzamento["Profissionais_Atendidos"] = cruzamento["Profissional"].apply(
          lambda x: ", ".join(x)
      )
      st.dataframe(
          cruzamento[
              [
                  "ID_Paciente",
                  "Nome_Paciente",
                  "Quantidade_Profissionais",
                  "Profissionais_Atendidos",
              ]
          ],
          use_container_width=True,
      )
    else:
      st.info("Nenhum atendimento registrado.")

# ---------------------------------------------------------
# 3. MÓDULO: CADASTRO DE PROFISSIONAIS
# ---------------------------------------------------------
elif menu == "Cadastro de Profissionais":
  st.title("👨‍⚕️ Cadastro de Profissionais & Modelos de Pacotes")
  if not st.session_state.profissionais.empty:
    st.dataframe(st.session_state.profissionais, use_container_width=True)
  else:
    st.info("Nenhum profissional.")

# ---------------------------------------------------------
# 4. MÓDULO: CADASTRO & GESTÃO DE PACOTES
# ---------------------------------------------------------
elif menu == "Cadastro & Gestão de Pacotes":
  st.title("📦 Cadastro de Pacotes Vinculados por ID")
  profs_prod = st.session_state.profissionais[
      st.session_state.profissionais["Modalidade"] == "Produtividade Variável"
  ]
  pacientes_lista = st.session_state.base_pacientes

  if pacientes_lista.empty or profs_prod.empty:
    st.warning(
        "Cadastre previamente profissionais e pacientes na Base Mestra."
    )
  else:
    with st.form("form_cad_pacote_id"):
      c_prof_pac = st.selectbox(
          "Profissional Responsável", profs_prod["Nome"].tolist()
      )

      # Seleção do Paciente por ID - evita homônimos
      pacientes_opcoes = (
          pacientes_lista["ID_Paciente"]
          + " - "
          + pacientes_lista["Nome_Completo"]
      ).tolist()
      pac_sel_str = st.selectbox(
          "Selecionar Paciente (ID - Nome)", pacientes_opcoes
      )

      id_pac_escolhido = pac_sel_str.split(" - ")[0]
      nome_pac_escolhido = pac_sel_str.split(" - ")[1]

      opcoes_prof = st.session_state.modelos_pacotes_profissional[
          st.session_state.modelos_pacotes_profissional["Profissional"]
          == c_prof_pac
      ]
      escolha_modelo = st.selectbox(
          "Modelo de Pacote",
          ["Personalizado"] + opcoes_prof["Descricao_Opcao"].tolist(),
      )

      d_sessoes, d_valor, cat_str = 4, 580.0, "Personalizado"
      if (
          escolha_modelo != "Personalizado"
          and not opcoes_prof.empty
      ):
        m_sel = opcoes_prof[
            opcoes_prof["Descricao_Opcao"] == escolha_modelo
        ].iloc[0]
        d_sessoes = int(m_sel["Total_Sessoes"])
        d_valor = float(m_sel["Valor_Sugerido"])
        cat_str = str(m_sel["Descricao_Opcao"])

      c1, c2 = st.columns(2)
      with c1:
        total_sessoes = st.number_input(
            "Quantidade de Sessões", min_value=1, value=d_sessoes, step=1
        )
      with c2:
        valor_total_pacote = st.number_input(
            "Valor Total do Pacote (R$)", min_value=0.0, value=d_valor, step=10.0
        )

      d_prof = profs_prod[profs_prod["Nome"] == c_prof_pac].iloc[0]
      perc_c = float(d_prof["Percentual_Clinica"])
      valor_repasse_total = valor_total_pacote * (perc_c / 100.0)

      if st.form_submit_button("Salvar Pacote Vinculado"):
        novo_id_pacote = len(st.session_state.pacotes_atendimento) + 1
        df_novo_p = pd.DataFrame([{
            "ID_Pacote": novo_id_pacote,
            "Profissional": c_prof_pac,
            "ID_Paciente": id_pac_escolhido,
            "Nome_Paciente": nome_pac_escolhido,
            "Categoria_Opcao": cat_str,
            "Total_Sessoes": total_sessoes,
            "Valor_Total_Pacote": valor_total_pacote,
            "Percentual_Clinica": perc_c,
            "Valor_Repasse_Total": valor_repasse_total,
            "Status_Pacote": "Ativo / Em Consumo",
            "Data_Cadastro": str(datetime.date.today()),
        }])
        st.session_state.pacotes_atendimento = pd.concat(
            [st.session_state.pacotes_atendimento, df_novo_p], ignore_index=True
        )
        registrar_auditoria(
            "Pacotes",
            "Cadastro",
            f"Paciente ID: {id_pac_escolhido} ({nome_pac_escolhido})",
        )
        st.success("Pacote cadastrado com sucesso!")
        st.rerun()

# ---------------------------------------------------------
# 5. MÓDULO: LANÇAMENTO DE PRODUTIVIDADE & CADASTRO INLINE
# ---------------------------------------------------------
elif menu == "Lançamento de Produtividade & Conta Corrente":
  st.title("💼 Lançamento de Atendimentos & Cadastro Rápido Inline")
  st.markdown(
      "🛡️ **Módulo Blindado:** Seleção por ID do Paciente com opção de cadastro"
      " instantâneo na mesma tela."
  )

  profs_prod = st.session_state.profissionais[
      st.session_state.profissionais["Modalidade"] == "Produtividade Variável"
  ]

  if profs_prod.empty:
    st.warning("Nenhum profissional cadastrado.")
  else:
    tab_l1, tab_l2 = st.tabs(
        ["➕ Registrar Atendimento", "📊 Conta Corrente & Extratos"]
    )

    with tab_l1:
      # FLUXO INLINE PARA CADASTRO RÁPIDO DE PACIENTE SEM SAIR DA TELA
      with st.expander(
          "➕ Não encontrou o paciente? Clique aqui para Cadastrar Rápido"
          " (Inline)",
          expanded=False,
      ):
        with st.form("form_inline_paciente"):
          c_nome_inc = st.text_input("Nome Completo do Novo Paciente")
          c_tel_inc = st.text_input("Telefone")
          if st.form_submit_button("Cadastrar e Usar Imediatamente"):
            if c_nome_inc.strip():
              novo_id_num = len(st.session_state.base_pacientes) + 1
              novo_id_str = f"PAC-{novo_id_num:04d}"
              df_novo_p = pd.DataFrame([{
                  "ID_Paciente": novo_id_str,
                  "Nome_Completo": c_nome_inc,
                  "Telefone": c_tel_inc,
                  "Email": "",
                  "Data_Cadastro": str(datetime.date.today()),
              }])
              st.session_state.base_pacientes = pd.concat(
                  [st.session_state.base_pacientes, df_novo_p],
                  ignore_index=True,
              )
              registrar_auditoria(
                  "Pacientes",
                  "Cadastro Rápido Inline",
                  f"ID: {novo_id_str}, Nome: {c_nome_inc}",
              )
              st.success(
                  f"Paciente cadastrado com ID **{novo_id_str}**! Já pode"
                  " selecionar abaixo."
              )
              st.rerun()

      st.markdown("---")
      with st.form("form_atendimento_hibrido_id"):
        c_prof = st.selectbox(
            "Selecionar Profissional", profs_prod["Nome"].tolist()
        )
        dados_prof_sel = profs_prod[profs_prod["Nome"] == c_prof].iloc[0]
        tipo_atendimento = dados_prof_sel["Tipo_Atendimento"]
        perc_clinica_padrao = float(dados_prof_sel["Percentual_Clinica"])

        tipo_cobranca = st.radio(
            "Modalidade do Atendimento",
            ["Atendimento Avulso", "Sessão de Pacote Cadastrado"],
        )

        pacientes_lista = st.session_state.base_pacientes
        if pacientes_lista.empty:
          st.error(
              "Nenhum paciente cadastrado. Cadastre acima antes de prosseguir."
          )
          st.stop()

        pacientes_opcoes = (
            pacientes_lista["ID_Paciente"]
            + " - "
            + pacientes_lista["Nome_Completo"]
        ).tolist()
        pac_sel_atd = st.selectbox(
            "Selecione o Paciente (ID e Nome)", pacientes_opcoes
        )

        id_pac_atd = pac_sel_atd.split(" - ")[0]
        nome_pac_atd = pac_sel_atd.split(" - ")[1]

        id_pacote_sel = None
        sessao_str = "Única"
        valor_unit_paciente = 250.0
        valor_repasse_atd = 0.0

        if tipo_cobranca == "Atendimento Avulso":
          c1, c2 = st.columns(2)
          with c1:
            d_atendimento = st.date_input("Data", datetime.date.today())
            h_atendimento = st.time_input(
                "Horário", datetime.datetime.now().time()
            )
          with c2:
            valor_unit_paciente = st.number_input(
                "Valor Pago pelo Paciente (R$)",
                min_value=0.0,
                value=250.0,
                step=10.0,
            )
            valor_repasse_atd = valor_unit_paciente * (
                perc_clinica_padrao / 100.0
            )
            st.info(
                f"📌 Repasse Devido à Clínica ({perc_clinica_padrao}%): R$"
                f" {valor_repasse_atd:,.2f}"
            )
        else:
          # Pacotes do Profissional filtrados pelo ID do Paciente
          pacs_prof = st.session_state.pacotes_atendimento[
              (st.session_state.pacotes_atendimento["Profissional"] == c_prof)
              & (
                  st.session_state.pacotes_atendimento["ID_Paciente"]
                  == id_pac_atd
              )
              & (
                  st.session_state.pacotes_atendimento["Status_Pacote"]
                  == "Ativo / Em Consumo"
              )
          ]
          if pacs_prof.empty:
            st.warning(
                "⚠️ Este paciente não possui pacotes ativos cadastrados para"
                f" o profissional {c_prof}."
            )
          else:
            pacs_prof["Label_Pacote"] = (
                "Pacote ID #"
                + pacs_prof["ID_Pacote"].astype(str)
                + " ("
                + pacs_prof["Categoria_Opcao"]
                + " - R$ "
                + pacs_prof["Valor_Total_Pacote"].astype(str)
                + ")"
            )
            pac_escolhido_label = st.selectbox(
                "Selecione o Pacote Ativo", pacs_prof["Label_Pacote"].tolist()
            )
            dados_pac_reg = pacs_prof[
                pacs_prof["Label_Pacote"] == pac_escolhido_label
            ].iloc[0]

            id_pacote_sel = int(dados_pac_reg["ID_Pacote"])
            total_s_pac = int(dados_pac_reg["Total_Sessoes"])

            atds_ja_lancados = st.session_state.atendimentos_produtividade[
                st.session_state.atendimentos_produtividade["ID_Pacote"]
                == id_pacote_sel
            ]
            num_sessao_atual = len(atds_ja_lancados) + 1
            sessoes_restantes = total_s_pac - len(atds_ja_lancados)

            st.markdown("---")
            st.markdown("### 🔍 **EXTRATO DE CONSUMO DO PACOTE**")
            col_inf1, col_inf2, col_inf3 = st.columns(3)
            col_inf1.metric("Total no Pacote", f"{total_s_pac} Sessões")
            col_inf2.metric(
                "Sessões Consumidas", f"{len(atds_ja_lancados)}"
            )
            col_inf3.metric("Sessões Restantes", f"{sessoes_restantes}")

            if num_sessao_atual > total_s_pac:
              st.error(
                  f"🚨 **BLOQUEIO CRÍTICO:** O pacote de {total_s_pac} sessões"
                  " já foi totalmente consumido!"
              )
            elif num_sessao_atual == total_s_pac:
              st.warning("⚠️ **ATENÇÃO:** Esta é a **ÚLTIMA SESSÃO** do pacote.")
            else:
              st.success(
                  f"✅ Registrando Sessão {num_sessao_atual:02d}-{total_s_pac:02d}"
              )

            sessao_str = f"{num_sessao_atual:02d}-{total_s_pac:02d}"
            c1, c2 = st.columns(2)
            with c1:
              d_atendimento = st.date_input(
                  "Data da Sessão", datetime.date.today()
              )
              h_atendimento = st.time_input(
                  "Horário", datetime.datetime.now().time()
              )
            with c2:
              valor_unit_paciente = 0.0
              valor_repasse_atd = 0.0

        if st.form_submit_button("Salvar Atendimento"):
          usuario_atual = st.session_state.get(
              "perfil_usuario", "Recepcionista"
          )
          novo_id = len(st.session_state.atendimentos_produtividade) + 1
          df_novo_atd = pd.DataFrame([{
              "ID_Atendimento": novo_id,
              "Data": str(d_atendimento),
              "Hora": h_atendimento.strftime("%H:%M"),
              "Profissional": c_prof,
              "Tipo_Atendimento": tipo_atendimento,
              "ID_Paciente": id_pac_atd,
              "Nome_Paciente": nome_pac_atd,
              "Tipo_Cobranca": tipo_cobranca,
              "ID_Pacote": id_pacote_sel if id_pacote_sel else 0,
              "Sessao_Atual": sessao_str,
              "Valor_Total_Paciente": valor_unit_paciente,
              "Percentual_Clinica": perc_clinica_padrao,
              "Valor_Repasse_Clinica": valor_repasse_atd,
              "Status_Pagamento": (
                  "Pendente (Conta Corrente)"
                  if tipo_cobranca == "Atendimento Avulso"
                  else "Sessão Consumida (Pacote)"
              ),
              "Data_Baixa": "",
              "Plano_Contas": (
                  "Receitas - Cessão de Espaço - Cessão de Espaço"
                  f" Produtividade - {c_prof}"
              ),
              "Registrado_Por": usuario_atual,
          }])
          st.session_state.atendimentos_produtividade = pd.concat(
              [st.session_state.atendimentos_produtividade, df_novo_atd],
              ignore_index=True,
          )
          registrar_auditoria(
              "Produtividade",
              "Lançamento",
              f"Profissional: {c_prof}, Paciente ID: {id_pac_atd}",
          )
          st.success("Atendimento registrado com sucesso!")
          st.rerun()

    with tab_l2:
      st.subheader("📊 Conta Corrente e Extratos")
      df_p = st.session_state.atendimentos_produtividade
      if not df_p.empty:
        prof_sel_cc = st.selectbox(
            "Selecionar Profissional", df_p["Profissional"].unique()
        )
        st.dataframe(
            df_p[df_p["Profissional"] == prof_sel_cc], use_container_width=True
        )
      else:
        st.info("Nenhum lançamento.")

# ---------------------------------------------------------
# OUTROS MÓDULOS DE SUPORTE
# ---------------------------------------------------------
elif menu == "Conciliação e Fluxo de Caixa (Auditável)":
  st.title("💰 Conciliação e Caixa")

elif menu == "Gestão de Usuários e Permissões":
  st.title("👥 Gestão de Usuários")
  st.dataframe(st.session_state.usuarios_sistema, use_container_width=True)

elif menu == "Auditoria do Sistema":
  st.title("🕵️ Trilha de Auditoria")
  if not st.session_state.audit_log.empty:
    st.dataframe(
        st.session_state.audit_log.sort_index(ascending=False),
        use_container_width=True
    )
  else:
    st.info("Nenhum log.")
