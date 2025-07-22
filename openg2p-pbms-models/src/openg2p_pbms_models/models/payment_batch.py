from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Boolean, DateTime, Double, Integer, String
from sqlalchemy.orm import mapped_column


class G2PPaymentBatch(BaseORMModel):
    __tablename__ = "g2p_payment_batch"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    cycle_id = mapped_column(Integer)
    stats_issued_transactions = mapped_column(Integer)
    stats_sent_transactions = mapped_column(Integer)
    stats_paid_transactions = mapped_column(Integer)
    stats_failed_transactions = mapped_column(Integer)
    tag_id = mapped_column(Integer)
    create_uid = mapped_column(Integer)
    write_uid = mapped_column(Integer)
    name = mapped_column(String)
    external_batch_ref = mapped_column(String)
    batch_has_started = mapped_column(Boolean)
    batch_has_completed = mapped_column(Boolean)
    stats_datetime = mapped_column(DateTime)
    create_date = mapped_column(DateTime)
    write_date = mapped_column(DateTime)
    stats_issued_amount = mapped_column(Double)
    stats_sent_amount = mapped_column(Double)
    stats_paid_amount = mapped_column(Double)
    stats_failed_amount = mapped_column(Double)
