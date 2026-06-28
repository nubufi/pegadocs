import json
from cryptography.fernet import Fernet
from app.infra.config import settings

fernet = Fernet(settings.FERNET_SECRET_KEY)


def encrypt_dict(data: dict) -> str:
    json_str = json.dumps(data)
    return fernet.encrypt(json_str.encode()).decode()


def decrypt_dict(token: str) -> dict:
    decrypted = fernet.decrypt(token.encode()).decode()
    return json.loads(decrypted)
