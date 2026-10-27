from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("FastAPI-ETL")
    .master("local[*]")
    .config(
        "spark.jars",
        "/opt/spark/jars/postgresql-42.7.8.jar"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")