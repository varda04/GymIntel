from collections import defaultdict
import datetime
from pymongo import MongoClient

class MongoDBTool:
    def __init__(self, uri="mongodb://localhost:27017", db_name="fitnessDB"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    # 1. CLIENT DATA
    def get_client_by_name(self, name):
        name = name.strip()
        print(f"[DEBUG] Searching client with name: '{name}'")
        matches = list(self.db.clients.find({
            "name": {"$regex": f"^{name}$", "$options": "i"}
        }))
        
        if not matches:
            return None
        elif len(matches) > 1:
            print(f"⚠️ Multiple matches for name '{name}', returning the first one.")
        
        return matches[0]  # or use additional logic to pick preferred one


    def get_client_by_email(self, email):
        return self.db.clients.find_one({"email": email})

    def get_client_by_phone(self, phone):
        res= self.db.clients.find_one({"phone": phone})
        print("[DEBUG] Res from Mongo:", res)
        return res

    def get_client_services(self, client_id):
        return list(self.db.orders.find({"client_id": client_id}))

    # 2. ORDER MANAGEMENT
    def get_order_by_id(self, order_id):
        return self.db.orders.find_one({"_id": order_id})

    def get_orders_by_client(self, client_id):
        return list(self.db.orders.find({"client_id": client_id}))

    def get_orders_by_status(self, status):
        return list(self.db.orders.find({"status": status}))

    # 3. PAYMENT INFO
    def get_payment_by_order_id(self, order_id):
        return self.db.payments.find_one({"order_id": order_id})

    def calculate_due_for_order(self, order_id):
        order = self.get_order_by_id(order_id)
        payment = self.get_payment_by_order_id(order_id)
        if not order:
            return None
        paid = payment["amount_paid"] if payment else 0
        return order["amount"] - paid

    # 4. COURSE/CLASS DISCOVERY
    def list_upcoming_classes(self):
        return list(self.db.classes.find({"status": "scheduled"}))

    def filter_classes_by_instructor(self, instructor):
        print(f"[DEBUG] from MongoDBTool: {instructor}")
        return list(self.db.classes.find({"instructor": instructor}))

    def filter_classes_by_status(self, status):
        return list(self.db.classes.find({"status": status}))

    # 5. DASHBOARD ANALYTICS
    def get_total_revenue(self, month: str = None, year: str = None):
        MONTHS = {
            "January": 1, "February": 2, "March": 3,
            "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9,
            "October": 10, "November": 11, "December": 12
        }

        match_conditions = []

        if month and month!= "Unknown":
            month_num = MONTHS.get(month.capitalize())
            if not month_num:
                return f"❌ Invalid month: {month}"
            match_conditions.append({
                "$eq": [
                    { "$month": { "$dateFromString": { "dateString": "$payment_date" } } },
                    month_num
                ]
            })

        if year and year!="Unknown":
            match_conditions.append({
                "$eq": [
                    { "$year": { "$dateFromString": { "dateString": "$payment_date" } } },
                    int(year)
                ]
            })

        pipeline = []
        if match_conditions:
            pipeline.append({
                "$match": {
                    "$expr": {
                        "$and": match_conditions
                    }
                }
            })

        pipeline.append({
            "$group": {
                "_id": None,
                "total": { "$sum": "$amount_paid" }
            }
        })

        result = list(self.db.payments.aggregate(pipeline))
        return result[0]["total"] if result else 0

    def get_outstanding_payments(self):
        pending_orders = self.db.orders.find({"status": "pending"})
        return sum(o["amount"] for o in pending_orders)

    def get_active_inactive_clients(self):
        active = self.db.clients.count_documents({"status": "active"})
        inactive = self.db.clients.count_documents({"status": "inactive"})
        return {"active": active, "inactive": inactive}
    
    from datetime import datetime, timedelta

    def get_clients_with_upcoming_birthdays(self):
        today = datetime.datetime.today()
        upcoming_clients = []

        for client in self.db.clients.find():
            try:
                bday_str = client.get("birthdate")
                bday_obj = datetime.datetime.strptime(bday_str, "%Y-%m-%d")

                this_year_bday = bday_obj.replace(year=today.year)

                # If it already passed this year, check next year
                if this_year_bday < today:
                    this_year_bday = this_year_bday.replace(year=today.year + 1)

                # Check if within next 30 days
                if 0 <= (this_year_bday - today).days <= 30:
                    upcoming_clients.append(client)

            except Exception as e:
                print(f"[ERROR] Parsing birthday for {client.get('name')}: {e}")
                continue

        return upcoming_clients

    def get_clients_joined_this_month(self):
        # Get start and end of current month
        today = datetime.datetime.today()
        start_of_month = datetime.datetime(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = datetime.datetime(today.year + 1, 1, 1)
        else:
            end_of_month = datetime.datetime(today.year, today.month + 1, 1)
        clients_collection = self.db["clients"]

        # Query clients whose 'joined_on' date is within this month
        new_clients = list(clients_collection.find({
            "joined_on": {
                "$gte": start_of_month,
                "$lt": end_of_month
            }
        }))

        return new_clients


    def get_service_analytics(self):
        orders = list(self.db.orders.find({"status": "paid"}))

        course_counts = defaultdict(int)
        monthly_trend = defaultdict(int)

        for o in orders:
            course = o.get("service_name", "Unknown")
            course_counts[course] += 1

            try:
                date = datetime.datetime.strptime(o["created_on"], "%Y-%m-%d")
                key = f"{date.year}-{str(date.month).zfill(2)}"
                monthly_trend[key] += 1
            except Exception as e:
                print("[ERROR] Parsing date in order:", o.get("_id"), e)
                continue

        top_courses = sorted(course_counts.items(), key=lambda x: -x[1])[:5]
        trend_sorted = sorted(monthly_trend.items())

        return {
            "top_services": [f"{course}: {count} enrollments" for course, count in top_courses] or ["No data available."],
            "trends": [f"{month}: {count} enrollments" for month, count in trend_sorted] or ["No data available."],
            "completion_rates": ["No data available."]  # You can populate this later
        }

    def get_course_completion_rates(self):
        return list(self.db.orders.aggregate([
            {"$group": {"_id": "$service_name", "total": {"$sum": 1},
                        "paid": {"$sum": {"$cond": [{"$eq": ["$status", "paid"]}, 1, 0]}}}},
            {"$project": {"completion_rate": {"$divide": ["$paid", "$total"]}}}
        ]))

    from collections import defaultdict

    def get_attendance_stats(self, class_id=None):
        records = list(self.db.attendance.find())

        if class_id is not None and True:
            class_data = defaultdict(lambda: {"attended": 0, "total": 0})

            for rec in records:
                if(rec["class_id"]!= class_id):
                    continue
                cid = rec["class_id"]
                class_data[cid]["total"] += 1
                if rec.get("attended") is True:
                    class_data[cid]["attended"] += 1

            # reports=[]
            report = {}

            for cid, stats in class_data.items():
                pct = (stats["attended"] / stats["total"]) * 100 if stats["total"] else 0
                dropoff = 100 - pct
                report = {
                    "class_id": cid,
                    "attendance_percent": f"{round(pct, 2)}%",
                    "drop_off_rate": f"{round(dropoff, 2)}%",
                    "total_sessions": stats["total"]
                }
                # reports.append(report)

            return report
        
        else:
            class_data = defaultdict(lambda: {"attended": 0, "total": 0})

            for rec in records:
                cid = rec["class_id"]
                class_data[cid]["total"] += 1
                if rec.get("attended") is True:
                    class_data[cid]["attended"] += 1

            reports=[]
            report = {}

            for cid, stats in class_data.items():
                pct = (stats["attended"] / stats["total"]) * 100 if stats["total"] else 0
                dropoff = 100 - pct
                report = {
                    "class_id": cid,
                    "attendance_percent": f"{round(pct, 2)}%",
                    "drop_off_rate": f"{round(dropoff, 2)}%",
                    "total_sessions": stats["total"]
                }
                reports.append(report)

            return reports



    def get_class_dropout_rate(self, class_id):
        records = list(self.db.attendance.find({"class_id": class_id}))
        if not records:
            return None
        dropped = sum(1 for r in records if not r["attended"])
        return dropped / len(records)