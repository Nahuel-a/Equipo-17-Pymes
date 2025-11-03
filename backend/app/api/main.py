from api.routers import user, auth, pyme, credits, admin, review
from fastapi import APIRouter, status

api_router = APIRouter()


api_router.include_router(
    auth.router,
    prefix="/api",
    tags=["Authentication"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Access forbidden"},
    },
)

api_router.include_router(
    user.router,
    prefix="/api/user",
    tags=["User"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Access forbidden"},
    },
)

api_router.include_router(
    pyme.router,
    prefix="/api/pyme",
    tags=["Pyme"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Access forbidden"},
    },
)

api_router.include_router(
    credits.router,
    prefix="/api/credits",
    tags=["Credits"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Access forbidden"},
    },
)

api_router.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["Admin"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Access forbidden"},
    },
)

api_router.include_router(
    review.router,
    prefix="/api/reviews",
    tags=["Reviews"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Access forbidden"},
    },
)