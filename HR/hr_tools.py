# HR/hr_tools.py

from langchain.tools import tool
import aiohttp
import requests
from typing import Annotated,Literal
from langgraph.prebuilt import InjectedState


# @tool
# def apply_leave_tool(
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

#     print("apply tool ========================")
#     url = f"http://127.0.0.1:7000/leave/request-creation?type_id={leave_type_id}&emp_id={emp_id}"
#     print("apply tool ++++++++++++++++++++++++++")
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

@tool
def apply_leave_tool(
    leave_type: Annotated[str, Literal["sick", "casual", "earned"]],
    start_date: str,
    end_date: str,
    description: str,
    state: Annotated[dict, InjectedState]={},
) -> str:
    """
    Use this tool only to apply leave request.

    Args:
        leave_type (str): Type of leave to apply for. Options: "sick", "casual", "earned".
        start_date (str): Start date of the leave.
        end_date (str): End date of the leave.
        description (str): Reason for the leave.
    """

    emp_id = 1  # (Hardcoded for now, can later be dynamic from state)

    # Map leave type to API IDs
    if leave_type.lower() == "sick":
        leave_type_id = 2
    elif leave_type.lower() == "casual":
        leave_type_id = 1
    elif leave_type.lower() == "earned":
        leave_type_id = 3
    else:
        return "Error: Invalid leave type. Use one of: sick, casual, earned."

    # API endpoint
    
    url = f"http://127.0.0.1:7000/leave/request-creation?type_id={leave_type_id}&emp_id={emp_id}"
    # url = f"http://127.0.0.1:7000/test/leave/user-request/"

    # Form data payload
    form_data = {
        "employee_id": str(emp_id),
        "leave_type_id": str(leave_type_id),
        "start_date": start_date,
        "start_date_breakdown": "full_day",
        "end_date": end_date,
        "end_date_breakdown": "full_day",
        "description": description,
    }

    try:
        response = requests.post(url, data=form_data)

        if response.status_code == 400:
            json_data = response.json()
            first_error = json_data.get("errors", {}).get("__all__", ["Unknown error"])[0]
            return f"Leave request failed: {first_error}"

        elif response.status_code == 200:
            json_data = response.json()
            leave_id = json_data.get("leave_request_id")
            if leave_id:
                return f"Leave request submitted successfully! Request ID: {leave_id}"
            return "Leave request submitted but no ID returned."

        else:
            return f"Unexpected response: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error while submitting leave request: {str(e)}"



@tool
def approve_leave_tool(
    req_id: Annotated[str, "Leave request ID to approve"]
) -> str:
    """
    Approve a leave request by its request ID.

    Args:
        req_id (str): The ID of the leave request to approve.

    Returns:
        str: Success or error message.
    """
    print("approve tool ++++++++++++++++++++++++++")
    url = f"http://127.0.0.1:8001/leave/request-approve/{req_id}"

    form_data = {"request_id": str(req_id)}

    try:
        response = requests.post(url, data=form_data)

        if response.status_code == 400:
            json_data = response.json()
            first_error = json_data.get("errors", {}).get("__all__", ["Unknown error"])[0]
            return f"Leave approval failed: {first_error}"

        elif response.status_code == 200:
            json_data = response.json()
            leave_id = json_data.get("leave_request_id")
            if leave_id:
                return f"Leave request approved successfully! Request ID: {leave_id}"
            return "Leave approved but no request ID returned."

        else:
            return f"Unexpected response {response.status_code}: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Network error while approving leave: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"