from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class DocumentsIn(BaseModel):
    contenido: str


class DocumentsOut(BaseModel):
    id: uuid.UUID
    pyme_id: uuid.UUID
    contenido: str
    firma_digital: Optional[str]
    fecha_firma: Optional[datetime]

    class Config:
        orm_mode = True
