"""
Authorization system for role-based access control.
This module provides decorators and functions to control access to endpoints based on user roles.
"""

from functools import wraps
from typing import Callable
from fastapi import HTTPException, status
from models.enums import RoleUser
from models.user import User


class PermissionManager:
    """
    Manages role hierarchy and permissions.
    """
    
    ROLE_HIERARCHY = {
        RoleUser.USER: 1,
        RoleUser.ADMIN: 2,
        RoleUser.SUPERADMIN: 3
    }
    
    @classmethod
    async def has_permission(cls, user_role: RoleUser, required_role: RoleUser) -> bool:
        """
        Verifies if a user with a specific role has permissions to access a resource.
        
        Args:
            user_role: Current user's role
            required_role: Minimum required role
            
        Returns:
            bool: True if has permissions, False otherwise
        """
        user_level = cls.ROLE_HIERARCHY.get(user_role, 0)
        required_level = cls.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level
    
    @classmethod
    async def can_modify_user_role(cls, modifier_role: RoleUser, target_role: RoleUser) -> bool:
        """
        Verifies if a user can modify another user's role.
        
        Rules:
        - SUPERADMIN can modify any role
        - ADMIN can only modify USER roles
        - USER cannot modify any role
        
        Args:
            modifier_role: Role of the user who wants to modify
            target_role: Target role to change to
            
        Returns:
            bool: True if can modify, False otherwise
        """
        if modifier_role == RoleUser.SUPERADMIN:
            return True
        
        if modifier_role == RoleUser.ADMIN:
            return target_role in [RoleUser.USER, RoleUser.ADMIN]
            
        return False


def require_minimum_role(minimum_role: RoleUser):
    """
    Decorator to require a minimum role in endpoints.
    
    Args:
        minimum_role: Minimum required role (includes higher roles in the hierarchy)
        
    Example:
        @require_minimum_role(RoleUser.ADMIN)  # ADMIN and SUPERADMIN can access
        async def admin_endpoint():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not await PermissionManager.has_permission(current_user.role, minimum_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Minimum role required: {minimum_role.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


from api.dependencies.user import CurrentUserDep

async def require_user_role(current_user: CurrentUserDep):
    """Dependency that requires USER role or higher"""
    if not await PermissionManager.has_permission(current_user.role, RoleUser.USER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role required"
        )
    return current_user


async def require_admin_role(current_user: CurrentUserDep):
    """Dependency that requires ADMIN role or higher"""
    if not await PermissionManager.has_permission(current_user.role, RoleUser.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user


async def require_superadmin_role(current_user: CurrentUserDep):
    """Dependency that requires SUPERADMIN role"""
    if not await PermissionManager.has_permission(current_user.role, RoleUser.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin role required"
        )
    return current_user


async def check_resource_ownership(user, resource_user_id: str) -> bool:
    """
    Verifies if a user can access a specific resource.
    
    Rules:
    - User can access their own resources
    - ADMIN can access USER resources
    - SUPERADMIN can access any resource
    
    Args:
        user: Current user
        resource_user_id: ID of the resource owner user
        
    Returns:
        bool: True if can access, False otherwise
    """
    if str(user.id) == str(resource_user_id):
        return True
    
    if user.role == RoleUser.SUPERADMIN:
        return True
    
    if user.role == RoleUser.ADMIN:
        return True
    
    return False