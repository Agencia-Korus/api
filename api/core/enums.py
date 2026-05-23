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
	RASCUNHO = 'rascunho'


class LeadStatus(str, Enum):
	NOVO = 'novo'
	CONTATO = 'contato'
	PROPOSTA = 'proposta'
	GANHO = 'ganho'
	PERDIDO = 'perdido'


class LeadPrioridade(str, Enum):
	BAIXA = 'baixa'
	MEDIA = 'media'
	ALTA = 'alta'
