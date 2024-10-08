from sqlalchemy import select
from fastapi import HTTPException
from src.database.session import AsyncSession, rdb
from src.api.user_students.student_dto import CreateStudent, UpdateStudent, SchoolDTO
from src.database.models import UserStudent, School
from passlib.context import CryptContext
import logging


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


@rdb.dao()
async def get_student_info(email: str, session: AsyncSession = rdb.inject_async()) -> UserStudent:
    logger.info(f"해당 계정이 연결됨 -> {email}")
    result = await session.execute(select(UserStudent).where(UserStudent.student_email == email))
    return result.scalars().first()


@rdb.dao()
async def create_student_info(student_info: CreateStudent, session: AsyncSession = rdb.inject_async()) -> None:
    db_user = UserStudent(
        school_id=student_info.school_id,
        student_grade=student_info.student_grade,
        student_class=student_info.student_class,
        student_number=student_info.student_number,
        student_email=student_info.student_email,
        student_name=student_info.student_name,
        student_password=pwd_context.hash(student_info.student_password),
        teacher_email=student_info.teacher_email,
    )
    session.add(db_user)
    await session.commit()


@rdb.dao()
async def update_student_info(email: str, student_info: UpdateStudent, session: AsyncSession = rdb.inject_async()) -> None:
    existing_student = await get_student_info(email)  
    if not existing_student:
        raise HTTPException(status_code=404, detail="해당되는 학생을 찾을 수 없습니다.")
    
    if not pwd_context.verify(student_info.student_password, existing_student.student_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )


    logger.info(f"기존 학생 정보: {existing_student}")
    
    existing_student.student_grade = student_info.student_grade or existing_student.student_grade
    existing_student.student_class = student_info.student_class or existing_student.student_class
    existing_student.student_number = student_info.student_number or existing_student.student_number
    existing_student.student_name = student_info.student_name or existing_student.student_name

    if student_info.student_new_password:
        existing_student.student_password = pwd_context.hash(student_info.student_new_password)

    logger.info(f"수정된 학생 정보: {existing_student}")
    session.add(existing_student)  
    await session.commit()  

    logger.info(f"학생 정보가 성공적으로 업데이트되었습니다: {existing_student}")
    
    
@rdb.dao()
async def check_duplicate_email(email: str, session: AsyncSession = rdb.inject_async()) -> bool:
    result = await session.execute(select(UserStudent).where(UserStudent.student_email == email))
    user = result.scalars().first()
    return user is not None


@rdb.dao()
async def get_student_list(session: AsyncSession = rdb.inject_async()):
    result = await session.execute(select(School))
    schools = result.scalars().all()
    return [SchoolDTO(school_id=school.school_id, school_name=school.school_name) for school in schools]