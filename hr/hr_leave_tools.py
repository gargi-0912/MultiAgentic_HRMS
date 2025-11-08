# from mcp.server.fastmcp import FastMCP
# from typing import Annotated, Literal
# from langgraph.prebuilt import InjectedState
# import requests
# import aiohttp
# import httpx

# #  Initialize MCP server (name = "LeaveServer")
# # mcp = FastMCP("LeaveServer")

# mcp = FastMCP("LeaveServer", port = 8002, host="0.0.0.0")

# # r8_start
# @mcp.tool()
# async def apply_leave_tool(
#     leave_type: Annotated[str, Literal["sick", "casual", "earned"]],
#     start_date: str,
#     end_date: str,
#     description: str,
#     state: Annotated[dict, InjectedState]={},
# ) -> str:
#     """
#     Use this tool only to apply leave request.

#     Args:
#         leave_type (str): Type of leave to apply for. Options: "sick", "casual", "earned".
#         start_date (str): Start date of the leave.
#         end_date (str): End date of the leave.
#         description (str): Reason for the leave.
#     """

#     emp_id = 2  # (Hardcoded for now, can later be dynamic from state)

#     # Map leave type to API IDs
#     if leave_type.lower() == "sick":
#         leave_type_id = 2
#     elif leave_type.lower() == "casual":
#         leave_type_id = 1
#     elif leave_type.lower() == "earned":
#         leave_type_id = 3
#     else:
#         return "Error: Invalid leave type. Use one of: sick, casual, earned."

#     # API endpoint
#     # url = f"https://agentrahrms.dev.vinove.com/leave/request-creation?type_id={leave_type_id}&emp_id={emp_id}"
#     url = f"http://127.0.0.1:7000/leave/request-creation?type_id={leave_type_id}&emp_id={emp_id}"
   
#     # url = f"http://127.0.0.1:7000/test/leave/user-request/"

#     # Form data payload
#     form_data = {
#         "employee_id": str(emp_id),
#         "leave_type_id": str(leave_type_id),
#         "start_date": start_date,
#         "start_date_breakdown": "full_day",
#         "end_date": end_date,
#         "end_date_breakdown": "full_day",
#         "description": description,
#     }

#     try:
#         response = requests.post(url, data=form_data)

#         if response.status_code == 400:
#             json_data = response.json()
#             first_error = json_data.get("errors", {}).get("__all__", ["Unknown error"])[0]
#             return f"Leave request failed: {first_error}"

#         elif response.status_code == 200:
#             json_data = response.json()
#             leave_id = json_data.get("leave_request_id")
#             if leave_id:
#                 return f"Leave request submitted successfully! Request ID: {leave_id}"
#             return "Leave request submitted but no ID returned."

#         else:
#             return f"Unexpected response: {response.status_code} - {response.text}"

#     except Exception as e:
#         return f"Error while submitting leave request: {str(e)}"




# @mcp.tool()
# async def approve_leave_tool(
#     req_id: int,
#     base_url: str = "http://127.0.0.1:7000/test/leave/approve/",
#     login_url: str = "http://127.0.0.1:7000/test/auth/login/",
#     username: str = "admin@vinove.com",
#     password: str = "vinove@123"
# ) -> str:
#     """
#     Approve a leave request by its ID.

#     Args:
#         req_id (int): Leave request ID to approve.
#         base_url (str): API base URL for leave approval endpoint.
#         login_url (str): API login endpoint.
#         username (str): Login username.
#         password (str): Login password.
#     Returns:
#         str: Success or failure message.
#     """
   

#     async with httpx.AsyncClient() as client:
#         #  1. Login to get JWT token
#         login_resp = await client.post(
#             login_url,
#             json={"username": username, "password": password},
#             headers={"Content-Type": "application/json"},
#         )

#         if login_resp.status_code != 200:
#             return f" Login failed: {login_resp.text}"

#         token = login_resp.json().get("access")
#         if not token:
#             return " Login succeeded but no token returned."

#         headers = {"Authorization": f"Bearer {token}"}

#         #  2. Approve leave request
#         url = f"{base_url}{req_id}/"
#         resp = await client.put(url, headers=headers)

#         if resp.status_code == 200:
#             return f" Leave request {req_id} approved successfully."
#         else:
#             return f" Failed to approve leave {req_id}. Status: {resp.status_code}, Response: {resp.text}"


# @mcp.tool()
# async def reject_leave_tool(
#     req_id: int,
#     base_url: str = "http://127.0.0.1:7000/test/leave/reject/",
#     login_url: str = "http://127.0.0.1:7000/test/auth/login/",
#     username: str = "admin@vinove.com",
#     password: str = "vinove@123"
# ) -> str:
#     """
#     Reject a leave request by its ID.

#     Args:
#         req_id (int): Leave request ID to reject.
#     """

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
#             return " Login succeeded but no token returned."

#         headers = {"Authorization": f"Bearer {token}"}

#         #  Reject leave request
#         url = f"{base_url}{req_id}/"
#         resp = await client.put(url, headers=headers)

#         if resp.status_code == 200:
#             return f" Leave request {req_id} rejected successfully."
#         else:
#             return f" Failed to reject leave {req_id}. Status: {resp.status_code}, Response: {resp.text}"



# # @mcp.tool()
# # async def approve_leave_tool(
# #     req_id: Annotated[str, "Leave request ID to approve"]
# # ) -> str:
# #     """
# #     Use this tool only to approve a leave request by request ID.

# #     Args:
# #         req_id (str): The ID of the leave request to approve.
# #     """
# #     url = f"http://127.0.0.1:7000/leave/request-approve/{req_id}"

# #     try:
# #         async with aiohttp.ClientSession() as session:
# #             async with session.post(url) as response:
# #                 if response.status == 200:
# #                     data = await response.json()
# #                     return f"Leave request {req_id} approved successfully. Response: {data}"
# #                 else:
# #                     error_text = await response.text()
# #                     return f"Failed to approve leave request {req_id}. Status: {response.status}, Error: {error_text}"

# #     except Exception as e:
# #         return f"Error while approving leave request {req_id}: {str(e)}"



# # from mcp.server import tool as mcp_tool
# import httpx


# @mcp.tool()
# async def get_all_requests_tool(
#     base_url: str = "http://127.0.0.1:7000/test/leave/user-request/",
# ) -> str:
#     """
#     Fetch all leave requests for the first employee (as per EmployeeLeaveRequestGetCreateAPIView).
#     This directly calls the Django endpoint you already tested in Postman.

#     Args:
#         base_url (str): API endpoint URL. Default is local test endpoint.

#     Returns:
#         str: JSON string of all leave requests (paginated).
#     """

#     async with httpx.AsyncClient() as client:
#         resp = await client.get(base_url)

#         if resp.status_code != 200:
#             return f" Failed to fetch leave requests: {resp.text}"

#         return resp.text


# @mcp.tool()
# async def delete_leave_tool(
#     leave_id: Annotated[int, "Leave request ID to delete"]
# ) -> str:
#     """
#     Use this tool only to delete a leave request by leave ID.

#     Args:
#         leave_id (int): The leave request ID to delete.
#     """
#     url = f"http://127.0.0.1:8001/leave/request-delete/{leave_id}"
#     print(f"Deleting leave request ID: ------------------")
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(url) as response:  # Using POST since API expects POST for delete
#                 if response.status == 200:
#                     try:
#                         data = await response.json()
#                         return f"Leave request {leave_id} deleted successfully. Response: {data}"
#                     except Exception:
#                         return f"Leave request {leave_id} deleted successfully. (No JSON response)"
#                 else:
#                     error_text = await response.text()
#                     return f"Failed to delete leave request {leave_id}. Status: {response.status}, Error: {error_text}"

#     except Exception as e:
#         return f"Error while deleting leave request {leave_id}: {str(e)}"


# import httpx
# @mcp.tool()
# async def cancel_leave_request_tool(
#     leave_id: Annotated[int, "Leave request ID to cancel"],
#     reason: Annotated[str, "Reason for cancellation"]
# ) -> str:
#     """
#     Cancel a leave request by leave_id.

#     Args:
#         leave_id (int): The ID of the leave request to cancel.
#         reason (str): Reason for cancelling the leave.
#     """
#     url = f"http://127.0.0.1:8001/api/leave/cancel/{leave_id}"
#     print(f"Cancelling leave request ID: ------------------")
#     payload = {"reason": reason}

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, json=payload)
#             response.raise_for_status()
#             return f"Leave request {leave_id} cancelled successfully. Server response: {response.text}"
#         except httpx.HTTPStatusError as e:
#             return f"Failed to cancel leave request {leave_id}. Error: {e.response.text}"
#         except Exception as e:
#             return f"Error cancelling leave request {leave_id}: {str(e)}"

# hr_leave_tools.py

from mcp.server.fastmcp import FastMCP
from typing import Annotated, Literal
import httpx

mcp = FastMCP("LeaveServer", port=8002, host="0.0.0.0")
AUTH_SERVICE_URL = "http://127.0.0.1:7000"

CHAT_BACKEND_URL = "http://0.0.0.0:8001"
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
                print(user_data,"======================================")
                # print(f"Validation successful for user: {user_data.get('username')}")
                # Check the 'is_superuser' flag from the response
                return user_data.get("is_superuser") is True
            else:
                print(f"Token validation failed. Status: {response.status_code}, Body: {response.text}")
                return False
                
        except httpx.RequestError as e:
            print(f"An error occurred during the API call: {e}")
            return False
        


@mcp.tool()
async def apply_leave_tool(
    leave_type: Annotated[str, Literal["sick", "casual", "earned"]],
    start_date: str,
    end_date: str,
    description: str,
    auth_header: str,  # Auth must be provided
) -> str:
    """Apply for leave. Returns user-facing message immediately, notifies manager asynchronously."""
    if not auth_header:
        return "Authentication error. Token is missing."

    headers = {"Authorization": auth_header}
    emp_id = 2  # default if profile fetch fails

    # Normalize leave type
    leave_type_id = None
    normalized_leave_type = leave_type.lower()
    if normalized_leave_type in ["sick", "sick leave"]:
        leave_type_id = 2
    elif normalized_leave_type in ["casual", "casual leave"]:
        leave_type_id = 1
    elif normalized_leave_type in ["earned", "earned leave"]:
        leave_type_id = 3

    if leave_type_id is None:
        return "Error: Invalid leave type. Use one of: sick, casual, earned."

    # Fetch employee profile (optional)
    try:
        async with httpx.AsyncClient() as client:
            profile_resp = await client.get(f"{AUTH_SERVICE_URL}/test/auth/profile/", headers=headers)
            if profile_resp.status_code == 200:
                emp_id = profile_resp.json().get("id", emp_id)
    except Exception as e:
        print("⚠️ Failed to fetch employee profile:", e)

    # Create leave request
    url = f"{AUTH_SERVICE_URL}/test/leave/user-request/"
    form_data = {
        "employee_id": str(emp_id),
        "leave_type_id": str(leave_type_id),
        "start_date": start_date,
        "start_date_breakdown": "full_day",
        "end_date": end_date,
        "end_date_breakdown": "full_day",
        "description": description,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=form_data, headers=headers)
            response.raise_for_status()
            leave_id = response.json().get("id")

            # Build the user-facing message
            user_msg = f"OK. I have applied for {leave_type} leave on {start_date} as event. Request ID is {leave_id}."

            # 🔔 Notify manager asynchronously (fire-and-forget)
            async def notify_manager():
                try:
                    async with httpx.AsyncClient() as notif_client:
                        notif_payload = {
                            "employee_id": emp_id,
                            "leave_id": leave_id,
                            "message": f"Employee {emp_id} applied for {leave_type} leave from {start_date} to {end_date}.Request ID is {leave_id}",
                        }
                        await notif_client.post(f"{CHAT_BACKEND_URL}/notify-manager", json=notif_payload, headers=headers)
                except Exception as e:
                    print(f"⚠️ Manager notification failed: {e}")


            # Schedule notification in background
            import asyncio
            asyncio.create_task(notify_manager())

            # Return user-facing message immediately
            return user_msg

        except httpx.HTTPStatusError as e:
            return f"❌ Leave request failed: {e.response.text}"

# @mcp.tool()
# async def apply_leave_tool(
#     leave_type: Annotated[str, Literal["sick", "casual", "earned"]],
#     start_date: str,
#     end_date: str,
#     description: str,
#     auth_header: str, # <-- KEY CHANGE: Auth is now an explicit argument
# ) -> str:
#     """Apply for leave. auth_header is a mandatory argument."""
#     if not auth_header: return "Authentication error. Token is missing."
#     print("Auth header received in apply_leave_tool:============", auth_header)
#     headers = {"Authorization": auth_header}
#     print("+++++++++++++++")
#     emp_id = 2
#     # leave_type_map = {"sick" or "sick leave": 2, "casual": 1, "earned": 3}
#     #     # Map leave type to API IDs
#     # if leave_type.lower() == "sick" or "sick leave":
#     #     leave_type_id = 2
#     # elif leave_type.lower() == "casual" or "casual leave":
#     #     leave_type_id = 1
#     # elif leave_type.lower() == "earned" or "earned leave":
#     #     leave_type_id = 3
#     # else:
#     #     return "Error: Invalid leave type. Use one of: sick, casual, earned."
#     leave_type_id = None
#     normalized_leave_type = leave_type.lower()

#     # --- CORRECTED LOGIC ---
#     if normalized_leave_type in ["sick", "sick leave"]:
#         leave_type_id = 2
#     elif normalized_leave_type in ["casual", "casual leave"]:
#         leave_type_id = 1
#     elif normalized_leave_type in ["earned", "earned leave"]:
#         leave_type_id = 3

#     if leave_type_id is None:
#         return "Error: Invalid leave type. Use one of: sick, casual, earned."

#     # leave_type_id = leave_type_map.get(leave_type.lower())
#     if not leave_type_id:
#         return "❌ Invalid leave type."

#     # Get employee ID
#     # emp_id = 2
#     try:
#         async with httpx.AsyncClient() as client:
#             profile_resp = await client.get(f"{AUTH_SERVICE_URL}/test/auth/profile/", headers=headers)
#             if profile_resp.status_code == 200:
#                 emp_id = profile_resp.json().get("id", emp_id)
#                 print(emp_id,"}================")
#     except Exception as e:
#         print("⚠️ Failed to fetch employee profile:", e)

#     # Create leave request
#     url = f"{AUTH_SERVICE_URL}/test/leave/user-request/"
#     form_data = {
#         "employee_id": str(emp_id),
#         "leave_type_id": str(leave_type_id),
#         "start_date": start_date,
#         "start_date_breakdown": "full_day",
#         "end_date": end_date,
#         "end_date_breakdown": "full_day",
#         "description": description,
#     }

#     # async with httpx.AsyncClient() as client:
#     #     try:
#     #         response = await client.post(url, data=form_data, headers=headers)
#     #         response.raise_for_status()
#     #         leave_id = response.json().get("id")
#     #         msg = f"✅ Leave request submitted successfully! Request ID: {leave_id}"

#     #         # 🔔 Notify manager via CHAT_BACKEND endpoint
#     #         notif_payload = {
#     #             "employee_id": emp_id,
#     #             "leave_id": leave_id,
#     #             "message": f"Employee {emp_id} applied for {leave_type} leave from {start_date} to {end_date}.",
#     #         }
#     #         await client.post(f"{CHAT_BACKEND_URL}/notify-manager", json=notif_payload, headers=headers)

#     #         return msg
#     #     except httpx.HTTPStatusError as e:
#     #         return f"❌ Leave request failed: {e.response.text}"


#     import asyncio
#     import httpx

#     async with httpx.AsyncClient() as client:
#         # 1️⃣ Submit leave request
#         response = await client.post(url, data=form_data, headers=headers)
#         response.raise_for_status()
        
#         leave_id = response.json().get("id")
#         msg = f"✅ Leave request submitted successfully! Request ID: {leave_id}"

#     # 2️⃣ Notify manager using a separate client (fire-and-forget)
#     async def notify_manager():
#         async with httpx.AsyncClient() as notify_client:
#             notif_payload = {
#                 "employee_id": emp_id,
#                 "leave_id": leave_id,
#                 "message": f"Employee {emp_id} applied for {leave_type} leave from {start_date} to {end_date} and leave request id is {leave_id}.",
#             }
#             try:
#                 await notify_client.post(f"{CHAT_BACKEND_URL}/notify-manager", json=notif_payload, headers=headers)
#             except Exception as e:
#                 print("⚠️ Failed to notify manager:", e)

#     # Schedule background notification
#     asyncio.create_task(notify_manager())

#     # 3️⃣ Return message immediately to UI
#     return msg


       
# @mcp.tool()
# async def apply_leave_tool(
#     leave_type: Annotated[str, Literal["sick", "casual", "earned"]],
#     start_date: str,
#     end_date: str,
#     description: str,
#     auth_header: str, # <-- KEY CHANGE: Auth is now an explicit argument
# ) -> str:
#     """Apply for leave. auth_header is a mandatory argument."""
#     if not auth_header: return "Authentication error. Token is missing."
#     print("Auth header received in apply_leave_tool:============", auth_header)
#     headers = {"Authorization": auth_header}
#     print("+++++++++++++++")
#     emp_id = 2
#     # leave_type_map = {"sick" or "sick leave": 2, "casual": 1, "earned": 3}
#     #     # Map leave type to API IDs
#     if leave_type.lower() == "sick" or "sick leave":
#         leave_type_id = 2
#     elif leave_type.lower() == "casual" or "casual leave":
#         leave_type_id = 1
#     elif leave_type.lower() == "earned" or "earned leave":
#         leave_type_id = 3
#     else:
#         return "Error: Invalid leave type. Use one of: sick, casual, earned."

#     # leave_type_id = leave_type_map.get(leave_type.lower())
#     if not leave_type_id:
#         return "Error: Invalid leave type."
#     print("leave_type_id",leave_type_id)
#     print("++++++++++............")

#     # url = f"{AUTH_SERVICE_URL}/leave/request-creation?type_id={leave_type_id}&emp_id={emp_id}"
#     url = f"{AUTH_SERVICE_URL}/test/leave/user-request/"
#     form_data = { "employee_id": str(emp_id), "leave_type_id": str(leave_type_id), "start_date": start_date, "start_date_breakdown": "full_day", "end_date": end_date, "end_date_breakdown": "full_day", "description": description }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, data=form_data, headers=headers)
#             response.raise_for_status()
#             print(response.json().get('id'),"--------------------")
#             return f"Leave request submitted successfully! Request ID: {response.json().get('id')}"
#         except httpx.HTTPStatusError as e:
#             return f"Leave request failed: {e.response.text}"



# r8
# @mcp.tool()
# async def approve_leave_tool(req_id: int, auth_header: str) -> str:
#     """Approve a leave request by ID. auth_header is a mandatory argument."""
#     # Manager check is now done directly inside the tool
#     if not await is_manager(auth_header):
#         return "Access Denied. Manager permissions are required."
#     print("Auth header received in approve_leave_tool:===============", auth_header)
#     headers = {"Authorization": auth_header}
#     url = f"{AUTH_SERVICE_URL}/test/leave/approve/{req_id}/"
#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.put(url, headers=headers)
#             resp.raise_for_status()
#             return f"Leave request {req_id} approved successfully."
#         except httpx.HTTPStatusError as e:
#             return f"Failed to approve leave {req_id}: {e.response.text}"

# @mcp.tool()
# async def reject_leave_tool(req_id: int, auth_header: str) -> str:
#     """Reject a leave request by its ID. auth_header is a mandatory argument."""
#     if not await is_manager(auth_header):
#         return "Access Denied. Manager permissions are required."
#     print("==================Reject leave============")
#     headers = {"Authorization": auth_header}
#     url = f"{AUTH_SERVICE_URL}/test/leave/reject/{req_id}/"

#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.put(url, headers=headers)
#             resp.raise_for_status()
#             return f"Leave request {req_id} rejected successfully."
#         except httpx.HTTPStatusError as e:
#             return f"Failed to reject leave {req_id}: {e.response.text}"



# @mcp.tool()
# async def bulk_approve_leave_tool(
#     req_ids: list[int] | None, 
#     auth_header: str,
#     approve_all: bool = False
# ) -> str:
#     """
#     Approve multiple leave requests in bulk.
#     - Pass req_ids (list of IDs) to approve specific ones.
#     - Or set approve_all=True to approve ALL pending requests.
#     auth_header is mandatory.
#     """
#     if not await is_manager(auth_header):
#         return "Access Denied. Manager permissions are required."

#     headers = {"Authorization": auth_header}
#     print("++++++++++")

#     # Case 1: Approve ALL
#     if approve_all:
#         # First fetch all pending leave requests
#         list_url = f"{AUTH_SERVICE_URL}/test/leave/user-request/"
#         print("-----------")
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(list_url, headers=headers)
#             if resp.status_code != 200:
#                 return f"Failed to fetch pending requests: {resp.text}"
#             data = resp.json()
#             req_ids = [req["id"] for req in data]  # collect all pending IDs
#             if not req_ids:
#                 return "No pending leave requests to approve."

#     # Case 2: Specific IDs (or after collecting all)
#     if not req_ids:
#         return "No request IDs provided."

#     url = f"{AUTH_SERVICE_URL}/test/leave/request-bulk-action/"
#     print("_____________")
#     form_data = [("leave_request_id", str(req_id)) for req_id in req_ids]

#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.put(url, data=form_data, headers=headers)
#             resp.raise_for_status()
#             return f"Bulk approval successful for requests: {req_ids}"
#         except httpx.HTTPStatusError as e:
#             return f"Bulk approval failed: {e.response.text}"





# @mcp.tool()
# async def get_all_leave_requests_tool(auth_header: str, base_url: str = "http://127.0.0.1:7000/test/leave/user-request/") -> str:
#     """
#     Fetch all leave requests for the employee. Requires manager authentication.

#     Args:
#         auth_header (str): Authorization token of the logged-in manager.
#         base_url (str): API endpoint URL. Default is local test endpoint.

#     Returns:
#         str: JSON string of all leave requests (paginated) or error message.
#     """
#     if not await is_manager(auth_header):
#         return "Access Denied. Manager permissions are required."

#     headers = {"Authorization": auth_header}
#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.get(base_url, headers=headers)
#             resp.raise_for_status()
#             print("------------------------ GET ALL REQUESTS ------------------------")
#             return resp.text
#         except httpx.HTTPStatusError as e:
#             return f"❌ Failed to fetch leave requests: {e.response.text}"
#         except Exception as e:
#             return f"❌ Unexpected error while fetching leave requests: {str(e)}"


import os
import psycopg2
from datetime import date, datetime
import logging

# @mcp.tool()
# async def get_requested_leave_from_db_tool(auth_header: str, limit: int = 10) -> str:
#     """
#     Fetch requested leave requests from the database and display in table format.
#     Resolves User ID to username and Leave Type ID to leave type name.
#     Limit capped at 10.
#     Requires manager authentication.

#     Args:
#         auth_header (str): Authorization token of the logged-in manager.
#         limit (int): Number of requested leave requests to fetch (max 10).

#     Returns:
#         str: Table of requested leave requests or error message.
#     """
#     # Manager permission check
#     if not await is_manager(auth_header):
#         return "Access Denied. Manager permissions are required."

#     limit = min(max(limit, 1), 10)  # Ensure limit is between 1 and 10
#     logging.info(f"Fetching last {limit} requested leave requests")

#     try:
#         conn = psycopg2.connect(
#             os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
#         )
#         conn.autocommit = True
#     except Exception as e:
#         return f"❌ Database connection failed: {e}"

#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT lr.id, e.username, lr.start_date, lr.end_date, lt.name AS leave_type, 
#                        lr.requested_days, lr.status
#                 FROM leave_leaverequest lr
#                 LEFT JOIN auth_user e ON lr.employee_id_id = e.id
#                 LEFT JOIN leave_leavetype lt ON lr.leave_type_id_id = lt.id
#                 WHERE lr.status = 'requested'
#                 ORDER BY lr.id DESC
#                 LIMIT %s
#             """, (limit,))
#             rows = cur.fetchall()
#     except Exception as e:
#         return f"❌ Failed to fetch leave requests from DB: {e}"
#     finally:
#         conn.close()

#     if not rows:
#         return "No requested leave requests found."

#     # Build table with proper formatting for chat
#     table = (
#         f"{'ID':<5} | {'Username':<15} | {'Start Date':<12} | {'End Date':<12} | "
#         f"{'Leave Type':<15} | {'Days':<5} | {'Status':<10}\n"
#         + "-" * 95 + "\n"
#     )
#     print(".........................")

#     for r in rows:
#         start_date = r[2].strftime("%Y-%m-%d") if isinstance(r[2], (date, datetime)) else "N/A"
#         end_date   = r[3].strftime("%Y-%m-%d") if isinstance(r[3], (date, datetime)) else "N/A"
#         username   = r[1] if r[1] else "N/A"
#         leave_type = r[4] if r[4] else "N/A"
#         days       = r[5] if r[5] is not None else "N/A"
#         status     = r[6] if r[6] else "N/A"

#         table += (
#             f"{r[0]:<5} | {username:<15} | {start_date:<12} | {end_date:<12} | "
#             f"{leave_type:<15} | {days:<5} | {status:<10}\n"
#         )
#         print("====================")

#     # Wrap in Markdown code block for proper chat display
#     return f"```\n{table}```"

# # r8
# @mcp.tool()
# async def get_requested_leave_from_db_tool(auth_header: str) -> str:
#     """
#     Fetch ALL requested leave requests from the database and display in table format.
#     Resolves User ID to username and Leave Type ID to leave type name.
#     Requires manager authentication.

#     Args:
#         auth_header (str): Authorization token of the logged-in manager.

#     Returns:
#         str: Table of requested leave requests or error message.
#     """
#     # Manager permission check
#     if not await is_manager(auth_header):
#         return "Access Denied. Manager permissions are required."

#     logging.info("Fetching ALL requested leave requests (most recent first)")

#     try:
#         conn = psycopg2.connect(
#             os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
#         )
#         conn.autocommit = True
#     except Exception as e:
#         return f"❌ Database connection failed: {e}"

#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT lr.id, e.username, lr.start_date, lr.end_date, lt.name AS leave_type, 
#                        lr.requested_days, lr.status
#                 FROM leave_leaverequest lr
#                 LEFT JOIN auth_user e ON lr.employee_id_id = e.id
#                 LEFT JOIN leave_leavetype lt ON lr.leave_type_id_id = lt.id
#                 WHERE lr.status = 'requested'
#                 ORDER BY lr.id DESC
#             """)
#             rows = cur.fetchall()
#     except Exception as e:
#         return f"❌ Failed to fetch leave requests from DB: {e}"
#     finally:
#         conn.close()

#     if not rows:
#         return "No requested leave requests found."

#     # Build table
#     table = (
#         f"{'ID':<5} | {'Username':<15} | {'Start Date':<12} | {'End Date':<12} | "
#         f"{'Leave Type':<15} | {'Days':<5} | {'Status':<10}\n"
#         + "-" * 95 + "\n"
#     )

#     for r in rows:
#         start_date = r[2].strftime("%Y-%m-%d") if isinstance(r[2], (date, datetime)) else "N/A"
#         end_date   = r[3].strftime("%Y-%m-%d") if isinstance(r[3], (date, datetime)) else "N/A"
#         username   = r[1] if r[1] else "N/A"
#         leave_type = r[4] if r[4] else "N/A"
#         days       = r[5] if r[5] is not None else "N/A"
#         status     = r[6] if r[6] else "N/A"

#         table += (
#             f"{r[0]:<5} | {username:<15} | {start_date:<12} | {end_date:<12} | "
#             f"{leave_type:<15} | {days:<5} | {status:<10}\n"
#         )

#     return f"```\n{table}```"



from typing import List, Dict

@mcp.tool()
async def get_requested_leave_from_db_tool(auth_header: str, as_list: bool = False) -> str | List[Dict]:
    """
    Fetch ALL requested leave requests from the database.
    
    Args:
        auth_header (str): Authorization token of the logged-in manager.
        as_list (bool): If True, returns raw list of dicts instead of table (for bulk approve).

    Returns:
        str: Table of requested leave requests (default)
        OR
        List[Dict]: Raw leave request data if as_list=True
    """
    # Manager permission check
    if not await is_manager(auth_header):
        return "Access Denied. Manager permissions are required."

    logging.info("Fetching ALL requested leave requests (most recent first)")

    try:
        conn = psycopg2.connect(
            os.getenv("POSTGRES_URL", "postgresql://horilla:horilla@localhost:5432/testdb")
        )
        conn.autocommit = True
    except Exception as e:
        return f"❌ Database connection failed: {e}"

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT lr.id, e.username, lr.start_date, lr.end_date, lt.name AS leave_type, 
                       lr.requested_days, lr.status
                FROM leave_leaverequest lr
                LEFT JOIN auth_user e ON lr.employee_id_id = e.id
                LEFT JOIN leave_leavetype lt ON lr.leave_type_id_id = lt.id
                WHERE lr.status = 'requested'
                ORDER BY lr.id DESC
            """)
            rows = cur.fetchall()
    except Exception as e:
        return f"❌ Failed to fetch leave requests from DB: {e}"
    finally:
        conn.close()

    if not rows:
        return [] if as_list else "No requested leave requests found."

    # Build raw list of dicts
    leave_data = []
    for r in rows:
        leave_data.append({
            "id": r[0],
            "username": r[1] or "N/A",
            "start_date": r[2].strftime("%Y-%m-%d") if isinstance(r[2], (date, datetime)) else "N/A",
            "end_date": r[3].strftime("%Y-%m-%d") if isinstance(r[3], (date, datetime)) else "N/A",
            "leave_type": r[4] or "N/A",
            "days": r[5] if r[5] is not None else "N/A",
            "status": r[6] or "N/A"
        })

    if as_list:
        return leave_data

    # Otherwise build table for chat display
    table = (
        f"{'ID':<5} | {'Username':<15} | {'Start Date':<12} | {'End Date':<12} | "
        f"{'Leave Type':<15} | {'Days':<5} | {'Status':<10}\n"
        + "-" * 95 + "\n"
    )

    for leave in leave_data:
        table += (
            f"{leave['id']:<5} | {leave['username']:<15} | {leave['start_date']:<12} | {leave['end_date']:<12} | "
            f"{leave['leave_type']:<15} | {leave['days']:<5} | {leave['status']:<10}\n"
        )

    return f"```\n{table}```"


# from typing import List, Optional
# import asyncio
# import httpx

# @mcp.tool()
# async def approve_leaves_tool(
#     req_ids: Optional[List[int]] = None, auth_header: str = ""
# ) -> str:
#     """
#     Approve multiple leave requests via backend API.

#     - If req_ids are given -> approve only those.
#     - If no req_ids -> fetch all requested leaves from DB and approve all.
#     """
#     if not await is_manager(auth_header):
#         return "❌ Access Denied. Manager permissions are required."

#     results = []

#     headers = {"Authorization": auth_header}

#     async def approve_single_leave(rid: int) -> str:
#         url = f"{AUTH_SERVICE_URL}/test/leave/request-bulk-action/"  # new bulk approve endpoint
#         payload = {"req_ids": [rid]}
#         async with httpx.AsyncClient() as client:
#             try:
#                 resp = await client.put(url, headers=headers, json=payload)
#                 resp.raise_for_status()
#                 return f"✅ Leave request {rid} approved successfully."
#             except httpx.HTTPStatusError as e:
#                 return f"❌ Failed to approve leave {rid}: {e.response.text}"

#     # Case 1: User provided specific IDs
#     if req_ids:
#         tasks = [approve_single_leave(rid) for rid in req_ids]
#         results = await asyncio.gather(*tasks)
#         return "\n".join(results)

#     # Case 2: Approve all requested leaves
#     # First, fetch all requested leaves as a list of dicts
#     leave_requests = await get_requested_leave_from_db_tool(auth_header=auth_header, as_list=True)
#     if not leave_requests:
#         return "✅ No pending leave requests to approve."

#     tasks = [approve_single_leave(leave["id"]) for leave in leave_requests]
#     results = await asyncio.gather(*tasks)

#     return "\n".join(results)


# @mcp.tool()
# async def reject_leaves_tool(
#     req_ids: Optional[List[int]] = None, auth_header: str = ""
# ) -> str:
#     """
#     Reject multiple leave requests via backend API.

#     - If req_ids are given -> reject only those.
#     - If no req_ids -> fetch all requested leaves from DB and reject all.
#     """
#     if not await is_manager(auth_header):
#         return "❌ Access Denied. Manager permissions are required."

#     headers = {"Authorization": auth_header}

#     async def reject_single_leave(rid: int) -> str:
#         url = f"{AUTH_SERVICE_URL}/test/leave/reject/{rid}/"  # new reject endpoint
#         print(":::::::::::::::::::::::::::::::")
#         async with httpx.AsyncClient() as client:
#             try:
#                 resp = await client.put(url, headers=headers)
#                 resp.raise_for_status()
#                 return f"❌ Leave request {rid} rejected successfully."
#             except httpx.HTTPStatusError as e:
#                 return f"⚠️ Failed to reject leave {rid}: {e.response.text}"

#     # Case 1: User provided specific IDs
#     if req_ids:
#         tasks = [reject_single_leave(rid) for rid in req_ids]
#         results = await asyncio.gather(*tasks)
#         return "\n".join(results)

#     # Case 2: Reject all requested leaves
#     leave_requests = await get_requested_leave_from_db_tool(auth_header=auth_header, as_list=True)
#     print("---------------------------------------")
#     if not leave_requests:
#         return "✅ No pending leave requests to reject."

#     tasks = [reject_single_leave(leave["id"]) for leave in leave_requests]
#     results = await asyncio.gather(*tasks)

#     return "\n".join(results)
from typing import List, Optional
import asyncio
import httpx
from datetime import datetime

EMP_NOTIF_URL = f"{CHAT_BACKEND_URL}/notify-employee"  # Employee notifications endpoint

async def notify_employee(employee_email: str, message: str):
    """Send a notification to the employee."""
    payload = {
        "employee_id": employee_email,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    async with httpx.AsyncClient() as client:
        try:
            await client.post(EMP_NOTIF_URL, json=payload, timeout=5)
        except Exception as e:
            print(f"Failed to notify employee: {e}")

# @mcp.tool()
# async def approve_leaves_tool(
#     req_ids: Optional[List[int]] = None, auth_header: str = ""
# ) -> str:
#     if not await is_manager(auth_header):
#         return "❌ Access Denied. Manager permissions are required."

#     headers = {"Authorization": auth_header}
#     results = []

#     async def approve_single_leave(rid: int) -> str:
#         url = f"{AUTH_SERVICE_URL}/test/leave/approve/{rid}/"
#         # payload = {"req_ids": rid}
#         async with httpx.AsyncClient() as client:
#             try:
#                 resp = await client.put(url, headers=headers)
#                 resp.raise_for_status()
#                 # data = resp.json()
#                 print("---------------------")

#                 # emp_email = data.get("employee_email")
#                 emp_id=None
#                 try:
#                     async with httpx.AsyncClient() as client:
#                         profile_resp = await client.get(f"{AUTH_SERVICE_URL}/test/auth/profile/", headers=headers)
#                         if profile_resp.status_code == 200:
#                             emp_id = profile_resp.json().get("id", emp_id)
#                 except Exception as e:
#                     print("⚠️ Failed to fetch employee profile:", e)

#                 if resp:
#                     emp_email = emp_id
#                     if emp_email:
#                         # Send notification to employee via notification API
#                         notif_payload = {
#                             "employee_id": emp_email,
#                             "message": f"✅ Your leave request {rid} has been APPROVED."
#                         }
#                         await client.post("http://127.0.0.1:8001/notify-employee", json=notif_payload)
#                         print("+++++++++++++++++++++++++++")

#                 return f"✅ Leave request {rid} approved successfully."
#             except httpx.HTTPStatusError as e:
#                 return f"❌ Failed to approve leave {rid}: {e.response.text}"

#     # Case 1: Approve specific IDs
#     if req_ids:
#         tasks = [approve_single_leave(rid) for rid in req_ids]
#         results = await asyncio.gather(*tasks)
#         return "\n".join(results)

#     # Case 2: Approve all requested leaves
#     leave_requests = await get_requested_leave_from_db_tool(auth_header=auth_header, as_list=True)
#     if not leave_requests:
#         return "✅ No pending leave requests to approve."

#     tasks = [approve_single_leave(leave["id"]) for leave in leave_requests]
#     results = await asyncio.gather(*tasks)
#     return "\n".join(results)

@mcp.tool()
async def approve_leaves_tool(
    req_ids: Optional[List[int]] = None, auth_header: str = ""
) -> str:
    if not await is_manager(auth_header):
        return "❌ Access Denied. Manager permissions are required."

    headers = {"Authorization": auth_header}

    async def approve_single_leave(rid: int) -> str:
        emp_id = None
        # 🔹 Get manager profile to determine emp_id
        try:
            async with httpx.AsyncClient() as client:
                profile_resp = await client.get(f"{AUTH_SERVICE_URL}/test/auth/profile/", headers=headers)
                if profile_resp.status_code == 200:
                    emp_id = profile_resp.json().get("id", None)
                    print(emp_id, "}================")
        except Exception as e:
            print("⚠️ Failed to fetch employee profile:", e)

        # 🔹 Approve leave
        url = f"{AUTH_SERVICE_URL}/test/leave/approve/{rid}/"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.put(url, headers=headers)
                resp.raise_for_status()

                # 🔹 Notify employee (emp_id from profile)
                if emp_id:
                    notif_payload = {
                        "employee_id": emp_id,
                        "leave_id": rid,
                        "message": f"✅ Your leave request {rid} has been APPROVED."
                    }
                    await client.post(
                        f"{CHAT_BACKEND_URL}/notify-employee",
                        json=notif_payload
                    )

                return f"✅ Leave request {rid} approved successfully."
            except httpx.HTTPStatusError as e:
                return f"❌ Failed to approve leave {rid}: {e.response.text}"
            except Exception as e:
                return f"⚠️ Error while approving leave {rid}: {str(e)}"

    # Case 1: Approve specific IDs
    if req_ids:
        results = await asyncio.gather(*[approve_single_leave(rid) for rid in req_ids])
        return "\n".join(results)

    # Case 2: Approve all pending leaves
    leave_requests = await get_requested_leave_from_db_tool(auth_header=auth_header, as_list=True)              
    if not leave_requests:
        return "✅ No pending leave requests to approve."
    results = await asyncio.gather(*[approve_single_leave(leave["id"]) for leave in leave_requests])
    return "\n".join(results)

# @mcp.tool()
# async def reject_leaves_tool(
#     req_ids: Optional[List[int]] = None, auth_header: str = ""
# ) -> str:
#     if not await is_manager(auth_header):
#         return "❌ Access Denied. Manager permissions are required."

#     headers = {"Authorization": auth_header}
#     results = []

#     async def reject_single_leave(rid: int) -> str:
#         url = f"{AUTH_SERVICE_URL}/test/leave/reject/{rid}/"
#         async with httpx.AsyncClient() as client:
#             try:
#                 resp = await client.put(url, headers=headers)
#                 print("++++++++++++++++++++++++++++++++++++++++++++++")
#                 resp.raise_for_status()
#                 data = resp.json()

#                 emp_email = data.get("employee_email")
#                 if emp_email:
#                     # Send notification to employee via notification API
#                     notif_payload = {
#                         "employee_id": emp_email,
#                         "message": f"❌ Your leave request {rid} has been REJECTED."
#                     }
#                     await client.post("http://127.0.0.1:8001/notify-employee", json=notif_payload)

#                 return f"❌ Leave request {rid} rejected successfully."
#             except httpx.HTTPStatusError as e:
#                 return f"⚠️ Failed to reject leave {rid}: {e.response.text}"

#     # Case 1: Reject specific IDs
#     if req_ids:
#         tasks = [reject_single_leave(rid) for rid in req_ids]
#         results = await asyncio.gather(*tasks)
#         return "\n".join(results)
    

#     # Case 2: Reject all requested leaves
#     leave_requests = await get_requested_leave_from_db_tool(auth_header=auth_header, as_list=True)
#     if not leave_requests:
#         return "✅ No pending leave requests to reject."

#     tasks = [reject_single_leave(leave["id"]) for leave in leave_requests]
#     results = await asyncio.gather(*tasks)
#     return "\n".join(results)
@mcp.tool()
async def reject_leaves_tool(
    req_ids: Optional[List[int]] = None, auth_header: str = ""
) -> str:
    if not await is_manager(auth_header):
        return "❌ Access Denied. Manager permissions are required."

    headers = {"Authorization": auth_header}

    async def reject_single_leave(rid: int) -> str:
        emp_id = None
        # 🔹 Get manager profile to determine emp_id
        try:
            async with httpx.AsyncClient() as client:
                profile_resp = await client.get(f"{AUTH_SERVICE_URL}/test/auth/profile/", headers=headers)
                if profile_resp.status_code == 200:
                    emp_id = profile_resp.json().get("id", None)
        except Exception as e:
            print("⚠️ Failed to fetch employee profile:", e)

        # 🔹 Reject leave
        url = f"{AUTH_SERVICE_URL}/test/leave/reject/{rid}/"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.put(url, headers=headers)
                resp.raise_for_status()

                # 🔹 Notify employee (use emp_id from profile)
                if emp_id:
                    notif_payload = {
                        "employee_id": emp_id,
                        "leave_id": rid,
                        "message": f" Your leave request {rid} has been REJECTED."
                    }
                    await client.post(f"{CHAT_BACKEND_URL}/notify-employee", json=notif_payload)

                return f"✅ Leave request {rid} rejected successfully."
            except httpx.HTTPStatusError as e:
                return f"❌ Failed to reject leave {rid}: {e.response.text}"
            except Exception as e:
                return f"⚠️ Error while rejecting leave {rid}: {str(e)}"

    # Case 1: Reject specific IDs
    if req_ids:
        results = await asyncio.gather(*[reject_single_leave(rid) for rid in req_ids])
        return "\n".join(results)

    # Case 2: Reject all pending leaves
    leave_requests = await get_requested_leave_from_db_tool(auth_header=auth_header, as_list=True)
    if not leave_requests:
        return "✅ No pending leave requests to reject."

    results = await asyncio.gather(*[reject_single_leave(leave["id"]) for leave in leave_requests])
    return "\n".join(results)




if __name__ == "__main__":
    print("Leave MCP Agent running (default host:8002)")
    mcp.run("streamable-http")