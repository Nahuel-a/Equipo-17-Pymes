from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
    # Assume you have DB setup (e.g., get_db dependency)

app = FastAPI()

@app.post("/application-reviews/", response_model=ApplicationReviewSchema)
def create_review(review: ApplicationReviewBase, db: Session = Depends(get_db)):
        # Insert into DB using SQLAlchemy model matching the schema
    db_review = ApplicationReview(**review.dict())  # Assuming SQLAlchemy model named ApplicationReview
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/application-reviews/{review_id}", response_model=ApplicationReviewSchema)
def get_review(review_id: UUID, db: Session = Depends(get_db)):
        # Query DB and return as Pydantic model
    return db.query(ApplicationReview).filter(ApplicationReview.id == review_id).first()

    # Add PUT/DELETE as needed for full CRUD
    