from crewai import Agent, Crew, Task
from agent_logic import parse_query_dashboard
from my_llm_wrapper import OllamaCrewAIWrapper
from tools.MongoToolWrapper import (
    AttendanceReportTool,
    RevenueMetricsTool,
    OutstandingPaymentsTool,
    ActiveInactiveClientsTool,
    FetchClientBirthdaysTool,
    NewClientsThisMonthTool,
    ServiceAnalyticsTool
    # ServiceAnalyticsTool,
    # AttendanceReportTool
)

# LLM Wrapper
ollama_llm = OllamaCrewAIWrapper(model_name="llama3")

# Map intents to tools and descriptions
INTENT_TOOL_MAP = {
    "get_revenue_metrics": {
        "tool": RevenueMetricsTool(),
        "description_template": "Get revenue for month {MONTH}, and year {YEAR} using the Revenue Metrics tool",
        "expected_output": "Values returned from the function in simple language, not restructured, fail gracefully if values not returned"
    },
    "get_outstanding_payment": {
        "tool": OutstandingPaymentsTool(),
        "description_template": "Get outstanding payment value using the OutstandingPayments tool",
        "expected_output": "Value returned from the function in simple language, not restructured"
    },
    "get_active_inactive_client_insights": {
        "tool": ActiveInactiveClientsTool(),
        "description_template": "Get active/inactive client counts using ActiveInactiveClientsTool.",
        "expected_output": "Value returned from the function in simple language for active count and inactive count, not restructured"
    },
    "get_client_birthday_reminder": {
        "tool": FetchClientBirthdaysTool(),
        "description_template": "Use this tool to fetch clients with birthdays in the next 30 days. This tool does NOT require any input. It fetches data from MongoDB directly.",
        "expected_output": "Value returned from the function in simple language for birth dates, not restructured"
    },
    "get_new_clients_this_month": {
        "tool": NewClientsThisMonthTool(),
        "description_template": "Use this tool to get clients which joined this month. This tool does NOT require any input. It fetches data from MongoDB directly.",
        "expected_output": "Value returned from the function in simple language for birth dates, not restructured"
    },
    "get_service_analytics": {
        "tool": ServiceAnalyticsTool(),
        "description_template": "Get service analytics including enrollment trends, top services, and course completion rates using the ServiceAnalyticsTool. This tool does NOT require any input. It fetches data from MongoDB directly.",
        "expected_output": "Analytics returned in a simple text format covering trends, top services, and completions."
    },
    "get_attendance_report": {
        "tool": AttendanceReportTool(),
        "description_template": "Get attendance percentages and drop-off rates. class id is {CLASS_ID}. This tool does NOT require any input. It fetches data from MongoDB directly.",
        "expected_output": "Value returned in simple text format for attendance and drop-off."
    }

    # "get_service_analytics": {
    #     "tool": ServiceAnalyticsTool(),
    #     "description_template": "Get service analytics including trends and top courses."
    # },
    # "get_attendance_report": {
    #     "tool": AttendanceReportTool(),
    #     "description_template": "Get attendance percentages and drop-off rates."
    # }
}

# Initialize the agent
dashboard_agent = Agent(
    name="Dashboard Agent",
    role="Provide analytics and metrics useful for business owners by using the tools",
    goal="""Deliver business insights such as revenue, client stats, attendance, 
            and course performance using MongoDB data.""",
    backstory="""You are a data-savvy assistant for a fitness business. You use 
                 data from MongoDB to answer questions about revenue, clients, 
                 courses, and attendance. Your responses should help owners make decisions.""",
    tools=[tool["tool"] for tool in INTENT_TOOL_MAP.values()],
    verbose=True,
    llm=ollama_llm,
    allow_delegation=True,
    allow_multiple_tool_calls_per_step=True
)

def run_dashboard_agent(query):
    # query = "Können Sie Kunden abrufen, deren Geburtstag bald ansteht?"
    parsed = parse_query_dashboard(query)
    print(f"[DEBUG] Parsed result : {parsed}")


    intent = parsed["intent"]
    entities = parsed.get("entities", {})

    # Match to tool
    mapping = INTENT_TOOL_MAP[intent]
    description = mapping["description_template"].format(
        MONTH=entities.get("MONTH", "Unknown"),
        MISC=entities.get("MISC", "Unknown"),
        YEAR=entities.get("YEAR", "Unknown"),
        CLASS_ID= entities.get("CLASS_ID", "Unknown")
    )
    expected_output = mapping["expected_output"]
    if not mapping:
        raise ValueError(f"❌ No tool found for intent: {intent}")

    tool = mapping["tool"]

    # Build input args (pass month and year if present)
    args = {}
    if "MONTH" in entities:
        args["month"] = entities["MONTH"]
    if "YEAR" in entities:
        args["year"] = entities["YEAR"]

    # Create a Task for the Agent to execute
    task = Task(
        description=description,
        agent=dashboard_agent,
        expected_output=expected_output,
        input= entities
    )

    print("\n[DEBUG] --- Task Created ---")
    print("[DEBUG] Task Object:", task)

    crew = Crew(
        agents=[dashboard_agent],
        tasks=[task],
        verbose=True,
        allow_tool_use=True,
        allow_multiple_tool_calls_per_step=True
    )

    print("[DEBUG] Crew Configured:")
    print(f"Agents: {[agent for agent in crew.agents]}")
    print(f"Tasks: {[t.name for t in crew.tasks]}")

    
    print("\n🚀 Starting Crew Task Execution...\n")
    try:
        result = crew.kickoff()
        print("\n✅ Result:")
        print(result)
        return result
    except Exception as e:
        import traceback
        print("\n❌ Crew failed:")
        traceback.print_exc()