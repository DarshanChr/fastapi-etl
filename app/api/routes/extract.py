from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.etl_service import run_spark_mode
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extract", tags=["Extract"])


@router.get("/run_etl")
def etl(db: Session = Depends(get_db)):
    logger.info("inside etl api")
    return run_spark_mode(db)