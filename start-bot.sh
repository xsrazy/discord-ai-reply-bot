#!/bin/bash
# Idempotent starter untuk Discord AI Reply Bot.
# Tidak akan start duplikat kalau bot sudah jalan (cek via bot.pid).
# Keluar diam-diam (exit 0) kalau config.json belum ada.
DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$DIR/bot.pid"
LOG="$DIR/bot.log"

if [ ! -f "$DIR/config.json" ]; then
  exit 0
fi

if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE")
  if kill -0 "$PID" 2>/dev/null && [ "$(readlink /proc/$PID/cwd 2>/dev/null)" = "$DIR" ]; then
    exit 0
  fi
  rm -f "$PIDFILE"
fi

cd "$DIR"
nohup python3 -u bot.py >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] bot started (pid $(cat $PIDFILE))" >> "$LOG"
