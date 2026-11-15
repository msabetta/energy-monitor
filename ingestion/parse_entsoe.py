# ingestion/parse_entsoe.py
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {"ns": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0"}

def parse_actual_load(xml_text: str, zone: str) -> list[dict]:
    """Converte il documento A65 in righe (timestamp_utc, zone, source, value, unit)."""
    root = ET.fromstring(xml_text)
    rows = []
    for ts in root.findall("ns:TimeSeries", NS):
        for period in ts.findall("ns:Period", NS):
            start = datetime.fromisoformat(
                period.find("ns:timeInterval/ns:start", NS).text.replace("Z", "+00:00")
            )
            resolution = period.find("ns:resolution", NS).text  # es. PT60M o PT15M
            step = timedelta(minutes=int(resolution[2:-1]))
            for point in period.findall("ns:Point", NS):
                pos = int(point.find("ns:position", NS).text)
                value = float(point.find("ns:quantity", NS).text)
                rows.append({
                    "timestamp_utc": start + step * (pos - 1),
                    "zone": zone,
                    "source": "entsoe",
                    "value": value,
                    "unit": "MW",
                })
    return rows