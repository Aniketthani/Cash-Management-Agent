from typing import TypedDict, List
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from core.tools import (
    _get_current_cash_balance,
    _get_top_cash_outflows_last_30_days
)

# -------------------------------------------------
# Agent State
# -------------------------------------------------
class AgentState(TypedDict):
    messages: List

# -------------------------------------------------
# LLM (Groq)
# -------------------------------------------------
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0
)

# -------------------------------------------------
# Finance Agent Logic
# -------------------------------------------------
def finance_agent(state: AgentState):
    user_query = state["messages"][-1].content.lower()

    # ===============================
    # WHY IS CASH REDUCING?
    # ===============================
    if "why" in user_query and "cash" in user_query:
        balance = _get_current_cash_balance()
        outflows = _get_top_cash_outflows_last_30_days()

        if not outflows["outflows"]:
            response = "Insufficient recent transaction data to explain cash reduction."
        else:
            lines = [
                "Your cash is reducing mainly due to the following expenses (last 30 days):"
            ]

            for item in outflows["outflows"]:
                lines.append(
                    f"- {item['category']}: approximately ₹{int(item['total_spent'])}"
                )

            lines.append(
                f"\nCurrent available cash balance is approximately ₹{int(balance['balance'])}."
            )

            response = "\n".join(lines)

        return {
            "messages": state["messages"] + [AIMessage(content=response)]
        }

    # ===============================
    # CURRENT BALANCE
    # ===============================
    if "balance" in user_query:
        balance = _get_current_cash_balance()
        response = f"Your current cash balance is approximately ₹{int(balance['balance'])}."
        return {
            "messages": state["messages"] + [AIMessage(content=response)]
        }

    # ===============================
    # CASH FLOW (LAST 30 DAYS)
    # ===============================
    if "cash flow" in user_query or "outflow" in user_query:
        outflows = _get_top_cash_outflows_last_30_days()

        if not outflows["outflows"]:
            response = "No cash outflow data available for the last 30 days."
        else:
            lines = ["Top cash outflows in the last 30 days:"]
            for item in outflows["outflows"]:
                lines.append(
                    f"- {item['category']}: approximately ₹{int(item['total_spent'])}"
                )
            response = "\n".join(lines)

        return {
            "messages": state["messages"] + [AIMessage(content=response)]
        }

    # ===============================
    # FALLBACK (EXPLANATION ONLY)
    # ===============================
    llm_response = llm.invoke([
        HumanMessage(
            content=(
                "You are a cash management assistant for an Indian company.\n"
                "Currency is INR.\n"
                "Explain clearly and concisely:\n\n"
                f"{state['messages'][-1].content}"
            )
        )
    ])

    return {
        "messages": state["messages"] + [llm_response]
    }

# -------------------------------------------------
# Graph
# -------------------------------------------------
graph = StateGraph(AgentState)
graph.add_node("finance_agent", finance_agent)
graph.set_entry_point("finance_agent")

finance_graph = graph.compile()
