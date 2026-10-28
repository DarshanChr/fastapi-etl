
from app.core.spark_config import spark
from sqlalchemy.orm import Session
from app.services.customer_service import get_customers
from pyspark.sql.functions import col, when, current_timestamp
import logging

logger = logging.getLogger(__name__)


def run_spark_mode(db: Session):
    logger.info("Running Spark mode")

    records = get_customers(db)
    logger.info("Successfully fetched %s customer records", len(records))

    if not records:
        return {"success": True, "processed_count": 0}

    # Convert Python records to a Spark DataFrame
    df = spark.createDataFrame(records)
    logger.info("Created Spark DataFrame")

    # 1. Remove invalid records
    valid_df = df.filter(
        col("customer_id").isNotNull()
        & col("customer_name").isNotNull()
        & col("salary").isNotNull()
        & (col("salary") >= 0)
    )

    # 2. Remove duplicate customer IDs
    clean_df = valid_df.dropDuplicates(["customer_id"])

    # 3. Derive salary band and processing timestamp
    clean_df = (
        clean_df
        .withColumn(
            "salary_band",
            when(col("salary") >= 50000, "HIGH").otherwise("NORMAL")
        )
        .withColumn("processed_at", current_timestamp())
    )

    # 4. Select columns matching the target table
    target_df = clean_df.select(
        "customer_id",
        "customer_name",
        "email",
        "age",
        "city",
        "salary",
        "salary_band",
        "processed_at"
    )

    logger.info("Validation and transformation completed")

    # PostgreSQL Service name: postgress
    jdbc_url = "jdbc:postgresql://postgress:5432/etldb"

    save_to_postgres(
        target_df,
        "customer_etl_target",
        jdbc_url,
        "admin",
        "admin"
    )

    logger.info("Saved transformed records to PostgreSQL")

    return {
        "success": True,
        "processed_count": target_df.count()
    }


def save_to_postgres(
    df,
    table_name: str,
    jdbc_url: str,
    username: str,
    password: str
):
    (
        df.write
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", f"public.{table_name}")
        .option("user", username)
        .option("password", password)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )
