from api.dependencies import get_session 
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastApi, Depends
from sqlalchemy.orm import Session
from crud.documents import ApplicationDocumentsCrud
from schemas.documents import ApplicationDocumentBase, ApplicationDocumentSchema

# Assuming you have SQLAlchemy models defined (e.g., ApplicationDocument, ApplicationReview)
# from your_app.models import ApplicationDocument, ApplicationReview
# from your_app.database import get_db
# Import your schemas
app = FastApi()

### Application Documents Endpoints

@app.post("/application-documents/", response_model=ApplicationDocumentSchema)
async def create_document(
    document: ApplicationDocumentBase, db: AsyncSession = Depends(get_session)):
    db_document = await ApplicationDocumentsCrud(db).create(document)
    return db_document
    """
    Create a new application document.
    """
    # Assuming ApplicationDocument is your SQLAlchemy model
    # db_document = ApplicationDocument(**document.dict())
    # db.add(db_document)
    # db.commit()
    # db.refresh(db_document)
    # return db_document
    # Placeholder response (replace with actual DB logic)
    

@app.get("/application-documents/{doc_id}", response_model=ApplicationDocumentSchema)
async def get_application_document(doc_id: str, db: AsyncSession = Depends(get_session)):
    """
    Retrieve a single application document by ID.
    """
    db_document = await ApplicationDocumentCrud(db).get(doc_id)
    return db_document
    #     raise HTTPException(status_code=404, detail="Document not found")
    # return db_document
    # Placeholder (replace with actual)
    raise HTTPException(status_code=404, detail="Document not found")  # Simulate logic

@app.get("/application-documents/", response_model=List[ApplicationDocumentSchema])
async def get_application_document(application_id: str = None, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """
    Retrieve a list of application documents. Filter by application_id if provided.
    """
    # query = db.query(ApplicationDocument)
    # if application_id:
    #     query = query.filter(ApplicationDocument.application_id == application_id)
    # documents = query.offset(skip).limit(limit).all()
    # return documents
    # Placeholder (replace with actual)
    return []  # Empty list simulation

@app.put("/application-documents/{doc_id}", response_model=ApplicationDocumentSchema)
async def update_application_document(
    doc_id: str, document: ApplicationDocumentBase, db: AsyncSession = Depends(get_session)
):
    """
    Update an existing application document.
    """
    # db_document = db.query(ApplicationDocument).filter(ApplicationDocument.id == doc_id).first()
    # if db_document is None:
    #     raise HTTPException(status_code=404, detail="Document not found")
    # for key, value in document.dict().items():
    #     setattr(db_document, key, value)
    # db.commit()
    # db.refresh(db_document)
    # return db_document
    # Placeholder
    raise HTTPException(status_code=404, detail="Document not found")

@app.delete("/application-documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application_document(doc_id: str, db: AsyncSession = Depends(get_session)):
    """
    Delete an application document by ID.
    """
    # db_document = db.query(ApplicationDocument).filter(ApplicationDocument.id == doc_id).first()
    # if db_document is None:
    #     raise HTTPException(status_code=404, detail="Document not found")
    # db.delete(db_document)
    # db.commit()
    # return None
    raise HTTPException(status_code=404, detail="Document not found")

### Application Reviews Endpoints
# Note: You provided models only for documents, so I'm defining placeholder schemas here.
# Add actual Pydantic models for reviews as needed.

