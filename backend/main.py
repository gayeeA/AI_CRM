import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schema import ChatRequest, InteractionState
from backend.agent import agent_executor, AgentState
import uvicorn

app = FastAPI(title="AIVOA.AI HCP Engine Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def handle_agent_chat(payload: ChatRequest):
    try:
        initial_state = AgentState(
            input_text=payload.message,
            current_form=payload.current_state
        )
        
        output = agent_executor.invoke(initial_state.model_dump())
        
        return {
            "reply": output["chat_response"],
            "form_state": output["updated_form"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)