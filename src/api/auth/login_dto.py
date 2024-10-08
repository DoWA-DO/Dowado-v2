from typing import Annotated
from fastapi import Form
from pydantic import BaseModel
from enum import Enum


# 클라이언트에게 반환되는 액세스 토큰과 토큰 유형(토큰 발급 시)
class Token(BaseModel): 
    access_token: str
    token_type: str
    
    
# 토큰에서 추출할 데이터 양식
class TokenData(BaseModel):
    email: str | None = None
    scopes: str | None = None
    

# 로그인 검증에 필요한 유저 정보
class TokenUserInfo(BaseModel):
    email: str
    password: str
