"""
JWT Authentication system for the LoFi IA YouTube API.

Provides secure token-based authentication with role-based access control (RBAC).
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import secrets

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate secure key (store in env in production)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class Token(BaseModel):
    """Token response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = "user"
    scopes: list[str] = []


class User(BaseModel):
    """User model."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field(default="user", description="User role (admin, user)")
    is_active: bool = Field(default=True, description="Is user active")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


class UserCreate(BaseModel):
    """User creation request."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")


class LoginRequest(BaseModel):
    """Login request."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


# JWT utilities
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in token

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        TokenData with user information

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_token(token)

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user data
    user_id: str = payload.get("sub")
    username: str = payload.get("username")
    role: str = payload.get("role", "user")
    scopes: list = payload.get("scopes", [])

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenData(user_id=user_id, username=username, role=role, scopes=scopes)


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        TokenData if user is active

    Raises:
        HTTPException: If user is inactive
    """
    # In production, check user status in database
    return current_user


async def require_admin(
    current_user: TokenData = Depends(get_current_active_user)
) -> TokenData:
    """
    Require admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        TokenData if user is admin

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_scope(required_scope: str):
    """
    Create a dependency that requires a specific scope.

    Args:
        required_scope: Required scope

    Returns:
        Dependency function
    """
    async def _require_scope(
        current_user: TokenData = Depends(get_current_active_user)
    ) -> TokenData:
        if required_scope not in current_user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{required_scope}' required"
            )
        return current_user

    return _require_scope


# Mock user database (replace with real DB in production)
fake_users_db = {
    "admin": {
        "id": "1",
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True,
    },
    "user": {
        "id": "2",
        "username": "user",
        "email": "user@example.com",
        "role": "user",
        "hashed_password": get_password_hash("user123"),
        "is_active": True,
    }
}


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user with username and password.

    Args:
        username: Username
        password: Password

    Returns:
        UserInDB if authentication successful, None otherwise
    """
    user_dict = fake_users_db.get(username)
    if not user_dict:
        return None

    user = UserInDB(**user_dict)
    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_tokens(user: UserInDB) -> Token:
    """
    Create access and refresh tokens for a user.

    Args:
        user: User to create tokens for

    Returns:
        Token with access and refresh tokens
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "scopes": ["read", "write"] if user.role == "admin" else ["read"]
    }

    access_token = create_access_token(token_data, expires_delta=access_token_expires)
    refresh_token = create_refresh_token({"sub": user.id})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
