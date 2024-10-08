from sqlalchemy import select, update
from fastapi import HTTPException
from src.database.session import AsyncSession, rdb
from src.api.user_teachers.teacher_dto import CreateTeacher, UpdateTeacher
from src.database.models import UserTeacher, EmailVerification
from passlib.context import CryptContext
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

@rdb.dao()
async def get_teacher_info(email: str, session: AsyncSession = rdb.inject_async()) -> UserTeacher:
    logger.info(f"해당 계정이 연결됨 -> {email}")
    result = await session.execute(select(UserTeacher).where(UserTeacher.teacher_email == email))
    return result.scalars().first()

@rdb.dao()
async def create_teacher_info(teacher_info: CreateTeacher, session: AsyncSession = rdb.inject_async()) -> None:
    db_teacher = UserTeacher(
        school_id=teacher_info.school_id,
        teacher_grade=teacher_info.teacher_grade,
        teacher_class=teacher_info.teacher_class,
        teacher_email=teacher_info.teacher_email,
        teacher_name=teacher_info.teacher_name,
        teacher_password=pwd_context.hash(teacher_info.teacher_password),
        is_verified=False  # 기본값으로 인증되지 않은 상태로 설정
    )
    session.add(db_teacher)
    await session.commit()

@rdb.dao()
async def update_teacher_info(email: str, teacher_info: UpdateTeacher, session: AsyncSession = rdb.inject_async()) -> None:
    existing_teacher = await get_teacher_info(email)
    if not existing_teacher:
        raise HTTPException(status_code=404, detail="해당되는 선생님을 찾을 수 없습니다.")

    if not pwd_context.verify(teacher_info.teacher_password, existing_teacher.teacher_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"기존 선생 정보: {existing_teacher}")
    
    # 업데이트할 필드 구성
    existing_teacher.teacher_grade = teacher_info.teacher_grade or existing_teacher.teacher_grade
    existing_teacher.teacher_class = teacher_info.teacher_class or existing_teacher.teacher_class
    existing_teacher.teacher_name = teacher_info.teacher_name or existing_teacher.teacher_name

    if teacher_info.teacher_new_password:
        existing_teacher.teacher_password = pwd_context.hash(teacher_info.teacher_new_password)
        
    logger.info(f"수정된 선생 정보: {existing_teacher}")
    session.add(existing_teacher)
    await session.commit()    
    
    logger.info("f'선생 정보가 성공적으로 업데이트 되었습니다. : {existing_teacher}")
    
        
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
