
from hr_agents import (
    hr_leave_type_agent,
    hr_work_type_agent,
    fallback_agent,
)
from hr_tools import apply_leave_tool, approve_leave_tool


def build_all_agents(model):
    try:
        print("++++++++++build++++++++++++++++")
        return [
            hr_leave_type_agent(model, tools=[apply_leave_tool, approve_leave_tool]),
            hr_work_type_agent(model),
            fallback_agent(model),
        ]
    except Exception as e:
        raise RuntimeError(f"❌ Agent build failed: {e}")