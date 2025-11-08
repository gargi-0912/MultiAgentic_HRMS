# import streamlit as st
# import requests
# import os

# # --- Config ---
# BACKEND_URL = os.getenv("HR_ASSISTANT_BACKEND", "http://0.0.0.0:8001/chat")

# st.set_page_config(page_title="HR Assistant", page_icon="🤖", layout="centered")

# # --- Title ---
# st.markdown(
#     "<h2 style='text-align: center;'>🤖 HR Assistant (Leave Management)</h2>",
#     unsafe_allow_html=True,
# )
# st.markdown("---")

# # --- Initialize chat history ---
# if "messages" not in st.session_state:
#     st.session_state["messages"] = []

# # --- Display chat history ---
# for msg in st.session_state["messages"]:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # --- Input box at the bottom ---
# if user_input := st.chat_input("Type your request..."):
#     # Store user message
#     st.session_state["messages"].append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     # Send to backend
#     try:
#         with st.spinner("Thinking..."):
#             response = requests.post(BACKEND_URL, json={"message": user_input}, timeout=60)
#             if response.status_code == 200:
#                 bot_reply = response.json().get("response", "⚠️ No response field in backend reply")
#             else:
#                 bot_reply = f"❌ Backend error {response.status_code}: {response.text}"
#     except requests.exceptions.ConnectionError:
#         bot_reply = "🚫 Could not connect to backend. Is it running?"
#     except Exception as e:
#         bot_reply = f"⚠️ Unexpected error: {e}"

#     # Store assistant reply
#     st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
#     with st.chat_message("assistant"):
#         st.markdown(bot_reply)


# import streamlit as st
# import requests
# import os
# import uuid

# # --- Configuration ---
# AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL", "http://127.0.0.1:7000")
# CHAT_BACKEND_URL = os.getenv("HR_ASSISTANT_BACKEND", "http://0.0.0.0:8001")

# # Specific endpoints
# LOGIN_URL = f"{AUTH_BACKEND_URL}/test/auth/login/"
# CHAT_URL = f"{CHAT_BACKEND_URL}/chat"
# REFRESH_URL = f"{CHAT_BACKEND_URL}/memory"

# st.set_page_config(page_title="HR Assistant", page_icon="🤖", layout="centered")

# # --- Session State Initialization ---
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "username" not in st.session_state:
#     st.session_state.username = ""
# if "token" not in st.session_state:
#     st.session_state.token = ""
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = str(uuid.uuid4())

# # =============================================
# # Login Gate
# # =============================================
# if not st.session_state.logged_in:
#     st.title("🔐 Welcome to the HR Assistant")
#     st.markdown("Please log in to continue.")
#     with st.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login")

#         if submitted:
#             try:
#                 response = requests.post(
#                     LOGIN_URL,
#                     json={"username": username, "password": password}
#                 )
#                 if response.status_code == 200:
#                     token_data = response.json()
#                     st.session_state.logged_in = True
#                     st.session_state.username = username
#                     st.session_state.token = token_data.get("access")
#                     st.rerun()
#                 else:
#                     st.error(f"Login failed: {response.json().get('detail', 'Invalid credentials')}")
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Could not connect to the authentication service: {e}")

# # =============================================
# # Main Chat Application
# # =============================================
# else:
#     # --- Sidebar ---
#     with st.sidebar:
#         st.markdown(f"Welcome, **{st.session_state.username}**!")
#         st.markdown("---")
#         if st.button("🔄️ New Chat"):
#             # Optional: Call backend to clear memory
#             try:
#                 headers = {"Authorization": f"Bearer {st.session_state.token}"}
#                 requests.post(f"{REFRESH_URL}/{st.session_state.thread_id}/refresh", headers=headers, timeout=10)
#             except Exception:
#                 pass # Fail silently if backend is down
#             st.session_state.messages = []
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.rerun()
#         if st.button("Logout"):
#             for key in list(st.session_state.keys()):
#                 del st.session_state[key]
#             st.rerun()

#     # --- Main Chat Interface ---
#     st.markdown("<h2 style='text-align: center;'>🤖 HR Assistant</h2>", unsafe_allow_html=True)
#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     if user_input := st.chat_input("Type your request..."):
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         # --- KEY CHANGE: Payload now includes username for the supervisor ---
#         payload = {
#             "message": user_input,
#             "thread_id": st.session_state["thread_id"],
#             "username": st.session_state["username"],
#         }
        
#         # --- KEY CHANGE: The token is sent in the header for authentication ---
#         headers = {"Authorization": f"Bearer {st.session_state.token}"}

#         try:
#             with st.spinner("Thinking..."):
#                 response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60)
#                 if response.status_code == 200:
#                     bot_reply = response.json().get("response", "No response from backend.")
#                 else:
#                     bot_reply = f"❌ Backend error {response.status_code}: {response.text}"
#         except requests.exceptions.RequestException as e:
#             bot_reply = f"⚠️ An error occurred: {e}"

#         st.session_state.messages.append({"role": "assistant", "content": bot_reply})
#         with st.chat_message("assistant"):
#             st.markdown(bot_reply)
# import streamlit as st
# import requests
# import os
# import uuid

# # --- Configuration ---
# AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL", "http://127.0.0.1:7000")
# CHAT_BACKEND_URL = os.getenv("HR_ASSISTANT_BACKEND", "http://0.0.0.0:8001")

# # Endpoints
# LOGIN_URL = f"{AUTH_BACKEND_URL}/test/auth/login/"
# CHAT_URL = f"{CHAT_BACKEND_URL}/chat"
# REFRESH_URL = f"{CHAT_BACKEND_URL}/memory"
# NOTIF_URL = f"{CHAT_BACKEND_URL}/notify-manager"  # fetch manager notifications

# st.set_page_config(page_title="HR Assistant", page_icon="🤖", layout="centered")

# # --- Session State Initialization ---
# for key in ["logged_in", "username", "token", "messages", "thread_id"]:
#     if key not in st.session_state:
#         if key == "thread_id":
#             st.session_state[key] = str(uuid.uuid4())
#         elif key == "messages":
#             st.session_state[key] = []
#         else:
#             st.session_state[key] = "" if key != "logged_in" else False

# # --- Helper function to fetch manager notifications ---
# def fetch_notifications(headers):
#     try:
#         resp = requests.get(NOTIF_URL, headers=headers, timeout=5)
#         if resp.status_code == 200:
#             return resp.json().get("notifications", [])
#     except Exception:
#         return []
#     return []

# # =============================================
# # Login Gate
# # =============================================
# if not st.session_state.logged_in:
#     st.title("🔐 Welcome to the HR Assistant")
#     st.markdown("Please log in to continue.")
#     with st.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login")

#         if submitted:
#             try:
#                 response = requests.post(
#                     LOGIN_URL,
#                     json={"username": username, "password": password}
#                 )
#                 if response.status_code == 200:
#                     token_data = response.json()
#                     st.session_state.logged_in = True
#                     st.session_state.username = username
#                     st.session_state.token = token_data.get("access")
#                     st.stop()  # restart app after login
#                 else:
#                     st.error(f"Login failed: {response.json().get('detail', 'Invalid credentials')}")
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Could not connect to the authentication service: {e}")

# # =============================================
# # Main Chat Application
# # =============================================
# else:
#     headers = {"Authorization": f"Bearer {st.session_state.token}"}

#     # --- Sidebar ---
#     with st.sidebar:
#         st.markdown(f"Welcome, **{st.session_state.username}**!")
#         st.markdown("---")
#         if st.button("🔄️ New Chat"):
#             try:
#                 requests.post(f"{REFRESH_URL}/{st.session_state.thread_id}/refresh", headers=headers, timeout=10)
#             except Exception:
#                 pass
#             st.session_state.messages = []
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.stop()
#         if st.button("Logout"):
#             for key in list(st.session_state.keys()):
#                 del st.session_state[key]
#             st.stop()

#     # --- Fetch and display notifications for managers ---
#     if st.session_state.username == "admin@vinove.com":
#         notifications = fetch_notifications(headers)
#         for notif in notifications:
#             if notif.get("message") not in [m["content"] for m in st.session_state.messages]:
#                 st.session_state.messages.append({"role": "assistant", "content": f"🔔 {notif.get('message')}"})

#     # --- Main Chat Interface ---
#     st.markdown("<h2 style='text-align: center;'>🤖 HR Assistant</h2>", unsafe_allow_html=True)

#     # Show previous messages including notifications
#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     # Chat input
#     if user_input := st.chat_input("Type your request..."):
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         payload = {
#             "message": user_input,
#             "thread_id": st.session_state["thread_id"],
#             "username": st.session_state["username"],
#         }

#         try:
#             with st.spinner("Thinking..."):
#                 response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60)
#                 if response.status_code == 200:
#                     bot_reply = response.json().get("response", "No response from backend.")
#                 else:
#                     bot_reply = f"❌ Backend error {response.status_code}: {response.text}"
#         except requests.exceptions.RequestException as e:
#             bot_reply = f"⚠️ An error occurred: {e}"

#         st.session_state.messages.append({"role": "assistant", "content": bot_reply})
#         with st.chat_message("assistant"):
#             st.markdown(bot_reply)



# r8
# import streamlit as st
# import requests
# import os
# import uuid
# from streamlit_autorefresh import st_autorefresh

# # --- Configuration ---
# AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL", "http://127.0.0.1:7000")
# CHAT_BACKEND_URL = os.getenv("HR_ASSISTANT_BACKEND", "http://0.0.0.0:8001")

# # Endpoints
# LOGIN_URL = f"{AUTH_BACKEND_URL}/test/auth/login/"
# CHAT_URL = f"{CHAT_BACKEND_URL}/chat"
# REFRESH_URL = f"{CHAT_BACKEND_URL}/memory"
# NOTIF_URL = f"{CHAT_BACKEND_URL}/notify-manager"
# EMP_NOTIF_URL = f"{CHAT_BACKEND_URL}/notify-employee"

# st.set_page_config(page_title="HR Assistant", page_icon="🤖", layout="centered")

# # --- Session State Initialization ---
# for key in ["logged_in", "username", "token", "messages", "thread_id", "last_notif_count"]:
#     if key not in st.session_state:
#         if key == "thread_id":
#             st.session_state[key] = str(uuid.uuid4())
#         elif key == "messages":
#             st.session_state[key] = []
#         elif key == "last_notif_count":
#             st.session_state[key] = 0
#         else:
#             st.session_state[key] = "" if key != "logged_in" else False

# # --- Helper function to fetch manager notifications ---
# def fetch_notifications(headers):
#     try:
#         resp = requests.get(NOTIF_URL, headers=headers, timeout=5)
#         if resp.status_code == 200:
#             return resp.json().get("notifications", [])
#     except Exception:
#         return []
#     return []

# # --- Helper function to fetch employee notifications ---
# def fetch_employee_notifications(headers, employee_id: str):
#     try:
#         resp = requests.get(
#             EMP_NOTIF_URL,
#             params={"employee_id": employee_id},
#             headers=headers,
#             timeout=5
#         )
#         if resp.status_code == 200:
#             return resp.json().get("notifications", [])
#     except Exception:
#         return []
#     return []

# # =============================================
# # Login Gate
# # =============================================
# if not st.session_state.logged_in:
#     st.title("🔐 Welcome to the HR Assistant")
#     st.markdown("Please log in to continue.")
#     with st.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login")

#         if submitted:
#             try:
#                 response = requests.post(
#                     LOGIN_URL,
#                     json={"username": username, "password": password}
#                 )
#                 if response.status_code == 200:
#                     token_data = response.json()
#                     st.session_state.logged_in = True
#                     st.session_state.username = username
#                     st.session_state.token = token_data.get("access")
#                     st.rerun()  # restart app after login
#                 else:
#                     st.error(f"Login failed: {response.json().get('detail', 'Invalid credentials')}")
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Could not connect to the authentication service: {e}")

# # =============================================
# # Main Chat Application
# # =============================================
# else:
#     headers = {"Authorization": f"Bearer {st.session_state.token}"}

#     # --- Sidebar ---
#     with st.sidebar:
#         st.markdown(f"Welcome, **{st.session_state.username}**!")
#         st.markdown("---")

#         if st.button("🔄️ New Chat"):
#             try:
#                 headers = {"Authorization": f"Bearer {st.session_state.token}"}
#                 requests.post(f"{REFRESH_URL}/{st.session_state.thread_id}/refresh", headers=headers, timeout=10)
#             except Exception:
#                 pass

#             # Reset chat state
#             st.session_state.messages = []
#             st.session_state.thread_id = str(uuid.uuid4())
#             st.rerun()

#         if st.button("Logout"):
#             for key in list(st.session_state.keys()):
#                 del st.session_state[key]
#             st.rerun()

#     # --- Autorefresh for notifications every 5 seconds ---
#     if st.session_state.username == "admin@vinove.com":
#         # Manager notifications
#         st_autorefresh(interval=5000, key="notif_refresh_mgr")
#         notifications = fetch_notifications(headers)
#         new_count = len(notifications)
#         if new_count > st.session_state.last_notif_count:
#             for notif in notifications[st.session_state.last_notif_count:]:
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": f"🔔 {notif.get('message')}"
#                 })
#             st.session_state.last_notif_count = new_count
#     else:
#         # Employee notifications
#         st_autorefresh(interval=5000, key="notif_refresh_emp")
#         notifications = fetch_employee_notifications(headers, st.session_state.username)
#         new_count = len(notifications)
#         if new_count > st.session_state.last_notif_count:
#             for notif in notifications[st.session_state.last_notif_count:]:
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": f"📩 {notif.get('message')}"
#                 })
#             st.session_state.last_notif_count = new_count

#     # --- Main Chat Interface ---
#     st.markdown("<h2 style='text-align: center;'>🤖 HR Assistant</h2>", unsafe_allow_html=True)

#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     # --- Chat input ---
#     # if user_input := st.chat_input("Type your request..."):
#     #     st.session_state.messages.append({"role": "user", "content": user_input})
#     #     with st.chat_message("user"):
#     #         st.markdown(user_input)

#     #     payload = {
#     #         "message": user_input,
#     #         "thread_id": st.session_state["thread_id"],
#     #         "username": st.session_state["username"],
#     #     }

#     #     try:
#     #         with st.spinner("Thinking..."):
#     #             response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60)
#     #             if response.status_code == 200:
#     #                 bot_reply = response.json().get("response", "No response from backend.")
#     #             else:
#     #                 bot_reply = f"❌ Backend error {response.status_code}: {response.text}"
#     #     except requests.exceptions.RequestException as e:
#     #         bot_reply = f"⚠️ An error occurred: {e}"

#     #     st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
#     #     st.rerun()
#     #     with st.chat_message("assistant"):
#     #         st.markdown(bot_reply)
#     # --- Chat input ---
#     if user_input := st.chat_input("Type your request..."):
#         # Add user message
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.markdown(user_input)

#         # Prepare payload
#         payload = {
#             "message": user_input,
#             "thread_id": st.session_state["thread_id"],
#             "username": st.session_state["username"],
#         }

#         # Call backend
#         try:
#             with st.spinner("Thinking..."):
#                 response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60)
#                 if response.status_code == 200:
#                     bot_reply = response.json().get("response", "No response from backend.")
#                 else:
#                     bot_reply = f"❌ Backend error {response.status_code}: {response.text}"
#         except requests.exceptions.RequestException as e:
#             bot_reply = f"⚠️ An error occurred: {e}"

#         # Append assistant reply
#         st.session_state.messages.append({"role": "assistant", "content": bot_reply})

#         # Show reply immediately (no rerun)
#         with st.chat_message("assistant"):
#             st.markdown(bot_reply)

       
# '''''''''''''''''''
import streamlit as st
import requests
import os
import uuid
from streamlit_autorefresh import st_autorefresh

# --- Configuration ---
AUTH_BACKEND_URL = os.getenv("AUTH_BACKEND_URL", "http://127.0.0.1:7000")
CHAT_BACKEND_URL = os.getenv("HR_ASSISTANT_BACKEND", "http://0.0.0.0:8001")

# Endpoints
LOGIN_URL = f"{AUTH_BACKEND_URL}/test/auth/login/"
CHAT_URL = f"{CHAT_BACKEND_URL}/chat"
REFRESH_URL = f"{CHAT_BACKEND_URL}/memory"
NOTIF_URL = f"{CHAT_BACKEND_URL}/notify-manager"
EMP_NOTIF_URL = f"{CHAT_BACKEND_URL}/notify-employee"

st.set_page_config(page_title="HR Assistant", page_icon="🤖", layout="centered")

# --- Session State Initialization ---
for key in ["logged_in", "username", "token", "messages", "thread_id", "last_notif_count"]:
    if key not in st.session_state:
        if key == "thread_id":
            st.session_state[key] = str(uuid.uuid4())
        elif key == "messages":
            st.session_state[key] = []
        elif key == "last_notif_count":
            st.session_state[key] = 0
        else:
            st.session_state[key] = "" if key != "logged_in" else False

# --- Helper Functions ---
def fetch_notifications(headers):
    try:
        resp = requests.get(NOTIF_URL, headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("notifications", [])
    except Exception:
        return []
    return []

def fetch_employee_notifications(headers, employee_id: str):
    try:
        resp = requests.get(EMP_NOTIF_URL, params={"employee_id": employee_id}, headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("notifications", [])
    except Exception:
        return []
    return []

def load_memory_from_backend():
    """Fetch memory from backend for current thread and update session_state.messages"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        resp = requests.get(f"{REFRESH_URL}/{st.session_state.thread_id}", headers=headers, timeout=5)
        if resp.status_code == 200:
            history = resp.json().get("history", [])
            # Avoid duplicate messages
            existing_contents = {m["content"] for m in st.session_state.messages}
            for m in history:
                if m["content"] not in existing_contents:
                    st.session_state.messages.append({"role": m["role"], "content": m["content"]})
    except Exception:
        pass

# =============================================
# Login Gate
# =============================================
if not st.session_state.logged_in:
    st.title("🔐 Welcome to the HR Assistant")
    st.markdown("Please log in to continue.")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            try:
                response = requests.post(
                    LOGIN_URL,
                    json={"username": username, "password": password}
                )
                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.token = token_data.get("access")
                    st.rerun()  # restart app after login
                else:
                    st.error(f"Login failed: {response.json().get('detail', 'Invalid credentials')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the authentication service: {e}")

# =============================================
# Main Chat Application
# =============================================
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # --- Sidebar ---
    with st.sidebar:
        st.markdown(f"Welcome, **{st.session_state.username}**!")
        st.markdown("---")

        if st.button("🔄️ New Chat"):
            try:
                requests.post(f"{REFRESH_URL}/{st.session_state.thread_id}/refresh", headers=headers, timeout=10)
            except Exception:
                pass

            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.last_notif_count = 0
            st.rerun()

        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- Autorefresh for notifications every 5 seconds ---
    if st.session_state.username.lower() == "admin@vinove.com":
        st_autorefresh(interval=5000, key="notif_refresh_mgr")
        notifications = fetch_notifications(headers)
    else:
        st_autorefresh(interval=5000, key="notif_refresh_emp")
        notifications = fetch_employee_notifications(headers, st.session_state.username)
        # st.rerun()

    new_count = len(notifications)
    if new_count > st.session_state.last_notif_count:
        for notif in notifications[st.session_state.last_notif_count:]:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"🔔 {notif.get('message')}" if st.session_state.username.lower() == "admin@vinove.com" else f"📩 {notif.get('message')}"
            })
        st.session_state.last_notif_count = new_count

    # --- Load memory from backend at start ---
    load_memory_from_backend()

    # --- Main Chat Interface ---
    st.markdown("<h2 style='text-align: center;'>🤖 HR Assistant</h2>", unsafe_allow_html=True)
   

    # Display all messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Chat Input ---
    if user_input := st.chat_input("Type your request..."):
        # Append user message locally
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Send to backend
        payload = {
            "message": user_input,
            "thread_id": st.session_state.thread_id,
            "username": st.session_state.username,
        }
        bot_reply = ""
        try:
            with st.spinner("Thinking..."):
                response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60)
                if response.status_code == 200:
                    bot_reply = response.json().get("response", "No response from backend.")
                else:
                    bot_reply = f"❌ Backend error {response.status_code}: {response.text}"
        except requests.exceptions.RequestException as e:
            bot_reply = f"⚠️ An error occurred: {e}"

        # Append assistant reply locally
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)


