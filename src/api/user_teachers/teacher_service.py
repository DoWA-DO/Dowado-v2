from src.api.user_teachers import teacher_dao
from src.api.user_teachers.teacher_dto import ReadTeacherInfo, CreateTeacher, UpdateTeacher
from fastapi import HTTPException

async def get_teacher_info(email: str) -> ReadTeacherInfo:
    teacher_info = await teacher_dao.get_teacher_info(email)
    if not teacher_info:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return ReadTeacherInfo(
        school_id=teacher_info.school_id,
        teacher_name=teacher_info.teacher_name,
        teacher_email=teacher_info.teacher_email,
        teacher_grade=teacher_info.teacher_grade,
        teacher_class=teacher_info.teacher_class,
        is_verified=teacher_info.is_verified
    )

async def create_teacher_info(teacher_info: CreateTeacher) -> None:
    if await teacher_dao.get_teacher_info(teacher_info.teacher_email):
        raise HTTPException(status_code=409, detail="Duplicate email")
    await teacher_dao.create_teacher_info(teacher_info)


async def update_teacher_info(email: str, teacher_info: UpdateTeacher) -> None:
    await teacher_dao.update_teacher_info(email, teacher_info)


async def save_verification_code(email: str, code: str) -> None:
    await teacher_dao.save_verification_code(email, code)

async def verify_email(email: str, code: str) -> None:
    await teacher_dao.verify_email(email, code)
