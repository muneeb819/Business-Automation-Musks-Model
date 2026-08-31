from app.core.security import get_password_hash, verify_password, create_access_token, decode_token
import pytest


class TestSecurity:
    def test_password_hash_and_verify(self):
        password = "SuperSecret123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)

    def test_access_token_roundtrip(self):
        token = create_access_token({"sub": "test-user-id"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        assert decode_token("invalid-token") is None
