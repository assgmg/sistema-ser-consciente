def init_db():
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

  # Garante compatibilidade adicionando colunas se a tabela for antiga
  try:
    cursor.execute("ALTER TABLE atendimentos ADD COLUMN status TEXT DEFAULT 'Ativo'")
  except sqlite3.OperationalError:
    pass

  try:
    cursor.execute("ALTER TABLE atendimentos ADD COLUMN consolidado INTEGER DEFAULT 0")
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
