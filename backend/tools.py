"""
LangGraph tools for AI-assisted HCP interaction logging
"""
import json
import re
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from pydantic import ValidationError

from config import settings
from database import SessionLocal
from models import HCPInteraction
from schemas import (
    HCPInteractionCreate,
    HCPInteractionUpdate,
    HCPInteractionResponse,
    LogInteractionArguments,
    EditInteractionArguments,
    GetInteractionArguments,
    DeleteInteractionArguments,
    SummarizeInteractionArguments,
)

from llm import chat_completion


def _tool_normalize_edit_args(updates: Any) -> Dict[str, Any]:
    """Normalize mis-shaped edit payloads.

    Some callers may send:
    - {"changed_fields": {...}}
    - {"data": {...}}
    - the correct payload: {...} (already the updates)
    """
    if updates is None:
        return {}
    if not isinstance(updates, dict):
        return {}
    if "updates" in updates and isinstance(updates["updates"], dict):
        return updates["updates"]
    if "changed_fields" in updates and isinstance(updates["changed_fields"], dict):
        return updates["changed_fields"]
    if "data" in updates and isinstance(updates["data"], dict):
        return updates["data"]
    return updates





def call_groq_llm(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Call Groq LLM with the specified prompt.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    return chat_completion(
        messages=messages,
        max_tokens=settings.MAX_TOKENS,
        temperature=settings.TEMPERATURE,
    )


def _extract_json_from_text(text: str) -> dict:
    """Try to robustly extract a JSON object from model output.

    Strategies:
    - Try full-text JSON load
    - Look for fenced code blocks (```json ... ``` or ``` ... ```)
    - Find the largest {...} substring and attempt to parse
    """
    # direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # look for ```json or ``` fenced blocks
    fence_matches = re.findall(r"```(?:json)?\n([\s\S]*?)```", text, re.IGNORECASE)
    for block in fence_matches:
        try:
            return json.loads(block.strip())
        except Exception:
            continue

    # fallback: find all {...} substrings and try the largest first
    obj_matches = re.findall(r"\{[\s\S]*?\}", text)
    if obj_matches:
        # try largest to smallest
        for candidate in sorted(obj_matches, key=len, reverse=True):
            try:
                return json.loads(candidate)
            except Exception:
                continue

    raise ValueError("No valid JSON object found in text")


# ============================================================================
# TOOL INPUT SCHEMAS
# ============================================================================


TOOL_INPUT_MODELS = {
    "log_interaction": LogInteractionArguments,
    "edit_interaction": EditInteractionArguments,
    "get_interaction": GetInteractionArguments,
    "delete_interaction": DeleteInteractionArguments,
    "summarize_interaction": SummarizeInteractionArguments,
}


# ============================================================================
# TOOL 1: LOG_INTERACTION
# ============================================================================
def log_interaction(user_input: str) -> Dict[str, Any]:
    """
    Log a new HCP interaction using strict schema output.
    """
    system_prompt = """You are an expert at extracting healthcare interaction details from natural language.

Return ONLY a single JSON object matching the following schema:
- hcp_name: string
- hcp_type: string or null
- interaction_type: string or null
- date: string in DD-MM-YYYY format or null
- time: string in HH:MM format or null
- attendees: string or null
- topics_discussed: string or null
- materials_shared: list of objects with a single key `type` and string values
- samples_distributed: list of objects with keys `name`, optional `quantity`, optional `description`
- sentiment: string or null
- outcomes: string or null
- follow_up_actions: string or null

materials_shared MUST be a list of objects, for example:
[{"type": "brochure"}]

Do not return raw strings inside materials_shared.
Do not return any text outside the JSON object.
If a field is absent, set it to null or an empty list as appropriate."""

    response_text = call_groq_llm(user_input, system_prompt)
    try:
        payload = _extract_json_from_text(response_text)
    except Exception as exc:
        return {
            "success": False,
            "tool": "log_interaction",
            "message": "LLM output did not contain valid JSON",
            "error": str(exc),
            "raw_output": response_text,
        }

    try:
        interaction = HCPInteractionCreate.parse_obj(payload)
    except ValidationError as exc:
        return {
            "success": False,
            "tool": "log_interaction",
            "message": "LLM output did not match the strict interaction schema",
            "error": exc.errors(),
            "raw_output": payload,
        }

    interaction_data = interaction.dict()
    if not interaction_data.get("date"):
        interaction_data["date"] = date.today().strftime("%d-%m-%Y")
    if not interaction_data.get("time"):
        interaction_data["time"] = datetime.now().strftime("%H:%M")

    return {
        "success": True,
        "tool": "log_interaction",
        "message": f"Extracted interaction for {interaction_data['hcp_name']}",
        "data": interaction_data,
    }


# ============================================================================
# TOOL 2: EDIT_INTERACTION
# ============================================================================
def edit_interaction(current: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Apply validated partial updates to the current interaction.

    Expected call signature (strict):
      - current: current interaction state (dict)
      - updates: ONLY the fields to change (partial dict)

    Robustness:
      If upstream accidentally nests the fields under fallback keys like
      `changed_fields` or `data`, we accept them.

    Returns:
      - success: bool
      - tool: str
      - message: str
      - updated_interaction_data: dict (merged)
      - updated_fields: dict (only the provided/changed fields)
    """

    try:
        # Normalize fallback shapes from misbehaving callers.
        if not isinstance(updates, dict):
            # If a wrong type is passed, fail cleanly.
            return {
                "success": False,
                "tool": "edit_interaction",
                "message": "`updates` must be an object",
                "error": {"type": str(type(updates))},
            }

        fallback_updates = updates
        if "updates" not in updates and isinstance(updates, dict):
            # LLM might send: {changed_fields: {...}} or {data: {...}}
            if "changed_fields" in updates and isinstance(updates["changed_fields"], dict):
                fallback_updates = updates["changed_fields"]
            elif "data" in updates and isinstance(updates["data"], dict):
                fallback_updates = updates["data"]

        if fallback_updates is None:
            fallback_updates = {}

        # Validate provided partial fields against schema.
        if fallback_updates:
            validated = HCPInteractionUpdate.parse_obj(fallback_updates)
            updated_fields = validated.dict(exclude_none=True)
        else:
            updated_fields = {}

        # Merge partial updates onto existing state.
        merged = dict(current or {})
        merged.update(updated_fields)

        return {
            "success": True,
            "tool": "edit_interaction",
            "message": "Interaction updated successfully",
            "updated_fields": updated_fields,
            "updated_interaction_data": merged,
        }

    except ValidationError as exc:
        return {
            "success": False,
            "tool": "edit_interaction",
            "message": "Provided updates did not match the update schema",
            "error": exc.errors(),
        }
    except Exception as exc:
        return {
            "success": False,
            "tool": "edit_interaction",
            "message": "Tool execution failed",
            "error": str(exc),
        }



# ============================================================================
# TOOL 3: GET_INTERACTION
# ============================================================================
def get_interaction(interaction_id: int) -> Dict[str, Any]:
    """Fetch a persisted interaction by ID."""
    db = SessionLocal()
    try:
        interaction = db.query(HCPInteraction).filter(HCPInteraction.id == interaction_id).first()
        if not interaction:
            return {
                "success": False,
                "tool": "get_interaction",
                "message": "Interaction not found",
            }
        result = HCPInteractionResponse.model_validate(interaction).model_dump()
        return {
            "success": True,
            "tool": "get_interaction",
            "message": "Interaction retrieved",
            "data": result,
        }
    finally:
        db.close()


# ============================================================================
# TOOL 4: DELETE_INTERACTION
# ============================================================================
def delete_interaction(interaction_id: int) -> Dict[str, Any]:
    """Delete a persisted interaction by ID."""
    db = SessionLocal()
    try:
        interaction = db.query(HCPInteraction).filter(HCPInteraction.id == interaction_id).first()
        if not interaction:
            return {
                "success": False,
                "tool": "delete_interaction",
                "message": "Interaction not found",
            }
        db.delete(interaction)
        db.commit()
        return {
            "success": True,
            "tool": "delete_interaction",
            "message": "Interaction deleted",
        }
    finally:
        db.close()


# ============================================================================
# TOOL 5: SUMMARIZE_INTERACTION
# ============================================================================
def summarize_interaction(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a concise summary of an interaction."""
    system_prompt = """You are an expert summarizer for healthcare interaction records.
Respond with a short natural-language summary of the interaction data.
Do not return JSON. Only return plain text."""

    prompt = (
        "Summarize this HCP interaction in two sentences:\n\n"
        f"{json.dumps(interaction_data, indent=2, default=str)}"
    )
    summary = call_groq_llm(prompt, system_prompt)
    return {
        "success": True,
        "tool": "summarize_interaction",
        "message": "Generated a summary",
        "summary": summary.strip(),
    }


# ============================================================================
# TOOL REGISTRY
# ============================================================================
TOOLS = {
    "log_interaction": log_interaction,
    "edit_interaction": edit_interaction,
    "get_interaction": get_interaction,
    "delete_interaction": delete_interaction,
    "summarize_interaction": summarize_interaction,
}


# ============================================================================
# TOOL EXECUTION
# ============================================================================
def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool with strongly typed arguments."""
    if tool_name not in TOOLS:
        return {
            "success": False,
            "tool": tool_name,
            "message": f"Unknown tool: {tool_name}",
        }

    if tool_name in TOOL_INPUT_MODELS:
        try:
            TOOL_INPUT_MODELS[tool_name].parse_obj(kwargs)
        except ValidationError as exc:
            return {
                "success": False,
                "tool": tool_name,
                "message": "Tool arguments did not match schema",
                "error": exc.errors(),
            }

    try:
        return TOOLS[tool_name](**kwargs)
    except TypeError as exc:
        return {
            "success": False,
            "tool": tool_name,
            "message": f"Invalid tool arguments: {str(exc)}",
        }
    except Exception as exc:
        return {
            "success": False,
            "tool": tool_name,
            "message": f"Tool execution failed: {str(exc)}",
        }
