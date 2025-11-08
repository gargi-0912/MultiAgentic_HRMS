
# hr_supervisor/orchestrator.py
# hr_supervisor/orchestrator.py

from dotenv import load_dotenv
import os
from build_all_agents import build_all_agents

# Load environment variables
load_dotenv()

# ------------------ Load Model ------------------
# from langchain_groq import ChatGroq
# model = ChatGroq(
#     groq_api_key=os.getenv("GROQ_API_KEY"),
#     model="llama-3.1-8b-instant",  # Alternatives: "mixtral-8x7b-32768", "gemini-2.0-flash" llama-3.1-70b-instant llama-3.1-8b-instant
#     temperature=0
# )

from langchain_google_genai import ChatGoogleGenerativeAI
# model = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     google_api_key=os.getenv("GOOGLE_API_KEY"),
#     temperature=0
# )
from langchain_google_genai import ChatGoogleGenerativeAI  #model="llama3-8b-8192"  llama-3.1-8b-instant
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
# model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# from langchain_groq import ChatGroq
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
# model = ChatGroq(model="llama-3.1-8b-instant")
# ✅ Build all agents
agents = build_all_agents(model)
print("✅ Agents built successfully.")


print("✅ Loaded Agents:")
for agent in agents:
    print(f" - {agent.name}")

    

# ------------------ Supervisor Prompt ------------------
supervisor_prompt = """
You are the HR Orchestrator.

## Available Agents:
1. hr_leave_type_agent → handles leave actions (apply, approve, reject).
2. hr_work_type_agent → handles work from home (WFH) actions (apply, approve, reject).
3. fallback_agent → handles irrelevant, unclear, or off-topic queries.

## Routing Rules:
Choose exactly ONE agent per user query.
If the query is about leave → route to hr_leave_type_agent.
If the query is about work from home (WFH) → route to hr_work_type_agent.
Otherwise → route to fallback_agent.

## Important:
Once the chosen agent/tool provides a valid response, STOP and return that response to the user.
Do NOT keep routing the response back to yourself or to another agent.
Never echo the user’s input back. Your job is routing + termination.
"""

# ------------------ Supervisor Workflow ------------------
from langgraph_supervisor import create_supervisor
from langgraph.graph import END


# ✅ Create supervisor
workflow = create_supervisor(
    agents=agents,
    model=model,
    prompt=supervisor_prompt
)



# Compile
app = workflow.compile()

# ------------------ Run Agent Workflow ------------------
def run_agent_workflow(user_message: str):
    """
    Runs the LangGraph agent workflow with supervisor routing.

    Args:
        user_message (str): User input query.

    Returns:
        list[str]: Final cleaned responses from agents.
    """
    try:
        result = app.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            
        )
    except Exception as e:
        return [f"❌ Workflow execution failed: {str(e)}"]

    if isinstance(result, dict) and "error" in result:
        return [f"❌ {result['error']}"]

    # Extract responses
    responses = [
        msg.content for msg in result["messages"]
    ]

    # Filter out routing chatter
    filtered_responses = [
        r for r in responses
        if r.strip()
        and not r.strip().lower().startswith(("successfully transferred",
                                              "transferring back",
                                              "the user's request is",
                                              "i'll route this",
                                              "i'm back",
                                              "the response is not appropriate"))
    ]

    # Ensure not echoing user input
    filtered_responses = [
        r for r in filtered_responses
        if r.strip().lower() != user_message.strip().lower()
    ]

    return filtered_responses or ["⚠️ No valid response from agent. Please try again."]

# ------------------ Example Usage ------------------
if __name__ == "__main__":
    query = "Apply for sick leave from 2037-07-29 to 2037-07-30, I'm feeling unwell."
    # query = "approve the leave of id 31"
    print(run_agent_workflow(query))