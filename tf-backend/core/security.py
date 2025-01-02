from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """ 
    Hash password using bcrypt
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hased_password: str) -> bool:
    """ 
    Verify password against hash
    """
    return pwd_context.verify(plain_password, hased_password)