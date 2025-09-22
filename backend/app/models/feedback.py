from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Feedback(Base):
    """Model for storing user feedback."""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="User's name")
    email = Column(String(255), nullable=False, comment="User's email address")
    message = Column(Text, nullable=False, comment="User's feedback message")
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="Timestamp when feedback was submitted"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when feedback was last updated"
    )

    def __repr__(self):
        return f"<Feedback(id={self.id}, name='{self.name}', email='{self.email}', created_at='{self.created_at}')>"