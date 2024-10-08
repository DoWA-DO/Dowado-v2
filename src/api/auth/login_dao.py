from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import NoResultFound
from src.database.models import UserTeacher, UserStudent, School
from src.config.status import ER
from src.database.session import AsyncSession, rdb
from src.api.auth.login_dto import TokenUserInfo
from fastapi import HTTPException
import logging


logger = logging.getLogger(__name__)

@rdb.dao()
async def get_user_student(username: str, session: AsyncSession = rdb.inject_async()) -> TokenUserInfo:
    '''
    데이터베이스에서 학생 정보를 가져오는 함수
    '''
    student_result = await session.execute(select(UserStudent).filter(UserStudent.student_email == username).limit(1))
    student = student_result.scalars().first()
    if student:
        return TokenUserInfo(email=student.student_email, password=student.student_password)
    else:
        return None

@rdb.dao()
async def get_user_teacher(username: str, session: AsyncSession = rdb.inject_async()) -> TokenUserInfo:
    '''
    데이터베이스에서 선생 정보를 가져오는 함수
    '''
    teacher_result = await session.execute(select(UserTeacher).filter(UserTeacher.teacher_email == username).limit(1))
    teacher = teacher_result.scalars().first()
    if teacher:
        return TokenUserInfo(email=teacher.teacher_email, password=teacher.teacher_password)
    else:
        return None