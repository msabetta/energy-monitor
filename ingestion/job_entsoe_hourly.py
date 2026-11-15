# ingestion/job_entsoe_hourly.py
import sys
from datetime import datetime, timedelta, timezone

from ingestion.entsoe_client import fetch_actual_load
from ingestion.parse_entsoe import parse_actual_load
from ingestion.write_trusted import write_trusted_load, get_spark

ZONES = {"IT_NORD": "10Y1001A1001A73I"}  # estendere con le altre zone dopo la verifica dei codici EIC

def run(window_end: datetime, zone_name: str, zone_code: str) -> None:
    window_start = window_end - timedelta(hours=1)
    fetched_at = datetime.now(timezone.utc)

    # 1. Download (payload grezzo)
    xml = fetch_actual_load(zone_code, window_start, window_end)

    # 2. Raw zone: payload invariato, un record per download
    spark = get_spark()
    spark.createDataFrame(
        [(fetched_at, "A65", zone_name, xml)],
        "fetched_at timestamp, document_type string, zone string, payload string",
    ).writeTo("energy.raw_entsoe").append()

    # 3. Parsing e trusted zone
    rows = parse_actual_load(xml, zone=zone_name)
    if not rows:
        print(f"[{zone_name}] nessun dato nella finestra {window_start}–{window_end}")
        return
    raw_ref = f"raw_entsoe@{fetched_at.isoformat()}"
    write_trusted_load(rows, raw_file=raw_ref)
    print(f"[{zone_name}] {len(rows)} righe caricate")

if __name__ == "__main__":
    # Ultima ora completa in UTC, oppure un'ora passata come argomento ISO
    if len(sys.argv) > 1:
        end = datetime.fromisoformat(sys.argv[1]).astimezone(timezone.utc)
    else:
        end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    for name, code in ZONES.items():
        run(end, name, code)