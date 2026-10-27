from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
import logging


logger = logging.getLogger(__name__)


def get_customers(db: Session):

    logger.info("Customer extraction started")

    try:
        result = db.execute(
            text("""
                SELECT customer_id, customer_name, email,
                age, city, salary
                FROM customers_source
                ORDER BY customer_id
            """)    
        )
        

        customers = [
            dict(row)
            for row in result.mappings().all()
        ]

        logger.info("Customer extraction completed: rows=%d", len(customers))

        return customers

    except Exception as exc:
        logger.exception("Customer extraction failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch customer details from database postgress sql"
        ) from exc
