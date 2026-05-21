from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.deps import PaginationDep, SessionDep
from core.enums import UserRole, UserStatus
from core.security import require_role
from modules.users.schema import (
    UsuarioCreate,
    UsuarioRegister,
    UsuarioResponse,
    UsuarioUpdate
)
from modules.users.service import UsuarioService

router = APIRouter(prefix='/usuarios', tags=['Usuários'])
