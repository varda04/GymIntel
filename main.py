# main.py

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timezone
from bson import ObjectId

from DashboardAgent import run_dashboard_agent
from SupportAgent import run_support_agent

app = FastAPI()

client = MongoClient("mongodb://127.0.0.1:27017")
db = client["fitnessDB"]

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/dashboard", response_class=HTMLResponse)
def dashboard_query(request: Request, query: str = Form(...)):
    result = run_dashboard_agent(query)
    return templates.TemplateResponse("partials.html", {
        "request": request,
        "agent": "Dashboard Agent",
        "query": query,
        "response": result
    })

@app.post("/support", response_class=HTMLResponse)
def support_query(request: Request, query: str = Form(...)):
    result = run_support_agent(query)
    return templates.TemplateResponse("partials.html", {
        "request": request,
        "agent": "Support Agent",
        "query": query,
        "response": result
    })

class Enquiry(BaseModel):
    name: str
    email: str
    phone: str
    notes: str

class Order(BaseModel):
    client_id: str
    service_name: str
    amount: float

@app.post("/enquiry")
def create_enquiry(enquiry: Enquiry):
    data = enquiry.model_dump()
    data["created_on"] = datetime.now(timezone.utc).date().isoformat()
    result = db.enquiries.insert_one(data)
    return {"status": "success", "enquiry_id": str(result.inserted_id)}

@app.post("/order")
def create_order(order: Order):
    # Optional: validate client_id exists
    if not db.clients.find_one({"_id": order.client_id}):
        raise HTTPException(status_code=404, detail="Client not found")
    # print("[DEBUG] DB Name:", db.name)

    data = order.model_dump()
    data["status"] = "pending"
    data["created_on"] = datetime.now(timezone.utc).date().isoformat()
    result = db.orders.insert_one(data)
    return {"status": "success", "order_id": str(result.inserted_id)}