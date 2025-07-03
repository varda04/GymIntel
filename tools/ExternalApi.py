# tools/external_api.py

import requests

class ExternalAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def create_enquiry(self, name: str, email: str, phone: str, notes: str = ""):
        """
        Call backend to create a new enquiry.
        """
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "notes": notes
        }
        print(f"[DEBUG] in ExternalApi.py- create_enquiry() data: {data}")
        try:
            res = requests.post(f"{self.base_url}/enquiry", json=data)
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def create_order(self, client_id: str, service_name: str, amount: float):
        data = {
            "client_id": client_id,
            "service_name": service_name,
            "amount": amount
        }
        print(f"[ExternalAPI] Sending POST to /order with: {data}")
        try:
            res = requests.post(f"{self.base_url}/order", json=data)
            res.raise_for_status()
            print(f"[ExternalAPI] Success: {res.json()}")
            return res.json()
        except Exception as e:
            print(f"[ExternalAPI] Failed: {str(e)}")
            return {"error": str(e)}