from api.routers import user, auth, pyme, credits
from fastapi import APIRouter, status

api_router = APIRouter()


api_router.include_router(
    auth.router,
    prefix="/api",
    tags=["Authentication"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)

api_router.include_router(
    user.router,
    prefix="/api/user",
    tags=["User"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)

api_router.include_router(
    pyme.router,
    prefix="/api/pyme",
    tags=["Pyme"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)

api_router.include_router(
    credits.router,
    prefix="/api/credits",
    tags=["Credits"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)