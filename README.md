# Discord AI Reply Bot

A Discord bot that automatically replies to every new message in a channel
using AI (Gemini), in casual native-like English with abbreviations
(`lol`, `ngl`, `tbh`, `fr`, `idk`, `gonna`, `wanna`, etc.).

Created by **[Xsrazy](https://github.com/xsrazy)**.

## How it works

- Monitors the channel every 5 seconds (`poll_interval`)
- When someone new types, it replies with a context-aware Gemini-generated message
- Replies use Discord's reply feature (attached to the user's message)
- Its own messages and other bots' messages are skipped

## Anti-spam

- **Global cooldown** 60 seconds: max 1 reply per minute
- **Per-user cooldown** 5 minutes: the same user won't get replied to repeatedly

## Setup

1. Install dependencies:

```bash
pip install requests colorama
```

2. Copy `config.example.json` to `config.json` and fill it in:

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY_FROM_AI_STUDIO",
  "gemini_model": "gemini-3-flash-preview",
  "gemini_model_fallback": "gemini-3.1-flash-lite",
  "discord_token": "YOUR_DISCORD_USER_TOKEN",
  "channel_id": "TARGET_CHANNEL_ID",
  "poll_interval": 5,
  "reply_cooldown_global": 60,
  "reply_cooldown_user": 300
}
```

3. Run it:

```bash
python bot.py
```

Or use `start-bot.sh` (idempotent, won't start duplicates):

```bash
bash start-bot.sh
```

## Notes

- Uses a Discord **user token** (self-bot). Discord strictly forbids automation
  with user tokens — the account can get banned if detected. Use a spare
  account / at your own risk.
- Get a Gemini API key at [Google AI Studio](https://aistudio.google.com/).
  The free tier is enough for normal use (~1500 requests/day max).
- The reply style can be changed via `system_prompt` in `config.json`.
