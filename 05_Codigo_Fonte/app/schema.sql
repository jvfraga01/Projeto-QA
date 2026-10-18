PRAGMA foreign_keys = ON;

-- 1) Pessoa + login (usuário e colaborador são a mesma entidade).
--    Nunca é apagada: desabilitar = status 'Inativo' (preserva o histórico da folha).
CREATE TABLE IF NOT EXISTS colaborador (
    matricula               INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                    TEXT    NOT NULL CHECK (length(trim(nome)) > 0),
    data_nascimento         TEXT    NOT NULL,
    data_cadastro           TEXT    NOT NULL DEFAULT (date('now')),
    data_inicio_contrato    TEXT    NOT NULL,
    data_fim_contrato       TEXT,                       -- NULL = contrato ativo
    nivel_acesso            INTEGER NOT NULL CHECK (nivel_acesso IN (1,2,3)), -- 1 Admin/RH, 2 Financeiro, 3 Comum
    status                  TEXT    NOT NULL DEFAULT 'Ativo' CHECK (status IN ('Ativo','Inativo')),
    senha_hash              TEXT    NOT NULL,
    tipo                    TEXT    NOT NULL CHECK (tipo IN ('PADRAO','COMISSIONADO','PRODUCAO')),
    salario_base_centavos   INTEGER NOT NULL CHECK (salario_base_centavos >= 0),
    percentual_comissao_bp  INTEGER NOT NULL DEFAULT 0 CHECK (percentual_comissao_bp >= 0), -- 5,50% = 550
    valor_unidade_centavos  INTEGER NOT NULL DEFAULT 0 CHECK (valor_unidade_centavos >= 0),
    CHECK (data_fim_contrato IS NULL OR data_fim_contrato >= data_inicio_contrato)
);

-- 2) Mês da folha. Fechado = congelado (não reabre).
CREATE TABLE IF NOT EXISTS periodo (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ano     INTEGER NOT NULL,
    mes     INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    status  TEXT    NOT NULL DEFAULT 'ABERTO' CHECK (status IN ('ABERTO','FECHADO')),
    UNIQUE (ano, mes)
);

-- 3) Folha de cada colaborador em cada mês: guarda os valores daquele momento (fotografia).
CREATE TABLE IF NOT EXISTS folha (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    periodo_id              INTEGER NOT NULL REFERENCES periodo(id),
    matricula               INTEGER NOT NULL REFERENCES colaborador(matricula),
    nome                    TEXT    NOT NULL,
    tipo                    TEXT    NOT NULL,
    salario_base_centavos   INTEGER NOT NULL CHECK (salario_base_centavos >= 0),
    percentual_comissao_bp  INTEGER NOT NULL DEFAULT 0,   -- comissão base cadastrada
    valor_unidade_centavos  INTEGER NOT NULL DEFAULT 0,
    meta                    INTEGER NOT NULL DEFAULT 0,   -- centavos (vendas) ou unidades (produção)
    vendas_centavos         INTEGER NOT NULL DEFAULT 0 CHECK (vendas_centavos >= 0),
    quantidade_produzida    INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_produzida >= 0),
    meta_atingida           INTEGER NOT NULL DEFAULT 0,
    percentual_aplicado_bp  INTEGER NOT NULL DEFAULT 0,   -- % final (comissão) ou bônus (produção)
    adicionais_centavos     INTEGER NOT NULL DEFAULT 0 CHECK (adicionais_centavos >= 0),
    total_centavos          INTEGER NOT NULL,
    UNIQUE (periodo_id, matricula),
    CHECK (total_centavos = salario_base_centavos + adicionais_centavos)
);

-- Folha de período fechado não muda nem some, nem pelo banco.
CREATE TRIGGER IF NOT EXISTS folha_fechada_no_update BEFORE UPDATE ON folha
WHEN (SELECT status FROM periodo WHERE id = OLD.periodo_id) = 'FECHADO'
BEGIN SELECT RAISE(ABORT, 'Folha fechada não pode ser alterada'); END;

CREATE TRIGGER IF NOT EXISTS folha_fechada_no_delete BEFORE DELETE ON folha
WHEN (SELECT status FROM periodo WHERE id = OLD.periodo_id) = 'FECHADO'
BEGIN SELECT RAISE(ABORT, 'Folha fechada não pode ser apagada'); END;
