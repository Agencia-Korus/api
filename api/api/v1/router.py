from fastapi import APIRouter

from modules.users.controller import router as users_router

api_router = APIRouter()

api_router.include_router(users_router)
