import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão Clínica - Instituto Ser Consciente",
    page_icon="🦋",
    layout="wide",
)

# ---------------------------------------------------------
# INICIALIZAÇÃO DA BASE DE DADOS (SESSION STATE DINÂMICO)
# ---------------------------------------------------------
if "perfil_usuario" not in st.session_state:
  st.session_state.perfil_usuario = "Antônio Sérgio"

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
      },
      {
          "ID_Usuario": "USER-002",
          "Nome": "Nathália",
          "Email": "recepcao@institutoserconsciente.com.br",
          "Perfil": "Recepcionista",
          "Status": "Ativo",
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
# BARRA LATERAL (COM LOGOMARCA E CONTROLE DE PERMISSÕES)
# ---------------------------------------------------------
if os.path.exists("logo.png"):
  st.sidebar.image("logo.png", use_container_width=True)
else:
  st.sidebar.markdown(
      "### 🦋 Clínica Instituto Ser Consciente"
  )  # Fallback caso a imagem ainda não tenha sido enviada

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Identificação de Usuário")

usuarios_ativos_lista = st.session_state.usuarios_sistema[
    st.session_state.usuarios_sistema["Status"] == "Ativo"
]["Nome"].tolist()
if not usuarios_ativos_lista:
  usuarios_ativos_lista = ["Antônio Sérgio"]

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

st.sidebar.markdown(f"**Cargo:** {cargo_str}")
st.sidebar.markdown("---")
st.sidebar.subheader("Módulos do Sistema")

if cargo_str == "Recepcionista":
  menu = st.sidebar.selectbox(
      "Escolha o Módulo",
      [
          "Lançamento de Produtividade & Conta Corrente",
          "Cadastro Mestre de Pacientes",
          "Cadastro & Gestão de Pacotes",
      ],
  )
else:
  menu = st.sidebar.selectbox(
      "Escolha o Módulo",
      [
          "Dashboard Gerencial & Relatórios",
          "Lançamento de Produtividade & Conta Corrente",
          "Cadastro Mestre de Pacientes",
          "Cadastro & Gestão de Pacotes",
          "Cadastro de Profissionais",
          "Gestão de Usuários e Permissões",
          "Auditoria do Sistema",
      ],
  )

# ---------------------------------------------------------
# CABEÇALHO PRINCIPAL DA TELA (COM LOGO E NOME)
# ---------------------------------------------------------
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
  if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
with col_titulo:
  st.markdown("## Clínica Instituto Ser Consciente")
  st.markdown("*Em busca da saúde integral*")

st.markdown("---")

# ---------------------------------------------------------
# 1. MÓDULO: CADASTRO MESTRE DE PACIENTES
# ---------------------------------------------------------
if menu == "Cadastro Mestre de Pacientes":
  st.title("👤 Cadastro Mestre de Pacientes")
  tab_p1, tab_p2 = st.tabs(["📋 Pacientes Cadastrados", "➕ Novo Cadastro"])

  with tab_p1:
    if not st.session_state.base_pacientes.empty:
      st.dataframe(
          st.session_state.base_pacientes, use_container_width=True
      )

      st.markdown("### 🗑️ Excluir Paciente")
      pac_excluir = st.selectbox(
          "Selecione o paciente",
          st.session_state.base_pacientes["ID_Paciente"]
          + " - "
          + st.session_state.base_pacientes["Nome_Completo"],
      )
      if st.button("Remover Paciente Selecionado"):
        id_excl = pac_excluir.split(" - ")[0]
        st.session_state.base_pacientes = st.session_state.base_pacientes[
            st.session_state.base_pacientes["ID_Paciente"] != id_excl
        ]
        registrar_auditoria("Pacientes", "Exclusão", f"ID Removido: {id_excl}")
        st.success("Paciente removido com sucesso!")
        st.rerun()
    else:
      st.info("Nenhum paciente cadastrado.")

  with tab_p2:
    with st.form("form_cad_paciente_flex"):
      c1, c2 = st.columns(2)
      with c1:
        novo_nome_pac = st.text_input("Nome Completo do Paciente")
        tel_pac = st.text_input("Telefone / WhatsApp")
      with c2:
        email_pac = st.text_input("E-mail")

      if st.form_submit_button("Salvar Novo Paciente"):
        if not novo_nome_pac.strip():
          st.error("O nome é obrigatório.")
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
              "Cadastro",
              f"ID: {novo_id_str}, Nome: {novo_nome_pac}",
          )
          st.success(
              f"Paciente cadastrado com sucesso! ID gerado: **{novo_id_str}**"
          )
          st.rerun()

# ---------------------------------------------------------
# 2. MÓDULO: CADASTRO DE PROFISSIONAIS
# ---------------------------------------------------------
elif menu == "Cadastro de Profissionais":
  st.title("👨‍⚕️ Gestão de Profissionais & Regras")
  tab_prof1, tab_prof2 = st.tabs(
      ["📋 Profissionais Ativos", "➕ Cadastrar Novo Profissional"]
  )

  with tab_prof1:
    if not st.session_state.profissionais.empty:
      st.dataframe(st.session_state.profissionais, use_container_width=True)

      st.markdown("### 🗑️ Remover Profissional")
      prof_rem = st.selectbox(
          "Selecione o profissional para remover",
          st.session_state.profissionais["Nome"].tolist(),
      )
      if st.button("Remover Profissional"):
        st.session_state.profissionais = st.session_state.profissionais[
            st.session_state.profissionais["Nome"] != prof_rem
        ]
        registrar_auditoria("Profissionais", "Remoção", f"Nome: {prof_rem}")
        st.success("Profissional removido com sucesso!")
        st.rerun()
    else:
      st.info("Nenhum profissional cadastrado.")

  with tab_prof2:
    with st.form("form_cad_prof_flex"):
      c1, c2 = st.columns(2)
      with c1:
        nome_prof = st.text_input("Nome do Profissional")
        especialidade_prof = st.text_input("Especialidade")
      with c2:
        tipo_atd_prof = st.selectbox(
            "Terminologia de Atendimento", ["Sessão", "Consulta", "Procedimento"]
        )
        perc_clinica = st.number_input(
            "Percentual Devido à Clínica (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=1.0,
        )

      if st.form_submit_button("Salvar Profissional"):
        if not nome_prof.strip():
          st.error("O nome é obrigatório.")
        else:
          novo_id = len(st.session_state.profissionais) + 1
          df_novo_pr = pd.DataFrame([{
              "ID": novo_id,
              "Nome": nome_prof,
              "Especialidade": especialidade_prof,
              "Tipo_Atendimento": tipo_atd_prof,
              "Modalidade": "Produtividade Variável",
              "Percentual_Clinica": perc_clinica,
              "Status": "Ativo",
          }])
          st.session_state.profissionais = pd.concat(
              [st.session_state.profissionais, df_novo_pr], ignore_index=True
          )
          registrar_auditoria(
              "Profissionais", "Cadastro", f"Nome: {nome_prof}"
          )
          st.success("Profissional cadastrado com sucesso!")
          st.rerun()

# ---------------------------------------------------------
# 3. MÓDULO: CADASTRO & GESTÃO DE PACOTES
# ---------------------------------------------------------
elif menu == "Cadastro & Gestão de Pacotes":
  st.title("📦 Cadastro & Gestão de Pacotes Flexíveis")
  profs_prod = st.session_state.profissionais
  pacientes_lista = st.session_state.base_pacientes

  tab_pc1, tab_pc2 = st.tabs(["📋 Pacotes Contratados", "➕ Novo Pacote"])

  with tab_pc1:
    if not st.session_state.pacotes_atendimento.empty:
      st.dataframe(
          st.session_state.pacotes_atendimento, use_container_width=True
      )

      st.markdown("### 🗑️ Cancelar/Remover Pacote")
      pac_del_id = st.selectbox(
          "Selecione o ID do Pacote",
          st.session_state.pacotes_atendimento["ID_Pacote"].tolist(),
      )
      if st.button("Remover Pacote Selecionado"):
        st.session_state.pacotes_atendimento = st.session_state.pacotes_atendimento[
            st.session_state.pacotes_atendimento["ID_Pacote"] != pac_del_id
        ]
        registrar_auditoria("Pacotes", "Exclusão", f"ID Pacote: {pac_del_id}")
        st.success("Pacote removido com sucesso!")
        st.rerun()
    else:
      st.info("Nenhum pacote registrado.")

  with tab_pc2:
    if pacientes_lista.empty or profs_prod.empty:
      st.warning(
          "Cadastre previamente profissionais e pacientes nos respectivos"
          " menus."
      )
    else:
      with st.form("form_cad_pacote_flexivel"):
        c_prof_pac = st.selectbox(
            "Profissional Responsável", profs_prod["Nome"].tolist()
        )
        pacientes_opcoes = (
            pacientes_lista["ID_Paciente"]
            + " - "
            + pacientes_lista["Nome_Completo"]
        ).tolist()
        pac_sel_str = st.selectbox("Selecionar Paciente", pacientes_opcoes)

        id_pac_escolhido = pac_sel_str.split(" - ")[0]
        nome_pac_escolhido = pac_sel_str.split(" - ")[1]

        c1, c2 = st.columns(2)
        with c1:
          total_sessoes = st.number_input(
              "Quantidade de Sessões no Pacote", min_value=1, value=4, step=1
          )
          cat_str = st.text_input(
              "Descrição / Categoria", value="Pacote Personalizado"
          )
        with c2:
          valor_total_pacote = st.number_input(
              "Valor Total do Pacote (R$)", min_value=0.0, value=580.0, step=10.0
          )

        d_prof = profs_prod[profs_prod["Nome"] == c_prof_pac].iloc[0]
        perc_c = float(d_prof["Percentual_Clinica"])
        valor_repasse_total = valor_total_pacote * (perc_c / 100.0)

        if st.form_submit_button("Criar Pacote Flexível"):
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
              "Pacotes", "Cadastro", f"Paciente ID: {id_pac_escolhido}"
          )
          st.success("Pacote criado com sucesso!")
          st.rerun()

# ---------------------------------------------------------
# 4. MÓDULO: LANÇAMENTO DE PRODUTIVIDADE & CONTA CORRENTE
# ---------------------------------------------------------
elif menu == "Lançamento de Produtividade & Conta Corrente":
  st.title("💼 Lançamento de Atendimentos & Conta Corrente")
  profs_prod = st.session_state.profissionais

  if profs_prod.empty:
    st.warning("Cadastre profissionais primeiro.")
  else:
    tab_l1, tab_l2 = st.tabs(
        ["➕ Registrar Atendimento", "📊 Extrato de Conta Corrente"]
    )

    with tab_l1:
      with st.form("form_atendimento_flex"):
        c_prof = st.selectbox(
            "Selecionar Profissional", profs_prod["Nome"].tolist()
        )
        dados_prof_sel = profs_prod[profs_prod["Nome"] == c_prof].iloc[0]
        tipo_atendimento = dados_prof_sel["Tipo_Atendimento"]
        perc_clinica_padrao = float(dados_prof_sel["Percentual_Clinica"])

        tipo_cobranca = st.radio(
            "Modalidade", ["Atendimento Avulso", "Sessão de Pacote Cadastrado"]
        )

        pacientes_lista = st.session_state.base_pacientes
        if pacientes_lista.empty:
          st.error("Cadastre pacientes primeiro.")
          st.stop()

        pacientes_opcoes = (
            pacientes_lista["ID_Paciente"]
            + " - "
            + pacientes_lista["Nome_Completo"]
        ).tolist()
        pac_sel_atd = st.selectbox("Selecione o Paciente", pacientes_opcoes)

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
                "Valor do Atendimento (R$)",
                min_value=0.0,
                value=250.0,
                step=10.0,
            )
            valor_repasse_atd = valor_unit_paciente * (
                perc_clinica_padrao / 100.0
            )
            st.info(f"Repasse Clínica ({perc_clinica_padrao}%): R$ {valor_repasse_atd:,.2f}")
        else:
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
                "⚠️ Este paciente não possui pacotes ativos para este"
                " profissional."
            )
          else:
            pacs_prof["Label_Pacote"] = (
                "Pacote ID #"
                + pacs_prof["ID_Pacote"].astype(str)
                + " ("
                + pacs_prof["Categoria_Opcao"]
                + ")"
            )
            pac_escolhido_label = st.selectbox(
                "Selecione o Pacote", pacs_prof["Label_Pacote"].tolist()
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
            sessao_str = f"{num_sessao_atual:02d}-{total_s_pac:02d}"
            st.info(f"Registrando Sessão {sessao_str}")

            d_atendimento = datetime.date.today()
            h_atendimento = datetime.datetime.now().time()
            valor_repasse_atd = 0.0

        if st.form_submit_button("Salvar Atendimento"):
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
              "Plano_Contas": f"Produtividade - {c_prof}",
              "Registrado_Por": st.session_state.get(
                  "perfil_usuario", "Administrador"
              ),
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
      st.subheader("📊 Extrato de Conta Corrente & Ajustes")
      df_p = st.session_state.atendimentos_produtividade
      if not df_p.empty:
        prof_sel_cc = st.selectbox(
            "Selecionar Profissional para Extrato",
            df_p["Profissional"].unique(),
            key="cc_prof_sel",
        )
        st.dataframe(
            df_p[df_p["Profissional"] == prof_sel_cc], use_container_width=True
        )

        st.markdown("### 🗑️ Excluir Lançamento Indevido")
        id_atd_del = st.selectbox(
            "Selecione o ID do Atendimento",
            df_p[df_p["Profissional"] == prof_sel_cc][
                "ID_Atendimento"
            ].tolist(),
        )
        if st.button("Excluir Lançamento"):
          st.session_state.atendimentos_produtividade = (
              st.session_state.atendimentos_produtividade[
                  st.session_state.atendimentos_produtividade["ID_Atendimento"]
                  != id_atd_del
              ]
          )
          registrar_auditoria(
              "Produtividade", "Exclusão", f"Atendimento ID: {id_atd_del}"
          )
          st.success("Lançamento removido com sucesso!")
          st.rerun()
      else:
        st.info("Nenhum lançamento registrado.")

# ---------------------------------------------------------
# 5. MÓDULO: DASHBOARD GERENCIAL
# ---------------------------------------------------------
elif menu == "Dashboard Gerencial & Relatórios":
  st.title("📊 Dashboard Executivo Dinâmico")
  df_prod = st.session_state.atendimentos_produtividade

  if not df_prod.empty:
    st.markdown("### 🎛️ Filtros do Dashboard")
    prof_filtro = st.multiselect(
        "Filtrar por Profissional",
        df_prod["Profissional"].unique(),
        default=df_prod["Profissional"].unique(),
    )
    df_filtrado = df_prod[df_prod["Profissional"].isin(prof_filtro)]

    if not df_filtrado.empty:
      resumo_prof = (
          df_filtrado.groupby("Profissional")
          .agg(
              Total_Atendimentos=("ID_Atendimento", "count"),
              Repasse_Total_Gerado=("Valor_Repasse_Clinica", "sum"),
          )
          .reset_index()
      )

      col1, col2 = st.columns(2)
      with col1:
        st.metric(
            "Total de Atendimentos Filtrados",
            int(resumo_prof["Total_Atendimentos"].sum()),
        )
      with col2:
        st.metric(
            "Repasse Total Gerado (R$)",
            f"R$ {resumo_prof['Repasse_Total_Gerado'].sum():,.2f}",
        )

      st.markdown("---")
      st.dataframe(resumo_prof, use_container_width=True)
      fig = px.bar(
          resumo_prof,
          x="Profissional",
          y="Repasse_Total_Gerado",
          title="Repasse Total por Profissional (R$)",
          text_auto=".2f",
      )
      st.plotly_chart(fig, use_container_width=True)
    else:
      st.warning("Nenhum dado encontrado para os filtros selecionados.")
  else:
    st.info("Sem dados de atendimentos registrados no momento.")

# ---------------------------------------------------------
# 6. MÓDULO: GESTÃO DE USUÁRIOS E PERMISSÕES
# ---------------------------------------------------------
elif menu == "Gestão de Usuários e Permissões":
  st.title("👥 Gestão de Usuários & Acessos")
  tab_u1, tab_u2 = st.tabs(["📋 Usuários Cadastrados", "➕ Novo Usuário"])

  with tab_u1:
    st.dataframe(st.session_state.usuarios_sistema, use_container_width=True)

    st.markdown("### 🗑️ Remover Usuário")
    user_rem = st.selectbox(
        "Selecione o usuário para remover",
        st.session_state.usuarios_sistema["Nome"].tolist(),
    )
    if st.button("Remover Usuário"):
      if len(st.session_state.usuarios_sistema) <= 1:
        st.error("Você não pode remover o último usuário do sistema.")
      else:
        st.session_state.usuarios_sistema = st.session_state.usuarios_sistema[
            st.session_state.usuarios_sistema["Nome"] != user_rem
        ]
        registrar_auditoria("Usuários", "Exclusão", f"Nome: {user_rem}")
        st.success("Usuário removido com sucesso!")
        st.rerun()

  with tab_u2:
    with st.form("form_cad_usuario"):
      c1, c2 = st.columns(2)
      with c1:
        nome_u = st.text_input("Nome do Usuário")
        email_u = st.text_input("E-mail Profissional")
      with c2:
        perfil_u = st.selectbox(
            "Perfil de Acesso", ["Administrador", "Recepcionista"]
        )

      if st.form_submit_button("Salvar Novo Usuário"):
        if not nome_u.strip():
          st.error("O nome é obrigatório.")
        else:
          prox_id = f"USER-{len(st.session_state.usuarios_sistema) + 1:03d}"
          df_nu = pd.DataFrame([{
              "ID_Usuario": prox_id,
              "Nome": nome_u,
              "Email": email_u,
              "Perfil": perfil_u,
              "Status": "Ativo",
          }])
          st.session_state.usuarios_sistema = pd.concat(
              [st.session_state.usuarios_sistema, df_nu], ignore_index=True
          )
          registrar_auditoria("Usuários", "Cadastro", f"Nome: {nome_u}")
          st.success("Usuário cadastrado com sucesso!")
          st.rerun()

# ---------------------------------------------------------
# 7. MÓDULO: AUDITORIA DO SISTEMA
# ---------------------------------------------------------
elif menu == "Auditoria do Sistema":
  st.title("🕵️ Trilha de Auditoria & Logs")

  if not st.session_state.audit_log.empty:
    st.dataframe(
        st.session_state.audit_log.sort_index(ascending=False),
        use_container_width=True,
    )

    if st.button("🧹 Limpar Histórico de Auditoria"):
      st.session_state.audit_log = pd.DataFrame(columns=[
          "Timestamp",
          "Usuario",
          "Modulo",
          "Acao",
          "Detalhes",
      ])
      st.success("Logs limpos com sucesso!")
      st.rerun()
  else:
    st.info("Nenhum log de auditoria registrado até o momento.")
