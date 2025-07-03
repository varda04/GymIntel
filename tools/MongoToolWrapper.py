from typing import List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel
from tools.MongoTool import MongoDBTool
from tools.ExternalApi import ExternalAPI

mongo = MongoDBTool()
api = ExternalAPI()

class ListClassesToolSchema(BaseModel):
    pass

class GetClientInfoToolSchema(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

class GetClientServicesToolSchema(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

class FilterClassesByInstructorSchema(BaseModel):
    name: str | None = None

class FilterClassesByStatusSchema(BaseModel):
    name: str | None = None

class RevenueMetricsSchema(BaseModel):
    name: str | None = None
    month: str | None = None
    year: str | None = None

class OutstandingPaymentsSchema(BaseModel):
    pass

class GetClientInfoTool(BaseTool):
    name: str = "Get Client Info"
    description: str = "Get client info by name, email, or phone"
    args_schema: type = GetClientInfoToolSchema

    def _run(self, name=None, email=None, phone=None) -> str:
        print(f"{name}, {email}, {phone} debug from get client info")
        if name and name != "Unknown":
            client= mongo.get_client_by_name(name)
        if email and email != "Unknown":
            client= mongo.get_client_by_email(email)
        if phone and phone != "Unknown":
            client= mongo.get_client_by_phone(phone)
        if not client:
            return "❌ Client not found."
        return {
            "id": client["_id"],
            "name": client["name"],
            "email": client["email"],
            "phone": client["phone"],
            "status": client["status"],
            "birthdate": client["birthdate"],
            "joining date": client["joined_on"]
        }

class GetClientServicesTool(BaseTool):
    name: str = "Get Client Services"
    description: str = "Get list of services the client is enrolled in"
    args_schema: type= GetClientServicesToolSchema

    def _run(self, name= None, **kwargs) -> str:
        client = mongo.get_client_by_name(name)
        if not client:
            return f"❌ No client found with name {name}"

        services = mongo.get_client_services(client["_id"])
        if not services:
            return f"ℹ️ {name} has not enrolled in any services yet."

        response = f"📋 Services for {name}:\n"
        for s in services:
            response += f"- {s['service_name']} (Status: {s['status']})\n"
        return response.strip()


class ListClassesTool(BaseTool):
    name: str = "List Classes"
    description: str = "Lists all upcoming scheduled classes or services."
    args_schema: type= ListClassesToolSchema

    def _run(self, **kwargs) -> str:
        upcoming = mongo.list_upcoming_classes()
        print("[DEBUG] Mongo results:", upcoming)
        if not upcoming:
            return "📭 No upcoming classes found."
        return {
            "upcoming_classes": [
                {"instructor": c["instructor"], "date": str(c["date"])}
                for c in upcoming
            ]
        }
    def invoke(self, input_data, **kwargs):
        """
        Overrides BaseTool.invoke to handle malformed inputs.
        """
        import json

        # Try to parse input if it's a string
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
                if isinstance(input_data, list):
                    # Convert list of dicts to single merged dict
                    input_data = {k: v for d in input_data if isinstance(d, dict) for k, v in d.items()}
            except Exception:
                input_data = {}

        if not isinstance(input_data, dict):
            input_data = {}

        return self._run(**input_data)


class FilterClassesByInstructorTool(BaseTool):
    name: str = "Filter Classes by Instructor"
    description: str = "Filter scheduled classes by instructor name."
    args_schema: type= FilterClassesByInstructorSchema

    def _run(self, name= None) -> str:
        print(f"[DEBUG] Instructor name passed to this function: {name}")
        if name is None:
            return "❌ No instructor name provided."

        classes = mongo.filter_classes_by_instructor(name)
        if not classes:
            return f"📭 No classes found for instructor {name}."

        return f"📘 Classes by {name}:\n" + "\n".join(f"- {c['course_id']} on {c['date']}" for c in classes)
    
    def invoke(self, input_data, **kwargs):
        import json

        # Try to parse string input
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except Exception:
                input_data = {}

        if not isinstance(input_data, dict):
            input_data = {}

        return self._run(**input_data)


class FilterClassesByStatusTool(BaseTool):
    name: str = "Filter Classes by Status"
    description: str = "Filter classes based on their status (e.g., scheduled, completed, canceled)."
    args_schema: type= FilterClassesByStatusSchema

    def _run(self, name= str) -> str:
        if not name:
            return "❌ No status provided."
        print(f"[DEBUG] Status passed to FilterClassesByStatusTool: {name}")

        classes = mongo.filter_classes_by_status(name.lower())
        if not classes:
            return f"📭 No classes found with status '{name}'."

        return f"📘 Classes with status '{name}':\n" + "\n".join(f"- {c['instructor']} on {c['date']}" for c in classes)
    
    def invoke(self, input_data, **kwargs):
        import json

        # Try to parse string input
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except Exception:
                input_data = {}

        if not isinstance(input_data, dict):
            input_data = {}

        return self._run(**input_data)
    
class RevenueMetricsTool(BaseTool):
    name:str = "Revenue Metrics"
    description:str = "Get total revenue from payment records."
    args_schema: type= RevenueMetricsSchema
    
    def _run(self, name:str= None, month: str = None, year: int = None) -> str:
        revenue = mongo.get_total_revenue(month=month, year=year)
        return f"📈 Total revenue{f' for {month} {year}' if month and year else ''}: ₹{revenue}"
    def invoke(self, input_data, **kwargs):
        """
        Overrides BaseTool.invoke to handle malformed inputs.
        """
        import json

        # Try to parse input if it's a string
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
                if isinstance(input_data, list):
                    # Convert list of dicts to single merged dict
                    input_data = {k: v for d in input_data if isinstance(d, dict) for k, v in d.items()}
            except Exception:
                input_data = {}

        if not isinstance(input_data, dict):
            input_data = {}

        return self._run(**input_data)
    
class OutstandingPaymentsTool(BaseTool):
    name:str = "Return Outstanding Payments"
    description:str = "Fetch cummulation of outstanding payments from payment records."
    args_schema: type= OutstandingPaymentsSchema
    
    def _run(self, **kwargs) -> str:
        print("[DEBUG] OutstandingPaymentsTool._run was called")
        outstanding_total = mongo.get_outstanding_payments()
        return f"📈 Total outstanding payments amount: ₹{outstanding_total}"
    
class ActiveInactiveClientsSchema(BaseModel):
    pass

class ActiveInactiveClientsTool(BaseTool):
    name: str = "Active vs Inactive Clients"
    description: str = "Get counts of active and inactive clients from client records."
    args_schema: type = ActiveInactiveClientsSchema

    def _run(self, **kwargs) -> str:
        print("[DEBUG] ActiveInactiveClientsTool._run was called")
        print("[DEBUG] activeinactiveTool is actually being called with:", kwargs)
        counts = mongo.get_active_inactive_clients()
        return f"👥 Active clients: {counts['active']}, Inactive clients: {counts['inactive']}"
    def invoke(self, input_data, **kwargs):
        """
        Overrides BaseTool.invoke to handle malformed inputs.
        """
        import json

        # Try to parse input if it's a string
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
                if isinstance(input_data, list):
                    # Convert list of dicts to single merged dict
                    input_data = {k: v for d in input_data if isinstance(d, dict) for k, v in d.items()}
            except Exception:
                input_data = {}

        if not isinstance(input_data, dict):
            input_data = {}

        return self._run(**input_data)

class BirthdayRemindersSchema(BaseModel):
    pass

class FetchClientBirthdaysTool(BaseTool):
    name: str = "FetchUpcomingBirthdays"
    description: str = "Use this tool to get clients whose birthdays fall within the next 30 days. Always use this when asked about upcoming birthdays."
    args_schema: type = BirthdayRemindersSchema

    def _run(self, **kwargs) -> str:
        print("[DEBUG] BirthdayRemindersTool._run was called")
        print("[DEBUG] BirthdayTool is actually being called with:", kwargs)

        birthdays = mongo.get_clients_with_upcoming_birthdays()
        if not birthdays:
            return "🎉 No client birthdays in the next 30 days."

        lines = [f"{client['name']} (🎂 {client['birthdate']})" for client in birthdays]
        return "🎂 Clients with birthdays in the next 30 days:\n" + "\n".join(lines)

    def invoke(self, input_data, **kwargs):
        """
        Overrides BaseTool.invoke to handle malformed inputs.
        """
        import json

        # Try to parse input if it's a string
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
                if isinstance(input_data, list):
                    # Convert list of dicts to single merged dict
                    input_data = {k: v for d in input_data if isinstance(d, dict) for k, v in d.items()}
            except Exception:
                input_data = {}

        if not isinstance(input_data, dict):
            input_data = {}

        return self._run(**input_data)
    
class NewClientsSchema(BaseModel):
    pass

class NewClientsThisMonthTool(BaseTool):
    name: str = "New Clients This Month"
    description: str = "Use this tool to get clients who joined in the current month."
    args_schema: type = NewClientsSchema

    def _run(self, **kwargs) -> str:
        print("[DEBUG] NewClientsThisMonthTool._run was called")
        print("[DEBUG] NewClientsThisMonthTool is actually being called with:", kwargs)

        if not isinstance(kwargs, dict):
            print("[ERROR] kwargs is not a dict. Defaulting to empty dict.")
            kwargs = {}

        clients = mongo.get_clients_joined_this_month()
        if not clients:
            return "📭 No clients joined this month."

        lines = [f"{c['name']} (📅 {c['join_date']})" for c in clients]
        return "🆕 Clients who joined this month:\n" + "\n".join(lines)

    def invoke(self, input_data, **kwargs):
        import json
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
                if isinstance(input_data, list):
                    input_data = {k: v for d in input_data if isinstance(d, dict) for k, v in d.items()}
            except Exception:
                input_data = {}

        if not isinstance(input_data, dict):
            input_data = {}

        return self._run(**input_data)
    
class ServiceAnalyticsSchema(BaseModel):
    pass
    
class ServiceAnalyticsTool(BaseTool):
    name: str = "Service Analytics"
    description: str = "Analyze enrollment trends, top services, and course completion rates."
    args_schema: type = ServiceAnalyticsSchema

    def _run(self, **kwargs) -> str:
        print("[DEBUG] ServiceAnalyticsTool._run was called")
        
        analytics = mongo.get_service_analytics() 
        if not analytics:
            return "📉 No service analytics data available."

        response = (
            f"📈 Enrollment Trends: {analytics.get('trends')}\n"
            f"🏆 Top Services: {analytics.get('top_services')}\n"
            f"✅ Course Completion Rates: {analytics.get('completion_rates')}"
        )
        return response

    def invoke(self, input_data=None, **kwargs):
        return self._run()
    
class AttendanceReportSchema(BaseModel):
    class_name: Optional[str] = None

    
class AttendanceReportTool(BaseTool):
    name: str = "Attendance Reports"
    description: str = "Get attendance percentage by class and drop-off rates."
    args_schema: type = AttendanceReportSchema

    def _run(self, class_id: str = None, **kwargs) -> str:
        print("[DEBUG] AttendanceReportTool._run called with class:", class_id)

        data = mongo.get_attendance_stats(class_id=class_id)
        if not data:
            return "📭 No attendance data available."

        if isinstance(data, dict):
            # Single class report
            response = (
                f"📊 Attendance Percentage for {data['class_id']}: {data['attendance_percent']}\n"
                f"📉 Drop-off Rate: {data['drop_off_rate']}\n"
                f"📅 Total Sessions: {data['total_sessions']}"
            )
        elif isinstance(data, list):
            # All classes report
            lines = []
            for d in data:
                lines.append(
                    f"🏷️ Class ID: {d['class_id']}\n"
                    f"📊 Attendance: {d['attendance_percent']}\n"
                    f"📉 Drop-off: {d['drop_off_rate']}\n"
                    f"📅 Total Sessions: {d['total_sessions']}"
                )
            response = "📋 Attendance Report for All Classes:\n\n" + "\n\n".join(lines)
        else:
            response = "⚠️ Unexpected data format received from MongoDB."

        return response


    def invoke(self, input_data=None, **kwargs):
        import json
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except Exception:
                input_data = {}

        return self._run(**input_data)

