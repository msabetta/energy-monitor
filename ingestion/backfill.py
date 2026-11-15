# ingestion/backfill.py
import sys
from datetime import datetime, timedelta, timezone
from ingestion.job_entsoe_hourly import run, ZONES

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    # Ritardo di sicurezza di 3 ore: i dati di carico non sono ancora completi
    last = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) - timedelta(hours=3)
    hours = days * 24
    for i in range(hours):
        end = last - timedelta(hours=hours - 1 - i)
        for name, code in ZONES.items():
            try:
                run(end, name, code)
            except Exception as exc:
                print(f"[{name}] errore {end.isoformat()}: {exc}")