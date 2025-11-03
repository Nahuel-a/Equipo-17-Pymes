from sqlalchemy.exc import SQLAlchemyError
from api.dependencies.db import get_session
from crud.review import ReviewCrud
from crud.credits import CreditsCrud
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.review import ReviewSchema, ReviewCreate, ReviewDecision
from sqlalchemy.ext.asyncio.session import AsyncSession
from utils.permissions import require_admin_role
from models.user import User
from typing import List
import uuid

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewSchema,
)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin_role),
):
    """
    Create a new review for a credit application (Admin/SuperAdmin only).
    This will change the credit status from PENDING to IN_PROGRESS.
    """
    try:
        review_crud = ReviewCrud(db)
        return await review_crud.create_review_for_credit(
            credits_id=review_data.credits_id,
            reviewer_id=current_user.id,
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating review"
        )


@router.put(
    "/{review_id}/decision/",
    status_code=status.HTTP_200_OK,
    response_model=ReviewSchema,
)
async def make_review_decision(
    review_id: uuid.UUID,
    decision_data: ReviewDecision,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin_role),
):
    """
    Make a decision on an existing credit review (Admin/SuperAdmin only).
    This will update both the review record and the credit status to the final decision.
    """
    try:
        review_crud = ReviewCrud(db)
        return await review_crud.make_decision(
            review_id=review_id,
            decision=decision_data.decision,
            reviewer_id=current_user.id,
            review_comments=decision_data.review_comments
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while processing decision"
        )


@router.get(
    "/pending/",
    status_code=status.HTTP_200_OK,
    response_model=List[ReviewSchema],
)
async def get_pending_reviews(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin_role),
):
    """
    Get all pending reviews (Admin/SuperAdmin only).
    Returns reviews that haven't been decided yet.
    """
    try:
        review_crud = ReviewCrud(db)
        return await review_crud.get_pending_reviews()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching pending reviews"
        )


@router.get(
    "/credit/{credits_id}/history/",
    status_code=status.HTTP_200_OK,
    response_model=List[ReviewSchema],
)
async def get_credit_review_history(
    credits_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin_role),
):
    """
    Get complete review history for a specific credit (Admin/SuperAdmin only).
    Shows all reviews that have been made for this credit over time.
    Useful for audit trails and understanding the credit's review journey.
    """
    try:
        review_crud = ReviewCrud(db)
        reviews = await review_crud.get_by_credits_id(credits_id)
        
        if not reviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reviews found for this credit"
            )
        
        return reviews
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching credit review history"
        )


@router.get(
    "/credit/{credits_id}/active/",
    status_code=status.HTTP_200_OK,
    response_model=ReviewSchema,
)
async def get_active_review_for_credit(
    credits_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin_role),
):
    """
    Get the current active (pending) review for a credit (Admin/SuperAdmin only).
    Returns the review that is currently in progress and hasn't been decided yet.
    Useful for:
    - Checking if a credit is currently under review
    - Finding which review to make a decision on
    - Preventing multiple concurrent reviews
    """
    try:
        review_crud = ReviewCrud(db)
        review = await review_crud.get_active_review_for_credit(credits_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active review found for this credit"
            )
        
        return review
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching active review"
        )


# Endpoint adicional: Ver créditos disponibles para revisar
@router.get(
    "/available-credits/",
    status_code=status.HTTP_200_OK,
)
async def get_credits_available_for_review(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin_role),
):
    """
    Get credits that are available for review (PENDING status) (Admin/SuperAdmin only).
    Shows credits that can be selected for review.
    """
    try:
        credits_crud = CreditsCrud(db)
        # Get all credits with PENDING status (available for review)
        pending_credits = await credits_crud.get_all_by_attribute("status", "pending")
        
        return {
            "available_credits": [
                {
                    "id": str(credit.id),
                    "amount": credit.amount,
                    "pyme_id": str(credit.pyme_id),
                    "status": credit.status.value,
                    "created_at": credit.created_at
                }
                for credit in pending_credits
            ],
            "count": len(pending_credits)
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching available credits"
        )


@router.get(
    "/{review_id}/",
    status_code=status.HTTP_200_OK,
    response_model=ReviewSchema,
)
async def get_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin_role),
):
    """
    Get a specific review by ID (Admin/SuperAdmin only).
    """
    try:
        review_crud = ReviewCrud(db)
        review = await review_crud.get(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        return review
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching review"
        )