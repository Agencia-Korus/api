from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import UserRole, UserStatus
from core.exceptions import BadRequestError, ConflictError, NotFoundError
from core.password  import hash_password
from modules.users.model import Admin, Cliente, Funcionario, Usuario
