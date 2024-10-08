from src.api.user_students.student_dto import ReadStudentInfo, CreateStudent, UpdateStudent, SchoolDTO
from src.api.user_students import student_dao
from fastapi import HTTPException
from src.config.status import ER
from src.config.security import Crypto
from typing import List


async def get_student_info(email: str) -> ReadStudentInfo:
    student_info = await student_dao.get_student_info(email)
    if not student_info:
        raise HTTPException(status_code=404, detail="Student not found")
    return ReadStudentInfo(
        school_id=student_info.school_id,
        student_name=student_info.student_name,
        student_email=student_info.student_email,
        student_grade=student_info.student_grade,
        student_class=student_info.student_class,
        student_number=student_info.student_number,
        teacher_email=student_info.teacher_email
    )

async def create_student_info(student_info: CreateStudent) -> None:
    if await student_dao.check_duplicate_email(student_info.student_email):
        raise HTTPException(status_code=409, detail="Duplicate email")
    await student_dao.create_student_info(student_info)
    
    
async def update_student_info(email: str, student_info: UpdateStudent) -> None:
    await student_dao.update_student_info(email, student_info)
    

async def get_student_list() -> List[SchoolDTO]:
    return await student_dao.get_student_list()