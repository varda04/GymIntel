from pydantic import BaseModel
from crewai.tools import BaseTool
from tools.ExternalApi import ExternalAPI
from tools.MongoTool import MongoDBTool

api = ExternalAPI()
mongo_tool = MongoDBTool()

# --- Argument Schemas ---
class EnquiryArgs(BaseModel):
    PER: str = None
    PHONE: str = None
    EMAIL: str = None
    MISC: str = None

class OrderArgs(BaseModel):
    PER: str
    MISC: str  # Assuming this is service name


# --- Create Enquiry Tool ---
class CreateEnquiryTool(BaseTool):
    name: str = "Create Enquiry"
    description: str = "Create a new client enquiry using name, email, phone, and optional notes."
    args_schema: type = EnquiryArgs

    def _run(self, PER=None, PHONE=None, EMAIL=None, MISC=None) -> str:
        if not (EMAIL or PHONE):
            return "❌ Missing contact information to create enquiry."
        print(f"[DEBUG] in ExternalApiWrapper- CreateEnquiryTool {PER}--{PHONE}---{EMAIL}----{MISC}")
        notes = MISC or "No additional notes."
        res = api.create_enquiry(PER, EMAIL, PHONE, notes)
        return f"✅ Enquiry created: {res}"


# --- Create Order Tool ---
class CreateOrderTool(BaseTool):
    name: str = "Create Order"
    description: str = "Create a new order for an existing client and service."
    args_schema: type = OrderArgs

    def _run(self, PER=None, MISC=None) -> str:
        print("[DEBUG] Create order tool has been invoked")

        if not (PER and MISC):
            return "❌ Missing client name or service name."

        client = mongo_tool.get_client_by_name(PER)
        if not client:
            return f"❌ No client found with name: {PER}"

        client_id = client["_id"]
        existing_order = mongo_tool.db.orders.find_one({"service_name": MISC})
        print(f"[DEBUG] existing orders checked for price. found {existing_order}")

        amount = existing_order.get("amount", 1000) if existing_order else 1000
        res = api.create_order(client_id, MISC, amount)
        return f"✅ Order created: {res}"