"""Compatibility wrapper.

The repository previously had an imperative agent.
For the assignment we must use a real LangGraph workflow.

`langgraph_agent.py` contains the actual LangGraph StateGraph.
This file keeps the old import path (`from agent import get_agent`)
used by `backend/main.py`.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from langgraph_agent import run_agent


class HCPInteractionAgent:
    def chat(
        self,
        user_message: str,
        current_interaction: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return run_agent(user_message, current_interaction)


_agent: Optional[HCPInteractionAgent] = None


def get_agent() -> HCPInteractionAgent:
    global _agent
    if _agent is None:
        _agent = HCPInteractionAgent()
    return _agent

