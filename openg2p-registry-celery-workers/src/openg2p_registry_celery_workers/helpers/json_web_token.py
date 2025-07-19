import base64
import json
import logging
from datetime import datetime

import httpx
from openg2p_fastapi_common.service import BaseService

from ..config import Settings
from .oauth_token import OAuthTokenService

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class JWTService(BaseService):
    def __init__(self):
        super().__init__()
        self.oauth_token_service = OAuthTokenService()

        self.keymanager_api_base_url = _config.keymanager_api_base_url
        self.keymanager_api_timeout = _config.keymanager_api_timeout

    def create_jwt_token(
        self,
        payload,
        expiration_minutes=60,
        include_payload=False,
        include_certificate=False,
        include_cert_hash=False,
    ):
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        elif isinstance(payload, str):
            payload = payload.encode()
        km_token = self.get_keymanager_auth_token()
        current_time = self.get_current_isotimestamp()
        with httpx.Client() as client:
            response = client.post(
                f"{self.keymanager_api_base_url}/jwtSign",
                json={
                    "id": "string",
                    "version": "string",
                    "requesttime": current_time,
                    "metadata": {},
                    "request": {
                        "dataToSign": self.urlsafe_b64encode(payload),
                        "applicationId": _config.sign_key_keymanager_app_id or "",
                        "referenceId": _config.sign_key_keymanager_ref_id or "",
                        "includePayload": include_payload,
                        "includeCertificate": include_certificate,
                        "includeCertHash": include_cert_hash,
                    },
                },
                cookies={"Authorization": km_token},
                timeout=self.keymanager_api_timeout,
            )
        _logger.debug("Keymanager JWT Sign API response: %s", response.text)
        response.raise_for_status()
        return ((response.json() or {}).get("response") or {}).get("jwtSignedData")

    def get_keymanager_auth_token(self):
        token = self.oauth_token_service.get_oauth_token()
        return token

    def urlsafe_b64encode(self, input_data: bytes) -> str:
        return base64.urlsafe_b64encode(input_data).decode().rstrip("=")

    def get_current_isotimestamp(self):
        return f'{datetime.now().isoformat(timespec = "milliseconds")}Z'
