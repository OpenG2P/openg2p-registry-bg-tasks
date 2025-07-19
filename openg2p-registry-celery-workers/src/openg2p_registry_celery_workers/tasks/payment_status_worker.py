import logging
import requests

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from openg2p_pbms_models.models import (
    G2PPayment,
    G2PPaymentBatch
)

from ..helpers import JWTService
from ..app import celery_app, get_engine
from ..config import Settings

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="payment_status_worker")
def payment_status_worker(batch_id):
    _logger.info(f"Starting payment status worker for batch id: {batch_id}")
    session_maker = sessionmaker(bind=_engine.get("pbms"), expire_on_commit=False)

    with session_maker() as session:
        # Fetch the batch
        batch = session.get(G2PPaymentBatch, batch_id)
        if not batch:
            _logger.error(f"No batch found with id: {batch_id}")
            return

        _logger.info(f"Internal batch ref number: {batch.name}")

        # Fetch payments for this batch
        payments = (
            session.execute(
                select(G2PPayment).filter(
                    G2PPayment.batch_id == batch.id,
                    # based on the Odoo domain logic:
                    # ("remittance_statement_id", "=", False),
                    # ("reversal_statement_id", "=", False),
                    (G2PPayment.remittance_statement_id == None) | (G2PPayment.reversal_statement_id == None),
                )
            )
            .scalars()
            .all()
        )

        _logger.info("Total Payments for Status Check: %s", len(payments))
        for payment in payments:
            _logger.info(f"Payment for Status Check: {payment}")
            _logger.info(f"Payment Disbursement Id: {payment.disbursement_id}")

        _logger.info(f"Batch Id for Status Check: {batch.id}")
        _logger.info(f"Payment for Status Check: {len(payments)}")

        # Compose status_data
        status_data = {
            "header": {
                "version": "1.0.0",
                "message_id": "string",
                "message_ts": "string",
                "action": "string",
                "sender_id": _config.sender_id,
                "sender_uri": "",
                "receiver_id": "",
                "total_count": 0,
                "is_msg_encrypted": False,
                "meta": "string",
            },
            "message": [str(payment.disbursement_id) for payment in payments],
        }

        try:
            _logger.info("G2P Connect Disbursement Status Data: %s", status_data)

            jwt_service = JWTService()
            token = jwt_service.create_jwt_token(status_data)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Signature": token,
            }
            status_endpoint_url = getattr(_config, "status_endpoint_url", None)
            if not status_endpoint_url:
                _logger.warning("No status_endpoint_url configured, skipping status check.")
                return

            response = requests.post(
                status_endpoint_url,
                json=status_data,
                headers=headers,
            )
            _logger.debug("G2P Connect Disbursement Status response: %s", response.content)

            response.raise_for_status()
            response = response.json()
            response_list = response.get("message", [])

            for response_item in response_list:
                _logger.info(f"Disbursement ID inside Loop: {response_item.get('disbursement_id')}")
                # Find payment by disbursement_id
                payment_by_ref = (
                    session.execute(
                        select(G2PPayment).filter(
                            G2PPayment.disbursement_id == response_item.get("disbursement_id")
                        )
                    )
                    .scalars()
                    .first()
                )
                if not payment_by_ref:
                    _logger.warning(f"No payment found for disbursement_id: {response_item.get('disbursement_id')}")
                    continue

                recon_records = response_item.get("disbursement_recon_records", {})
                for recon in recon_records.get("disbursement_recon_payloads", []):
                    # Update payment fields
                    for field in [
                        "remittance_reference_number",
                        "remittance_statement_id",
                        "remittance_entry_sequence",
                        "remittance_entry_date",
                        "reversal_statement_id",
                        "reversal_entry_sequence",
                        "reversal_entry_date",
                        "reversal_reason",
                    ]:
                        if hasattr(payment_by_ref, field) and field in recon:
                            setattr(payment_by_ref, field, recon[field])
                    session.add(payment_by_ref)
                session.commit()

        except Exception as e:
            _logger.exception(
                "G2P Connect Disbursement Status Check Failed with unknown reason. %s",
                str(e),
            )
