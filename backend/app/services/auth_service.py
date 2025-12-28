"""
Authentication utilities for JWT token generation and validation
"""
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict

# Secret key for JWT - should be in .env
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(data: Dict) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dict containing user data (typically user_id, email)
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token data if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None


def get_current_admin(token: str) -> Optional[Dict]:
    """
    Get current admin from token
    
    Args:
        token: JWT token string
    
    Returns:
        Admin data if valid token, None otherwise
    """
    payload = verify_access_token(token)
    if not payload:
        return None
    
    return {
        "id": payload.get("id"),
        "email": payload.get("email")
    }
