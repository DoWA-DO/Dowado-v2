"""
메일 인증 관련 API 라우터
"""
from fastapi import APIRouter
from src.api.mail.mail_dto import EmailRequest
from src.api.mail import mail_service
import logging


# 로깅 및 라우터 객체 생성 - 기본적으로 추가
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mail", tags=["SMTP 인증(Naver Mail Server) API"])

@router.post("/send_email")
async def send_email_handler(email_request: EmailRequest):
    verification_code = mail_service.generate_verification_code()
    response = await mail_service.send_email(email_request, verification_code)
    # 인증 코드 저장
    await mail_service.save_verification_code(email_request.to_email, verification_code)
    
    return {"verification_code": verification_code, "message": response["message"]}
