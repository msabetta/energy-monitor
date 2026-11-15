# ingestion/spark_session.py
import os
from pyspark.sql import SparkSession

APP_ENV = os.environ.get("ENERGY_ENV", "local")  # local | test | prod

def get_spark(app_name: str = "energy-monitor") -> SparkSession:
    """Restituisce una SparkSession con il catalogo Iceberg adatto all'ambiente."""
    if APP_ENV == "local":
        builder = SparkSession.builder.config("spark.jars.packages", os.environ.get(
            "ICEBERG_PACKAGE",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2",
        ))
        builder = builder.config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
            .config("spark.sql.catalog.energy", "org.apache.iceberg.spark.SparkCatalog") \
            .config("spark.sql.catalog.energy.type", "hadoop") \
            .config("spark.sql.catalog.energy.warehouse", os.environ.get("ENERGY_WAREHOUSE", "file:///tmp/energy-warehouse")) \
            .config("spark.sql.defaultCatalog", "energy")
    else:
        # test e prod: metastore Hive e warehouse da variabili d'ambiente
        builder = (
            SparkSession.builder
            .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
            .config("spark.sql.catalog.energy", "org.apache.iceberg.spark.SparkCatalog")
            .config("spark.sql.catalog.energy.type", "hive")
            .config("spark.sql.catalog.energy.uri", os.environ["HIVE_METASTORE_URI"])
            .config("spark.sql.catalog.energy.warehouse", os.environ["ENERGY_WAREHOUSE"])
            .config("spark.sql.defaultCatalog", "energy")
        )

    builder = builder.config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    return builder.appName(app_name).getOrCreate()