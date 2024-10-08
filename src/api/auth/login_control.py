"""
계정 권한 관련(로그인) API 라우터
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path
from src.config.security import (
    STUDENT_SCOPE,
    TEACHER_SCOPE,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT,
    Crypto,
)
from src.api.auth import login_service
from src.api.auth.login_dto import Token, TokenUserInfo, TokenData
from src.config.status import ER, SU, Status
from fastapi import Form, HTTPException, status
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["계정 권한 관련(로그인) API"], responses=Status.docs(SU.SUCCESS))


@router.post(
    "/login",
    summary="액세스 토큰을 발급하는 로그인 엔드포인트",
    description="- 학생/선생 구분하여 토큰 발급",
    response_model = Token,
    responses=Status.docs(SU.SUCCESS, ER.UNAUTHORIZED)
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    if form_data.scopes == ["student"]:
        scope = STUDENT_SCOPE
    elif form_data.scopes == ["teacher"]:
        scope = TEACHER_SCOPE

    user = await login_service.authenticate_user(form_data.username, form_data.password, scope)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password", 
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await login_service.get_access_token(email=user.email, scope=scope)
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/info",
    summary="엑세스된 토큰에서 사용자 정보 추출하는 엔드포인트",
    description="- 인증된 사용자에 대한 토큰 정보 반환",
    responses=Status.docs(SU.SUCCESS, ER.UNAUTHORIZED)
)
async def get_depends(current_user: Annotated[TokenData, Depends(login_service.get_current_user)],):
    return current_user