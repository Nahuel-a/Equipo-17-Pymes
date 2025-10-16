"""
Admin endpoints for user and role management.
Only accessible by administrators and superadministrators.
"""

from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from api.dependencies.db import get_session
from crud.user import UserCrud
from models.enums import RoleUser
from schemas.user import RoleUpdateRequest, UserRoleResponse
from utils.permissions import (
    require_admin_role, 
    PermissionManager
)
import uuid

router = APIRouter()

@router.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    response_model=List[UserRoleResponse]
)
async def get_all_users(
    db: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin_role),
    role_filter: Annotated[Optional[RoleUser], Query(description="Filter users by role")] = None,
    is_active: Annotated[Optional[bool], Query(description="Filter by active status")] = None,
    skip: Annotated[int, Query(ge=0, description="Number of users to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description="Maximum number of users to return")] = 100
):
    """
    Get all users (Admin+ only).
    Allows filtering by role and pagination.
    """
    try:
        users = await UserCrud(db).get_all()
        
        # Apply filters
        filtered_users = users
        
        if role_filter:
            filtered_users = [u for u in filtered_users if u.role == role_filter]
            
        if is_active is not None:
            filtered_users = [u for u in filtered_users if u.is_active == is_active]
        
        # Apply pagination
        paginated_users = filtered_users[skip:skip + limit]
        
        # Convert to response model
        return [
            UserRoleResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            )
            for user in paginated_users
        ]
        
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching users"
        )


@router.put(
    "/users/role/",
    status_code=status.HTTP_200_OK
)
async def update_user_role(
    role_request: RoleUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user = Depends(require_admin_role),
):
    """
    Update user role (Admin+ only with restrictions).
    
    Rules:
    - SUPERADMIN can modify any role
    - ADMIN can only promote/demote USER roles
    - Cannot modify own role
    """
    # Cannot modify own role
    if current_user.id == role_request.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own role"
        )
    
    try:
        # Use a single UserCrud instance for the entire operation
        user_crud = UserCrud(db)
        
        # Get the target user
        target_user = await user_crud.get(role_request.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify specific permissions
        if not await PermissionManager.can_modify_user_role(current_user.role, role_request.new_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions to assign {role_request.new_role.value} role"
            )
        
        # If ADMIN is trying to modify another ADMIN or SUPERADMIN
        if (current_user.role == RoleUser.ADMIN and 
            target_user.role in [RoleUser.ADMIN, RoleUser.SUPERADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify admin or superadmin roles"
            )
        
        # Update role directly
        # Get admin user email safely
        admin_email = "admin"
        try:
            # Explicitly load current_user to access its attributes
            admin_user_fresh = await user_crud.get(current_user.id)
            if admin_user_fresh and admin_user_fresh.email:
                admin_email = admin_user_fresh.email
        except Exception:
            admin_email = "admin"
        
        # Update role using CRUD
        await user_crud.update_attribute(
            target_user.id, 
            "role", 
            role_request.new_role
        )
        
        # Complete and safe response
        return {
            "message": "User role updated successfully",
            "user_id": str(role_request.user_id),
            "new_role": role_request.new_role.value,
            "updated_by": admin_email
        }
        
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating user role"
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user role: {str(error)}"
        )


@router.post(
    "/users/{user_id}/activate/",
    status_code=status.HTTP_200_OK
)
async def activate_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user = Depends(require_admin_role),
):
    """
    Activate a user account (Admin+ only).
    """
    try:
        user_crud = UserCrud(db)
        user = await user_crud.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already active"
            )
        
        # Get admin user email safely
        admin_email = "admin"
        try:
            admin_user_fresh = await user_crud.get(current_user.id)
            if admin_user_fresh and admin_user_fresh.email:
                admin_email = admin_user_fresh.email
        except Exception:
            admin_email = "admin"
        
        await user_crud.update_attribute(user_id, "is_active", True)
        
        return {
            "message": "User activated successfully",
            "user_id": str(user_id),
            "activated_by": admin_email
        }
        
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while activating user"
        )


@router.post(
    "/users/{user_id}/deactivate/",
    status_code=status.HTTP_200_OK
)
async def deactivate_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user = Depends(require_admin_role),
):
    """
    Deactivate a user account (Admin+ only).
    Cannot deactivate own account or superadmin accounts (unless you're superadmin).
    """
    # Verify that it's not trying to deactivate own account
    try:
        if str(current_user.id) == str(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
    except Exception:
        # Si hay problema accediendo al ID, por seguridad no permitimos la operación
        pass
    
    try:
        user_crud = UserCrud(db)
        user = await user_crud.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only SUPERADMIN can deactivate other ADMIN or SUPERADMIN
        try:
            if (user.role in [RoleUser.ADMIN, RoleUser.SUPERADMIN] and 
                current_user.role != RoleUser.SUPERADMIN):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot deactivate admin or superadmin accounts"
                )
        except Exception:
            # Si hay problema accediendo al rol, asumimos que no es SUPERADMIN por seguridad
            if user.role in [RoleUser.ADMIN, RoleUser.SUPERADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot deactivate admin or superadmin accounts"
                )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already inactive"
            )
        
        # Get admin user email safely
        admin_email = "admin"
        try:
            admin_user_fresh = await user_crud.get(current_user.id)
            if admin_user_fresh and admin_user_fresh.email:
                admin_email = admin_user_fresh.email
        except Exception:
            admin_email = "admin"
        
        await user_crud.update_attribute(user_id, "is_active", False)
        
        return {
            "message": "User deactivated successfully",
            "user_id": str(user_id),
            "deactivated_by": admin_email
        }
        
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deactivating user"
        )
