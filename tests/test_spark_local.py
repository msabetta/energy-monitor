# tests/test_spark_local.py
import os
import shutil
import tempfile
from datetime import datetime, timezone

import pytest

# Forza l'ambiente locale prima di importare il modulo
os.environ["ENERGY_ENV"] = "local"
WAREHOUSE = tempfile.mkdtemp(prefix="energy-test-")
os.environ["ENERGY_WAREHOUSE"] = f"file://{WAREHOUSE}"

from ingestion.spark_session import get_spark  # noqa: E402


@pytest.fixture(scope="module")
def spark():
    session = get_spark("energy-test")
    session.sql("CREATE NAMESPACE IF NOT EXISTS energy")
    session.sql("""
        CREATE TABLE IF NOT EXISTS energy.trusted_load (
            timestamp_utc  TIMESTAMP NOT NULL,
            zone           STRING    NOT NULL,
            source         STRING    NOT NULL,
            value          DOUBLE,
            unit           STRING    NOT NULL,
            ingested_at    TIMESTAMP NOT NULL,
            raw_file       STRING    NOT NULL
        )
        USING iceberg
        PARTITIONED BY (zone, days(timestamp_utc))
    """)
    yield session
    session.stop()
    shutil.rmtree(WAREHOUSE, ignore_errors=True)


def _merge(spark, rows):
    df = spark.createDataFrame(rows)
    df.createOrReplaceTempView("incoming_load")
    spark.sql("""
        MERGE INTO energy.trusted_load AS t
        USING incoming_load AS s
        ON t.zone = s.zone AND t.source = s.source AND t.timestamp_utc = s.timestamp_utc
        WHEN MATCHED AND (t.value <> s.value OR t.value IS NULL) THEN UPDATE SET
            t.value = s.value, t.ingested_at = s.ingested_at, t.raw_file = s.raw_file
        WHEN NOT MATCHED THEN INSERT
            (timestamp_utc, zone, source, value, unit, ingested_at, raw_file)
            VALUES (s.timestamp_utc, s.zone, s.source, s.value, s.unit, s.ingested_at, s.raw_file)
    """)


def _row(ts, value, raw="test"):
    return {
        "timestamp_utc": ts,
        "zone": "IT_NORD",
        "source": "entsoe",
        "value": value,
        "unit": "MW",
        "ingested_at": datetime.now(timezone.utc),
        "raw_file": raw,
    }


def test_session_uses_iceberg_catalog(spark):
    catalogs = [r[0] for r in spark.sql("SHOW CATALOGS").collect()]
    assert "energy" in catalogs


def test_merge_inserts_then_is_idempotent(spark):
    ts = datetime(2026, 11, 14, 10, 0, tzinfo=timezone.utc)
    _merge(spark, [_row(ts, 5000.0)])
    _merge(spark, [_row(ts, 5000.0)])  # riscarico identico
    count = spark.sql("SELECT COUNT(*) FROM energy.trusted_load").collect()[0][0]
    assert count == 1


def test_merge_updates_changed_value(spark):
    ts = datetime(2026, 11, 14, 11, 0, tzinfo=timezone.utc)
    _merge(spark, [_row(ts, 5000.0)])
    _merge(spark, [_row(ts, 5100.0, raw="reload")])
    value = spark.sql(
        f"SELECT value FROM energy.trusted_load WHERE timestamp_utc = TIMESTAMP '{ts:%Y-%m-%d %H:%M:%S}'"
    ).collect()[0][0]
    assert value == 5100.0