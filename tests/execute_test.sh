export ENERGY_ENV=local
#export ENERGY_WAREHOUSE=file:///tmp/energy-warehouse # hdfs:///... su cluster
#export HIVE_METASTORE_URI=thrift://<host>:9083       # solo test/prod
pytest tests/test_spark_local.py -v