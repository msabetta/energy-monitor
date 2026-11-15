# tests/test_parse_entsoe.py
from ingestion.parse_entsoe import parse_actual_load

def test_parse_returns_rows_with_utc_timestamps():
    with open("raw_load_nord.xml") as f:
        rows = parse_actual_load(f.read(), zone="IT_NORD")
    assert rows, "nessuna riga estratta"
    assert all(r["timestamp_utc"].tzinfo is not None for r in rows)
    assert all(r["value"] >= 0 for r in rows)