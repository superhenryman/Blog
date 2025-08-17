import hmac
import hashlib
import os

secret_key = os.getenv("SECRET").encode("utf-8")

def sign_client_id(client_id: str) -> str:
    signature = hmac.new(secret_key, client_id.encode(), hashlib.sha256).hexdigest()
    return signature


def verify_signature(client_id: str, signature: str) -> bool:
    if client_id is None or signature is None:
        return False
    expected_sig = sign_client_id(client_id)
    return hmac.compare_digest(expected_sig, signature)
