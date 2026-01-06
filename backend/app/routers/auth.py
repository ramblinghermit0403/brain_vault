from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core import security
from app.core.config import settings
from app.api import deps
from app.schemas.user import UserCreate, User as UserSchema, UserLogin
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Create new user.
    """
    # Normalize email
    user_in.email = user_in.email.lower()
    
    result = await db.execute(select(User).where(func.lower(User.email) == user_in.email))
    user = result.scalars().first()
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    hashed_password = security.get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login")
async def login(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Normalize input
    email = form_data.username.lower()
    
    # Case-insensitive lookup to handle legacy mixed-case data
    result = await db.execute(select(User).where(func.lower(User.email) == email))
    user = result.scalars().first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, extra_claims={"email": user.email, "name": user.name}
        ),
        "refresh_token": security.create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/verify", response_model=UserSchema)
def verify_token(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Verify current token validity.
    """
    return current_user

from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Refresh access token using refresh token.
    """
    from jose import jwt, JWTError
    from app.core.config import settings
    
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    # Check if user still exists/active
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    
    if not user or not user.is_active:
         raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # We can perform refresh token rotation here if desired, for now just new access token
    
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires, extra_claims={"email": user.email, "name": user.name}
        ),
        "token_type": "bearer",
        "refresh_token": request.refresh_token # Return same or a new one
    }

import httpx
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str):
    if provider == "google":
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": f"{settings.BACKEND_URL}{settings.API_V1_STR}/auth/oauth/google/callback",
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return RedirectResponse(url)
    elif provider == "github":
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": f"{settings.BACKEND_URL}{settings.API_V1_STR}/auth/oauth/github/callback",
            "scope": "user:email"
        }
        url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
        return RedirectResponse(url)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    db: AsyncSession = Depends(deps.get_db)
):
    try:
        user_email = None
        user_name = None
        
        async with httpx.AsyncClient() as client:
            if provider == "google":
                # Exchange code for token
                token_url = "https://oauth2.googleapis.com/token"
                data = {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{settings.BACKEND_URL}{settings.API_V1_STR}/auth/oauth/google/callback",
                }
                response = await client.post(token_url, data=data)
                response.raise_for_status()
                access_token = response.json()["access_token"]
                
                # Get User Info
                user_info_resp = await client.get(
                    "https://www.googleapis.com/oauth2/v1/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_info = user_info_resp.json()
                user_email = user_info.get("email")
                user_name = user_info.get("name")
                
            elif provider == "github":
                # Exchange code for token
                token_url = "https://github.com/login/oauth/access_token"
                headers = {"Accept": "application/json"}
                data = {
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": f"{settings.BACKEND_URL}{settings.API_V1_STR}/auth/oauth/github/callback",
                }
                response = await client.post(token_url, data=data, headers=headers)
                response.raise_for_status()
                access_token = response.json().get("access_token")
                
                # Get User Info
                user_resp = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_data = user_resp.json()
                user_name = user_data.get("name") or user_data.get("login")
                
                # Get Email (might be private)
                emails_resp = await client.get(
                    "https://api.github.com/user/emails",
                     headers={"Authorization": f"Bearer {access_token}"}
                )
                emails = emails_resp.json()
                primary_email = next((e for e in emails if e.get("primary")), None)
                if primary_email:
                    user_email = primary_email["email"]
                else:
                    user_email = emails[0]["email"] if emails else None

        if not user_email:
            raise HTTPException(status_code=400, detail="Could not retrieve email from provider")

        # Find or Create User
        result = await db.execute(select(User).where(func.lower(User.email) == user_email.lower()))
        user = result.scalars().first()
        
        if not user:
            # Create user (random password)
            import secrets
            random_password = secrets.token_urlsafe(16)
            hashed_passwd = security.get_password_hash(random_password)
            user = User(
                email=user_email,
                name=user_name,
                hashed_password=hashed_passwd,
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        # Generate Tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires, extra_claims={"email": user.email, "name": user.name}
        )
        refresh_token = security.create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        )
        
        # Redirect to Frontend
        # We assume frontend is running on FRONTEND_URL
        redirect_url = f"{settings.FRONTEND_URL}/login?access_token={access_token}&refresh_token={refresh_token}"
        return RedirectResponse(redirect_url)


    except Exception as e:
        # On error redirect to login with error param
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=OAuth_Failed")

class GoogleOneTapRequest(BaseModel):
    credential: str

@router.post("/google-one-tap")
async def google_one_tap_login(
    request: GoogleOneTapRequest,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Login using Google One Tap credential (ID Token)
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        # Verify the token
        # You might need to supply clock_skew_in_seconds if time sync is an issue
        id_info = id_token.verify_oauth2_token(
            request.credential, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        email = id_info['email']
        name = id_info.get('name', email.split('@')[0])
        
        # Check if email is verified? Google ID tokens usually imply verified email.
        if not id_info.get('email_verified'):
             raise HTTPException(status_code=400, detail="Google email not verified")

        # Find or Create User
        result = await db.execute(select(User).where(func.lower(User.email) == email.lower()))
        user = result.scalars().first()
        
        if not user:
             # Create user
            import secrets
            random_password = secrets.token_urlsafe(16)
            hashed_passwd = security.get_password_hash(random_password)
            user = User(
                email=email,
                name=name,
                hashed_password=hashed_passwd,
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        # Generate Tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires, extra_claims={"email": user.email, "name": user.name}
            ),
            "refresh_token": security.create_refresh_token(
                user.id, expires_delta=refresh_token_expires
            ),
            "token_type": "bearer",
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Token")
    except Exception as e:
        print(f"Google One Tap Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
