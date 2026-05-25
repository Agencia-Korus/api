from enum import Enum
from typing import Iterable


def enum_values(cls: type[Enum]) -> Iterable[str]:
	"""Função para listar os valores textuais de uma enumeração."""
	return [member.value for member in cls]


class UserRole(str, Enum):
	"""Enumeração com os valores permitidos para user role."""

	CLIENTE = 'cliente'
	FUNCIONARIO = 'funcionario'
	ADMIN = 'admin'


class UserStatus(str, Enum):
	"""Enumeração com os valores permitidos para user status."""

	ATIVO = 'ativo'
	INATIVO = 'inativo'
	PENDENTE = 'pendente'


class ServicoStatus(str, Enum):
	"""Enumeração com os valores permitidos para servico status."""

	ATIVO = 'ativo'
	INATIVO = 'inativo'


class AcademyTipo(str, Enum):
	"""Enumeração com os valores permitidos para academy tipo."""

	EBOOK = 'ebook'
	CURSO = 'curso'


class LeadStatus(str, Enum):
	"""Enumeração com os valores permitidos para lead status."""

	NOVO = 'novo'
	EM_CONTATO = 'em_contato'
	QUALIFICADO = 'qualificado'
	CONVERTIDO = 'convertido'
	PERDIDO = 'perdido'


class LeadPrioridade(str, Enum):
	"""Enumeração com os valores permitidos para lead prioridade."""

	BAIXA = 'baixa'
	MEDIA = 'media'
	ALTA = 'alta'


class ProjetoStatus(str, Enum):
	"""Enumeração com os valores permitidos para projeto status."""

	PLANEJAMENTO = 'planejamento'
	EM_ANDAMENTO = 'em_andamento'
	EM_REVISAO = 'em_revisao'
	CONCLUIDO = 'concluido'
	PAUSADO = 'pausado'


class TarefaStatus(str, Enum):
	"""Enumeração com os valores permitidos para tarefa status."""

	A_FAZER = 'a_fazer'
	EM_PROGRESSO = 'em_progresso'
	EM_REVISAO = 'em_revisao'
	CONCLUIDO = 'concluido'


class Complexidade(str, Enum):
	"""Enumeração com os valores permitidos para complexidade."""

	BAIXA = 'baixa'
	MEDIA = 'media'
	ALTA = 'alta'
	CRITICA = 'critica'


class Prioridade(str, Enum):
	"""Enumeração com os valores permitidos para prioridade."""

	BAIXA = 'baixa'
	MEDIA = 'media'
	ALTA = 'alta'


class ComunicadoAlvo(str, Enum):
	"""Enumeração com os valores permitidos para comunicado alvo."""

	TODOS = 'todos'
	FUNCIONARIOS = 'funcionarios'
	CLIENTES = 'clientes'
	ADMINS = 'admins'


class EventoTipo(str, Enum):
	"""Enumeração com os valores permitidos para evento tipo."""

	REUNIAO = 'reuniao'
	ENTREGA = 'entrega'
	TAREFA = 'tarefa'
	PESSOAL = 'pessoal'


class SolicitacaoStatus(str, Enum):
	"""Enumeração com os valores permitidos para solicitacao status."""

	PENDENTE = 'pendente'
	ACEITA = 'aceita'
	RECUSADA = 'recusada'
	CANCELADA = 'cancelada'


class ConsentimentoTipo(str, Enum):
	"""Enumeração com os valores permitidos para consentimento tipo."""

	ESSENCIAL = 'essencial'
	ANALYTICS = 'analytics'
	MARKETING = 'marketing'


class IntegracaoStatus(str, Enum):
	"""Enumeração com os valores permitidos para integracao status."""

	CONECTADO = 'conectado'
	DESCONECTADO = 'desconectado'
