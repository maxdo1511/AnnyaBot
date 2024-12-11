from cryptography.fernet import Fernet
import os

key = os.getenv("HASH_KEY")
cipher = Fernet(key)


def encrypt(data):
    return cipher.encrypt(data.encode('utf-8')).decode('utf-8')


def decrypt(data):
    return cipher.decrypt(data.encode('utf-8')).decode('utf-8')