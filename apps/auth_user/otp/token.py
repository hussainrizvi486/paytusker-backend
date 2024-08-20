from django.db import models
from cryptography.fernet import Fernet
import jwt


key = Fernet.generate_key()
cipher_suite = Fernet(key)
from server import settings

JWT_SECRET = settings.SECRET_KEY


def is_valid_token(payload: dict):
    exp_time = payload.get("exp")


def create_token(payload):
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    encrypted_token = cipher_suite.encrypt(token.encode()).decode()
    return encrypted_token


def decrypt_token(enc_token):
    try:
        dec_token = cipher_suite.decrypt(enc_token.encode()).decode()
        payload = jwt.decode(dec_token, JWT_SECRET, algorithms=["HS256"])
        return {"payload": payload, "status": True}
    except:
        return {"status": False}
