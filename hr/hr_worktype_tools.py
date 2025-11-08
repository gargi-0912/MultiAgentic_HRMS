# # hr_worktype_tools.py
# from mcp.server.fastmcp import FastMCP
# from pydantic import BaseModel
# from typing import Literal, Annotated, Optional
# import httpx
# import json
# import asyncio

# # --- MCP server instance ---

# mcp = FastMCP("worktype_agent", port=8003, host="0.0.0.0")
# @mcp.tool()
# async def worktype_tool(
#     action: Annotated[str, Literal["get", "post", "put", "delete"]],
#     pk: int | None = None,
#     work_type: str | None = None,
#     is_active: bool = True,
#     base_url: str = "http://127.0.0.1:7000/test/base/worktypes/",
#     username: str = "admin1@gmail.com",
#     password: str = "admin@123"
# ) -> str:
#     """
#     Manage WorkTypes (GET, POST, PUT, DELETE).

#     Args:
#         action (str): "get" → fetch all or by id, 
#                       "post" → create, 
#                       "put" → update by id,
#                       "delete" → remove by id.
#         pk (int): WorkType ID (required for put/delete, optional for get).
#         work_type (str): Name of the work type (required for post/put).
#         is_active (bool): Active status (default=True).
#     """

#     login_url = "http://127.0.0.1:7000/test/auth/login/"

#     async with httpx.AsyncClient() as client:
#         #  1. Login to get token
#         login_resp = await client.post(
#             login_url,
#             json={"username": username, "password": password},
#             headers={"Content-Type": "application/json"}
#         )
#         if login_resp.status_code != 200:
#             return f" Login failed: {login_resp.text}"

#         token = login_resp.json().get("access")
#         if not token:
#             return " Login succeeded but no token returned."

#         headers = {"Authorization": f"Bearer {token}"}

#         #  GET all or by id
#         if action == "get":
#             url = f"{base_url}{pk}/" if pk else base_url
#             resp = await client.get(url, headers=headers)
#             return resp.text if resp.status_code == 200 else f" Error: {resp.text}"

#         #  POST new WorkType
#         elif action == "post":
#             if not work_type:
#                 return " 'work_type' is required to create a WorkType."
#             payload = {"work_type": work_type, "is_active": is_active}
#             resp = await client.post(base_url, json=payload, headers=headers)
#             return resp.text if resp.status_code in (200, 201) else f" Error: {resp.text}"

#         #  PUT update existing WorkType
#         elif action == "put":
#             if not pk or not work_type:
#                 return "'pk' and 'work_type' are required to update."
#             url = f"{base_url}{pk}/"
#             payload = {"work_type": work_type, "is_active": is_active}
#             resp = await client.put(url, json=payload, headers=headers)
#             return resp.text if resp.status_code in (200, 201) else f" Error: {resp.text}"

#         #  DELETE existing WorkType
#         elif action == "delete":
#             if not pk:
#                 return " 'pk' is required to delete."
#             url = f"{base_url}{pk}/"
#             resp = await client.delete(url, headers=headers)
#             return " Deleted successfully." if resp.status_code == 200 else f" Error: {resp.text}"

#         else:
#             return "Invalid action. Use 'get', 'post', 'put', or 'delete'."
        


# @mcp.tool()
# async def worktype_request_tool(
#     action: Annotated[str, Literal["post", "get"]],
#     work_type: Annotated[str, Literal["work from home", "remote", "onsite"]] | None = None,
#     requested_date: str | None = None,
#     requested_till: str | None = None,
#     description: str | None = None,
#     is_permanent_work_type: bool = False,
#     base_url: str = "http://127.0.0.1:7000/test/base/worktype-requests/"
# ) -> str:
#     """
#     Tool to create or fetch WorkType Requests.
#     (No authentication required)

#     Args:
#         action (str): 
#             - "post" → create a new WorkType request
#             - "get" → fetch all requests
#         work_type (str): Type of work requested. Options: "work from home", "remote", "onsite".
#         requested_date (str): Start date (YYYY-MM-DD) (required for post)
#         requested_till (str): End date (YYYY-MM-DD) (required for post)
#         description (str): Reason for request (required for post)
#         is_permanent_work_type (bool): Permanent request or not (default False)
#     """

#     emp_id = 2  # 🔹 Hardcoded Employee ID

#     # 🔹 Mapping work_type string to ID
#     work_type_map = {
#         "work from home": 3,
#         "remote": 4,
#         "onsite": 5,
#     }

#     async with httpx.AsyncClient() as client:

#         #  GET requests
#         if action == "get":
#             resp = await client.get(base_url)
#             return resp.text if resp.status_code == 200 else f" Error: {resp.text}"

#         #  POST request (create new)
#         elif action == "post":
#             if not work_type or not requested_date or not requested_till or not description:
#                 return " work_type, requested_date, requested_till, and description are required."

#             work_type_id = work_type_map.get(work_type.lower())
#             if not work_type_id:
#                 return f" Invalid work_type '{work_type}'. Use one of: {list(work_type_map.keys())}"

#             payload = {
#                 "employee_id": emp_id,
#                 "work_type_id": work_type_id,
#                 "requested_date": requested_date,
#                 "requested_till": requested_till,
#                 "description": description,
#                 "is_permanent_work_type": is_permanent_work_type
#             }

#             resp = await client.post(base_url, json=payload)

#             if resp.status_code in (200, 201):
#                 try:
#                     data = resp.json()
#                     req_id = data.get("id")
#                     if req_id:
#                         return f" WorkType Request for '{work_type}' submitted successfully! Request ID: {req_id}"
#                     return f" WorkType Request for '{work_type}' submitted successfully (but no ID returned)."
#                 except Exception:
#                     return f" WorkType Request for '{work_type}' submitted successfully (response parsing failed)."

#             return f" Error creating request: {resp.text}"

#         else:
#             return " Invalid action. Use 'get' or 'post'."


# @mcp.tool()
# async def worktype_request_approve_tool(
#     req_id: int,
#     base_url: str = "http://127.0.0.1:7000/test/base/worktype-requests-approve/",
#     login_url: str = "http://127.0.0.1:7000/test/auth/login/",
#     username: str = "admin1@gmail.com",
#     password: str = "admin@123"
# ) -> str:
#     """
#     Approve a WorkType request by ID after logging in.

#     Args:
#         req_id (int): ID of the WorkType request to approve.
#     """
   
#     async with httpx.AsyncClient() as client:
#         # 1️⃣ Login to get token
#         login_resp = await client.post(
#             login_url,
#             json={"username": username, "password": password},
#             headers={"Content-Type": "application/json"}
#         )
#         if login_resp.status_code != 200:
#             return f" Login failed: {login_resp.text}"
        
#         token = login_resp.json().get("access")
#         if not token:
#             return " Login succeeded but no access token returned."

#         headers = {"Authorization": f"Bearer {token}"}

#         #  Approve the worktype request
#         url = f"{base_url}{req_id}/"
#         resp = await client.put(url, headers=headers)

#         if resp.status_code == 200:
#             return f" WorkType request {req_id} approved successfully."
#         else:
#             return f" Failed to approve request {req_id}. Status: {resp.status_code}, Response: {resp.text}"



# @mcp.tool()
# async def worktype_request_reject_tool(
#     req_id: int,
#     base_url: str = "http://127.0.0.1:7000/test/base/worktype-requests-cancel/",
#     login_url: str = "http://127.0.0.1:7000/test/auth/login/",
#     username: str = "admin1@gmail.com",
#     password: str = "admin@123"
# ) -> str:
#     """
#     Reject a WorkType request by ID after logging in.

#     Args:
#         req_id (int): ID of the WorkType request to reject.
#     """
#     print("???????????")
#     async with httpx.AsyncClient() as client:
#         #  Login to get token
#         login_resp = await client.post(
#             login_url,
#             json={"username": username, "password": password},
#             headers={"Content-Type": "application/json"}
#         )
#         if login_resp.status_code != 200:
#             return f" Login failed: {login_resp.text}"
        
#         token = login_resp.json().get("access")
#         if not token:
#             return " Login succeeded but no access token returned."

#         headers = {"Authorization": f"Bearer {token}"}

#         #  reject the worktype request
#         url = f"{base_url}{req_id}/"
#         resp = await client.put(url, headers=headers)

#         if resp.status_code == 200:
#             return f" WorkType request {req_id} rejected successfully."
#         else:
#             return f" Failed to reject request {req_id}. Status: {resp.status_code}, Response: {resp.text}"

# if __name__ == "__main__":
#     mcp.run(transport="streamable-http")






# # Run MCP server
# # ------------------------------
# if __name__ == "__main__":
#     print("Worktype MCP Agent running on http://0.0.0.0:8003/mcp")
#     mcp.run("streamable-http")




# hr_worktype_tools.py
# hr_worktype_tools.py

from mcp.server.fastmcp import FastMCP
from typing import Literal, Annotated
import httpx

mcp = FastMCP("worktype_agent", port=8003, host="0.0.0.0")
AUTH_SERVICE_URL = "http://127.0.0.1:7000"


async def is_manager(auth_header: str) -> bool:
    if not auth_header or "Bearer" not in auth_header:
        return False
    
    # Point to the NEW user profile endpoint
    user_profile_url = f"{AUTH_SERVICE_URL}/test/auth/profile/"
    headers = {"Authorization": auth_header}
    
    async with httpx.AsyncClient() as client:
        try:
            # Use a GET request to retrieve user data
            response = await client.get(user_profile_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"Validation successful for user: {user_data.get('username')}")
                # Check the 'is_superuser' flag from the response
                return user_data.get("is_superuser") is True
            else:
                print(f"Token validation failed. Status: {response.status_code}, Body: {response.text}")
                return False
                
        except httpx.RequestError as e:
            print(f"An error occurred during the API call: {e}")
            return False

@mcp.tool()
async def worktype_request_tool(
    action: Annotated[str, Literal["post"]],
    work_type: Literal["work from home", "hybrid"],
    requested_date: str,
    requested_till: str,
    description: str,
    auth_header: str, # <-- KEY CHANGE: Auth is now an explicit argument
) -> str:
    """Create a new WorkType request. auth_header is a mandatory argument."""
    if not auth_header: return "Authentication error. Token is missing."
    
    headers = {"Authorization": auth_header}
    print("========================================")
    employee_id = 2
    work_type_map = {"work from home": 3, "hybrid": 4}
    work_type_id = work_type_map.get(work_type.lower())
    if not work_type_id:
        return "Error: Invalid work type."

    payload = { "employee_id": employee_id, "work_type_id": work_type_id, "requested_date": requested_date, "requested_till": requested_till, "description": description }
    url = f"{AUTH_SERVICE_URL}/test/base/worktype-requests/"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            print("+++++++++++++++++")
            return f"WorkType Request applied successfully with ID: {resp.json().get('id')}"
        except httpx.HTTPStatusError as e:
            return f"Error creating request: {e.response.text}"
    print("++++++++++++++++++++++")

@mcp.tool()
async def worktype_request_approve_tool(req_id: int, auth_header: str) -> str:
    """Approve a WorkType request by ID. auth_header is a mandatory argument."""
    if not await is_manager(auth_header):
        return "Access Denied. Manager permissions are required."
    print("====================approve ===============")
    headers = {"Authorization": auth_header}
    url = f"{AUTH_SERVICE_URL}/test/base/worktype-requests-approve/{req_id}/"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.put(url, headers=headers)
            resp.raise_for_status()
            return f"WorkType request {req_id} approved successfully."
        except httpx.HTTPStatusError as e:
            return f"Failed to approve request {req_id}: {e.response.text}"

@mcp.tool()
async def worktype_request_reject_tool(req_id: int, auth_header: str) -> str:
    """Reject a WorkType request by ID. auth_header is a mandatory argument."""
    if not await is_manager(auth_header):
        return "Access Denied. Manager permissions are required."
    print("==============Reject======================")
    headers = {"Authorization": auth_header}
    url = f"{AUTH_SERVICE_URL}/test/base/worktype-requests-cancel/{req_id}/"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.put(url, headers=headers)
            resp.raise_for_status()
            return f"WorkType request {req_id} rejected successfully."
        except httpx.HTTPStatusError as e:
            return f"Failed to reject request {req_id}: {e.response.text}"




# import os
# import psycopg2
# from datetime import date, datetime
# import logging


# @mcp.tool()
# async def get_requested_worktype_from_db_tool(auth_header: str, limit: int = 10) -> str:
#     """
#     Fetch pending WorkType requests from the database and display them in a table format.
#     Resolves User IDs to usernames and WorkType IDs to names.
#     Results are capped at 10. Requires manager authentication.

#     Args:
#         auth_header (str): The authentication token of the manager.
#         limit (int): Number of pending requests to fetch (default 10, max 10).

#     Returns:
#         str: A formatted table of pending WorkType requests or an error message.
#     """
#     # Manager permission check
#     if not await is_manager(auth_header):
#         return "❌ Access Denied. Manager permissions are required."

#     limit = min(max(limit, 1), 10)  # ensure limit is 1–10
#     logging.info(f"Fetching last {limit} pending WorkType requests")

#     try:
#         conn = psycopg2.connect(
#             os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/horilla_main")
#         )
#         conn.autocommit = True
#     except Exception as e:
#         logging.error(f"Database connection failed: {e}")
#         return f"❌ Database connection failed: {e}"

#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT 
#                     wr.id, 
#                     u.username, 
#                     wr.requested_date, 
#                     wr.requested_till, 
#                     wt.work_type, 
#                     wr.description
#                 FROM base_worktyperequest wr
#                 LEFT JOIN auth_user u ON wr.employee_id_id = u.id
#                 LEFT JOIN base_worktype wt ON wr.work_type_id_id = wt.id
#                 WHERE wr.approved = false AND wr.canceled = false
#                 ORDER BY wr.id DESC
#                 LIMIT %s
#             """, (limit,))
#             rows = cur.fetchall()
#     except Exception as e:
#         logging.error(f"Failed to fetch WorkType requests: {e}")
#         return f"❌ Failed to fetch WorkType requests from the database: {e}"
#     finally:
#         conn.close()

#     if not rows:
#         return "✅ No pending WorkType requests found."

#     # Build Markdown table header
#     table = (
#         f"{'ID':<5} | {'Username':<15} | {'Start Date':<12} | {'End Date':<12} | "
#         f"{'WorkType':<15} | {'Description':<20} | {'Status':<10}\n"
#         + "-" * 110 + "\n"
#     )

#     # Populate rows
#     for r in rows:
#         req_id, username, start_date_obj, end_date_obj, work_type_name, desc_text = r

#         start_date = start_date_obj.strftime("%Y-%m-%d") if isinstance(start_date_obj, (date, datetime)) else "N/A"
#         end_date = end_date_obj.strftime("%Y-%m-%d") if isinstance(end_date_obj, (date, datetime)) else "N/A"
#         description = (desc_text[:17] + "...") if desc_text and len(desc_text) > 20 else (desc_text or "N/A")

#         table += (
#             f"{req_id:<5} | {username or 'N/A':<15} | {start_date:<12} | {end_date:<12} | "
#             f"{work_type_name or 'N/A':<15} | {description:<20} | {'Requested':<10}\n"
#         )

#     # Return wrapped in Markdown code block for clean chat display
#     return f"📋 Pending WorkType Requests:\n\n```\n{table}"
import os
import psycopg2
from datetime import date, datetime
import logging


@mcp.tool()
async def get_requested_worktype_from_db_tool(auth_header: str) -> str:
    """
    Fetch ALL pending WorkType requests from the database and display them in a table format.
    Resolves User IDs to usernames and WorkType IDs to names.
    Requires manager authentication.

    Args:
        auth_header (str): The authentication token of the manager.

    Returns:
        str: A formatted table of pending WorkType requests or an error message.
    """
    # Manager permission check
    if not await is_manager(auth_header):
        return "❌ Access Denied. Manager permissions are required."

    logging.info("Fetching ALL pending WorkType requests (most recent first)")

    try:
        conn = psycopg2.connect(
            os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
        )
        conn.autocommit = True
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return f"❌ Database connection failed: {e}"

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    wr.id, 
                    u.username, 
                    wr.requested_date, 
                    wr.requested_till, 
                    wt.work_type, 
                    wr.description
                FROM base_worktyperequest wr
                LEFT JOIN auth_user u ON wr.employee_id_id = u.id
                LEFT JOIN base_worktype wt ON wr.work_type_id_id = wt.id
                WHERE wr.approved = false AND wr.canceled = false
                ORDER BY wr.id DESC
            """)
            rows = cur.fetchall()
    except Exception as e:
        logging.error(f"Failed to fetch WorkType requests: {e}")
        return f"❌ Failed to fetch WorkType requests from the database: {e}"
    finally:
        conn.close()

    if not rows:
        return "✅ No pending WorkType requests found."

    # Build Markdown table header
    table = (
        f"{'ID':<5} | {'Username':<15} | {'Start Date':<12} | {'End Date':<12} | "
        f"{'WorkType':<15} | {'Description':<20} | {'Status':<10}\n"
        + "-" * 110 + "\n"
    )

    # Populate rows
    for r in rows:
        req_id, username, start_date_obj, end_date_obj, work_type_name, desc_text = r

        start_date = start_date_obj.strftime("%Y-%m-%d") if isinstance(start_date_obj, (date, datetime)) else "N/A"
        end_date = end_date_obj.strftime("%Y-%m-%d") if isinstance(end_date_obj, (date, datetime)) else "N/A"
        description = (desc_text[:17] + "...") if desc_text and len(desc_text) > 20 else (desc_text or "N/A")

        table += (
            f"{req_id:<5} | {username or 'N/A':<15} | {start_date:<12} | {end_date:<12} | "
            f"{work_type_name or 'N/A':<15} | {description:<20} | {'Requested':<10}\n"
        )

    # Return wrapped in Markdown code block for clean chat display
    return f"📋 Pending WorkType Requests:\n\n```\n{table}```"


if __name__ == "__main__":
    print("Worktype MCP Agent running on http://0.0.0.0:8003/mcp")
    mcp.run("streamable-http")