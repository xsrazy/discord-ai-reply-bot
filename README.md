# Discord AI Reply Bot

Bot Discord yang otomatis membalas tiap pesan baru di channel pake AI (Gemini),
dengan gaya bahasa Inggris casual ala native speaker (singkatan kayak `lol`,
`ngl`, `tbh`, `fr`, `idk`, `gonna`, `wanna`).

## Cara kerja

- Mantau channel tiap 5 detik (`poll_interval`)
- Tiap ada pesan baru dari user lain, langsung dibalesin pake Gemini (nyambung ke isi pesannya)
- Balasan pake reply (nempel ke pesan orangnya)
- Pesan sendiri & pesan bot lain diskip

## Anti-spam

- **Cooldown global** 60 detik: maksimal 1 balasan per menit
- **Cooldown per user** 5 menit: user yang sama ga dibalesin terus-terusan

## Setup

1. Install dependency:

```bash
pip install requests colorama
```

2. Copy `config.example.json` jadi `config.json`, isi:

```json
{
  "gemini_api_key": "API_KEY_DARI_GOOGLE_AI_STUDIO",
  "gemini_model": "gemini-3-flash-preview",
  "gemini_model_fallback": "gemini-3.1-flash-lite",
  "discord_token": "USER_TOKEN_DISCORD_LU",
  "channel_id": "ID_CHANNEL_TARGET",
  "poll_interval": 5,
  "reply_cooldown_global": 60,
  "reply_cooldown_user": 300
}
```

3. Jalanin:

```bash
python bot.py
```

Atau pake `start-bot.sh` (idempotent, ga bakal start duplikat):

```bash
bash start-bot.sh
```

## Catatan

- Pake **user token** Discord (self-bot). Discord ngelarang otomasi pake user token,
  akun bisa kena ban kalo kedetect. Pake akun cadangan / tanggung risiko sendiri.
- API key Gemini dibikin di [Google AI Studio](https://aistudio.google.com/).
  Free tier cukup buat pemakaian wajar (maks ~1500 request/hari).
- Gaya bahasa bisa diubah lewat `system_prompt` di `config.json`.
