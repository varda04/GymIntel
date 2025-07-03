from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import random
import uuid

client = MongoClient("mongodb://localhost:27017")
db = client["fitnessDB"]

# Drop old collections
for col in ["clients", "courses", "classes", "orders", "payments", "attendance", "enquiries"]:
    db[col].drop()

# 1. Clients
first_names = ["Priya", "Amit", "Ravi", "Sneha", "Karan", "Megha", "Rahul", "Nisha", "Vikram", "Tanvi"]
last_names = ["Sharma", "Verma", "Kapoor", "Mehta", "Patel"]
clients = []

for i in range(25):
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    client_id = f"client_{str(i+1).zfill(3)}"
    clients.append({
        "_id": client_id,
        "name": f"{fname} {lname}",
        "email": f"{fname.lower()}{i}@example.com",
        "phone": f"98765{random.randint(10000, 99999)}",
        "birthdate": f"199{random.randint(0,9)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "status": random.choice(["active", "inactive"]),
        "joined_on": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    })

db.clients.insert_many(clients)

# 2. Courses
course_names = ["Yoga Beginner", "Pilates Intermediate", "Zumba Advanced", "HIIT Express", "Strength Training", "Meditation Basics"]
instructors = ["Anjali Mehta", "Rahul Kapoor", "Sonal Jain", "Aakash Bhatt", "Ishita Roy", "Vikram Singh"]

courses = []
for i in range(6):
    courses.append({
        "_id": f"course_{i+1}",
        "name": course_names[i],
        "instructor": instructors[i],
        "status": random.choice(["ongoing", "scheduled"]),
        "duration_weeks": random.choice([4, 6, 8])
    })

db.courses.insert_many(courses)

# 3. Classes
classes = []
today = datetime.today()
for i in range(30):
    course = random.choice(courses)
    class_date = today + timedelta(days=random.randint(1, 21))
    classes.append({
        "_id": f"class_{i+1}",
        "course_id": course["_id"],
        "date": class_date.strftime("%Y-%m-%d"),
        "instructor": course["instructor"],
        "status": "scheduled"
    })

db.classes.insert_many(classes)

# 4. Orders
orders = []
for i in range(40):
    client = random.choice(clients)
    course = random.choice(courses)
    status = random.choices(["paid", "pending"], weights=[0.7, 0.3])[0]
    orders.append({
        "_id": f"order_{i+1}",
        "client_id": client["_id"],
        "service_name": course["name"],
        "amount": random.randint(1000, 2500),
        "status": status,
        "created_on": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    })

db.orders.insert_many(orders)

# 5. Payments (only for some orders)
paid_orders = [o for o in orders if o["status"] == "paid"]
payments = []
for i, order in enumerate(random.sample(paid_orders, k=28)):  # some paid orders left out
    payments.append({
        "_id": f"payment_{i+1}",
        "order_id": order["_id"],
        "amount_paid": order["amount"],
        "payment_date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "method": random.choice(["UPI", "Credit Card", "Cash", "NetBanking"])
    })

db.payments.insert_many(payments)

# 6. Attendance
attendance = []
for i in range(60):
    class_obj = random.choice(classes)
    client = random.choice(clients)
    attendance.append({
        "_id": f"att_{i+1}",
        "class_id": class_obj["_id"],
        "client_id": client["_id"],
        "attended": random.choice([True, False])
    })

db.attendance.insert_many(attendance)

#Additional collection: enquiry
enquiries = [
    {
        "name": "Divya Menon",
        "email": "divya@example.com",
        "phone": "9876543210",
        "notes": "Wants to join Pilates",
        "created_on": datetime.now(timezone.utc).isoformat()
    },
    {
        "name": "Aarav Patel",
        "email": "aarav@example.com",
        "phone": "9999911111",
        "notes": "Interested in nutrition plan",
        "created_on": datetime.now(timezone.utc).isoformat()
    }
]

db.enquiries.insert_many(enquiries)


print("Mock data inserted: 25 clients, 6 courses, 30 classes, 40 orders, 28 payments, 60 attendance records.")