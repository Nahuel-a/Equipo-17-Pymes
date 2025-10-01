from abc import ABC
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession

"""
Base class for CRUD operations (Create, Read, Update, Delete) using SQLAlchemy with asynchronous sessions.
This abstract class provides a base implementation for common database operations.
Each specific model will inherit from this class to obtain basic CRUD functionality.
"""


class BaseCrud(ABC):
    model = None  # Model to be defined in the inherited class

    def __init__(self, session: AsyncSession):
        """
        BaseCrud class constructor.
        Args:
            session (AsyncSession): Asynchronous SQLAlchemy session for interacting with the database
        Raises:
            ValueError: If the model is not defined in the child class
        """
        if not self.model:
            raise ValueError("Model must be defined in the subclass")
        self.session = session

    async def get(self, model_id: int):
        """
        Gets a model instance by its ID.
        Args:
            model_id (int): ID of the model to fetch
        Returns:
            Model: Model instance found, or None if it doesn't exist
        Raises:
            RuntimeError: If an error occurs while retrieving the model
        """
        try:
            statement = select(self.model).where(self.model.id == model_id)
            result = await self.session.execute(statement)
            return result.scalars().first()

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Error retrieving {self.model.__name__} with id {model_id}"
            ) from e
    
    async def create(self, data: BaseModel):
        """
        Creates a new model instance in the database.
        Args:
            data (BaseModel): Data validated by Pydantic to create the instance
        Returns:
            Model: New instance created and saved in the database
        Raises:
            RuntimeError: If an error occurs during creation
        """
        new_instance = self.model(**data.model_dump())
        try:
            self.session.add(new_instance)
            await self.session.commit()
            await self.session.refresh(new_instance)
            return new_instance
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error creating {self.model.__name__}") from e
    
    async def update(self, model_id: int, data: BaseModel):
        """
       Updates an existing model instance by its ID.
        Args:
            model_id (int): ID of the model to update
            data (BaseModel): Data validated by Pydantic with the updates
        Returns:
            Model: Updated model instance
        Raises:
            ValueError: If the instance is not found
            RuntimeError: If an error occurs during the update
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

    async def delete(self, model_id: int):
        """
        Deletes a model instance by its ID.
        Args:
            model_id (int): ID of the model to delete
        Raises:
            ValueError: If the instance is not found
            RuntimeError: If an error occurs during deletion
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
