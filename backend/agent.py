from langgraph.graph import StateGraph
from typing import TypedDict
from groq import Groq

# ✅ Define state schema (MANDATORY)
class AgentState(TypedDict):
    input: str
    output: str

client = Groq(api_key="YOUR_GROQ_API_KEY")

# ✅ Agent node
def agent_node(state: AgentState):
    user_input = state["input"]

    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[{"role": "user", "content": user_input}]
    )

    return {
        "output": response.choices[0].message.content
    }

# ✅ Pass schema here

graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.set_entry_point("agent")

app = graph.compile()