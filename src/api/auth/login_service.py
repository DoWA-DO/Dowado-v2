from typing import Optional, Annotated
from fastapi import HTTPException, Depends, status
from src.config.status import ER
from src.api.auth import login_dao
from src.config.security import (
    Crypto, 
    JWT, 
    oauth2_scheme, 
    STUDENT_SCOPE, 
    TEACHER_SCOPE,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.api.auth.login_dto import Token, TokenUserInfo, TokenData
import logging
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import timedelta, datetime


logger = logging.getLogger(__name__)

async def authenticate_user(username: str, password: str, scope: str) -> TokenUserInfo:
    '''
    - 사용자 인증 함수 (비밀번호 검증)
    - 사용자의 이름과 비밀번호를 검증하여 유효한 사용자인지 확인
    '''
    if scope == STUDENT_SCOPE:
        user = await login_dao.get_user_student(username)
    elif scope == TEACHER_SCOPE:
        user = await login_dao.get_user_teacher(username)
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid scope"
        )

    if not user or not Crypto.verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"{scope.capitalize()} user authenticated: {username}")
    return user


async def get_access_token(email: str, scope: str):
    ''' email, scope, 현재 시간 으로부터 새로운 토큰 발급 '''
    acces_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWT.create_access_token(
        data={"sub": email, "scope": scope}, expires_delta=acces_token_expires
    )
    return access_token


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenUserInfo:
    ''' 
    - 현재 사용자 정보를 가져오는 함수 (JWT 토큰에서 사용자 정보 추출)
    - JWT 토큰을 디코딩하여 사용자 정보를 추출하고 검증
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = JWT.decode_token(token)
        username: str = payload.get("sub")
        scope: str = payload.get("scope")
        
        if username is None or scope is None:
            raise credentials_exception       
    
        if scope == STUDENT_SCOPE:
            user = await login_dao.get_user_student(username)
        elif scope == TEACHER_SCOPE:
            user = await login_dao.get_user_teacher(username)
        
        if user is None:
            raise credentials_exception
        return user
    
    except InvalidTokenError:
        raise credentials_exception
        
    