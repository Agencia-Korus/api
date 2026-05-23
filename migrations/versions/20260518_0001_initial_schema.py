"""Initial Korus schema and bootstrap admin.

Revision ID: 20260518_0001
Revises:
Create Date: 2026-05-18
"""

from collections.abc import Sequence

from alembic import op

revision: str = '20260518_0001'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ADMIN_EMAIL = 'admin@email.com'
ADMIN_NOME = 'Admin Korus'
ADMIN_SENHA_HASH = (
	'$2b$12$lURftWrAQLj8Rc3NwqLFq.YPR9F8nLI9FLgnpUT/fZGD/U/uMbFLa'
)
ADMIN_NIVEL_ACESSO = 5


UPGRADE_STATEMENTS: tuple[str, ...] = (
	"""CREATE EXTENSION IF NOT EXISTS "pgcrypto";""",
	"""CREATE EXTENSION IF NOT EXISTS "citext";""",
	"""CREATE TYPE user_role         AS ENUM ('cliente', 'funcionario', 'admin');""",
	"""CREATE TYPE user_status       AS ENUM ('ativo', 'inativo', 'pendente');""",
	"""CREATE TYPE servico_status    AS ENUM ('ativo', 'inativo');""",
	"""CREATE TYPE academy_tipo      AS ENUM ('ebook', 'curso');""",
	"""CREATE TYPE lead_status       AS ENUM ('novo', 'em_contato', 'qualificado', 'convertido', 'perdido');""",
	"""CREATE TYPE lead_prioridade   AS ENUM ('baixa', 'media', 'alta');""",
	"""CREATE TYPE projeto_status    AS ENUM ('planejamento', 'em_andamento', 'em_revisao', 'concluido', 'pausado');""",
	"""CREATE TYPE tarefa_status     AS ENUM ('a_fazer', 'em_progresso', 'em_revisao', 'concluido');""",
	"""CREATE TYPE complexidade      AS ENUM ('baixa', 'media', 'alta', 'critica');""",
	"""CREATE TYPE prioridade        AS ENUM ('baixa', 'media', 'alta');""",
	"""CREATE TYPE comunicado_alvo   AS ENUM ('todos', 'funcionarios', 'clientes', 'admins');""",
	"""CREATE TYPE evento_tipo       AS ENUM ('reuniao', 'entrega', 'tarefa', 'pessoal');""",
	"""CREATE TYPE solicitacao_status AS ENUM ('pendente', 'aceita', 'recusada', 'cancelada');""",
	"""CREATE TYPE consentimento_tipo AS ENUM ('essencial', 'analytics', 'marketing');""",
	"""CREATE TYPE integracao_status AS ENUM ('conectado', 'desconectado');""",
	"""CREATE TABLE usuario (
  id            BIGSERIAL PRIMARY KEY,
  nome          VARCHAR(150) NOT NULL,
  email         CITEXT       NOT NULL UNIQUE,
  senha_hash    VARCHAR(255) NOT NULL,
  role          user_role    NOT NULL,
  avatar        VARCHAR(500),
  telefone      VARCHAR(20),
  status        user_status  NOT NULL DEFAULT 'ativo',
  criado_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  atualizado_em TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_usuario_role ON usuario(role);""",
	"""CREATE TABLE cliente (
  id           BIGINT PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
  razao_social VARCHAR(200) NOT NULL,
  cnpj_cpf     VARCHAR(20)  NOT NULL UNIQUE,
  segmento     VARCHAR(100)
);""",
	"""CREATE TABLE funcionario (
  id            BIGINT PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
  cargo         VARCHAR(100) NOT NULL,
  especialidade VARCHAR(100),
  data_admissao DATE         NOT NULL DEFAULT CURRENT_DATE,
  xp_total      INTEGER      NOT NULL DEFAULT 0,
  nivel         INTEGER      NOT NULL DEFAULT 1
);""",
	"""CREATE TABLE admin (
  id            BIGINT PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
  nivel_acesso  SMALLINT NOT NULL DEFAULT 1,
  data_promocao DATE     NOT NULL DEFAULT CURRENT_DATE
);""",
	"""CREATE TABLE servico (
  id        BIGSERIAL PRIMARY KEY,
  nome      VARCHAR(150) NOT NULL,
  slug      VARCHAR(150) NOT NULL UNIQUE,
  descricao TEXT,
  icone     VARCHAR(50),
  status    servico_status NOT NULL DEFAULT 'ativo',
  criado_em TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);""",
	"""CREATE TABLE entregavel (
  id         BIGSERIAL PRIMARY KEY,
  servico_id BIGINT NOT NULL REFERENCES servico(id) ON DELETE CASCADE,
  descricao  VARCHAR(255) NOT NULL,
  ordem      SMALLINT NOT NULL DEFAULT 0
);""",
	"""CREATE INDEX idx_entregavel_servico ON entregavel(servico_id);""",
	"""CREATE TABLE lead (
  id         BIGSERIAL PRIMARY KEY,
  servico_id BIGINT REFERENCES servico(id) ON DELETE SET NULL,
  nome       VARCHAR(150) NOT NULL,
  email      CITEXT       NOT NULL,
  whatsapp   VARCHAR(20),
  empresa    VARCHAR(200),
  orcamento  VARCHAR(50),
  prazo_desejado DATE,
  termos_aceitos BOOLEAN NOT NULL DEFAULT FALSE,
  status     lead_status     NOT NULL DEFAULT 'novo',
  prioridade lead_prioridade NOT NULL DEFAULT 'media',
  mensagem   TEXT,
  data       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_lead_status  ON lead(status);""",
	"""CREATE INDEX idx_lead_servico ON lead(servico_id);""",
	"""CREATE TABLE projeto (
  id          BIGSERIAL PRIMARY KEY,
  cliente_id  BIGINT NOT NULL REFERENCES cliente(id) ON DELETE RESTRICT,
  servico_id  BIGINT REFERENCES servico(id) ON DELETE SET NULL,
  nome        VARCHAR(200) NOT NULL,
  descricao   TEXT,
  status      projeto_status NOT NULL DEFAULT 'planejamento',
  progresso   SMALLINT NOT NULL DEFAULT 0 CHECK (progresso BETWEEN 0 AND 100),
  data_inicio DATE,
  data_fim    DATE,
  criado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_projeto_cliente ON projeto(cliente_id);""",
	"""CREATE INDEX idx_projeto_status  ON projeto(status);""",
	"""CREATE TABLE projeto_funcionario (
  projeto_id     BIGINT NOT NULL REFERENCES projeto(id)     ON DELETE CASCADE,
  funcionario_id BIGINT NOT NULL REFERENCES funcionario(id) ON DELETE CASCADE,
  papel          VARCHAR(80),
  data_entrada   DATE NOT NULL DEFAULT CURRENT_DATE,
  PRIMARY KEY (projeto_id, funcionario_id)
);""",
	"""CREATE TABLE tarefa (
  id             BIGSERIAL PRIMARY KEY,
  projeto_id     BIGINT NOT NULL REFERENCES projeto(id)    ON DELETE CASCADE,
  responsavel_id BIGINT REFERENCES funcionario(id)         ON DELETE SET NULL,
  titulo         VARCHAR(200) NOT NULL,
  descricao      TEXT,
  status         tarefa_status NOT NULL DEFAULT 'a_fazer',
  complexidade   complexidade  NOT NULL DEFAULT 'media',
  prioridade     prioridade    NOT NULL DEFAULT 'media',
  categoria      VARCHAR(80),
  prazo          DATE,
  ordem          INTEGER NOT NULL DEFAULT 0,
  criado_em      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  concluido_em   TIMESTAMPTZ
);""",
	"""CREATE INDEX idx_tarefa_projeto     ON tarefa(projeto_id);""",
	"""CREATE INDEX idx_tarefa_responsavel ON tarefa(responsavel_id);""",
	"""CREATE INDEX idx_tarefa_status      ON tarefa(status);""",
	"""CREATE TABLE comentario (
  id        BIGSERIAL PRIMARY KEY,
  tarefa_id BIGINT NOT NULL REFERENCES tarefa(id)  ON DELETE CASCADE,
  autor_id  BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  conteudo  TEXT NOT NULL,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_comentario_tarefa ON comentario(tarefa_id);""",
	"""CREATE TABLE anexo (
  id        BIGSERIAL PRIMARY KEY,
  tarefa_id BIGINT NOT NULL REFERENCES tarefa(id) ON DELETE CASCADE,
  nome      VARCHAR(200) NOT NULL,
  url       VARCHAR(500) NOT NULL,
  tipo      VARCHAR(50),
  tamanho   INTEGER,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_anexo_tarefa ON anexo(tarefa_id);""",
	"""CREATE TABLE portfolio (
  id         BIGSERIAL PRIMARY KEY,
  projeto_id BIGINT REFERENCES projeto(id) ON DELETE SET NULL,
  nome       VARCHAR(200) NOT NULL,
  cliente    VARCHAR(150),
  categoria  VARCHAR(100),
  descricao  TEXT,
  imagem     VARCHAR(500),
  ano        SMALLINT,
  destaque   BOOLEAN NOT NULL DEFAULT FALSE,
  tags       TEXT[] NOT NULL DEFAULT '{}',
  criado_em  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_portfolio_destaque ON portfolio(destaque) WHERE destaque = TRUE;""",
	"""CREATE TABLE academy (
  id          BIGSERIAL PRIMARY KEY,
  titulo      VARCHAR(200) NOT NULL,
  tipo        academy_tipo NOT NULL,
  descricao   TEXT,
  preco       NUMERIC(10,2) NOT NULL DEFAULT 0,
  imagem      VARCHAR(500),
  url_externa VARCHAR(500) NOT NULL,
  publicado   BOOLEAN NOT NULL DEFAULT FALSE,
  criado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_academy_publicado ON academy(publicado);""",
	"""CREATE TABLE comunicado (
  id       BIGSERIAL PRIMARY KEY,
  autor_id BIGINT NOT NULL REFERENCES admin(id) ON DELETE RESTRICT,
  titulo   VARCHAR(200) NOT NULL,
  conteudo TEXT NOT NULL,
  alvo     comunicado_alvo NOT NULL DEFAULT 'todos',
  data     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_comunicado_alvo ON comunicado(alvo);""",
	"""CREATE TABLE comunicado_leitura (
  comunicado_id BIGINT NOT NULL REFERENCES comunicado(id) ON DELETE CASCADE,
  usuario_id    BIGINT NOT NULL REFERENCES usuario(id)    ON DELETE CASCADE,
  lido_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (comunicado_id, usuario_id)
);""",
	"""CREATE TABLE evento_agenda (
  id          BIGSERIAL PRIMARY KEY,
  usuario_id  BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  titulo      VARCHAR(200) NOT NULL,
  descricao   TEXT,
  tipo        evento_tipo NOT NULL DEFAULT 'reuniao',
  data        DATE NOT NULL,
  hora        TIME,
  duracao_min INTEGER NOT NULL DEFAULT 60,
  criado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_evento_usuario_data ON evento_agenda(usuario_id, data);""",
	"""CREATE TABLE solicitacao_reuniao (
  id              BIGSERIAL PRIMARY KEY,
  remetente_id    BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  destinatario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  titulo          VARCHAR(200) NOT NULL,
  mensagem        TEXT,
  data            DATE NOT NULL,
  hora            TIME NOT NULL,
  status          solicitacao_status NOT NULL DEFAULT 'pendente',
  criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (remetente_id <> destinatario_id)
);""",
	"""CREATE INDEX idx_solicitacao_destinatario ON solicitacao_reuniao(destinatario_id, status);""",
	"""CREATE TABLE regra_xp (
  id           BIGSERIAL PRIMARY KEY,
  tarefa       VARCHAR(150) NOT NULL,
  complexidade complexidade NOT NULL,
  xp           INTEGER NOT NULL CHECK (xp >= 0)
);""",
	"""CREATE TABLE historico_xp (
  id             BIGSERIAL PRIMARY KEY,
  funcionario_id BIGINT NOT NULL REFERENCES funcionario(id) ON DELETE CASCADE,
  tarefa_id      BIGINT REFERENCES tarefa(id)              ON DELETE SET NULL,
  regra_id       BIGINT REFERENCES regra_xp(id)            ON DELETE SET NULL,
  acao           VARCHAR(150) NOT NULL,
  xp             INTEGER NOT NULL,
  data           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_historico_funcionario ON historico_xp(funcionario_id, data DESC);""",
	"""CREATE TABLE conquista (
  id        BIGSERIAL PRIMARY KEY,
  nome      VARCHAR(150) NOT NULL,
  icone     VARCHAR(50),
  descricao TEXT,
  xp_bonus  INTEGER NOT NULL DEFAULT 0
);""",
	"""CREATE TABLE funcionario_conquista (
  funcionario_id  BIGINT NOT NULL REFERENCES funcionario(id) ON DELETE CASCADE,
  conquista_id    BIGINT NOT NULL REFERENCES conquista(id)   ON DELETE CASCADE,
  desbloqueado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (funcionario_id, conquista_id)
);""",
	"""CREATE TABLE consentimento_lgpd (
  id         BIGSERIAL PRIMARY KEY,
  usuario_id BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  tipo       consentimento_tipo NOT NULL,
  aceito     BOOLEAN NOT NULL,
  ip         INET,
  user_agent VARCHAR(255),
  data       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE INDEX idx_consentimento_usuario ON consentimento_lgpd(usuario_id);""",
	"""CREATE TABLE integracao (
  id            BIGSERIAL PRIMARY KEY,
  nome          VARCHAR(100) NOT NULL UNIQUE,
  chave         VARCHAR(255),
  status        integracao_status NOT NULL DEFAULT 'desconectado',
  atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
	"""CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.atualizado_em = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;""",
	"""CREATE TRIGGER trg_usuario_updated
  BEFORE UPDATE ON usuario
  FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();""",
	"""INSERT INTO servico (nome, slug, descricao, icone) VALUES
  ('Identidade Visual',   'identidade-visual',   'Branding completo da sua marca.', 'palette'),
  ('Tráfego Pago',        'trafego-pago',        'Campanhas Meta/Google Ads.',      'megaphone'),
  ('Social Media',        'social-media',        'Gestão de redes sociais.',        'instagram'),
  ('Desenvolvimento Web', 'desenvolvimento-web', 'Sites e sistemas sob medida.',    'code');""",
	"""INSERT INTO regra_xp (tarefa, complexidade, xp) VALUES
  ('Comentar em card',           'baixa',   5),
  ('Concluir card de design',    'media',   25),
  ('Entregar projeto completo',  'alta',    50),
  ('Lançar campanha integrada',  'critica', 100);""",
	f"""INSERT INTO usuario (nome, email, senha_hash, role, status)
VALUES (
  '{ADMIN_NOME}',
  '{ADMIN_EMAIL}',
  '{ADMIN_SENHA_HASH}',
  'admin',
  'ativo'
)
ON CONFLICT (email) DO UPDATE SET
  role = 'admin',
  status = 'ativo';""",
	f"""INSERT INTO admin (id, nivel_acesso)
SELECT id, {ADMIN_NIVEL_ACESSO} FROM usuario WHERE email = '{ADMIN_EMAIL}'
ON CONFLICT (id) DO UPDATE SET nivel_acesso = EXCLUDED.nivel_acesso;""",
	"""INSERT INTO integracao (nome, status) VALUES
  ('google_calendar', 'desconectado')
ON CONFLICT (nome) DO NOTHING;""",
)


DOWNGRADE_STATEMENTS: tuple[str, ...] = (
	"""DROP TRIGGER IF EXISTS trg_usuario_updated ON usuario;""",
	"""DROP FUNCTION IF EXISTS fn_set_updated_at();""",
	"""DROP TABLE IF EXISTS integracao CASCADE;""",
	"""DROP TABLE IF EXISTS consentimento_lgpd CASCADE;""",
	"""DROP TABLE IF EXISTS funcionario_conquista CASCADE;""",
	"""DROP TABLE IF EXISTS conquista CASCADE;""",
	"""DROP TABLE IF EXISTS historico_xp CASCADE;""",
	"""DROP TABLE IF EXISTS regra_xp CASCADE;""",
	"""DROP TABLE IF EXISTS solicitacao_reuniao CASCADE;""",
	"""DROP TABLE IF EXISTS evento_agenda CASCADE;""",
	"""DROP TABLE IF EXISTS comunicado_leitura CASCADE;""",
	"""DROP TABLE IF EXISTS comunicado CASCADE;""",
	"""DROP TABLE IF EXISTS academy CASCADE;""",
	"""DROP TABLE IF EXISTS portfolio CASCADE;""",
	"""DROP TABLE IF EXISTS anexo CASCADE;""",
	"""DROP TABLE IF EXISTS comentario CASCADE;""",
	"""DROP TABLE IF EXISTS tarefa CASCADE;""",
	"""DROP TABLE IF EXISTS projeto_funcionario CASCADE;""",
	"""DROP TABLE IF EXISTS projeto CASCADE;""",
	"""DROP TABLE IF EXISTS lead CASCADE;""",
	"""DROP TABLE IF EXISTS entregavel CASCADE;""",
	"""DROP TABLE IF EXISTS servico CASCADE;""",
	"""DROP TABLE IF EXISTS admin CASCADE;""",
	"""DROP TABLE IF EXISTS funcionario CASCADE;""",
	"""DROP TABLE IF EXISTS cliente CASCADE;""",
	"""DROP TABLE IF EXISTS usuario CASCADE;""",
	"""DROP TYPE IF EXISTS integracao_status;""",
	"""DROP TYPE IF EXISTS consentimento_tipo;""",
	"""DROP TYPE IF EXISTS solicitacao_status;""",
	"""DROP TYPE IF EXISTS evento_tipo;""",
	"""DROP TYPE IF EXISTS comunicado_alvo;""",
	"""DROP TYPE IF EXISTS prioridade;""",
	"""DROP TYPE IF EXISTS complexidade;""",
	"""DROP TYPE IF EXISTS tarefa_status;""",
	"""DROP TYPE IF EXISTS projeto_status;""",
	"""DROP TYPE IF EXISTS lead_prioridade;""",
	"""DROP TYPE IF EXISTS lead_status;""",
	"""DROP TYPE IF EXISTS academy_tipo;""",
	"""DROP TYPE IF EXISTS servico_status;""",
	"""DROP TYPE IF EXISTS user_status;""",
	"""DROP TYPE IF EXISTS user_role;""",
)


def upgrade() -> None:
	for stmt in UPGRADE_STATEMENTS:
		op.execute(stmt)


def downgrade() -> None:
	for stmt in DOWNGRADE_STATEMENTS:
		op.execute(stmt)
