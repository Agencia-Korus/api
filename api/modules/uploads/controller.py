from typing import Annotated

from core.security import UsuarioAtual, obter_usuario_atual
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from modules.uploads.schema import UploadResposta
from modules.uploads.service import ServicoUpload

router = APIRouter(prefix='/uploads', tags=['Uploads'])


def _servico() -> ServicoUpload:
	"""Função para criar o serviço de upload."""
	return ServicoUpload()


DependenciaServico = Annotated[ServicoUpload, Depends(_servico)]
DependenciaUsuario = Annotated[UsuarioAtual, Depends(obter_usuario_atual)]


@router.post('/imagem', response_model=UploadResposta, status_code=status.HTTP_201_CREATED)
async def enviar_imagem(
	servico: DependenciaServico,
	_usuario: DependenciaUsuario,
	file: Annotated[UploadFile, File(description='Arquivo de imagem (até 5MB).')],
	folder: Annotated[str, Form(description='Pasta destino: avatars, portfolio ou academy.')] = 'avatars',
):
	"""Envia uma imagem ao storage e retorna a URL pública (requer login)."""
	url = await servico.enviar_imagem(file, folder)
	return UploadResposta(url=url)
