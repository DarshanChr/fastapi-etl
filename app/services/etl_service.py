from app.core.spark_config import spark
from sqlalchemy.orm import Session
from app.services.customer_service import get_customers
from pyspark.sql.functions import ( col, when, current_timestamp)
import logging

logger = logging.getLogger(__name__)


def run_spark_mode(db: Session):

    logger.info("Run spark mode")

    records = get_customers(db)

    logger.info(f"successflly fetched records:: {records} ")

    # 1. Convert Python records to a DataFrame
    df = spark.createDataFrame(records)

    logger.info("Created spark dataframe")

    # 2. Remove invalid records
    valid_df = df.filter(
    col("customer_id").isNotNull()
    & col("customer_name").isNotNull()
    & col("salary").isNotNull()
    & (col("salary") >= 0)
    )   

    # 3. Remove duplicate business keys
    clean_df = valid_df.dropDuplicates(["customer_id"])

    # 4. Standardize names
    clean_df = (
        clean_df
        .withColumn(
            "salary_band",
            when(col("salary") >= 50000, "HIGH")
            .otherwise("NORMAL")
    )
    .withColumn("processed_at", current_timestamp())
    )

    # Select only columns that exist in the target table
    target_df = clean_df.select(
    "customer_id",
    "customer_name",
    "email",
    "age",
    "city",
    "salary",
    "processed_at"
    )

    logger.info("Validation completed")

    save_to_postgres(
    target_df,
    "customer_etl_target",
    "jdbc:postgresql://localhost:5432/testdb",
    "postgres",
    "admin"
    )

    logger.info("Save to postgress completed")

    return {
        "success"
    }


def save_to_postgres(df, table_name: str, jdbc_url: str,
                     username: str, password: str):
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