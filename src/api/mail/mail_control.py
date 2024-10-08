"""
메일 인증 관련 API 라우터
"""
from fastapi import APIRouter
from .mail_dto import EmailRequest
from .mail_service import generate_verification_code, send_email
import logging
from src.api.user_teachers.teacher_service import save_verification_code # 위치 이동 필요

# 로깅 및 라우터 객체 생성 - 기본적으로 추가
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mail", tags=["SMTP 인증(Naver Mail Server) API"])

@router.post("/send_email")
async def send_email_handler(email_request: EmailRequest):
    verification_code = generate_verification_code()
    response = await send_email(email_request, verification_code)
    
    # 인증 코드 저장
    await save_verification_code(email_request.to_email, verification_code)
    
    return {"verification_code": verification_code, "message": response["message"]}
