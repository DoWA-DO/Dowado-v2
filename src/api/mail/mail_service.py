# naver smtp 이용하기 전 네이버 메일(서버)에서 pop3/smtp 사용으로 바꿔야 함.
# mail_service.py

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import smtplib
import string
from fastapi import HTTPException
from .mail_dto import EmailRequest
from src.config import settings


NAVER_EMAIL = settings.mail.NAVER_EMAIL_ADDRESS
NAVER_PASSWORD = settings.mail.NAVER_EMAIL_PASSWORD

# Generate random verification code
def generate_verification_code(length: int = 4) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))
  
async def send_email(email_request: EmailRequest, verification_code: str):
    smtp_server = "smtp.naver.com"
    smtp_port = 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(NAVER_EMAIL, NAVER_PASSWORD) #서버로 사용할 naver id pw

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "DOWA:DO 인증 코드입니다."
        msg['From'] = NAVER_EMAIL
        msg['To'] = email_request.to_email

        html = f"""
        <html>
          <body>
            <p>다음은 귀하의 인증 코드입니다: <strong>{verification_code}</strong></p>
            <p>인증 코드를 입력하여 계정을 인증하십시오.</p>
          </body>
        </html>
        """

        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        server.send_message(msg)
        server.quit()
        return {"message": "Email sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")