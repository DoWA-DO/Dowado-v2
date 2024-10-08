"""
JWT 기반 로그인에 사용될 보안 모듈
"""
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from typing import Annotated, Any, Callable, Tuple, Dict
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from src.config import settings
import logging


logger = logging.getLogger(__name__)

SECRET_KEY = settings.jwt.JWT_SECRET_KEY
ALGORITHM = settings.jwt.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 액세스 토큰의 만료 시간(분 단위)
STUDENT_SCOPE = "student"
TEACHER_SCOPE = "teacher"


# OAuth2PasswordBearer: "/token" 엔드포인트를 사용하여 토큰을 얻도록 설정
# 클라이언트가 토큰을 얻기 위해 이 URL을 호출
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth",
    scopes={"student": "Access as student", "teacher": "Access as teacher"}
)

class Crypto:
    '''
    비밀번호 해싱 및 검증을 위한 클래스
    '''
    # 비밀번호 해싱 및 검증을 위한 PassLib 컨텍스트 생성
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        '''
        - 평문 비밀번호와 해싱된 비밀번호를 비교하는 함수
        - 사용자가 입력한 비밀번호와 저장된 해시된 비밀번호를 비교
        '''
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        '''
        - 비밀번호를 해싱하는 함수
        - 새로운 사용자 생성 시 비밀번호를 해싱하여 저장
        '''
        return cls.pwd_context.hash(password)

    
class JWT:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        '''
        - JWT 액세스 토큰을 생성하는 함수
        - 사용자 정보를 포함한 JWT 토큰을 생성하고 반환
        '''
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        if "sub" not in to_encode or "scope" not in to_encode:
            raise ValueError("Missing required claims: 'sub' or 'scope'")
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


    @staticmethod
    def decode_token(token: str) -> dict:
        """
        - JWT 토큰을 디코딩 하는 함수
        - 주어진 JWT 토큰을 해독하여 포함된 내용을 반환
        - 유효하지 않은 토큰인 경우 HTTP 예외처리
        """
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def verify(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
        """
        - JWT 토큰에서 클레임을 추출하는 함수
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            logger.debug(f"=>> 입력 받은 토큰: {token}")
            if token.startswith("Bearer "):
                token = token[7:]  # "Bearer " 부분을 잘라내고 토큰만 남김
            payload = JWT.decode_token(token)
            logger.debug(f"=>> payload 디코딩 결과 : {payload}")
            
            email: str = payload.get("sub")
            scope: str = payload.get("scope")
            
            if email is None or scope is None:
                logger.error("토큰에서 email, scope를 찾을 수 없습니다.")
                raise credentials_exception 
            
            return {"email": email, "scope": scope}

        except InvalidTokenError:
            logger.error(f"=>> 토큰이 유효하지 않음")
            raise credentials_exception
    