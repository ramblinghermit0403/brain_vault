from cryptography.fernet import Fernet
import base64
import hashlib
from app.core.config import settings

class EncryptionService:
    def __init__(self):
        # Derive a 32-byte URL-safe base64 key from the SECRET_KEY
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode()).decode()

encryption_service = EncryptionService()
