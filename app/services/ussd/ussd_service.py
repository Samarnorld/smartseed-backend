# app/services/ussd/ussd_service.py
import os
from dotenv import load_dotenv
import africastalking
import pandas as pd
from app.services.nandi.config import BASE_PATH

load_dotenv()

# Africa's Talking Setup
username = os.getenv("AT_USERNAME")
api_key = os.getenv("AT_API_KEY")

if username and api_key:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
else:
    sms = None

# CSV PATH 
CSV_PATH = os.path.join(
    BASE_PATH,
    "WardAggregatedData",
    "Nandi_Ward_Recommendations.csv"
)
try:
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip() for c in df.columns]
    df["Ward"] = df["Ward"].str.strip()
    df.set_index("Ward", inplace=True)
    print("USSD CSV loaded successfully.")
except Exception as e:
    print(f"Error loading USSD CSV: {e}")
    df = None


# Ward Mapping
WARD_MAPPING = {
    "1": {"1": "OL'LESSOS", "2": "KAPCHORUA", "3": "CHEPKUNYUK", "4": "NANDI HILLS"},
    "2": {"1": "KAPSABET", "2": "KAPKANGANI", "3": "CHEPKUMIA", "4": "KILIBWONI"},
    "3": {"1": "CHEMUNDU/KAPNG'ETUNY", "2": "KOSIRAI", "3": "LELMOKWO/NGECHEK", "4": "KAPTEL/KAMOIYWO", "5": "KIPTUYA"},
    "4": {"1": "KABWARENG", "2": "TERIK", "3": "KEMELOI-MARABA", "4": "KOBUJOI", "5": "KAPTUMO-KABOI", "6": "KOYO-NDURIO"},
    "5": {"1": "TINDIRET", "2": "SONGHOR/SOBA", "3": "CHEMELIL/CHEMASE", "4": "KAPSIMOTWO"},
    "6": {"1": "KABIYET", "2": "NDALAT", "3": "KABISAGA", "4": "CHEPTERWAI", "5": "KURGUNG/SURUNGAI", "6": "KIPKAREN", "7": "SANGALO/KEBULONIK"}
}
def format_name(name: str) -> str:
    """
    Converts ALL CAPS ward names into Proper Case
    while preserving special characters like / and '
    """
    if not isinstance(name, str):
        return name

    parts = name.split("/")
    formatted_parts = []

    for part in parts:
        sub_parts = part.split("-")
        formatted_sub = [
            word.capitalize() for word in sub_parts
        ]
        formatted_parts.append("-".join(formatted_sub))

    return "/".join(formatted_parts)

# USSD TEXT PROCESSOR
def process_text(raw_text: str) -> str:
    if not raw_text:
        return ""
    slots = raw_text.split("*")
    processed = []
    for slot in slots:
        if slot == "0":
            if processed:
                processed.pop()
        else:
            processed.append(slot)

    return "*".join(processed)

# MAIN USSD HANDLER
def handle_ussd(session_id: str, phone_number: str, raw_text: str) -> str:

    text = process_text(raw_text)
    data = text.split("*") if text else []
    level = len(data)

    # LEVEL 0 — Sub County Menu
    if level == 0:
        return (
            "CON SmartSeed Nandi\n"
            "Select Sub-County:\n"
            "1. Nandi Hills\n"
            "2. Emgwen\n"
            "3. Chesumei\n"
            "4. Aldai\n"
            "5. Tinderet\n"
            "6. Mosop"
        )

    # LEVEL 1 — Ward Menu
    elif level == 1:
        sub_id = data[0]
        wards = WARD_MAPPING.get(sub_id)

        if not wards:
            return "END Area coming soon."

        response = "CON Select Ward:\n"
        for key, ward in wards.items():
            response += f"{key}. {format_name(ward)}\n"
        response += "0. Back"

        return response

    # LEVEL 2 — CSV Recommendation
    elif level == 2:
        sub_id = data[0]
        ward_id = data[1]
        ward_name = WARD_MAPPING.get(sub_id, {}).get(ward_id)
        if not ward_name:
            return "END Ward not found."
        if df is None or ward_name not in df.index:
            return "END Ward data unavailable."

        # Pull CSV Data
        ward_row = df.loc[ward_name]
        seeds_raw = ward_row.get("LR_Seeds", "")

        if not isinstance(seeds_raw, str) or not seeds_raw.strip():
            return "END No seed data available."

        # Short USSD version
        first_seed = seeds_raw.split("|")[0].strip()

        response_text = (
            f"END SmartSeed {format_name(ward_name)}:\n"
            f"{first_seed}\n"
            "Full advisory sent via SMS."
        )

        # Send Full SMS
        if sms:
            try:
                sms_message = (
                    f"SmartSeed {format_name(ward_name)} - Long Rains\n"
                    f"{seeds_raw}"
                )
                sms.send(sms_message, [phone_number])
            except Exception as e:
                print(f"SMS sending failed: {e}")
        return response_text
    return "END Invalid request."