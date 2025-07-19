import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from openg2p_pbms_models.models import G2PPaymentBatch

from ..app import celery_app, get_engine
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="payment_status_beat_producer")
def payment_status_beat_producer():
    _logger.info("Checking for payment batches for status check")
    session_maker = sessionmaker(bind=_engine.get("pbms"), expire_on_commit=False)

    with session_maker() as session:
        now = datetime.now()
        interval_days = getattr(_config, "payment_status_check_interval", 2)
        interval_start = now - timedelta(days=interval_days)

        batches = (
            session.execute(
                select(G2PPaymentBatch).filter(
                    G2PPaymentBatch.stats_datetime > interval_start
                )
            )
            .scalars()
            .all()
        )
        _logger.info(f"Total batches for status check: {len(batches)}")

        for batch in batches:
            _logger.info(f"Queing batch id {batch.id} for status check")
            celery_app.send_task(
                "payment_status_worker",
                args=(batch.id,),
                queue="payment_status_check_queue",
            )
    _logger.info("Completed checking for payment batches for status check")
