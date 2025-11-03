from crud.abstract import BaseCrud
from models.review import Reviews
from models.credits import Credits
from models.enums import StatusCredit
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from fastapi import HTTPException, status
import uuid


class ReviewCrud(BaseCrud):
    model = Reviews
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
    
    async def get_by_credits_id(self, credits_id: uuid.UUID) -> List[Reviews]:
        """Get all reviews for a specific credit"""
        result = await self.session.execute(
            select(Reviews).where(Reviews.credits_id == credits_id)
        )
        return list(result.scalars().all())
    
    async def get_by_reviewer_id(self, reviewer_id: uuid.UUID) -> List[Reviews]:
        """Get all reviews made by a specific reviewer"""
        result = await self.session.execute(
            select(Reviews).where(Reviews.reviewer_id == reviewer_id)
        )
        return list(result.scalars().all())
    
    async def get_pending_reviews(self) -> List[Reviews]:
        """Get all reviews that haven't been decided yet"""
        result = await self.session.execute(
            select(Reviews).where(Reviews.decision.is_(None))
        )
        return list(result.scalars().all())
    
    async def get_active_review_for_credit(self, credits_id: uuid.UUID) -> Optional[Reviews]:
        """Get the active (pending) review for a credit, if any"""
        result = await self.session.execute(
            select(Reviews).where(
                Reviews.credits_id == credits_id,
                Reviews.decision.is_(None)
            )
        )
        return result.scalar_one_or_none()
    
    async def make_decision(
        self, 
        review_id: uuid.UUID, 
        decision: StatusCredit, 
        reviewer_id: uuid.UUID,
        review_comments: Optional[str] = None
    ) -> Reviews:
        """
        Make a decision on an existing credit review.
        This method handles the complete business logic:
        1. Validates the review exists and hasn't been decided yet
        2. Updates the associated credit status
        3. Records the decision in the review for audit
        4. Commits the transaction
        
        Args:
            review_id: ID of the review to decide on
            decision: The StatusCredit enum decision
            reviewer_id: ID of the user making the decision
            review_comments: Optional comments from the reviewer
            
        Returns:
            The updated review object
            
        Raises:
            HTTPException: If review not found, already decided, or database error
        """
        try:
            # Get the review
            review = await self.get(review_id)
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Review not found"
                )
            
            # Check if review has already been decided
            if review.decision is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This review has already been decided"
                )
            
            # Get the associated credit
            credit_result = await self.session.execute(
                select(Credits).where(Credits.id == review.credits_id)
            )
            credit = credit_result.scalar_one_or_none()
            if not credit:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Associated credit not found"
                )
            
            # Business logic: Update credit status
            credit.status = decision
            
            # Audit: Store decision in review as string
            review.decision = decision.value
            review.review_comments = review_comments

            await self.session.commit()
            
            await self.session.refresh(review)
            await self.session.refresh(credit)
            
            return review
            
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing review decision: {str(e)}"
            )
    
    async def create_review_for_credit(
        self, 
        credits_id: uuid.UUID, 
        reviewer_id: uuid.UUID,
        review_comments: Optional[str] = None
    ) -> Reviews:
        """
        Create a new review for a credit application.
        This is REQUIRED before any status change can be made on the credit.
        
        Args:
            credits_id: ID of the credit to review
            reviewer_id: ID of the reviewer (admin/superadmin)
            review_comments: Initial comments for the review
            
        Returns:
            The created review object
            
        Raises:
            HTTPException: If credit not found, already has pending review, or database error
        """
        try:
            credit_result = await self.session.execute(
                select(Credits).where(Credits.id == credits_id)
            )
            credit = credit_result.scalar_one_or_none()
            if not credit:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Credit not found"
                )
            # Check if credit is in a reviewable state
            if credit.status != StatusCredit.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Credit status is '{credit.status.value}', can only review PENDING credits"
                )
            
            # Check if there's already a pending review for this credit
            existing_review_result = await self.session.execute(
                select(Reviews).where(
                    Reviews.credits_id == credits_id,
                    Reviews.decision.is_(None)
                )
            )
            existing_review = existing_review_result.scalar_one_or_none()
            if existing_review:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This credit already has a pending review"
                )
            
            # Business logic: Update credit status to IN_PROGRESS when review starts
            credit.status = StatusCredit.IN_PROGRESS

            new_review = Reviews(
                credits_id=credits_id,
                reviewer_id=reviewer_id,
                review_comments=review_comments,
                is_active=True
            )
            
            self.session.add(new_review)

            await self.session.commit()
            await self.session.refresh(new_review)
            
            return new_review
            
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating review: {str(e)}"
            )