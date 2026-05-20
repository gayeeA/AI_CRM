from sqlalchemy import Column, Integer, String, Text
from db import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String)
    topics = Column(Text)
    sentiment = Column(String)
    outcome = Column(Text)