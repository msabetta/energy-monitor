# ingestion/write_trusted.py
from pyspark.sql import SparkSession, Row
from datetime import datetime, timezone

def get_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("energy-trusted-load")
        .enableHiveSupport()
        .getOrCreate()
    )

def write_trusted_load(rows: list[dict], raw_file: str) -> None:
    spark = get_spark()
    ingested_at = datetime.now(timezone.utc)

    # Aggiunge metadati di ingestione a ogni riga
    records = [
        Row(**r, ingested_at=ingested_at, raw_file=raw_file)
        for r in rows
    ]
    incoming = spark.createDataFrame(records)
    incoming.createOrReplaceTempView("incoming_load")

    spark.sql("""
        MERGE INTO energy.trusted_load AS t
        USING incoming_load AS s
        ON  t.zone = s.zone
        AND t.source = s.source
        AND t.timestamp_utc = s.timestamp_utc
        WHEN MATCHED AND (t.value <> s.value OR t.value IS NULL) THEN
            UPDATE SET
                t.value = s.value,
                t.ingested_at = s.ingested_at,
                t.raw_file = s.raw_file
        WHEN NOT MATCHED THEN
            INSERT (timestamp_utc, zone, source, value, unit, ingested_at, raw_file)
            VALUES (s.timestamp_utc, s.zone, s.source, s.value, s.unit, s.ingested_at, s.raw_file)
    """)