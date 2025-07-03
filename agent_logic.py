from transformers import pipeline
import re
import langdetect

# Zero-shot classifier for intent detection
intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Named Entity Recognizer
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

INTENT_LABELS_SUPPORT = [
    "create_order",
    "create_enquiry",
    "list_upcoming_classes",
    "get_client_info",
    "get_client_services",
    "filter_classes_by_instructor",
    "filter_classes_by_status"
]

INTENT_LABELS_DASHBOARD=[
    "get_revenue_metrics",
    "get_outstanding_payment",
    "get_active_inactive_client_insights",
    "get_client_birthday_reminder",
    "get_new_clients_this_month",
    "get_service_analytics",
    "get_attendance_report"
]

SERVICE_NAMES = [
    "Yoga Beginner", "Strength Training", "Zumba Advanced",
    "HIIT Express", "Pilates Intermediate", "Meditation Basics"
]

STATUS_NAMES = [
    "Upcoming", "Scheduled", "Completed", "Ongoing", "Canceled"
]

MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}

def extract_class_id(query):
    # Try to find something like 'class_22'
    match = re.search(r'class[_\s]?(\d+)', query, re.IGNORECASE)
    if match:
        return f"class_{match.group(1)}"  # return full class_id
    return None

def extract_month(query):
    for word in query.lower().split():
        if word in MONTHS:
            return word.capitalize()
    return None

def extract_year(query):
    match = re.search(r"\b(20\d{2})\b", query)
    if match:
        return match.group(1)
    return None

def extract_status(query):
    for status in STATUS_NAMES:
        if status.lower() in query.lower():
            return status
        
    return None

def extract_service(query):
    for service in SERVICE_NAMES:
        if service.lower() in query.lower():
            return service
    return None

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r"\b\d{10}\b", text)
    return match.group(0) if match else None

def merge_entities(entities_raw):
    merged = {}
    current_type = None
    buffer = []
    last_end = -1

    for ent in entities_raw:
        tag = ent["entity_group"]
        word = ent["word"]
        start = ent["start"]

        is_subword = word.startswith("##")
        word = word.replace("##", "")

        if tag != current_type or start > last_end + 1:
            if current_type and buffer:
                merged[current_type] = "".join(buffer)
            buffer = [word]
            current_type = tag
        else:
            if is_subword:
                buffer[-1] += word  # Append without space
            else:
                buffer.append(" " + word)  # Add space if it's a new word

        last_end = ent["end"]

    if current_type and buffer:
        merged[current_type] = "".join(buffer)

    return merged

from deep_translator import GoogleTranslator
import langdetect

def detect_language(text):
    return langdetect.detect(text)

def translate_text(text, target_language="en"):
    return GoogleTranslator(source="auto", target=target_language).translate(text)

def translation(text):
    original_language = detect_language(text)
    if original_language == "en":
        return text
    translated_text = translate_text(text, "en")
    print(f"[DEBUG] Translated: '{translated_text}' from '{original_language}'")
    return translated_text

def parse_query_support(query: str):
    query= translation(query)
    intent_result = intent_classifier(query, INTENT_LABELS_SUPPORT)
    intent = intent_result["labels"][0]

    entities_raw = ner_pipeline(query)
    named_entities = merge_entities(entities_raw)

    # Add regex-based email/phone extraction
    email = extract_email(query)
    if email:
        named_entities["EMAIL"] = email

    phone = extract_phone(query)
    if phone:
        named_entities["PHONE"] = phone

    service = extract_service(query)
    if service:
        named_entities["MISC"] = service

    status= extract_status(query)
    if status:
        named_entities["STATUS"] = status

    return {
        "intent": intent,
        "entities": named_entities,
        "raw": {
            "intent_scores": intent_result,
            "entities_raw": entities_raw
        }
    }

def parse_query_dashboard(query: str):
    query= translation(query)
    intent_result = intent_classifier(query, INTENT_LABELS_DASHBOARD)
    intent = intent_result["labels"][0]

    entities_raw = ner_pipeline(query)
    named_entities = merge_entities(entities_raw)

    # # Add regex-based email/phone extraction
    # email = extract_email(query)
    # if email:
    #     named_entities["EMAIL"] = email

    # phone = extract_phone(query)
    # if phone:
    #     named_entities["PHONE"] = phone

    service = extract_service(query)
    if service:
        named_entities["MISC"] = service

    # status= extract_status(query)
    # if status:
    #     named_entities["STATUS"] = status

    month = extract_month(query)
    if month:
        named_entities["MONTH"] = month

    year = extract_year(query)
    if year:
        named_entities["YEAR"] = year

    class_id= extract_class_id(query)
    if class_id:
        named_entities["CLASS_ID"]= class_id

    return {
        "intent": intent,
        "entities": named_entities,
        "raw": {
            "intent_scores": intent_result,
            "entities_raw": entities_raw
        }
    }