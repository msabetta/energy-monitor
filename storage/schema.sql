-- storage/schema.sql
CREATE TABLE IF NOT EXISTS energy.trusted_load (
    timestamp_utc  TIMESTAMP   NOT NULL,
    zone           STRING      NOT NULL,
    source         STRING      NOT NULL,
    value          DOUBLE,
    unit           STRING      NOT NULL,
    ingested_at    TIMESTAMP   NOT NULL,
    raw_file       STRING      NOT NULL
)
USING iceberg
PARTITIONED BY (zone, days(timestamp_utc))
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- Raw zone: payload invariato, un record per file scaricato
CREATE TABLE IF NOT EXISTS energy.raw_entsoe (
    fetched_at     TIMESTAMP   NOT NULL,
    document_type  STRING      NOT NULL,
    zone           STRING      NOT NULL,
    payload        STRING      NOT NULL
)
USING iceberg
PARTITIONED BY (days(fetched_at));