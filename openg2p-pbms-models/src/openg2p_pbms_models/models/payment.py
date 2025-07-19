from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import mapped_column


class G2PPayment(BaseORMModel):
    __tablename__ = "g2p_payment"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_number = mapped_column(String)
    amount_issued = mapped_column(Integer)
    amount_paid = mapped_column(Integer)
    batch_id = mapped_column(Integer)
    company_id = mapped_column(Integer)
    create_date = mapped_column(DateTime)
    create_uid = mapped_column(Integer)
    cycle_id = mapped_column(Integer)
    disbursement_id = mapped_column(String)
    dispatch_status = mapped_column(String)
    entitlement_id = mapped_column(Integer)
    issuance_date = mapped_column(DateTime)
    journal_id = mapped_column(Integer)
    name = mapped_column(String)
    payment_datetime = mapped_column(DateTime)
    payment_fee = mapped_column(Integer)
    remittance_entry_date = mapped_column(String)
    remittance_entry_sequence = mapped_column(String)
    remittance_reference_number = mapped_column(String)
    remittance_statement_id = mapped_column(String)
    reversal_entry_date = mapped_column(String)
    reversal_entry_sequence = mapped_column(String)
    reversal_reason = mapped_column(String)
    reversal_statement_id = mapped_column(String)
    state = mapped_column(String)
    status = mapped_column(String)
    status_datetime = mapped_column(DateTime)
    status_is_final = mapped_column(Integer)
    write_date = mapped_column(DateTime)
    write_uid = mapped_column(Integer)
