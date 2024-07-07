import re

from cryptography.fernet import Fernet

key = 'pHIXnnoiH0V9vcb2AU3ZGUYgIfNjED9o6FnrwaI0Fj8='.encode()


def encrypt(message):
    fernet = Fernet(key)
    return fernet.encrypt(message.encode()).decode()


def decrypt(enc_message):
    fernet = Fernet(key)
    return fernet.decrypt(enc_message).decode()


def validate_email(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if re.fullmatch(regex, email):
        return True
    else:
        return False


def validate_password(password: str) -> tuple:
    # Check if the password has at least 8 characters
    if len(password) < 8:
        return False, 'Password should be at least 8 characters'

    # Check if the password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, 'Password should contains at least one uppercase letter'

    # Check if the password contains at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, 'Password should contains at least one lowercase letter'

    # Check if the password contains at least one digit
    if not re.search(r'\d', password):
        return False, 'Password should contains at least one digit'

    # Check if the password contains at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Password should contains at least one special character'

    # If all the conditions are met, the password is valid
    return True, ''
