from __future__ import annotations
import json
import sys

POSITIVE_EVENTS = {"reply_positive", "stripe_completed"}

def normalize(event_type: str, payload: dict) -> dict:
    return {
        "eventType": event_type,
        "positiveSignal": event_type in POSITIVE_EVENTS,
        "payload": payload,
    }

if __name__ == "__main__":
    event_type = sys.argv[1] if len(sys.argv) > 1 else "reply_positive"
    payload = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(normalize(event_type, payload), ensure_ascii=False))
