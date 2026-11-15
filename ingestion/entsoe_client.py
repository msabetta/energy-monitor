# ingestion/entsoe_client.py
import os
import requests
from datetime import datetime, timedelta, timezone
from utils import set_env_variable_from_file, get_env_variable

BASE_URL = "https://web-api.tp.entsoe.eu/api"
#TOKEN = os.environ["ENTSOE_TOKEN"]
set_env_variable_from_file("ENTSOE_TOKEN", "config/token.txt", 1) # Legge il token dalla prima riga del file config/token.txt


# Codici EIC delle zone italiane: verificarli nella documentazione ENTSO-E prima dell'uso
ZONE_IT_NORD = "10Y1001A1001A73I"

def fetch_actual_load(zone: str, start: datetime, end: datetime) -> str:
    """Carico reale (documentType A65, processType A16), restituisce XML grezzo."""
    params = {
        "securityToken": get_env_variable("ENTSOE_TOKEN"),
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": zone,
        "periodStart": start.strftime("%Y%m%d%H%M"),
        "periodEnd": end.strftime("%Y%m%d%H%M"),
    }
    resp = requests.get(BASE_URL, params=params, timeout=60)
    resp.raise_for_status()
    return resp.text  # il dato grezzo va salvato così com'è nella raw zone

if __name__ == "__main__":
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=1)
    xml = fetch_actual_load(ZONE_IT_NORD, start, end)
    with open("raw_load_nord.xml", "w") as f:
        f.write(xml)
    print("Salvati", len(xml), "byte")