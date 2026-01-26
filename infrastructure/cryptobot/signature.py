import hashlib
import hmac


def verify_cryptopay_signature(*, api_token: str, raw_body: bytes, signature_hex: str) -> bool:
    secret = hashlib.sha256(api_token.encode("utf-8")).digest()
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_hex)
