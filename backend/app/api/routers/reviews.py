from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_session
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from crud.reviews import ApplicationReviewCrud
from schemas.reviews import ApplicationReviewBase, ApplicationReviewSchema  # Add Review schemas similarly

    # Assume you have DB setup (e.g., get_db dependency)

app = FastAPI()

@app.post("/application-reviews/", response_model=ApplicationReviewSchema)
async def create_review(review: ApplicationReviewBase, db: AsyncSession = Depends(get_session)):
        # Insert into DB using SQLAlchemy model matching the schema
    db_review = await ApplicationReviewCrud(db).create(review)
    
    return db_review

@app.get("/application-reviews/{review_id}", response_model=ApplicationReviewSchema)
async def get_review(review_id: str, db: AsyncSession = Depends(get_session)):
        # Query DB and return as Pydantic model
    review = await ApplicationReviewCrud(db).get(review_id)
    
    return review

@app.put("/application-reviews/{review_id}", response_model=ApplicationReviewSchema)
async def update_application_review(
    review_id: str, review: ApplicationReviewBase, db: AsyncSession = Depends(get_session)
):
    await ApplicationReviewCrud(db).update(review_id, review)
    updated_review = await ApplicationReviewCrud(db).get(review_id)
    return updated_review

@app.delete("/application-reviews/{review_id}", response_model=ApplicationReviewSchema )
async def delete_application_review(review_id: str, db: AsyncSession = Depends(get_session)):
    """
    Delete an application review by ID.
    """
    await ApplicationReviewCrud(db).delete(review_id)
    return {"detail": "Review deleted"}
   # Add PUT/DELETE as needed for full CRUD
    