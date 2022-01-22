from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Integer, String

from api.database import Base

# Class Upload contains the DB model for the Uploads Table.
class Upload(Base):
    """Uploads Table"""

    __tablename__ = "uploads"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    file_name = Column(String)
    file_hash = Column(String)
    byte_size = Column(BigInteger)
    created = Column(BigInteger)
    updated = Column(BigInteger)
    skipped = Column(BigInteger)
    failed = Column(BigInteger)
    total_count = Column(BigInteger)
    
    user = relationship("User", back_populates="uploads", foreign_keys=[user_id])

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"{self.id} | {self.name}"