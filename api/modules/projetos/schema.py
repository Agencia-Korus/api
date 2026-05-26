from datetime import date, datetime

from core.constants import (
	PROGRESSO_MAXIMO,
	PROGRESSO_MINIMO,
	TAMANHO_MAXIMO_PAPEL,
	TAMANHO_MAXIMO_TITULO,
)
from core.enums import SituacaoProjeto
from pydantic import BaseModel, ConfigDict, Field


class ProjetoBase(BaseModel):
	"""Classe que define os dados de projeto usados pela API."""

	nome: str = Field(max_length=TAMANHO_MAXIMO_TITULO)
	descricao: str | None = None
	cliente_id: int
	servico_id: int | None = None
	data_inicio: date | None = None
	data_fim: date | None = None


class ProjetoCriar(ProjetoBase):
	"""Classe que define os dados de projeto usados pela API."""

	status: SituacaoProjeto = SituacaoProjeto.PLANEJAMENTO
	progresso: int = Field(
		default=PROGRESSO_MINIMO, ge=PROGRESSO_MINIMO, le=PROGRESSO_MAXIMO
	)

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'nome': 'Redesign do site institucional',
				'descricao': 'Atualização visual e técnica do site.',
				'cliente_id': 1,
				'servico_id': 2,
				'data_inicio': '2026-05-01',
				'data_fim': '2026-07-15',
				'status': 'planejamento',
				'progresso': 0,
			}
		}
	)


class ProjetoAtualizar(BaseModel):
	"""Classe que define os dados de projeto usados pela API."""

	nome: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_TITULO)
	descricao: str | None = None
	servico_id: int | None = None
	data_inicio: date | None = None
	data_fim: date | None = None
	status: SituacaoProjeto | None = None
	progresso: int | None = Field(
		default=None, ge=PROGRESSO_MINIMO, le=PROGRESSO_MAXIMO
	)

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'status': 'em_andamento',
				'progresso': 45,
				'data_fim': '2026-07-30',
			}
		}
	)


class ProjetoResposta(ProjetoBase):
	"""Classe que define os dados de projeto usados pela API."""

	id: int
	status: SituacaoProjeto
	progresso: int
	criado_em: datetime
	model_config = ConfigDict(from_attributes=True)


class ProjetoFuncionarioCriar(BaseModel):
	"""Classe que define os dados de membro do projeto usados pela API."""

	funcionario_id: int
	papel: str | None = Field(default=None, max_length=TAMANHO_MAXIMO_PAPEL)

	model_config = ConfigDict(
		json_schema_extra={
			'example': {
				'funcionario_id': 2,
				'papel': 'Designer responsável',
			}
		}
	)


class ProjetoFuncionarioResposta(BaseModel):
	"""Classe que define os dados de membro do projeto usados pela API."""

	projeto_id: int
	funcionario_id: int
	papel: str | None
	data_entrada: date
	model_config = ConfigDict(from_attributes=True)
