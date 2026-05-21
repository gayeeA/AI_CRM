"""
FastAPI application for AI CRM HCP Module
Main entry point with all API routes
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from config import settings
from database import engine, get_db, Base
from models import HCPInteraction, AIConversationHistory
from schemas import (
    HCPInteractionCreate, 
    HCPInteractionUpdate, 
    HCPInteractionResponse,
    AIMessageRequest,
    AIMessageResponse,
    AIConversationHistoryResponse,
    ToolExecutionRequest,
    ToolExecutionResponse
)
from agent import get_agent
from tools import execute_tool

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-First CRM HCP Module with LangGraph and Groq LLM Integration"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI CRM HCP Module",
        "version": settings.API_VERSION
    }


@app.get("/api/config", tags=["Configuration"])
async def get_config():
    """Get API configuration"""
    return {
        "model": settings.GROQ_MODEL,
        "max_tokens": settings.MAX_TOKENS,
        "temperature": settings.TEMPERATURE,
        "available_tools": ["log_interaction", "edit_interaction", "get_interaction", "delete_interaction", "summarize_interaction"]
    }


# ============================================================================
# INTERACTION ENDPOINTS
# ============================================================================

@app.get("/api/interactions", response_model=List[HCPInteractionResponse], tags=["Interactions"])
async def list_interactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all HCP interactions with pagination"""
    interactions = db.query(HCPInteraction).offset(skip).limit(limit).all()
    return interactions


@app.get("/api/interactions/{interaction_id}", response_model=HCPInteractionResponse, tags=["Interactions"])
async def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific HCP interaction"""
    interaction = db.query(HCPInteraction).filter(HCPInteraction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )
    return interaction


@app.post("/api/interactions", response_model=HCPInteractionResponse, tags=["Interactions"])
async def create_interaction(
    interaction: HCPInteractionCreate,
    db: Session = Depends(get_db)
):
    """Create a new HCP interaction"""
    db_interaction = HCPInteraction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@app.put("/api/interactions/{interaction_id}", response_model=HCPInteractionResponse, tags=["Interactions"])
async def update_interaction(
    interaction_id: int,
    interaction_update: HCPInteractionUpdate,
    db: Session = Depends(get_db)
):
    """Update an HCP interaction"""
    db_interaction = db.query(HCPInteraction).filter(HCPInteraction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )
    
    # Update only provided fields
    update_data = interaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_interaction, key, value)
    
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@app.delete("/api/interactions/{interaction_id}", tags=["Interactions"])
async def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """Delete an HCP interaction"""
    db_interaction = db.query(HCPInteraction).filter(HCPInteraction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )
    
    db.delete(db_interaction)
    db.commit()
    return {"message": "Interaction deleted successfully"}


# ============================================================================
# AI CHAT ENDPOINTS
# ============================================================================

@app.post("/api/chat", response_model=AIMessageResponse, tags=["AI Chat"])
async def process_ai_message(
    request: AIMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Process a message through the AI agent
    
    The AI agent will:
    1. Understand user intent
    2. Select appropriate tool(s)
    3. Process the interaction data
    4. Return updated interaction state
    """
    
    try:
        # Get or create interaction
        current_interaction = None
        if request.interaction_id:
            persisted_interaction = db.query(HCPInteraction).filter(
                HCPInteraction.id == request.interaction_id
            ).first()
            
            if not persisted_interaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interaction not found"
                )
            current_interaction = persisted_interaction.to_dict()

        if request.current_interaction:
            current_interaction = {
                **(current_interaction or {}),
                **request.current_interaction,
            }

        # Get AI agent and process message
        agent = get_agent()
        result = agent.chat(request.message, current_interaction)
        
        # Extract updated interaction data
        updated_data = result.get("updated_interaction_data", {})
        
        # Save or update interaction in database
        if request.interaction_id and updated_data:
            db_interaction = db.query(HCPInteraction).filter(
                HCPInteraction.id == request.interaction_id
            ).first()
            
            # Update fields
            for key, value in updated_data.items():
                if hasattr(db_interaction, key) and value is not None:
                    setattr(db_interaction, key, value)
            
            db.commit()
            db.refresh(db_interaction)
            updated_interaction = db_interaction
        
        elif updated_data and updated_data.get("hcp_name"):
            # Create new interaction
            new_interaction = HCPInteraction(**updated_data)
            db.add(new_interaction)
            db.commit()
            db.refresh(new_interaction)
            updated_interaction = new_interaction
        
        else:
            updated_interaction = None
        
        # Save conversation history
        conversation = AIConversationHistory(
            interaction_id=request.interaction_id,
            user_message=request.message,
            ai_response=result.get("ai_response", ""),
            tool_used=result.get("tool_used")
        )
        db.add(conversation)
        db.commit()
        
        # Format response
        response = AIMessageResponse(
            status="success",
            message="Message processed successfully",
            tool_used=result.get("tool_used"),
            ai_response=result.get("ai_response", ""),
            updated_interaction=updated_interaction if updated_interaction else None,
            next_steps=result.get("next_steps", [])
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@app.get("/api/conversation-history/{interaction_id}", response_model=List[AIConversationHistoryResponse], tags=["AI Chat"])
async def get_conversation_history(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation history for an interaction"""
    history = db.query(AIConversationHistory).filter(
        AIConversationHistory.interaction_id == interaction_id
    ).all()
    return history


# ============================================================================
# TOOL EXECUTION ENDPOINTS
# ============================================================================

@app.post("/api/tools/execute", response_model=ToolExecutionResponse, tags=["Tools"])
async def execute_direct_tool(
    request: ToolExecutionRequest,
):
    """
    Directly execute a specific tool
    
    Available tools:
    - log_interaction: Extract interaction data from text
    - edit_interaction: Update specific fields
    - suggest_follow_ups: Generate follow-up suggestions
    - extract_entities: Extract named entities
    - validate_sentiment: Analyze sentiment
    """
    
    try:
        tool_name = request.tool_name
        
        if tool_name == "log_interaction":
            result = execute_tool(tool_name, user_input=request.user_input)
        
        elif tool_name == "edit_interaction":
            result = execute_tool(
                tool_name,
                current_data=request.interaction_data,
                user_input=request.user_input
            )
        
        elif tool_name == "suggest_follow_ups":
            result = execute_tool(tool_name, interaction_data=request.interaction_data)
        
        elif tool_name == "extract_entities":
            result = execute_tool(tool_name, user_input=request.user_input)
        
        elif tool_name == "validate_sentiment":
            result = execute_tool(
                tool_name,
                text=request.user_input,
                current_sentiment=request.interaction_data.get("sentiment")
            )
        
        else:
            return ToolExecutionResponse(
                success=False,
                tool_used=tool_name,
                result={"error": f"Unknown tool: {tool_name}"}
            )
        
        return ToolExecutionResponse(
            success=result.get("success", False),
            tool_used=tool_name,
            result=result,
            updated_fields=result.get("updated_fields") or result.get("data")
        )
    
    except Exception as e:
        return ToolExecutionResponse(
            success=False,
            tool_used=request.tool_name,
            result={"error": str(e)}
        )


@app.get("/api/tools/list", tags=["Tools"])
async def list_tools():
    """List available tools and their descriptions"""
    return {
        "tools": [
            {
                "name": "log_interaction",
                "description": "Extract interaction data from natural language and create a new interaction",
                "example": "Today I met with Dr. Smith and discussed product X efficiency. The sentiment was positive and I shared the brochures."
            },
            {
                "name": "edit_interaction",
                "description": "Update specific fields in an existing interaction",
                "example": "Sorry, the name was actually Dr. John and the sentiment was negative"
            },
            {
                "name": "suggest_follow_ups",
                "description": "Generate AI-suggested follow-up actions based on interaction data",
                "example": "What should I do after this meeting?"
            },
            {
                "name": "extract_entities",
                "description": "Extract named entities (names, organizations, products, locations, dates) from text",
                "example": "I met with Dr. Smith from XYZ Hospital about our Aspirin product on March 15"
            },
            {
                "name": "validate_sentiment",
                "description": "Analyze and validate sentiment classification of interactions",
                "example": "Is the sentiment of 'Great discussion!' positive or negative?"
            }
        ]
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "detail": "Internal server error",
            "error": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn
    # Use import string to enable reload/workers reliably
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

