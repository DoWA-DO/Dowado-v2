from src.database.session import AsyncSession, rdb
from src.database.models import EmailVerification
from sqlalchemy import select, update
from fastapi import HTTPException
from src.database.session import AsyncSession, rdb
from src.database.models import UserTeacher, EmailVerification
import logging


@rdb.dao()
async def save_verification_code(email: str, code: str, session: AsyncSession = rdb.inject_async()) -> None:
    db_verification = EmailVerification(
        email=email,
        verification_code=code
    )
    session.add(db_verification)
    await session.commit()
    
    
@rdb.dao()
async def verify_email(email: str, code: str, session: AsyncSession = rdb.inject_async()) -> None:
    result = await session.execute(select(EmailVerification).where(EmailVerification.email == email))
    verification = result.scalars().first()
    if verification and verification.verification_code == code:
        await session.execute(update(UserTeacher).where(UserTeacher.teacher_email == email).values(is_verified=True))
        await session.commit()
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code")