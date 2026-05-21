"""LangGraph-based AI agent for HCP interaction logging.

This module defines a real LangGraph StateGraph that:
1) Uses an LLM to choose which tool to call
2) Validates the tool call with strict schemas
3) Executes one of the defined tool functions
4) Produces a clean assistant response

The public entrypoint is `run_agent(message, current_interaction)`.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, List, TypedDict

from llm import chat_completion
from langgraph.graph import StateGraph, END

# Work around compatibility issue between langgraph/langchain-core
# where langchain_core expects `langchain.debug` to exist.
import langchain  # type: ignore
if not hasattr(langchain, "debug"):
    setattr(langchain, "debug", False)

from schemas import ToolCall
from tools import execute_tool, _extract_json_from_text


class AgentState(TypedDict):
    user_input: str
    current_interaction: Dict[str, Any]
    tool_call: Dict[str, Any]
    tool_result: Dict[str, Any]
    updated_interaction_data: Dict[str, Any]
    ai_response: str
    next_steps: List[str]


SYSTEM_PROMPT = """You are an AI assistant for a healthcare CRM system.

Choose exactly one tool from the following list and return only a single JSON object with two keys: `tool_name` and `arguments`.

Tools:
- log_interaction
- edit_interaction
- get_interaction
- delete_interaction
- summarize_interaction

Rules:
1. `log_interaction` is used when the user is creating or logging a new interaction.
2. `edit_interaction` is used when the user wants to change an existing interaction.
3. `get_interaction` is used when the user asks to retrieve an interaction by ID.
4. `delete_interaction` is used when the user asks to remove an interaction by ID.
5. `summarize_interaction` is used when the user asks for a short summary of the interaction.

For `log_interaction`, return arguments with:
- user_input: the full user message

For `edit_interaction`, return arguments with:
- current_data: the current interaction state
- user_input: the full user message

For `get_interaction` and `delete_interaction`, return arguments with:
- interaction_id: integer

For `summarize_interaction`, return arguments with:
- interaction_data: the current interaction state

Important schema requirement for `log_interaction` and `edit_interaction`:
- `materials_shared` must always be a list of objects with a single key `type`.
- Example: [{"type": "brochure"}]
- Do not return raw strings in materials_shared.

Example output:
{"tool_name": "log_interaction", "arguments": {"user_input": "Today I met Dr Smith, shared brochures, sentiment was positive"}}

Return only the JSON object. Do not return any additional text."""


def _extract_tool_call(text: str) -> ToolCall:
    try:
        payload = _extract_json_from_text(text)
    except Exception as exc:
        raise ValueError(f"Failed to extract tool call JSON: {exc}\nRaw output: {text}")
    return ToolCall.parse_obj(payload)


def _groq_call(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 800) -> str:
    return chat_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def decide_tool_node(state: AgentState) -> AgentState:
    user_content = state["user_input"]
    if state["current_interaction"]:
        user_content = (
            "Current interaction state:\n"
            f"{json.dumps(state['current_interaction'], indent=2, default=str)}\n\n"
            "Use this state to decide whether to log a new interaction or edit the existing one. "
            "If the user is correcting fields, choose edit_interaction and provide only the changed fields. "
            "Do not invent unrelated values.\n\n"
            f"User request: {state['user_input']}"
        )

    raw = _groq_call(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=300,
    )

    tool_call = _extract_tool_call(raw)
    state["tool_call"] = tool_call.dict()
    return state


def execute_tool_node(state: AgentState) -> AgentState:
    tool_call = state["tool_call"]
    tool_name = tool_call["tool_name"]
    arguments = tool_call["arguments"]

    state["tool_result"] = execute_tool(tool_name, **arguments)
    state["updated_interaction_data"] = arguments.get("current_data", {})

    if state["tool_result"].get("success") and state["tool_result"].get("data"):
        state["updated_interaction_data"] = state["tool_result"]["data"]
    if state["tool_result"].get("success") and state["tool_result"].get("updated_fields"):
        updated = dict(state["updated_interaction_data"])
        updated.update(state["tool_result"]["updated_fields"])
        state["updated_interaction_data"] = updated

    return state


def generate_ai_response_node(state: AgentState) -> AgentState:
    tool_result = state["tool_result"]
    tool_name = state["tool_call"].get("tool_name", "unknown")
    user_input = state["user_input"]

    ai_messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Summarize the outcome of the tool execution in three short bullets.",
        },
        {
            "role": "user",
            "content": (
                f"User message: {user_input}\n"
                f"Tool called: {tool_name}\n"
                f"Tool result: {json.dumps(tool_result, default=str)}"
            ),
        },
    ]

    raw = _groq_call(ai_messages, temperature=0.5, max_tokens=250)
    state["ai_response"] = raw.strip()

    next_steps: List[str] = []
    for line in raw.split("\n"):
        if any(keyword in line.lower() for keyword in ["next", "follow", "recommend", "schedule", "send"]):
            next_steps.append(line.strip("-• "))
    state["next_steps"] = next_steps[:3]

    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("decide_tool", decide_tool_node)
    graph.add_node("execute_tool", execute_tool_node)
    graph.add_node("respond", generate_ai_response_node)

    graph.set_entry_point("decide_tool")
    graph.add_edge("decide_tool", "execute_tool")
    graph.add_edge("execute_tool", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


_graph = build_graph()


def run_agent(user_message: str, current_interaction: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if current_interaction is None:
        current_interaction = {}

    state: AgentState = {
        "user_input": user_message,
        "current_interaction": current_interaction,
        "tool_call": {},
        "tool_result": {},
        "updated_interaction_data": current_interaction.copy(),
        "ai_response": "",
        "next_steps": [],
    }

    out = _graph.invoke(state)
    return {
        "status": "success",
        "tool_used": out["tool_call"].get("tool_name"),
        "ai_response": out.get("ai_response", ""),
        "updated_interaction_data": out.get("updated_interaction_data", {}),
        "next_steps": out.get("next_steps", []),
        "tool_result": out.get("tool_result", {}),
    }

