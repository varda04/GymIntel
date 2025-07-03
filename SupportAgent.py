from dotenv import load_dotenv
load_dotenv()

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

from crewai import Agent, Task, Crew
from langchain_ollama import OllamaLLM

from agent_logic import parse_query_support
from my_llm_wrapper import OllamaCrewAIWrapper
from tools.ExternalApiWrapper import CreateEnquiryTool, CreateOrderTool
from tools.MongoToolWrapper import (
    GetClientInfoTool,
    GetClientServicesTool,
    ListClassesTool,
    FilterClassesByInstructorTool,
    FilterClassesByStatusTool
)

# Optional telemetry
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

# Initialize your model wrapper
ollama_llm = OllamaCrewAIWrapper(model_name="llama3")

# === Define intent-to-tool mapping ===
INTENT_TOOL_MAP = {
    "create_order": {
        "tool": CreateOrderTool,
        "description_template": "Create an order for {MISC} for client {PER} with email {EMAIL} and phone number {PHONE}",
        "expected_output": "Confirmation of order creation"
    },
    "create_enquiry": {
        "tool": CreateEnquiryTool,
        "description_template": "Create an enquiry for {MISC} for {PER} with email {EMAIL} and phone number {PHONE}",
        "expected_output": "Confirmation of enquiry creation"
    },
    "get_client_info": {
        "tool": GetClientInfoTool,
        "description_template": "Fetch information for client {PER} with email {EMAIL} and phone number {PHONE}",
        "expected_output": "Client info retrieved"
    },
    "get_client_services": {
        "tool": GetClientServicesTool,
        "description_template": "Get services for client {PER}",
        "expected_output": "List of client services"
    },
    "list_upcoming_classes": {
        "tool": ListClassesTool,
        "description_template": "List all available classes and use the tool described by ListClassesTool",
        "expected_output": "List of classes from the database"
    },
    "filter_classes_by_instructor": {
        "tool": FilterClassesByInstructorTool,
        "description_template": "Filter classes by instructor {PER} using the tool described by FilterClassesByInstructor",
        "expected_output": "Filtered class list"
    },
    "filter_classes_by_status": {
        "tool": FilterClassesByStatusTool,
        "description_template": "Filter classes with status {STATUS}",
        "expected_output": "Filtered class list"
    },
}

# === Agent with all tools ===
support_agent = Agent(
    name="Support Agent",
    role="Help customers resolve their queries",
    goal="Handle customer requests",
    backstory="You are responsible for managing orders and clients.",
    tools=[
        tool_class()
        for tool_class in {mapping["tool"] for mapping in INTENT_TOOL_MAP.values()}
    ],
    llm=ollama_llm,
    allow_delegation=True,
    allow_multiple_tool_calls_per_step=True
)

def run_support_agent(query):
    parsed_result = parse_query_support(query)
    print(f"[DEBUG] Parsed result : {parsed_result}")

    intent = parsed_result.get("intent")
    entities = parsed_result.get("entities", {})

    # === Build task based on intent ===
    if intent not in INTENT_TOOL_MAP:
        raise ValueError(f"❌ Unsupported intent: {intent}")

    mapping = INTENT_TOOL_MAP[intent]
    description = mapping["description_template"].format(
        PER=entities.get("PER", "Unknown"),
        MISC=entities.get("MISC", "Unknown"),
        EMAIL=entities.get("EMAIL", "Unknown"),
        PHONE=entities.get("PHONE", "Unknown"),
        STATUS= entities.get("STATUS", "Unknown")
    )
    expected_output = mapping["expected_output"]
    # print("[DEBUG] Raw entities before sanitizing:", entities)
    # print(f"[DEBUG] Entity types: { {k: type(v) for k, v in entities.items()} }")
    # Flatten input dictionary for CrewAI (strip out nested descriptions if any)
    clean_entities = {
        k: v["description"] if isinstance(v, dict) and "description" in v else v
        for k, v in entities.items()
    }
    print("[DEBUG] Clean entities after sanitizing:", clean_entities)

    task = Task(
        description=description,
        expected_output=expected_output,
        agent=support_agent,
        input=clean_entities
    )

    # === Crew setup ===
    crew = Crew(
        agents=[support_agent],
        tasks=[task],
        verbose=True,
        allow_multiple_tool_calls_per_step=True
    )

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