from db import SessionLocal
from models import Interaction

# 1. Log Interaction
def log_interaction(data):
    db = SessionLocal()
    interaction = Interaction(**data)
    db.add(interaction)
    db.commit()
    return {"message": "Interaction saved"}

# 2. Edit Interaction
def edit_interaction(interaction_id, updates):
    db = SessionLocal()
    interaction = db.query(Interaction).get(interaction_id)
    for key, value in updates.items():
        setattr(interaction, key, value)
    db.commit()
    return {"message": "Updated"}

# 3. Fetch History
def fetch_interactions():
    db = SessionLocal()
    return db.query(Interaction).all()

# 4. Suggest Follow-up
def suggest_followup():
    return {"suggestion": "Schedule follow-up in 2 weeks"}

# 5. HCP Insights
def hcp_insights():
    return {"insight": "Doctor prefers digital materials"}