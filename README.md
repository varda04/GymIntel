<h1 align="center">
  <br>
  GymIntel
  <br>
</h1> <h4 align="center">From birthday reminders and revenue breakdowns to multilingual client support, GymIntel turns your data into decisions.</h4> <p align="center"> <a href="#key-features">Key Features</a> • <a href="#getting-started">Getting Started</a> • <a href="#usage">Usage</a> • <a href="#tech-stack">Tech Stack</a></p>
---
GymIntel is your AI-native analytics and support cockpit built for modern fitness businesses. Powered by cutting-edge tools like FastAPI, CrewAI, HTMX, and Ollama, it brings real-time insights, smart assistants, and context-aware automation — all on your own infrastructure.

## Key Features

- 📊 **Dashboard Agent**: Get analytics on revenue, attendance, client engagement, and more.
- 🎂 **Birthday Reminders**: Fetch clients with upcoming birthdays.
- 🤖 **Support Agent**: Answer common support questions from your gym clients.
- 🌍 **Multilingual Queries**: Type in English, Hindi, or German — agents will understand!
- 💡 **Agent-based design**: Each agent has a specific role and uses tools for smart, context-aware answers.
- 🧠 **LLM Integration**: Powered by your choice of local or hosted LLMs (e.g., Ollama, OpenAI).
- 📦 **MongoDB** backend support for real client and service data.
- ⚡ **Real-time UI**: Built with HTMX + TailwindCSS for smooth interactivity.


## Getting Started
Firstly, clone the repo
```
git clone https://github.com/varda04/GymIntel.git
```
Change directory
```
cd GymIntel
```
Start a virtual environament to isolate dependencies and activate it
```
python -m venv venv
venv\Scripts\activate on Windows
```
Run the req file
```
pip install -r requirements.txt
```
Make sure MongoDB is running and accessible on your local port: default is mongodb://127.0.0.1:27017

Run the app:
```
uvicorn main:app --reload
```
Then open: http://localhost:8000

## Usage
🛠️ Support Agent Queries
CreateOrderTool-	Create an order for Varda Kannal for Strength Training
CreateEnquiry-	Create an enquiry for XYZ with email xyz@gmail.com for Pilates Intermediate
ListUpcomingClasses-	List upcoming classes
GetClientServicesTool-	Fetch client services for Ravi Mehta
FilterClassesByInstructor-	Fetch all the courses by instructor Vikram Singh
FilterClassesByStatus-	Fetch all the courses with Scheduled status

📊 Dashboard Agent Queries
RevenueMetricsTool-	What was the total revenue for month January of the year 2025
OutstandingPaymentsTool-	Retrieve total outstanding payment till now
ActiveInactiveClientsTool-	Get active and inactive client counts
FetchClientBirthdaysTool-	Can you retrieve clients with birthdays coming up soon? or Können Sie Kunden abrufen, deren Geburtstag bald ansteht?
NewClientsThisMonthTool-	Fetch clients that joined in the last month
ServiceAnalyticsTool-	Fetch service analytics
AttendanceReportTool-	Fetch attendance report or Fetch attendance report for class_7 or Anwesenheitsberichte für class_7 abrufen

🧠 Multilingual Queries
This system supports multilingual inputs (e.g., German queries like Anwesenheitsberichte für class_7 abrufen) and dynamically translates them for tool invocation.

## Tech Stack
⚙️ Backend
FastAPI – Lightning-fast modern web framework for building robust APIs.
CrewAI – Multi-agent orchestration framework that delegates and executes tasks intelligently.
Ollama – Locally hosted large language models (specifically LLaMA here) for secure and offline inference.
🖼️ Frontend
HTMX – Minimal JavaScript, maximum interactivity. Powers dynamic behavior directly from HTML.
Tailwind CSS – Utility-first CSS framework for elegant and responsive UI.
🗃️ Database
MongoDB – Document-based database used for storing clients, orders, revenue, and attendance data.
🌐 Dev Tools
Uvicorn – ASGI web server for running FastAPI.
GitHub – For version control and collaboration.
Python venv – Virtual environment for isolating project dependencies.
