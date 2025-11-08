

# # # # //////////////
# import typing
# try:
#     from typing import NotRequired
# except ImportError:
#     from typing_extensions import NotRequired
#     typing.NotRequired = NotRequired

# import os
# import psycopg2
# import uuid
# from datetime import datetime
# from fastapi import FastAPI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import logging

# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph_supervisor import create_supervisor
# from langgraph.prebuilt import create_react_agent
# from langmem import create_manage_memory_tool, create_search_memory_tool
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

# load_dotenv()
# app = FastAPI()

# # configure logging
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# logging.basicConfig(level=LOG_LEVEL)
# logger = logging.getLogger("hr_assistant")


# # -----------------------------
# # Postgres-backed memory store
# # -----------------------------
# class PostgresMemoryStore:
#     def __init__(self, dsn):
#         self.conn = psycopg2.connect(dsn)
#         self.conn.autocommit = True
#         self._ensure_table()

#     def _ensure_table(self):
#         with self.conn.cursor() as cur:
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS agent_memories8 (
#                     id SERIAL PRIMARY KEY,
#                     thread_id TEXT NOT NULL,
#                     agent_name TEXT NOT NULL,
#                     role TEXT NOT NULL, -- 'user' or 'assistant' or 'tool'
#                     message TEXT NOT NULL,
#                     created_at TIMESTAMP DEFAULT NOW()
#                 );
#             """)
#         logger.info("[Memory Store] Table ensured: agent_memories8")

#     def save_message(self, thread_id: str, agent_name: str, role: str, message: str):
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 """
#                 INSERT INTO agent_memories8 (thread_id, agent_name, role, message, created_at)
#                 VALUES (%s, %s, %s, %s, %s)
#                 """,
#                 (thread_id, agent_name, role, message, datetime.utcnow()),
#             )
#         logger.debug(f"[Memory Saved] {role} ({agent_name}) -> {message}")

#     def get_history(self, thread_id: str, limit: int = 200):
#         """Fetch history (default 200)"""
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 """
#                 SELECT role, message, created_at, agent_name
#                 FROM agent_memories8
#                 WHERE thread_id=%s
#                 ORDER BY created_at ASC
#                 LIMIT %s
#                 """,
#                 (thread_id, limit),
#             )
#             rows = cur.fetchall()
#             return [
#                 {"role": r, "agent": a, "message": m, "created_at": str(c)}
#                 for (r, m, c, a) in rows
#             ]

#     def get_recent_history(self, thread_id: str, limit: int = 8):
#         """Fetch only last `limit` messages (default 8)"""
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 """
#                 SELECT role, message, created_at, agent_name
#                 FROM agent_memories8
#                 WHERE thread_id=%s
#                 ORDER BY created_at DESC
#                 LIMIT %s
#                 """,
#                 (thread_id, limit),
#             )
#             rows = cur.fetchall()
#             # reverse to maintain chronological order
#             rows.reverse()
#             return [
#                 {"role": r, "agent": a, "message": m, "created_at": str(c)}
#                 for (r, m, c, a) in rows
#             ]

#     def clear_history(self, thread_id: str):
#         """Delete all memory for a given thread"""
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 "DELETE FROM agent_memories8 WHERE thread_id=%s",
#                 (thread_id,),
#             )
#         logger.info(f"[Memory Cleared] thread_id={thread_id}")


# # -----------------------------
# # Pydantic schema
# # -----------------------------
# from typing import Optional
# class Query(BaseModel):
#     message: str
#     thread_id: str = "default-thread"
#     username: str

#     # # added by me
#     # role: str
#     # emp_id: Optional[int] = None  # Add this field
#     # token: str


# # -----------------------------
# # Global setup
# # -----------------------------
# POSTGRES_DSN = os.getenv(
#     "POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb"
# )
# store = PostgresMemoryStore(POSTGRES_DSN)

# namespace = ("agent_memories8",)
# checkpointer = MemorySaver()

# # Memory tools (explicit)
# memory_tools = [
#     create_manage_memory_tool(namespace, store=store),
#     create_search_memory_tool(namespace, store=store),
# ]


# # -----------------------------
# # Supervisor & Agents
# # -----------------------------
# async def setup_supervisor():
#     client = MultiServerMCPClient(
#         {
#             "applyleave": {
#                 "url": "http://0.0.0.0:8002/mcp",
#                 "transport": "streamable_http",
#             },
#             "worktypeserver": {
#                 "url": "http://0.0.0.0:8003/mcp",
#                 "transport": "streamable_http",
#             },
#         }
#     )

#     try:
#         tools = await client.get_tools()
#         logger.info(f"[MCP] Discovered {len(tools)} tools from MCP.")
#     except Exception as e:
#         tools = []
#         logger.exception("[MCP] Error while fetching tools: %s", e)

#     tool_names = []
#     for t in tools:
#         try:
#             tool_names.append(getattr(t, "name", str(t)))
#         except Exception:
#             tool_names.append(str(t))
#     logger.info("[MCP] Tools: %s", tool_names)

#     leave_tools = [t for t in tools if "leave" in getattr(t, "name", "").lower() or "leave" in str(t).lower()]
#     worktype_tools = [t for t in tools if "worktype" in getattr(t, "name", "").lower() or "workfromhome" in getattr(t, "name", "").lower() or "wfh" in getattr(t, "name", "").lower() or "worktype" in str(t).lower()]

#     from langchain_google_genai import ChatGoogleGenerativeAI
#     # os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
#     import random
#     api_keys = [
#         os.getenv("GOOGLE_API_KEY_1"),
#         os.getenv("GOOGLE_API_KEY_2"),
#         os.getenv("GOOGLE_API_KEY_3"),
#     ]

#     # Filter out any None values (in case some are missing)
#     api_keys = [key for key in api_keys if key]

#     # Pick a random one
#     if api_keys:
#         selected_api = random.choice(api_keys)
#         os.environ.setdefault("GOOGLE_API_KEY", selected_api)
#     else:
#         raise ValueError("No Google API keys found in environment variables")
#     model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

  
#     leave_prompt = (
#     "You are the Leave Agent. ONLY handle leave-related requests (apply, approve, reject, cancel, check status).\n"
#     "RULES (MANDATORY):\n"
#     "1) For ANY leave-related action, you MUST call the correct leave tool (apply/approve/reject/etc.).\n"
#     "2) If extra context is required (like employee details, previous leave history), first call memory tools.\n"
#     "3) Never answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#     "4) Only produce a short summary AFTER tool execution, and MUST include the raw tool output inside it.\n"
#     "5) Do NOT hallucinate values (e.g., leave IDs, status). Always rely on tool/database output.\n"
#     )
#     worktype_prompt = (
#     "You are the WorkType Agent. ONLY handle worktype-related requests (e.g., Work From Home or WFH or wfh , Shift changes).\n"
#     "RULES (MANDATORY):\n"
#     "1) For ANY worktype action (apply/approve/reject/query), you MUST call the correct worktype tool.\n"
#     "2) If user context is missing, first call memory tools.\n"
#     "3) NEVER guess worktype names/IDs. Always confirm via tools.\n"
#     "4) Do not answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#     "5) Only give a summary AFTER tool execution, embedding the raw tool output inside.\n"
#     "6)Do not hallucinate - rely on tool outputs.\n"
#     )
#     fallback_prompt = (
#     "You are the Fallback Agent.\n"
#     "RULES (MANDATORY):\n"
#     "1) If user asks about personal info (name, preferences, past chats), ALWAYS first call `search_memory`.\n"
#     "2) If new personal info is given, ALWAYS call `manage_memory` to store it.\n"
#     "3) If query is unrelated to HR (leave/worktype) and no relevant memory exists, politely decline.\n"
    
#     )



#     leave_agent = create_react_agent(model, leave_tools + memory_tools, name="leave_agent", prompt=leave_prompt)
#     worktype_agent = create_react_agent(model, worktype_tools + memory_tools, name="worktype_agent", prompt=worktype_prompt)
#     fallback_agent = create_react_agent(model, memory_tools, name="fallback_agent", prompt=fallback_prompt)

#     all_tools = list(memory_tools) + list(tools)
#     logger.info("[Supervisor] Attaching %d total tools (memory + MCP) to supervisor", len(all_tools))

#     supervisor = create_supervisor(
#         model=model,
#         agents=[leave_agent, worktype_agent, fallback_agent],
#         tools=all_tools,
#         store=store,
#         checkpointer=checkpointer,
        
#         prompt = (

#             "You are the HR Supervisor. Your task is to route user queries to the correct specialized agent(s).\n\n"
#             "ROUTING RULES:\n"
#             "- If the query is about **leave** (apply, approve, reject, cancel, status, previous/above leave request) "
#             "-> route to leave_agent.\n"
#             "- If the query is about **worktype** requests, including any of these synonyms:\n"
#             "   • 'Work From Home'\n"
#             "   • 'WFH' (uppercase)\n"
#             "   • 'wfh' (lowercase)\n"
#             "   • 'remote work'\n"
#             "   • 'shift change'\n"
#             "   Then route to worktype_agent.\n"
#             "- If the query involves BOTH leave + worktype in the same request -> call BOTH agents in parallel.\n"
#             "- Otherwise -> fallback_agent.\n\n"
#             "MANDATORY EXECUTION RULES:\n"
#             "1) ALWAYS include only the last 8 messages from Postgres when preparing tool calls.\n"
#             "2) If the user refers to 'above request', 'previous request', or similar:\n"
#             "   - Resolve it using the last stored request_id from memory/context.\n"
#             "   - Example: if last WFH request had id=18 and user says 'approve above WFH request', call worktype_request_approve_tool(req_id=18).\n"
#             "   - Example: if last WFH request had id=21 and user says 'reject above request', call worktype_request_reject_tool(req_id=21).\n"
#             "3) User may write 'Work From Home', 'WFH', 'wfh', or 'remote work' interchangeably. Always treat them as worktype requests.\n"
#             "4) If a tool exists for the requested action, the chosen agent MUST call that tool. Never generate a direct text answer.\n"
#             "5) When tools are called, the supervisor MUST return their ToolMessage(s) as the canonical result.\n"
#             "6) Agents must NOT re-run tools unless explicitly required by missing/incorrect data.\n"
#             "7) Always prioritize accurate execution through tools over generating natural language responses.\n"
#         )



#     )
   

#     try:
#         compiled = supervisor.compile()
#         logger.info("[Supervisor] Compiled successfully.")
#         return compiled
#     except Exception as e:
#         logger.exception("[Supervisor] Failed to compile: %s", e)
#         raise

# # r8
# # -----------------------------
# # API endpoints
# # -----------------------------
# @app.post("/chat")
# async def chat(query: Query):
#     supervisor = await setup_supervisor()
   
#     request_id = str(uuid.uuid4())

#     store.save_message(query.thread_id, "user", "user", query.message)

#     # Only fetch last 8 messages
#     history = store.get_recent_history(query.thread_id, limit=8)
#     history_messages = []
#     for h in history:
#         if h["role"] == "user":
#             history_messages.append(HumanMessage(content=h["message"]))
#         else:
#             history_messages.append(AIMessage(content=h["message"]))

#     messages_invoke = history_messages + [HumanMessage(content=query.message)]

#     try:
#         response_state = await supervisor.ainvoke(
#             {"messages": messages_invoke},
#             config={"configurable": {"thread_id": query.thread_id}},
#         )
#     except Exception as e:
#         logger.exception("[Supervisor] ainvoke failed: %s", e)
#         return {
#             "request_id": request_id,
#             "thread_id": query.thread_id,
#             "response": f"Supervisor execution failed: {e}",
#             "history": store.get_recent_history(query.thread_id),
#         }

#     last_tool_response = None
#     saved = False
#     for msg in reversed(response_state.get("messages", [])):
#         try:
#             if isinstance(msg, ToolMessage):
#                 tool_name = getattr(msg, "tool_name", None) or getattr(msg, "tool", None) or None
#                 content = getattr(msg, "content", None) or str(msg)
#                 agent_name = tool_name or "tool"
#                 store.save_message(query.thread_id, agent_name, "tool", content)
#                 last_tool_response = content
#                 saved = True
#                 logger.info("[Chat] ToolMessage saved from %s", agent_name)
#                 break
#             elif isinstance(msg, AIMessage):
#                 content = getattr(msg, "content", None) or str(msg)
#                 store.save_message(query.thread_id, "assistant", "assistant", content)
#                 last_tool_response = content
#                 saved = True
#                 logger.info("[Chat] AIMessage saved as assistant response.")
#                 break
#         except Exception as e:
#             logger.exception("[Chat] Error processing message object: %s", e)
#             try:
#                 text = str(msg)
#                 store.save_message(query.thread_id, "assistant", "assistant", text)
#                 last_tool_response = text
#                 saved = True
#                 break
#             except Exception:
#                 continue

#     if not saved:
#         try:
#             raw_out = response_state.get("output") or response_state.get("result") or str(response_state)
#             store.save_message(query.thread_id, "assistant", "assistant", str(raw_out))
#             last_tool_response = str(raw_out)
#             logger.warning("[Chat] No typed messages; saved raw response_state.")
#         except Exception as e:
#             logger.exception("[Chat] Could not save fallback supervisor output: %s", e)
#             last_tool_response = "No valid response produced by supervisor."

#     return {
#         "request_id": request_id,
#         "thread_id": query.thread_id,
#         "response": last_tool_response,
#         "history": store.get_recent_history(query.thread_id),
#     }


# @app.get("/memory/{thread_id}")
# def get_memory(thread_id: str):
#     return {"thread_id": thread_id, "history": store.get_recent_history(thread_id)}


# @app.post("/memory/{thread_id}/refresh")
# def refresh_memory(thread_id: str):
#     store.clear_history(thread_id)
#     return {"thread_id": thread_id, "status": "Memory cleared successfully"}

# # ........


# # 2
# import typing
# try:
#     from typing import NotRequired
# except ImportError:
#     from typing_extensions import NotRequired
#     typing.NotRequired = NotRequired

# import os
# import psycopg2
# import uuid
# import random
# from contextlib import asynccontextmanager
# from datetime import datetime
# from fastapi import FastAPI, Request, HTTPException
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import logging

# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph_supervisor import create_supervisor
# from langgraph.prebuilt import create_react_agent
# from langmem import create_manage_memory_tool, create_search_memory_tool
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI

# # --- Load Environment Variables and Configure Logging ---
# load_dotenv()
# logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
# logger = logging.getLogger("hr_assistant_supervisor")


# # --- FastAPI Lifespan for Startup Initialization ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Application startup: Initializing agent supervisor...")
    
#     # Using app.state to store the supervisor object
#     api_keys = [key for key in [os.getenv("GOOGLE_API_KEY_3"), os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")] if key]
#     if not api_keys:
#         raise ValueError("No Google API keys found in environment variables")
#     selected_api_key = random.choice(api_keys)
#     os.environ.setdefault("GOOGLE_API_KEY", selected_api_key)
#     model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
#     # Fetch MCP Tools
#     client = MultiServerMCPClient({
#         "applyleave": {"url": "http://0.0.0.0:8002/mcp", "transport": "streamable_http"},
#         "worktypeserver": {"url": "http://0.0.0.0:8003/mcp", "transport": "streamable_http"},
#     })
#     try:
#         mcp_tools = await client.get_tools()
#         logger.info(f"[MCP] Discovered {len(mcp_tools)} tools from MCP.")
#     except Exception as e:
#         mcp_tools = []
#         logger.exception("[MCP] Error fetching tools: %s", e)

#     # Create and Compile Supervisor
#     supervisor = create_agent_supervisor(model, mcp_tools)
#     app.state.supervisor = supervisor.compile()
#     logger.info("[Supervisor] Compiled successfully and is ready to serve requests.")
    
#     yield
    
#     logger.info("Application shutdown: Cleaning up resources.")

# app = FastAPI(lifespan=lifespan)


# # --- Postgres-backed memory store ---
# class PostgresMemoryStore:
#     def __init__(self, dsn):
#         self.conn = psycopg2.connect(dsn)
#         self.conn.autocommit = True
#         self._ensure_table()

#     def _ensure_table(self):
#         with self.conn.cursor() as cur:
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS agent_memories9 (
#                     id SERIAL PRIMARY KEY,
#                     thread_id TEXT NOT NULL,
#                     agent_name TEXT NOT NULL,
#                     role TEXT NOT NULL,
#                     message TEXT NOT NULL,
#                     created_at TIMESTAMP DEFAULT NOW()
#                 );
#             """)

#     def save_message(self, thread_id: str, agent_name: str, role: str, message: str):
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 "INSERT INTO agent_memories9 (thread_id, agent_name, role, message, created_at) VALUES (%s, %s, %s, %s, %s)",
#                 (thread_id, agent_name, role, message, datetime.utcnow()),
#             )

#     def get_recent_history(self, thread_id: str, limit: int = 8):
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 "SELECT role, message FROM agent_memories9 WHERE thread_id=%s ORDER BY created_at DESC LIMIT %s",
#                 (thread_id, limit),
#             )
#             rows = cur.fetchall()
#             rows.reverse()
#             messages = []
#             for r, m in rows:
#                 if r == 'user': messages.append(HumanMessage(content=m))
#                 elif r == 'assistant': messages.append(AIMessage(content=m))
#                 elif r == 'tool': messages.append(ToolMessage(content=m))
#             return messages

#     def clear_history(self, thread_id: str):
#         with self.conn.cursor() as cur:
#             cur.execute("DELETE FROM agent_memories9 WHERE thread_id=%s", (thread_id,))
#         logger.info(f"[Memory Cleared] thread_id={thread_id}")

# # --- Pydantic Schema ---
# # The Query model is updated to expect the username from the frontend request.
# class Query(BaseModel):
#     message: str
#     thread_id: str
#     username: str

# # --- Global Setup ---
# POSTGRES_DSN = os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
# store = PostgresMemoryStore(POSTGRES_DSN)
# namespace = ("agent_memories9",)
# checkpointer = MemorySaver()

# # --- Supervisor Setup Function ---
# def create_agent_supervisor(model, mcp_tools: list):
#     # This is your existing supervisor creation logic. No changes are needed here.
#     memory_tools = [create_manage_memory_tool(namespace, store=store), create_search_memory_tool(namespace, store=store)]
#     leave_tools = [t for t in mcp_tools if "leave" in getattr(t, "name", "").lower()]
#     worktype_tools = [t for t in mcp_tools if "worktype" in getattr(t, "name", "").lower() or "wfh" in getattr(t, "name", "").lower()]
    
#     # --- KEY CHANGE: Updated prompts with strict instructions for the agent ---
#     common_rules = (
#         "MANDATORY RULE: Before calling any tool, you MUST find the special <CONTEXT> block in the chat history. "
#         "From that block, you MUST extract the value of the auth_header and pass it as the auth_header argument to the tool you are calling. "
#         "This is not optional. Every tool call must include the auth_header argument."
#     )

#     leave_prompt = (
#             "You are the Leave Agent. ONLY handle leave-related requests (apply, approve, reject).\n{common_rules}"
#             "RULES (MANDATORY):\n"
#             "1) For ANY leave-related action, you MUST call the correct leave tool (apply/approve/reject/etc.).\n"
#             "2) If essential information for a tool is missing (e.g., start date, end date, leave type, reason), you MUST ask the user for the missing details. DO NOT guess or call the tool with incomplete arguments.\n"
#             "3) If extra context is required (like employee details, previous leave history), first call memory tools.\n"
#             "4) Never answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#             "5) Only produce a short summary AFTER tool execution, and MUST include the raw tool output inside it.\n"
#             "6) Do NOT hallucinate values (e.g., leave IDs, status). Always rely on tool/database output.\n"
#         )
#     worktype_prompt = (
#         "You are the WorkType Agent. ONLY handle worktype-related requests (e.g., Work From Home or WFH or wfh, hybrid,  Shift changes).\n{common_rules}"
#         "RULES (MANDATORY):\n"
#         "1) For ANY worktype action (apply/approve/reject/query), you MUST call the correct worktype tool.\n"
#         "2) If information required for a tool is missing (e.g., date for a WFH request, reason for rejection), you MUST ask the user for clarification. DO NOT call the tool with placeholder or missing values.\n"
#         "3) If user context is missing, first call memory tools.\n"
#         "4) NEVER guess worktype names/IDs. Always confirm via tools.\n"
#         "5) Do not answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#         "6) Only give a summary AFTER tool execution, embedding the raw tool output inside.\n"
#         "7) Do not hallucinate - rely on tool outputs.\n"
#     )
#     # fallback_prompt = (
#     #     "You are the General Assistant and Fallback Agent. Your primary role is to handle general conversation and questions that are NOT related to specific HR tasks like (apply, approve, reject) leave or worktype.\n\n"
#     #     "RULES (MANDATORY):\n"
#     #     "1) First, check if the query is about personal information. If the user asks about themselves (e.g., 'what is my name?', 'what did I ask before?'), you MUST use the search_memory tool. If they provide new information about themselves (e.g., 'my name is Alex'), you MUST use the manage_memory tool to save it.\n\n"
#     #     "2) If the query is a general question, a greeting, or conversational chit-chat (e.g., 'How are you?', 'What is the capital of France?', 'Tell me a joke'), answer it helpfully and directly. You do not need a tool for this.\n\n"
#     #     # "3) You must NOT attempt to answer questions about leave or worktype. If you are asked about these, politely state that another specialized agent should handle such requests."
#     # )
#     fallback_prompt = (
#         "You are the General Assistant and Fallback Agent. Your job is to handle general conversation, explanations, "
#         "and questions that are NOT about directly executing HR tasks (such as applying, approving, or rejecting leave, "
#         "or changing worktype).\n\n"

#         "RULES (MANDATORY):\n"
#         "1) Memory Handling:\n"
#         "   - If the user asks about their own information (e.g., 'what is my name?', 'what did I ask before?'), "
#         "use the search_memory tool.\n"
#         "   - If the user provides new personal information (e.g., 'my name is Alex'), use the manage_memory tool to save it.\n\n"

#         "2) General & Conversational Queries:\n"
#         "   - If the query is general (greetings, small talk, trivia, knowledge questions, etc.), answer directly "
#         "using your reasoning without tools.\n\n"

#         "3) HR Concept Explanations:\n"
#         "   - If the query is about HR concepts (e.g., 'what is sick leave?', 'what are different types of leave?', "
#         "'what is casual leave?', 'explain worktype'), provide a clear and helpful explanation using your knowledge.\n"
#         "   - DO NOT attempt to perform HR actions (like applying, approving, rejecting, or modifying leave/worktype).\n\n"

#         "4) Task Execution Boundary:\n"
#         "   - If the query is about performing an HR task (e.g., 'apply leave', 'approve leave', 'change my worktype'), "
#         "you must NOT answer or take any action.\n"
#         "   - Instead, return nothing so the orchestrator can route the request to the correct specialized agent.\n"
        
#     )
#     supervisor_prompt = (
#         "You are the HR Supervisor. Your task is to route user queries to the correct specialized agent(s).\n\n"
#         "ROUTING RULES:\n"
#         "- If the query is about **leave** (apply, approve, reject, cancel, status, previous/above leave request) "
#         "-> route to leave_agent.\n"
#         "- If the query is about **worktype** requests, including any of these synonyms:\n"
#         "   • 'Work From Home'\n"
#         "   • 'WFH' (uppercase)\n"
#         "   • 'wfh' (lowercase)\n"
#         "   • 'remote work'\n"
#         "   • 'shift change'\n"
#         "   Then route to worktype_agent.\n"
#         "- If the query involves BOTH leave + worktype in the same request -> call BOTH agents in parallel.\n"
#         "- Otherwise -> fallback_agent.\n\n"
#         "MANDATORY EXECUTION RULES:\n"
#         "1) ALWAYS include only the last 8 messages from Postgres when preparing tool calls.\n"
#         "2) If the user refers to 'above request', 'previous request', or similar:\n"
#         "   - Resolve it using the last stored request_id from memory/context.\n"
#         "   - Example: if last WFH request had id=18 and user says 'approve above WFH request', call worktype_request_approve_tool(req_id=18).\n"
#         "   - Example: if last WFH request had id=21 and user says 'reject above request', call worktype_request_reject_tool(req_id=21).\n"
#         "3) User may write 'Work From Home', 'WFH', 'wfh', or 'remote work' interchangeably. Always treat them as worktype requests.\n"
#         "4) If a tool exists for the requested action, the chosen agent MUST call that tool. Never generate a direct text answer.\n"
#         "5) When tools are called, the supervisor MUST return their ToolMessage(s) as the canonical result.\n"
#         "6) Agents must NOT re-run tools unless explicitly required by missing/incorrect data.\n"
#         "7) Always prioritize accurate execution through tools over generating natural language responses.\n"
#     )
#     leave_agent = create_react_agent(model, leave_tools + memory_tools, name="leave_agent", prompt=leave_prompt)
#     worktype_agent = create_react_agent(model, worktype_tools + memory_tools, name="worktype_agent", prompt=worktype_prompt)
#     fallback_agent = create_react_agent(model, memory_tools, name="fallback_agent", prompt=fallback_prompt)
#     return create_supervisor(
#         model=model,
#         agents=[leave_agent, worktype_agent, fallback_agent],
#         tools=memory_tools + mcp_tools,
#         store=store,
#         checkpointer=checkpointer,
#         prompt=supervisor_prompt
#     )

# # # --- API Endpoints ---
# @app.post("/chat")
# async def chat(query: Query, request: Request):
#     if not hasattr(request.app.state, "supervisor"):
#         raise HTTPException(status_code=503, detail="Supervisor not initialized.")
#     supervisor = request.app.state.supervisor

#     request_id = str(uuid.uuid4())
#     store.save_message(query.thread_id, "user", "user", query.message)
    
#     # --- KEY CHANGE 1: Capture User Identity ---
#     # The user's token for authentication is in the header.
#     auth_header = request.headers.get("Authorization")

#     # --- KEY CHANGE: Inject a context block directly into the message history ---
#     # This makes the auth info visible to the agent LLM.
#     context_message = HumanMessage(
#         content=f"<CONTEXT>\n<auth_header>{auth_header}</auth_header>\n</CONTEXT>\n\nUser query: {query.message}"
#     )

#     # The user's username for permission checks is in the request body.
#     logged_in_username = query.username
#     print("Logged in user:", logged_in_username)    
#     # logged_in_password = query.password
#     # print("Logged in password:", logged_in_password)

#     history_messages = store.get_recent_history(query.thread_id, limit=8)
#     # messages_to_invoke = history_messages + [HumanMessage(content=query.message)]

#     # Replace the last user message with our new combined context message
#     if history_messages and history_messages[-1].type == "human":
#         history_messages[-1] = context_message
#     else:
#         history_messages.append(context_message)
        

#     try:
#         # --- KEY CHANGE 2: Inject Identity into Agent State ---
#         # This 'metadata' is passed into the LangGraph state and becomes
#         # accessible to all tools, allowing the @manager_only decorator to work.
#         response_state = await supervisor.ainvoke(
#             {"messages": history_messages},
#         )
#     except Exception as e:
#         logger.exception("[Supervisor] ainvoke failed: %s", e)
#         return {"request_id": request_id, "thread_id": query.thread_id, "response": f"Supervisor execution failed: {e}"}

#     # Logic to extract and save the final message
#     final_response_content = "No valid response was generated."
#     final_messages = response_state.get("messages", [])
#     if final_messages:
#         last_message = final_messages[-1]
#         final_response_content = getattr(last_message, 'content', str(last_message))
#         # Persist the AI's final response to memory
#         store.save_message(query.thread_id, "assistant", "assistant", final_response_content)

#     return {
#         "request_id": request_id,
#         "thread_id": query.thread_id,
#         "response": final_response_content,
#     }
# # @app.post("/chat")
# # async def chat(query: Query, request: Request):
# #     if not hasattr(request.app.state, "supervisor"):
# #         raise HTTPException(status_code=503, detail="Supervisor not initialized.")
# #     supervisor = request.app.state.supervisor

# #     request_id = str(uuid.uuid4())
# #     store.save_message(query.thread_id, "user", "user", query.message)
    
# #     # --- KEY CHANGE 1: Capture User Identity ---
# #     auth_header = request.headers.get("Authorization")

# #     # --- KEY CHANGE: Inject a context block directly into the message history ---
# #     context_message = HumanMessage(
# #         content=f"<CONTEXT>\n<auth_header>{auth_header}</auth_header>\n</CONTEXT>\n\nUser query: {query.message}"
# #     )

# #     logged_in_username = query.username
# #     print("Logged in user:", logged_in_username)

# #     history_messages = store.get_recent_history(query.thread_id, limit=8)

# #     # Replace the last user message with our new combined context message
# #     if history_messages and history_messages[-1].type == "human":
# #         history_messages[-1] = context_message
# #     else:
# #         history_messages.append(context_message)
        
# #     try:
# #         # --- KEY CHANGE 2: Inject Identity into Agent State ---
# #         response_state = await supervisor.ainvoke(
# #             {"messages": history_messages},
# #         )
# #     except Exception as e:
# #         logger.exception("[Supervisor] ainvoke failed: %s", e)
# #         return {
# #             "request_id": request_id,
# #             "thread_id": query.thread_id,
# #             "response": f"Supervisor execution failed: {e}",
# #         }

# #     # --- FIX: Extract the final assistant message only ---
# #     final_response_content = "No valid response was generated."
# #     final_messages = response_state.get("messages", [])

# #     if final_messages:
# #         # Filter only assistant responses with real content
# #         ai_messages = [
# #             m for m in final_messages
# #             if getattr(m, "type", None) == "ai" and getattr(m, "content", None)
# #         ]
# #         print(".....................",ai_messages)

# #         if ai_messages:
# #             last_message = ai_messages[-1]  # pick last AI-generated response
# #             final_response_content = last_message.content
            

# #             # Persist the AI's final response to memory
# #             store.save_message(query.thread_id, "assistant", "assistant", final_response_content)
# #     print(final_response_content)
# #     print("=========================")
# #     return {
# #         "request_id": request_id,
# #         "thread_id": query.thread_id,
# #         "response": final_response_content,
# #     }
# @app.get("/memory/{thread_id}")
# def get_memory(thread_id: str):
#     history = store.get_recent_history(thread_id)
#     serializable_history = [{"role": m.type, "content": m.content} for m in history]
#     return {"thread_id": thread_id, "history": serializable_history}

# @app.post("/memory/{thread_id}/refresh")
# def refresh_memory(thread_id: str):
#     store.clear_history(thread_id)
#     return {"thread_id": thread_id, "status": "Memory cleared successfully"}



# # 3
# import typing
# try:
#     from typing import NotRequired
# except ImportError:
#     from typing_extensions import NotRequired
#     typing.NotRequired = NotRequired

# import os
# import psycopg2
# import uuid
# import random
# from contextlib import asynccontextmanager
# from datetime import datetime
# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import logging

# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph_supervisor import create_supervisor
# from langgraph.prebuilt import create_react_agent
# from langmem import create_manage_memory_tool, create_search_memory_tool
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI

# # --- Load Environment Variables and Configure Logging ---
# load_dotenv()
# logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
# logger = logging.getLogger("hr_assistant_supervisor")


# # --- FastAPI Lifespan for Startup Initialization ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Application startup: Initializing agent supervisor...")
    
#     # Using app.state to store the supervisor object
#     api_keys = [key for key in [ os.getenv("GOOGLE_API_KEY_3")] if key]
#     if not api_keys:
#         raise ValueError("No Google API keys found in environment variables")
#     selected_api_key = random.choice(api_keys)
#     os.environ.setdefault("GOOGLE_API_KEY", selected_api_key)
#     model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
#     # Fetch MCP Tools
#     client = MultiServerMCPClient({
#         "applyleave": {"url": "http://0.0.0.0:8002/mcp", "transport": "streamable_http"},
#         "worktypeserver": {"url": "http://0.0.0.0:8003/mcp", "transport": "streamable_http"},
#     })
#     try:
#         mcp_tools = await client.get_tools()
#         logger.info(f"[MCP] Discovered {len(mcp_tools)} tools from MCP.")
#     except Exception as e:
#         mcp_tools = []
#         logger.exception("[MCP] Error fetching tools: %s", e)

#     # Create and Compile Supervisor
#     supervisor = create_agent_supervisor(model, mcp_tools)
#     app.state.supervisor = supervisor.compile()
#     logger.info("[Supervisor] Compiled successfully and is ready to serve requests.")
    
#     yield
    
#     logger.info("Application shutdown: Cleaning up resources.")

# app = FastAPI(lifespan=lifespan)


# # --- Postgres-backed memory store ---
# class PostgresMemoryStore:
#     def __init__(self, dsn):
#         self.conn = psycopg2.connect(dsn)
#         self.conn.autocommit = True
#         self._ensure_table()

#     def _ensure_table(self):
#         with self.conn.cursor() as cur:
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS agent_memories9 (
#                     id SERIAL PRIMARY KEY,
#                     thread_id TEXT NOT NULL,
#                     agent_name TEXT NOT NULL,
#                     role TEXT NOT NULL,
#                     message TEXT NOT NULL,
#                     created_at TIMESTAMP DEFAULT NOW()
#                 );
#             """)

#     def save_message(self, thread_id: str, agent_name: str, role: str, message: str):
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 "INSERT INTO agent_memories9 (thread_id, agent_name, role, message, created_at) VALUES (%s, %s, %s, %s, %s)",
#                 (thread_id, agent_name, role, message, datetime.utcnow()),
#             )

#     def get_recent_history(self, thread_id: str, limit: int = 8):
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 "SELECT role, message FROM agent_memories9 WHERE thread_id=%s ORDER BY created_at DESC LIMIT %s",
#                 (thread_id, limit),
#             )
#             rows = cur.fetchall()
#             rows.reverse()
#             messages = []
#             for r, m in rows:
#                 if r == 'user': messages.append(HumanMessage(content=m))
#                 elif r == 'assistant': messages.append(AIMessage(content=m))
#                 elif r == 'tool': messages.append(ToolMessage(content=m))
#             return messages

#     def clear_history(self, thread_id: str):
#         with self.conn.cursor() as cur:
#             cur.execute("DELETE FROM agent_memories9 WHERE thread_id=%s", (thread_id,))
#         logger.info(f"[Memory Cleared] thread_id={thread_id}")

# # --- Pydantic Schema ---
# class Query(BaseModel):
#     message: str
#     thread_id: str
#     username: str

# # --- Global Setup ---
# POSTGRES_DSN = os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
# store = PostgresMemoryStore(POSTGRES_DSN)
# namespace = ("agent_memories9",)
# checkpointer = MemorySaver()

# # --- Supervisor Setup Function with IMPROVED PROMPTS ---
# def create_agent_supervisor(model, mcp_tools: list):
#     memory_tools = [create_manage_memory_tool(namespace, store=store), create_search_memory_tool(namespace, store=store)]
#     leave_tools = [t for t in mcp_tools if "leave" in getattr(t, "name", "").lower()]
#     worktype_tools = [t for t in mcp_tools if "worktype" in getattr(t, "name", "").lower() or "wfh" in getattr(t, "name", "").lower()]
    
#     leave_prompt = (
#         "You are the Leave Agent. ONLY handle leave-related requests (apply, approve, reject).\n"
#         "RULES (MANDATORY):\n"
#         "1) For ANY leave-related action, you MUST call the correct leave tool.\n"
#         "2) If essential information for a tool is missing (e.g., start date, end date), you MUST ask the user for the missing details. DO NOT guess.\n"
#         "3) If extra context is required (like employee details), first call memory tools.\n"
#         "4) Never answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#         "5) After a tool is executed successfully, DO NOT show the raw technical output. Instead, interpret the result and inform the user in a clear, friendly sentence. For example, say 'Your leave request has been successfully submitted!' instead of showing '{\"success\": true}'.\n"
#         "6) Do NOT hallucinate values (e.g., leave IDs, status). Always rely on tool/database output.\n"
#     )
#     worktype_prompt = (
#         "You are the WorkType Agent. ONLY handle worktype-related requests (e.g., Work From Home, hybrid, Shift changes).\n"
#         "RULES (MANDATORY):\n"
#         "1) For ANY worktype action, you MUST call the correct worktype tool.\n"
#         "2) If information required for a tool is missing (e.g., date for a WFH request), you MUST ask the user for clarification. DO NOT call the tool with missing values.\n"
#         "3) If user context is missing, first call memory tools.\n"
#         "4) NEVER guess worktype names/IDs. Always confirm via tools.\n"
#         "5) Do not answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#         "6) After a tool is executed, interpret the result and provide a clear, user-friendly summary. Do not include raw tool output in your final answer.\n"
#         "7) Do not hallucinate - rely only on tool outputs.\n"
#     )
#     # fallback_prompt = (
#     #     "You are the General Assistant. Your primary role is to handle general conversation and questions that are NOT related to HR tasks like leave or worktype.\n\n"
#     #     "RULES (MANDATORY):\n"
#     #     "1) First, check if the query is about personal information. If the user asks about themselves (e.g., 'what is my name?'), you MUST use the search_memory tool. If they provide new information (e.g., 'my name is Alex'), you MUST use the manage_memory tool to save it.\n\n"
#     #     "2) If the query is a general knowledge question, a greeting, or conversational chit-chat, answer it helpfully and directly without using a tool.\n\n"
#     #     "3) You must NOT attempt to answer questions about leave or worktype. If asked, politely state that you cannot handle such requests."
#     # )

#     fallback_prompt = (
#         "You are a friendly and helpful General Assistant. Your persona is professional, yet approachable.\n"
#         "Your primary role is to handle conversation and questions that are NOT related to specific HR tasks like leave or worktype.\n\n"
#         "RULES (MANDATORY):\n"
#         "1) **For greetings like 'Hi' or 'Hello', you MUST respond naturally and warmly.** For example, if the user says 'Hi', a good response is 'Hello! How can I help you today?'. DO NOT give robotic or system-like responses.\n\n"
#         "2) If the user asks a question about themselves (e.g., 'what is my name?'), you MUST use the search_memory tool. If they provide new information (e.g., 'my name is Alex'), you MUST use the manage_memory tool to save it.\n\n"
#         "3) For general knowledge questions, answer them directly and helpfully.\n\n"
#         "4) You MUST NOT attempt to answer questions about leave or worktype. If asked, politely state: 'I can't handle HR-specific requests myself, but I can find the right specialist for you.'"
#     )
#     supervisor_prompt = (
#         "You are the HR Supervisor. Your task is to analyze the user's query and route it to the single most appropriate agent. You must choose one of the following:\n\n"
#         "1. leave_agent: Select this for any requests related to time off, vacation, sick leave, holidays, or applying for leave. Keywords: 'leave', 'day off', 'sick', 'vacation'.\n\n"
#         "2. worktype_agent: Select this for requests about work arrangements like 'Work From Home (WFH)', 'remote work', 'shift changes', or office location. Keywords: 'WFH', 'remote', 'shift'.\n\n"
#         "3. fallback_agent: Select this for general conversation, greetings, questions about personal information ('who am I?', 'what's my name?'), or any topic not related to leave or worktype. If the user's intent is unclear, choose this agent."
#     )
    
#     leave_agent = create_react_agent(model, leave_tools + memory_tools, name="leave_agent", prompt=leave_prompt)
#     worktype_agent = create_react_agent(model, worktype_tools + memory_tools, name="worktype_agent", prompt=worktype_prompt)
#     fallback_agent = create_react_agent(model, memory_tools, name="fallback_agent", prompt=fallback_prompt)
    
#     return create_supervisor(
#         model=model,
#         agents=[leave_agent, worktype_agent, fallback_agent],
#         tools=memory_tools + mcp_tools,
#         store=store,
#         checkpointer=checkpointer,
#         prompt=supervisor_prompt
#     )

# # --- API Endpoints ---
# @app.post("/chat")
# async def chat(query: Query, request: Request):
#     if not hasattr(request.app.state, "supervisor"):
#         return {"error": "Supervisor not initialized. Please check server logs.", "status_code": 503}
#     supervisor = request.app.state.supervisor

#     request_id = str(uuid.uuid4())
#     store.save_message(query.thread_id, "user", "user", query.message)
    
#     auth_header = request.headers.get("Authorization")
#     logged_in_username = query.username
#     logger.info(f"User '{logged_in_username}' initiated a request.")
    
#     context_message_content = (
#         f"<CONTEXT>\n<auth_header>{auth_header}</auth_header>\n</CONTEXT>\n\nUser query: {query.message}"
#     )
#     history_messages = store.get_recent_history(query.thread_id, limit=6)

#     if history_messages and isinstance(history_messages[-1], HumanMessage):
#         history_messages[-1].content = context_message_content
#     else:
#         history_messages.append(HumanMessage(content=context_message_content))

#     try:
#         response_state = await supervisor.ainvoke(
#             {"messages": history_messages},
#             config={
#                 "configurable": {"thread_id": query.thread_id},
#                 "metadata": {
#                     "auth_header": auth_header,
#                     "username": logged_in_username
#                 }
#             },
#         )
#     except Exception as e:
#         logger.exception("[Supervisor] ainvoke failed: %s", e)
#         return {"request_id": request_id, "thread_id": query.thread_id, "response": f"Supervisor execution failed: {e}"}

#     # --- UPDATED: Improved logic to extract and save the final AI message ---
#     final_response_content = "Sorry, I couldn't generate a response. Please try again."
#     final_messages = response_state.get("messages", [])

#     if final_messages:
#         # Iterate backwards to find the last message from the AI.
#         # This is more reliable than just taking the last item, which could be a ToolMessage.
#         for message in reversed(final_messages):
#             if isinstance(message, AIMessage):
#                 # Ensure content is not empty or just whitespace
#                 if message.content and message.content.strip():
#                     final_response_content = message.content
#                     break  # Stop once we find the last valid AI message

#     # Persist the AI's final, clean response to memory
#     store.save_message(
#         thread_id=query.thread_id,
#         agent_name="assistant",
#         role="assistant",
#         message=final_response_content
#     )

#     return {
#         "request_id": request_id,
#         "thread_id": query.thread_id,
#         "response": final_response_content,
#     }

# @app.get("/memory/{thread_id}")
# def get_memory(thread_id: str):
#     history = store.get_recent_history(thread_id)
#     serializable_history = [{"role": m.type, "content": m.content} for m in history]
#     return {"thread_id": thread_id, "history": serializable_history}

# @app.post("/memory/{thread_id}/refresh")
# def refresh_memory(thread_id: str):
#     store.clear_history(thread_id)
#     return {"thread_id": thread_id, "status": "Memory cleared successfully"}

# # 4
# # app.py
# import typing
# try:
#     from typing import NotRequired
# except Exception:
#     from typing_extensions import NotRequired
#     typing.NotRequired = NotRequired

# import os
# import psycopg2
# import uuid
# import random
# from contextlib import asynccontextmanager
# from datetime import datetime
# from fastapi import FastAPI, Request, HTTPException
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import logging

# # langchain/langgraph imports you had
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph_supervisor import create_supervisor
# from langgraph.prebuilt import create_react_agent
# from langmem import create_manage_memory_tool, create_search_memory_tool
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI

# # --- Load Environment Variables and Configure Logging ---
# load_dotenv()
# logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
# logger = logging.getLogger("hr_assistant_supervisor")

# # --- FastAPI Lifespan for Startup Initialization ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Application startup: Initializing agent supervisor...")

#     # pick one of available GOOGLE API keys at random
#     api_keys = [key for key in [os.getenv("GOOGLE_API_KEY_3"), os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")] if key]
#     if not api_keys:
#         raise ValueError("No Google API keys found in environment variables")
#     selected_api_key = random.choice(api_keys)
#     os.environ.setdefault("GOOGLE_API_KEY", selected_api_key)

#     # model
#     model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

#     # Fetch MCP Tools
#     client = MultiServerMCPClient({
#         "applyleave": {"url": "http://0.0.0.0:8002/mcp", "transport": "streamable_http"},
#         "worktypeserver": {"url": "http://0.0.0.0:8003/mcp", "transport": "streamable_http"},
#     })
#     try:
#         mcp_tools = await client.get_tools()
#         logger.info(f"[MCP] Discovered {len(mcp_tools)} tools from MCP.")
#     except Exception as e:
#         mcp_tools = []
#         logger.exception("[MCP] Error fetching tools: %s", e)

#     # Create and Compile Supervisor
#     supervisor = create_agent_supervisor(model, mcp_tools)
#     # store compiled supervisor on app.state
#     app.state.supervisor = supervisor.compile()
#     logger.info("[Supervisor] Compiled successfully and ready to serve requests.")
#     yield
#     logger.info("Application shutdown: Cleaning up resources.")

# app = FastAPI(lifespan=lifespan)

# # --- Postgres-backed memory store ---
# class PostgresMemoryStore:
#     def __init__(self, dsn):
#         self.conn = psycopg2.connect(dsn)
#         self.conn.autocommit = True
#         self._ensure_table()

#     def _ensure_table(self):
#         with self.conn.cursor() as cur:
#             cur.execute("""
#             CREATE TABLE IF NOT EXISTS agent_memories9 (
#                 id SERIAL PRIMARY KEY,
#                 thread_id TEXT NOT NULL,
#                 agent_name TEXT NOT NULL,
#                 role TEXT NOT NULL,
#                 message TEXT NOT NULL,
#                 created_at TIMESTAMP DEFAULT NOW()
#             );
#             """)

#     def save_message(self, thread_id: str, agent_name: str, role: str, message: str):
#         with self.conn.cursor() as cur:
#             cur.execute(
#                 "INSERT INTO agent_memories9 (thread_id, agent_name, role, message, created_at) VALUES (%s, %s, %s, %s, %s)",
#                 (thread_id, agent_name, role, message, datetime.utcnow()),
#             )

    # def get_recent_history(self, thread_id: str, limit: int = 8):
    #     with self.conn.cursor() as cur:
    #         cur.execute(
    #             "SELECT role, message FROM agent_memories9 WHERE thread_id=%s ORDER BY created_at DESC LIMIT %s",
    #             (thread_id, limit),
    #         )
    #         rows = cur.fetchall()
    #     rows.reverse()
    #     messages = []
    #     for r, m in rows:
    #         if r == 'user':
    #             messages.append(HumanMessage(content=m))
    #         elif r == 'assistant':
    #             messages.append(AIMessage(content=m))
    #         elif r == 'tool':
    #             messages.append(ToolMessage(content=m))
    #         else:
    #             # unknown role: store as human
    #             messages.append(HumanMessage(content=m))
    #     return messages

#     def clear_history(self, thread_id: str):
#         with self.conn.cursor() as cur:
#             cur.execute("DELETE FROM agent_memories9 WHERE thread_id=%s", (thread_id,))
#         logger.info(f"[Memory Cleared] thread_id={thread_id}")

# # --- Pydantic Schema ---
# class Query(BaseModel):
#     message: str
#     thread_id: str
#     username: str

# # --- Global Setup ---
# POSTGRES_DSN = os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
# store = PostgresMemoryStore(POSTGRES_DSN)
# namespace = ("agent_memories9",)
# checkpointer = MemorySaver()

# # --- Supervisor Setup Function ---
# def create_agent_supervisor(model, mcp_tools: list):
#     # memory tools
#     memory_tools = [create_manage_memory_tool(namespace, store=store), create_search_memory_tool(namespace, store=store)]

#     # separate MCP tools by name
#     leave_tools = [t for t in mcp_tools if "leave" in getattr(t, "name", "").lower()]
#     worktype_tools = [t for t in mcp_tools if "worktype" in getattr(t, "name", "").lower() or "wfh" in getattr(t, "name", "").lower()]

#     # --- KEY CHANGE: common rules as one string ---
#     common_rules = (
#         "MANDATORY RULE: Before calling any tool, you MUST find the special <CONTEXT> block in the chat history. "
#         "From that block, you MUST extract the value of the auth_header and pass it as the auth_header argument to the tool you are calling. "
#         "This is not optional. Every tool call must include the auth_header argument."
#     )

#     # Note: use f-strings so {common_rules} actually gets into each prompt
#     leave_prompt = (
#         f"You are the Leave Agent. ONLY handle leave-related requests (apply, approve, reject).\n"
#         f"{common_rules}\n"
#         "RULES (MANDATORY):\n"
#         "1) For ANY leave-related action, you MUST call the correct leave tool (apply/approve/reject/etc.).\n"
#         "2) If essential information for a tool is missing (e.g., start date, end date, leave type, reason), you MUST ask the user for the missing details. DO NOT guess or call the tool with incomplete arguments.\n"
#         "3) If extra context is required (like employee details, previous leave history), first call memory tools.\n"
#         "4) Never answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#         "5) Only produce a short summary AFTER tool execution, and MUST include the raw tool output inside it.\n"
#         "6) Do NOT hallucinate values (e.g., leave IDs, status). Always rely on tool/database output.\n"
#     )

#     worktype_prompt = (
#         f"You are the WorkType Agent. ONLY handle worktype-related requests (WFH, hybrid, shift changes).\n"
#         f"{common_rules}\n"
#         "RULES (MANDATORY):\n"
#         "1) For ANY worktype action you MUST call the correct worktype tool.\n"
#         "2) If required information is missing, ask for clarification. DO NOT call the tool with placeholder values.\n"
#         "3) If user context is missing, call memory tools first.\n"
#         "4) NEVER guess worktype names/IDs. Always confirm via tools.\n"
#         "5) Do not answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
#         "6) Only give a summary AFTER tool execution, embedding the raw tool output inside.\n"
#         "7) Do not hallucinate - rely on tool outputs.\n"
#     )

#     # --- FIXED: fallback should answer conversational queries directly ---
#     fallback_prompt = (
#         "You are the General Assistant and Fallback Agent. Your job is to handle general conversation, explanations, "
#         "and questions that are NOT about directly executing HR tasks (such as applying, approving, or rejecting leave, "
#         "or changing worktype).\n\n"
#         "MANDATORY RULES:\n"
#         "1) If the user's query is a general question (greetings, knowledge, small talk, explanations), ANSWER DIRECTLY and helpfully using your reasoning.\n"
#         "2) If the user asks about their own saved info (e.g., 'what did I ask before?'), call the search_memory tool and return the result.\n"
#         "3) If the user supplies new personal info, call manage_memory to save it.\n"
#         "4) If the user explicitly requests to perform an HR action (apply leave, approve leave, change WFH), DO NOT execute that action here. Instead, respond with a short instruction message that the orchestrator should route this request to the specialized agent (leave_agent or worktype_agent). "
#         "   Example: 'This request needs to be handled by the leave agent — please route to leave_agent.'\n"
#         "5) Never pretend to have executed a tool when you haven't. Be explicit and honest.\n"
#     )

#     supervisor_prompt = (
#          "You are an expert HR Supervisor responsible for routing user queries to the correct specialized agent.\n"
#         "Answer the general question and greet the user effectively\n"
#         "Based on the user's request, choose one of the following agents:\n"
#         "- leave_agent: For any requests involving applying for, checking, approving, or discussing leave, vacation, sick days, or time off.\n"
#         "- worktype_agent: For any requests involving 'Work From Home' (WFH), shift changes, or other work arrangement queries.\n"
#         "- fallback_agent: For all other queries, including simple greetings ('Hi', 'Hello'), general questions ('What is...,Explain,Define'), and conversational chat."
        
#     )

#     # create agents
#     leave_agent = create_react_agent(model, leave_tools + memory_tools, name="leave_agent", prompt=leave_prompt)
#     worktype_agent = create_react_agent(model, worktype_tools + memory_tools, name="worktype_agent", prompt=worktype_prompt)
#     fallback_agent = create_react_agent(model, memory_tools, name="fallback_agent", prompt=fallback_prompt)

#     return create_supervisor(
#         model=model,
#         agents=[leave_agent, worktype_agent, fallback_agent],
#         tools=memory_tools + mcp_tools,
#         store=store,
#         checkpointer=checkpointer,
#         prompt=supervisor_prompt
#     )

# # --- /chat endpoint ---
# # --- /chat endpoint ---
# @app.post("/chat")
# async def chat(query: Query, request: Request):
#     if not hasattr(request.app.state, "supervisor"):
#         raise HTTPException(status_code=503, detail="Supervisor not initialized.")
#     supervisor = request.app.state.supervisor

#     request_id = str(uuid.uuid4())

#     # Save raw user message
#     store.save_message(query.thread_id, "user", "user", query.message)

#     # capture Authorization header
#     auth_header = request.headers.get("Authorization")

#     # wrap user query in context
#     context_message = HumanMessage(
#         content=f"<CONTEXT>\n<auth_header>{auth_header}</auth_header>\n</CONTEXT>\n\nUser query: {query.message}"
#     )

#     logged_in_username = query.username
#     logger.debug("Logged in user: %s", logged_in_username)

#     # fetch recent history (last 8) but only keep user messages
#     raw_history = store.get_recent_history(query.thread_id, limit=8)
#     history_messages = []
#     for h in raw_history:
#         # forward only user messages, skip assistant/tool
#         role = getattr(h, "type", None) or getattr(h, "role", None)
#         if role and role.lower() == "user":
#             history_messages.append(h)

#     # always append the new context-wrapped query
#     history_messages.append(context_message)

#     try:
#         # run supervisor
#         response_state = await supervisor.ainvoke({"messages": history_messages})
#     except Exception as e:
#         logger.exception("[Supervisor] ainvoke failed: %s", e)
#         return {
#             "request_id": request_id,
#             "thread_id": query.thread_id,
#             "response": f"Supervisor execution failed: {e}",
#         }

#     # --- Robust response selector ---
#     def _select_best_response(response_state):
#         if isinstance(response_state, dict):
#             messages = response_state.get("messages", []) or []
#         else:
#             messages = getattr(response_state, "messages", []) or []

#         normalized = []
#         for m in messages:
#             try:
#                 m_type = getattr(m, "type", None) or getattr(m, "role", None) or m.__class__.__name__.lower()
#                 m_content = getattr(m, "content", None)
#                 # ignore tool/function calls
#                 if hasattr(m, "additional_kwargs") and m.additional_kwargs.get("function_call"):
#                     continue
#             except Exception:
#                 m_type = "unknown"
#                 m_content = None
#             normalized.append({"type": m_type, "content": (m_content or "").strip(), "orig": m})

#         # 1) longest assistant/AI message
#         assistant_msgs = [
#             nm for nm in normalized
#             if nm["type"] and ("assistant" in nm["type"].lower() or "ai" in nm["type"].lower())
#             and nm["content"]
#         ]
#         if assistant_msgs:
#             best = max(assistant_msgs, key=lambda nm: len(nm["content"]))
#             return best["content"], {"picked": "longest_assistant"}

#         # 2) last meaningful human/assistant text (non-tool)
#         for nm in reversed(normalized):
#             if nm["content"] and "tool" not in str(nm["type"]).lower():
#                 return nm["content"], {"picked": "last_non_tool"}

#         # 3) concat tool outputs if exist
#         tool_texts = [nm["content"] for nm in normalized if "tool" in str(nm["type"]).lower() and nm["content"]]
#         if tool_texts:
#             return "\n\n".join(tool_texts), {"picked": "tool_concat"}

#         # 4) fallback
#         return "Sorry, I could not generate a response.", {"picked": "hard_fallback"}

#     final_response_content, debug_info = _select_best_response(response_state)

#     # Save assistant response
#     store.save_message(query.thread_id, "assistant", "assistant", final_response_content)

#     logger.debug("Response selection debug: %s", debug_info)

#     return {
#         "request_id": request_id,
#         "thread_id": query.thread_id,
#         "response": final_response_content,
#     }


# # --- Memory inspection endpoints ---
# @app.get("/memory/{thread_id}")
# def get_memory(thread_id: str):
#     history = store.get_recent_history(thread_id)
#     serializable_history = []
#     for m in history:
#         role = getattr(m, "type", None) or getattr(m, "role", None) or "unknown"
#         content = getattr(m, "content", None) or ""
#         serializable_history.append({"role": role, "content": content})
#     return {"thread_id": thread_id, "history": serializable_history}


# @app.post("/memory/{thread_id}/refresh")
# def refresh_memory(thread_id: str):
#     store.clear_history(thread_id)
#     return {"thread_id": thread_id, "status": "Memory cleared successfully"}


# 5. r8
import typing
try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired
    typing.NotRequired = NotRequired

import os
import psycopg2
import uuid
import random
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


# --- Load Environment Variables and Configure Logging ---
load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("hr_assistant_supervisor")


# --- FastAPI Lifespan for Startup Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing agent supervisor...")
    
    # Using app.state to store the supervisor object
    api_keys = [key for key in [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2"), os.getenv("GOOGLE_API_KEY_3")] if key]  #os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2"),
    if not api_keys:
        raise ValueError("No Google API keys found in environment variables")
    selected_api_key = random.choice(api_keys)
    os.environ.setdefault("GOOGLE_API_KEY", selected_api_key)
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    
    # Fetch MCP Tools
    client = MultiServerMCPClient({
        "applyleave": {"url": "http://0.0.0.0:8002/mcp", "transport": "streamable_http"},
        "worktypeserver": {"url": "http://0.0.0.0:8003/mcp", "transport": "streamable_http"},
    })
    try:
        mcp_tools = await client.get_tools()
        logger.info(f"[MCP] Discovered {len(mcp_tools)} tools from MCP.")
    except Exception as e:
        mcp_tools = []
        logger.exception("[MCP] Error fetching tools: %s", e)

    # Create and Compile Supervisor
    supervisor = create_agent_supervisor(model, mcp_tools)
    app.state.supervisor = supervisor.compile()
    logger.info("[Supervisor] Compiled successfully and is ready to serve requests.")
    
    yield
    
    logger.info("Application shutdown: Cleaning up resources.")

app = FastAPI(lifespan=lifespan)


# --- Postgres-backed memory store ---
class PostgresMemoryStore:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self._ensure_table()

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS agent_memories9 (
                    id SERIAL PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    def save_message(self, thread_id: str, agent_name: str, role: str, message: str):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO agent_memories9 (thread_id, agent_name, role, message, created_at) VALUES (%s, %s, %s, %s, %s)",
                (thread_id, agent_name, role, message, datetime.utcnow()),
            )

    def get_recent_history(self, thread_id: str, limit: int = 8):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT role, message FROM agent_memories9 WHERE thread_id=%s ORDER BY created_at DESC LIMIT %s",
                (thread_id, limit),
            )
            rows = cur.fetchall()
            rows.reverse()
            messages = []
            for r, m in rows:
                if r == 'user': messages.append(HumanMessage(content=m))
                elif r == 'assistant': messages.append(AIMessage(content=m))
                elif r == 'tool': messages.append(ToolMessage(content=m))
            return messages

    def clear_history(self, thread_id: str):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM agent_memories9 WHERE thread_id=%s", (thread_id,))
        logger.info(f"[Memory Cleared] thread_id={thread_id}")

# --- Pydantic Schema ---
# The Query model is updated to expect the username from the frontend request.
class Query(BaseModel):
    message: str
    thread_id: str
    username: str

# --- Global Setup ---
POSTGRES_DSN = os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
store = PostgresMemoryStore(POSTGRES_DSN)
namespace = ("agent_memories9",)
checkpointer = MemorySaver()

# --- Supervisor Setup Function ---
def create_agent_supervisor(model, mcp_tools: list):
    # This is your existing supervisor creation logic. No changes are needed here.
    memory_tools = [create_manage_memory_tool(namespace, store=store), create_search_memory_tool(namespace, store=store)]
    leave_tools = [t for t in mcp_tools if "leave" in getattr(t, "name", "").lower()]
    worktype_tools = [t for t in mcp_tools if "worktype" in getattr(t, "name", "").lower() or "wfh" in getattr(t, "name", "").lower()or "get_requested_worktype_requests_from_db_tool" in getattr(t, "name", "").lower()]
   
    leave_prompt = (
        "You are the Leave Agent. ONLY handle leave-related requests "
        "(apply_leave_tool, reject_leaves_tool, approve_leaves_tool, get_requested_leave_from_db_tool).\n"
        "RULES (MANDATORY):\n"
        "1) For ANY leave-related action, you MUST call the correct leave tool:\n"
        "   - Apply → apply_leave_tool\n"
        "   - Reject (single/multiple/all requests) → reject_leaves_tool\n"
        "   - Approve (single/multiple/all requests) → approve_leaves_tool\n"
        "   - List/show/fetch requested leaves → get_requested_leave_from_db_tool\n\n"
        "2) approve_leaves_tool usage:\n"
        "   - If the user provides one or multiple request IDs, call approve_leaves_tool with req_ids populated.\n"
        "   - If the user says 'approve all', 'approve every leave request', or provides no IDs, "
        "then call approve_leaves_tool without req_ids (it will auto-fetch all requested leaves from DB).\n\n"
        "3) reject_leaves_tool usage:\n"
        "   - If the user provides one or multiple request IDs, call reject_leaves_tool with req_ids populated.\n"
        "   - If the user says 'reject all', 'reject every leave request', or provides no IDs, "
        "then call reject_leaves_tool without req_ids (it will auto-fetch all requested leaves from DB).\n\n"
        "4) get_requested_leave_from_db_tool usage:\n"
        "   - ALWAYS return response in TABLE format.\n"
        "   - Use it only when the user explicitly asks to list, view, or fetch requested leaves.\n\n"
        "5) Input Handling:\n"
        "   - Accept leave start and end dates in ANY format given by user.\n"
        "   - If essential information (e.g., start date, end date, leave type, reason) is missing, "
        "ASK the user instead of guessing.\n\n"
        "6) Response Format:\n"
        "   - Never answer directly. ALWAYS return a ToolMessage when a tool is called "
        "and also include the request id(s) with the response.\n"
        "   - Only produce a short summary AFTER tool execution, and MUST include the raw tool output inside it.\n\n"
        "7) Do NOT hallucinate values (e.g., leave IDs, status). Always rely on tool/database output.\n"
    )




    worktype_prompt = (
        "You are the WorkType Agent. ONLY handle worktype-related requests (e.g., Work From Home or WFH or wfh, hybrid, get_requested_worktype_from_db_tool ).\n"
        "RULES (MANDATORY):\n"
        "1) For ANY worktype action (apply/approve/reject/get_requested_worktype_from_db_tool), you MUST call the correct worktype tool.\n"
            "-If user query is related to List, show, fetch or give details of requested work type or all requested worktype than call get_requested_worktype_from_db_tool tool and also return response in table format.\n "
            "-when this tool get_requested_worktype_from_db_tool is called return response in table format always."
        "2) If information required for a tool is missing (e.g., date for a WFH request, reason for rejection), you MUST ask the user for clarification. DO NOT call the tool with placeholder or missing values.\n"
        "3) If user context is missing, first call memory tools.\n"
        "4) NEVER guess worktype names/IDs. Always confirm via tools.\n"
        "5) Do not answer directly. ALWAYS return a ToolMessage when a tool is called.\n"
        "6) Only give a summary AFTER tool execution and also return request id eith response, embedding the raw tool output inside.\n"
        "7) Do not hallucinate - rely on tool outputs.\n"
    )
   
    supervisor_prompt = (
        "You are an expert HR Supervisor responsible for greeting effectively in short and routing user queries to the correct specialized agent.\n"
        "Answer the general question like what is leave, casual leave, sick leave and also other questions etc and greet the user effectively and understandable.\n"
        "handle all questions start from what, how, explain, and related things effectively and understandable.\n"
        "If the user asks a question about themselves (e.g., 'what is my name?'), you MUST use the memory_tools. If they provide new information (e.g., 'my name is Alex'), you MUST use the manage_memory tool to save it.\n\n"
        "Do not give response like this I have routed.... or any other unwanted response.\n"
        "Only give to the point response that user asks so as make it user friendly"
        "Based on the user's request, choose one of the following agents:\n"
        "- leave_agent: For any requests involving applying, approving, rejecting , or discussing leave, casual leave, sick leave.\n"
        "- worktype_agent: For any requests involving 'Work From Home' (WFH), hybrid, or other work arrangement queries.\n"
        # "- fallback_agent: For all other queries, including simple greetings ('Hi', 'Hello'), general questions ('What is...'), and conversational chat."
       " If you cannot find the right agent to handle a request, respond politely that you cannot help, instead of transferring to a fallback agent." 
       
    )

    # supervisor_prompt = (
    #     "You are the HR Supervisor. Your task is to route user queries to the correct specialized agent(s). Based on the user's query, select one of the following agents to perform the task: leave_agent, worktype_agent, or fallback_agent."
    # )
    leave_agent = create_react_agent(model, leave_tools + memory_tools, name="leave_agent", prompt=leave_prompt)
    worktype_agent = create_react_agent(model, worktype_tools + memory_tools, name="worktype_agent", prompt=worktype_prompt)
    # fallback_agent = create_react_agent(model, memory_tools, name="fallback_agent", prompt=fallback_prompt)
    return create_supervisor(
        model=model,
        agents=[leave_agent, worktype_agent],
        tools=memory_tools + mcp_tools,
        store=store,
        checkpointer=checkpointer,
        prompt=supervisor_prompt
    )

# --- /chat endpoint ---
@app.post("/chat")
async def chat(query: Query, request: Request):
    if not hasattr(request.app.state, "supervisor"):
        return {"error": "Supervisor not initialized. Please check server logs.", "status_code": 503}
    
    supervisor = request.app.state.supervisor
    request_id = str(uuid.uuid4())

    # --- Save user message in memory ---
    store.save_message(query.thread_id, "user", "user", query.message)

    # --- Capture user identity ---
    auth_header = request.headers.get("Authorization")
    logged_in_username = query.username

    context_message_content = (
        f"<CONTEXT>\n<auth_header>{auth_header}</auth_header>\n</CONTEXT>\n\nUser query: {query.message}"
    )

    # --- Fetch recent history from memory ---
    history_messages = store.get_recent_history(query.thread_id, limit=6)

    # Append current user message (do NOT overwrite)
    history_messages.append(HumanMessage(content=context_message_content))

    try:
        # --- Invoke supervisor with metadata ---
        response_state = await supervisor.ainvoke(
            {"messages": history_messages},
            config={
                "configurable": {"thread_id": query.thread_id},
                "metadata": {
                    "auth_header": auth_header,
                    "username": logged_in_username
                },
            },
        )
    except Exception as e:
        logger.exception("[Supervisor] ainvoke failed: %s", e)
        return {
            "request_id": request_id,
            "thread_id": query.thread_id,
            "response": f"Supervisor execution failed: {e}"
        }

    # --- Extract final AI response ---
    final_response_content = "No valid response was generated."
    final_messages = response_state.get("messages", [])
    if final_messages:
        last_message = final_messages[-1]
        final_response_content = getattr(last_message, 'content', str(last_message))
        # Save AI response to memory
        store.save_message(query.thread_id, "assistant", "assistant", final_response_content)

    return {
        "request_id": request_id,
        "thread_id": query.thread_id,
        "response": final_response_content,
    }


# --- Memory endpoints ---
@app.get("/memory/{thread_id}")
def get_memory(thread_id: str):
    history = store.get_recent_history(thread_id)
    serializable_history = [{"role": m.type, "content": m.content} for m in history]
    return {"thread_id": thread_id, "history": serializable_history}


@app.post("/memory/{thread_id}/refresh")
def refresh_memory(thread_id: str):
    store.clear_history(thread_id)
    return {"thread_id": thread_id, "status": "Memory cleared successfully"}


from typing import List

# In-memory notification store (for demo purposes)
notifications_store: List[dict] = []
 
@app.post("/notify-manager")
async def notify_manager_api(payload: dict):
    """
    External services (like leave tool) can call this to notify manager.
    """
    message = payload.get("message", "")
    if not message:
        return {"status": "failed", "reason": "No message provided"}

    notif = {"message": message, "timestamp": payload.get("timestamp", None)}
    notifications_store.append(notif)

    return {"status": "ok", "message": message}

@app.get("/notify-manager")
async def get_notifications():
    """
    Return all notifications (latest first)
    """
    return {"notifications": notifications_store[-50:]}  # last 50 notifications



from datetime import datetime
from typing import List, Dict

# In-memory store for employee-specific notifications
# notifications_employee_store: Dict[str, List[dict]] = {}
notifications_employee_store: List[dict] = []

@app.post("/notify-employee")
async def notify_employee_api(payload: dict):
    """
    External services (like approve_leaves_tool tool) can call this to notify manager.
    """
    message = payload.get("message", "")
    if not message:
        return {"status": "failed", "reason": "No message provided"}

    notif = {"message": message, "timestamp": payload.get("timestamp", None)}
    notifications_employee_store.append(notif)

    return {"status": "ok", "message": message}

@app.get("/notify-employee")
async def get_notifications():
    """
    Return all notifications (latest first)
    """
    return {"notifications": notifications_employee_store[-50:]}  # last 50 notifications
    # return {"notifications": []}

