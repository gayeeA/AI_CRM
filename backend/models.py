"""
SQLAlchemy ORM models for database tables
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from database import Base
from datetime import datetime


class HCPInteraction(Base):
    """Healthcare Professional (HCP) Interaction model"""
    __tablename__ = "hcp_interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=False, index=True)
    hcp_type = Column(String(100), default="Doctor")
    interaction_type = Column(String(100), default="Meeting")
    date = Column(String(50), nullable=False)
    time = Column(String(10), nullable=False)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    
    # Materials and samples
    materials_shared = Column(JSON, default=list)  # List of material names
    samples_distributed = Column(JSON, default=list)  # List of sample info
    
    # Sentiment analysis
    sentiment = Column(String(20), default="Neutral")  # Positive, Neutral, Negative
    
    # Outcomes and follow-ups
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    ai_suggestions = Column(JSON, default=list)  # List of AI-generated suggestions
    
    # AI processing metadata
    ai_summary = Column(Text, nullable=True)
    extracted_entities = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "hcp_name": self.hcp_name,
            "hcp_type": self.hcp_type,
            "interaction_type": self.interaction_type,
            "date": self.date,
            "time": self.time,
            "attendees": self.attendees,
            "topics_discussed": self.topics_discussed,
            "materials_shared": self.materials_shared,
            "samples_distributed": self.samples_distributed,
            "sentiment": self.sentiment,
            "outcomes": self.outcomes,
            "follow_up_actions": self.follow_up_actions,
            "ai_suggestions": self.ai_suggestions,
            "ai_summary": self.ai_summary,
            "extracted_entities": self.extracted_entities,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIConversationHistory(Base):
    """Store AI chat conversation history"""
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, nullable=True, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    tool_used = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "interaction_id": self.interaction_id,
            "user_message": self.user_message,
            "ai_response": self.ai_response,
            "tool_used": self.tool_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
