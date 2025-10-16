from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

class Documento(Base):
    __tablename__ = 'digital_signatures'
    id = Column(Integer, primary_key=True)
    firma_digital = Column(String)  # Stores the signature as an encoded string
    fecha_firma = Column(DateTime, default=datetime.utcnow)