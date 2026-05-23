from enum import Enum
from typing import Iterable


def enum_values(cls: type[Enum]) -> Iterable[str]:
	return [member.value for member in cls]


class UserRole(str, Enum):
	CLIENTE = 'cliente'
	FUNCIONARIO = 'funcionario'
	ADMIN = 'admin'


class UserStatus(str, Enum):
	ATIVO = 'ativo'
	INATIVO = 'inativo'
	PENDENTE = 'pendente'


class ServicoStatus(str, Enum):
	ATIVO = 'ativo'
	INATIVO = 'inativo'


class AcademyTipo(str, Enum):
	EBOOK = 'ebook'
	CURSO = 'curso'


class LeadStatus(str, Enum):
	NOVO = 'novo'
	EM_CONTATO = 'em_contato'
	QUALIFICADO = 'qualificado'
	CONVERTIDO = 'convertido'
	PERDIDO = 'perdido'


class LeadPrioridade(str, Enum):
	BAIXA = 'baixa'
	MEDIA = 'media'
	ALTA = 'alta'


class ProjetoStatus(str, Enum):
	PLANEJAMENTO = 'planejamento'
	EM_ANDAMENTO = 'em_andamento'
	EM_REVISAO = 'em_revisao'
	CONCLUIDO = 'concluido'
	PAUSADO = 'pausado'


class TarefaStatus(str, Enum):
	A_FAZER = 'a_fazer'
	EM_PROGRESSO = 'em_progresso'
	EM_REVISAO = 'em_revisao'
	CONCLUIDO = 'concluido'


class Complexidade(str, Enum):
	BAIXA = 'baixa'
	MEDIA = 'media'
	ALTA = 'alta'
	CRITICA = 'critica'


class Prioridade(str, Enum):
	BAIXA = 'baixa'
	MEDIA = 'media'
	ALTA = 'alta'


class ComunicadoAlvo(str, Enum):
	TODOS = 'todos'
	FUNCIONARIOS = 'funcionarios'
	CLIENTES = 'clientes'
	ADMINS = 'admins'


class EventoTipo(str, Enum):
	REUNIAO = 'reuniao'
	ENTREGA = 'entrega'
	TAREFA = 'tarefa'
	PESSOAL = 'pessoal'


class SolicitacaoStatus(str, Enum):
	PENDENTE = 'pendente'
	ACEITA = 'aceita'
	RECUSADA = 'recusada'
	CANCELADA = 'cancelada'


class ConsentimentoTipo(str, Enum):
	ESSENCIAL = 'essencial'
	ANALYTICS = 'analytics'
	MARKETING = 'marketing'


class IntegracaoStatus(str, Enum):
	CONECTADO = 'conectado'
	DESCONECTADO = 'desconectado'
