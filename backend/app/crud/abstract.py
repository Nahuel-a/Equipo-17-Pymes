from abc import ABC
from typing import Any
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession

"""
Base class for CRUD operations using SQLAlchemy with asynchronous sessions.
This abstract class provides a foundation for common database operations.
Each specific model will inherit from this class to obtain basic CRUD functionality.
"""


class BaseCrud(ABC):
    model = None  # Model to be defined in the inherited class

    def __init__(self, session: AsyncSession):
        """
        Initialize the BaseCrud instance.
        Args:
            session (AsyncSession): SQLAlchemy async session for database interactions
        Raises:
            ValueError: If model is not defined in the subclass
        """
        if not self.model:
            raise ValueError("Model must be defined in the subclass")
        self.session = session

    async def get(self, model_id: UUID):
        """
        Retrieve a model instance by its ID.
        Args:
            model_id (int): ID of the model to retrieve
        Returns:
            Model: Found model instance or None if not found
        Raises:
            RuntimeError: If there's an error during retrieval
        """
        try:
            statement = select(self.model).where(self.model.id == model_id)
            result = await self.session.execute(statement)
            return result.scalars().first()

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Error retrieving {self.model.__name__} with id {model_id}"
            ) from e
        
    async def get_all(self):
        """
        Retrieve all instances of the model.
        Returns:
            List[Model]: List of all model instances
        Raises:
            RuntimeError: If there's an error during retrieval
        """
        try:
            statement = select(self.model)
            result = await self.session.execute(statement)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Error retrieving all instances of {self.model.__name__}"
            ) from e

        
    async def get_by_attribute(self, attribute: str, value: Any):
        """
        Retrieve a model instance by a specific attribute value.
        Args:
            attribute (str): Name of the model attribute to search by
            value (Any): Value to match against the attribute
        Returns:
            Model: Found model instance or None if not found
        Raises:
            RuntimeError: If there's an error during retrieval
            AttributeError: If the specified attribute doesn't exist in the model
        """
        if hasattr(self.model, attribute):
            try:
                model_attribute = getattr(self.model, attribute)
                statement = select(self.model).where(model_attribute == value)
                result = await self.session.execute(statement)
                return result.scalars().first()
            except SQLAlchemyError as e:
                raise RuntimeError(
                    f"Error retrieving {self.model.__name__} by {attribute}={value}"
                ) from e
        else:
            raise AttributeError(
                f"Model {self.model.__name__} has no attribute {attribute}"
            )
    
    async def get_all_by_attribute(self, attribute: str, value: Any):
        """
        Retrieve all model instances that match a specific attribute value.
        
        Args:
            attribute (str): Name of the model attribute to search by
            value (Any): Value to match against the attribute
            
        Returns:
            List[Model]: List of found model instances (empty list if none found)
            
        Raises:
            RuntimeError: If there's an error during retrieval
            AttributeError: If the specified attribute doesn't exist in the model
        """
        if hasattr(self.model, attribute):
            try:
                model_attribute = getattr(self.model, attribute)
                statement = select(self.model).where(model_attribute == value)
                result = await self.session.execute(statement)
                instances = result.scalars().all()
                return instances  # Will return empty list if no matches are found
            except SQLAlchemyError as e:
                raise RuntimeError(
                    f"Error retrieving {self.model.__name__} instances by {attribute}={value}"
                ) from e
        else:
            raise AttributeError(
                f"Model {self.model.__name__} has no attribute {attribute}"
            )
        
    async def create(self, data: BaseModel):
        """
        Create a new instance of the model.
        Args:
            data (BaseModel): Pydantic model containing the data for the new instance
        Returns:
            Model: Created model instance
        Raises:
            RuntimeError: If there's an error during creation
        """
        # Convertir a diccionario y asegurarse de que los campos requeridos tengan valores
        data_dict = data.model_dump()
        
        # Crear instancia con valores por defecto para campos timestamp si es necesario
        from datetime import datetime
        if hasattr(self.model, 'created_at') and 'created_at' not in data_dict:
            data_dict['created_at'] = datetime.utcnow()
        if hasattr(self.model, 'updated_at') and 'updated_at' not in data_dict:
            data_dict['updated_at'] = datetime.utcnow()
            
        new_instance = self.model(**data_dict)
        try:
            self.session.add(new_instance)
            await self.session.commit()
            await self.session.refresh(new_instance)
            return new_instance
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error creating {self.model.__name__}") from e

    async def update(self, model_id: UUID, data: BaseModel):
        """
        Update an existing model instance by its ID.
        Args:
            model_id (UUID): ID of the model to update
            data (BaseModel): Pydantic model containing the updated data
        Returns:
            Model: Updated model instance
        Raises:
            ValueError: If the instance is not found
            RuntimeError: If there's an error during update
        """
        try:
            statement = select(self.model).where(self.model.id == model_id)
            result = await self.session.execute(statement)
            instance = result.scalars().first()

            if instance:
                for key, value in data.model_dump().items():
                    setattr(instance, key, value)
                await self.session.commit()
                await self.session.refresh(instance)
                return instance
            else:
                raise ValueError(f"Instance with id {model_id} not found")
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(
                f"Error updating {self.model.__name__} with id {model_id}"
            ) from e

    async def delete(self, model_id: UUID):
        """
        Delete a model instance by its ID.
        Args:
            model_id (UUID): ID of the model to delete
        Raises:
            ValueError: If the instance is not found
            RuntimeError: If there's an error during deletion
        """
        try:
            statement = select(self.model).where(self.model.id == model_id)
            result = await self.session.execute(statement)
            instance = result.scalars().first()
            if instance:
                await self.session.delete(instance)
                await self.session.commit()
            else:
                raise ValueError(f"Instance with id {model_id} not found")
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(
                f"Error deleting {self.model.__name__} with id {model_id}"
            ) from e
            
    async def update_attribute(self, model_id: UUID, attribute: str, value: Any):
        """
        Update a specific attribute of a model instance by its ID.
        
        Args:
            model_id (UUID): ID of the model to update
            attribute (str): Name of the attribute to update
            value (Any): New value for the attribute
            
        Returns:
            Model: Updated model instance
            
        Raises:
            ValueError: If the instance is not found or the attribute doesn't exist
            RuntimeError: If there's an error during the update
        """
        try:
            statement = select(self.model).where(self.model.id == model_id)
            result = await self.session.execute(statement)
            instance = result.scalars().first()
            
            if not instance:
                raise ValueError(f"Instance with id {model_id} not found")
                
            if not hasattr(instance, attribute):
                raise ValueError(f"Model {self.model.__name__} has no attribute {attribute}")
                
            setattr(instance, attribute, value)
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(
                f"Error updating attribute {attribute} of {self.model.__name__} with id {model_id}"
            ) from e