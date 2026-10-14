import requests
import time
import os
from colorama import Fore

# ============ CONFIGURATION (from config.json, chmod 600) ============
import json as _json

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
try:
    with open(_CONFIG_PATH) as _cf:
        _cfg = _json.load(_cf)
except FileNotFoundError:
    print("config.json not found. Fill in: gemini_api_key, discord_token, channel_id.")
    raise SystemExit(1)

GEMINI_API_KEY = _cfg.get("gemini_api_key", "")
GEMINI_MODEL = _cfg.get("gemini_model", "gemini-3-flash-preview")
GEMINI_MODEL_FALLBACK = _cfg.get("gemini_model_fallback", "gemini-3.1-flash-lite")
DISCORD_TOKEN = _cfg.get("discord_token", "")
CHANNEL_ID = _cfg.get("channel_id", "")
POLL_INTERVAL = int(_cfg.get("poll_interval", 5))
# Throttles to avoid spamming busy channels:
REPLY_COOLDOWN_GLOBAL = int(_cfg.get("reply_cooldown_global", 60))  # seconds between replies
REPLY_COOLDOWN_USER = int(_cfg.get("reply_cooldown_user", 300))    # seconds per same user
# AI reply style instructions, edit to your liking:
SYSTEM_PROMPT = _cfg.get("system_prompt", (
    "You're a chill friend hanging out in an international Discord server. "
    "Reply to the message below in casual, natural English like a native speaker "
    "texting friends: use abbreviations and slang (lol, ngl, tbh, fr, imo, idk, "
    "gonna, wanna, etc.), keep it short (1-3 sentences), never stiff or "
    "translation-like. Just the reply, no quotes."
))
# ================================================================

print("=============================================================\n")
print("Script       :        Discord AI Reply Bot (Gemini)\n")
print("Author       :        Xsrazy (https://github.com/xsrazy)\n")
print("=============================================================\n")

time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear')

headers = {"Authorization": DISCORD_TOKEN}
channel_id = CHANNEL_ID.strip()
base = f"https://discord.com/api/v9/channels/{channel_id}"


def api_get(path, params=None):
    r = requests.get(f"{base}{path}", headers=headers, params=params, timeout=20)
    return r


def gemini_reply(user_text, username):
    """Ask Gemini for 1 reply. Retry 2x per model, fall back to backup model."""
    prompt = f"{SYSTEM_PROMPT}\n\n{username} typed: {user_text}\nReply:"
    for model in (GEMINI_MODEL, GEMINI_MODEL_FALLBACK):
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={GEMINI_API_KEY}"
        )
        for attempt in range(2):
            try:
                r = requests.post(
                    url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30
                )
                if r.status_code in (429, 500, 502, 503):
                    print(Fore.RED + f"Gemini {model} {r.status_code}, retry...")
                    time.sleep(3)
                    continue
                r.raise_for_status()
                return (
                    r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    .strip().strip('"').strip("'").strip()
                )
            except requests.HTTPError as e:
                msg = str(e).replace(GEMINI_API_KEY, "[KEY]")
                print(Fore.RED + f"Gemini {model} failed: {msg}")
                break  # permanent error, try backup model right away
            except Exception as e:
                msg = str(e).replace(GEMINI_API_KEY, "[KEY]")
                print(Fore.RED + f"Gemini {model} error: {msg}, retry...")
                time.sleep(3)
    return None


# identify self so we never reply to our own messages
me = requests.get("https://discord.com/api/v9/users/@me",
                  headers=headers, timeout=20).json()
my_id = me.get("id")
print(Fore.GREEN + f"Logged in as: {me.get('username')} ({my_id})")
print(Fore.GREEN + f"Monitoring channel {channel_id}, replying to every new message...\n")

# start from the latest message so we don't reply to old history
init = api_get("/messages", params={"limit": 1})
last_id = init.json()[0]["id"] if init.status_code == 200 and init.json() else None

import time as _time
last_reply_global = 0.0
last_reply_user = {}

while True:
    try:
        params = {"limit": 25}
        if last_id:
            params["after"] = last_id
        r = api_get("/messages", params=params)

        if r.status_code == 401:
            print(Fore.RED + "Discord token invalid / expired. Stopping.")
            break
        if r.status_code == 429:
            retry = int(r.json().get("retry_after", 5))
            print(Fore.RED + f"Rate limited, waiting {retry}s")
            time.sleep(retry)
            continue
        if r.status_code != 200:
            print(Fore.RED + f"Failed to fetch messages: {r.status_code}")
            time.sleep(POLL_INTERVAL)
            continue

        messages = r.json()
        now = _time.time()
        # process oldest first so reply order is correct
        for m in reversed(messages):
            last_id = m["id"]
            author = m.get("author", {})
            if author.get("id") == my_id or author.get("bot"):
                continue
            content = (m.get("content") or "").strip()
            if not content or len(content) < 2:
                continue
            username = author.get("username", "user")
            print(Fore.WHITE + f"{username}: {content[:80]}")

            # throttle: global + per-user cooldown
            if now - last_reply_global < REPLY_COOLDOWN_GLOBAL:
                print(Fore.RED + "  -> skipped (global cooldown)")
                continue
            if now - last_reply_user.get(author.get("id"), 0) < REPLY_COOLDOWN_USER:
                print(Fore.RED + f"  -> skipped (cooldown for user {username})")
                continue

            reply = gemini_reply(content, username)
            if not reply:
                continue

            send = requests.post(
                f"{base}/messages",
                json={
                    "content": reply,
                    "message_reference": {"message_id": m["id"]},
                },
                headers=headers,
                timeout=20,
            )
            if send.status_code in (200, 201):
                print(Fore.YELLOW + f"  -> replied: {reply[:80]}")
                last_reply_global = _time.time()
                last_reply_user[author.get("id")] = _time.time()
                now = _time.time()
            elif send.status_code == 429:
                retry = int(send.json().get("retry_after", 5))
                print(Fore.RED + f"  -> rate limited, waiting {retry}s")
                time.sleep(retry)
            else:
                print(Fore.RED + f"  -> failed to send: {send.status_code}")

        time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(Fore.GREEN + "\nStop.")
        break
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        time.sleep(POLL_INTERVAL)
