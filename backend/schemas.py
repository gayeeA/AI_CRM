from pydantic import BaseModel

class InteractionCreate(BaseModel):
    hcp_name: str
    topics: str
    sentiment: str
    outcome: str