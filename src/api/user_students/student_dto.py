from typing import Annotated, Union
from pydantic import EmailStr, Field, validator
from fastapi import Form
from src.config.dto import BaseDTO


class KeyStudent(BaseDTO):
    student_email: Annotated[Union[EmailStr, None], Form(description="학생 메일")]

class UpdateStudent(BaseDTO):
    student_grade: Annotated[Union[int, None], Form(description="학생 학년")]
    student_class: Annotated[Union[int, None], Form(description="학생 반")]
    student_number: Annotated[Union[str, None], Form(description="학생 번호")]
    student_name: Annotated[Union[str, None], Form(description="학생 이름")]
    student_password: Annotated[Union[str, None], Form(description="학생 비밀번호")]
    student_new_password: Annotated[Union[str, None], Form(description="학생 신규 비밀번호")]

class CreateStudent(KeyStudent):
    school_id: Annotated[Union[int, None], Form(description="학교 ID")]
    student_grade: Annotated[Union[int, None], Form(description="학생 학년")]
    student_class: Annotated[Union[int, None], Form(description="학생 반")]
    student_number: Annotated[Union[int, None], Form(description="학생 번호")]
    student_name: Annotated[Union[str, None], Form(description="학생 이름")]
    student_password: Annotated[Union[str , None], Form(description="학생 비밀번호")]
    student_password2: Annotated[Union[str, None], Form(description="학생 비밀번호 확인")]
    teacher_email: Annotated[Union[EmailStr, None], Form(description="선생님 이메일")]  # 선생님 이메일 추가

    @validator('student_email', 'student_password', 'student_password2', 'student_name', 'teacher_email')
    def not_empty(cls, v):
        if not v or not str(v).strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

    @validator('student_grade', 'student_class', 'student_number')
    def check_integer(cls, v):
        if v is not None and not isinstance(v, int):
            raise ValueError('정수 값이 필요합니다.')
        return v

    @validator('student_password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'student_password' in values and v != values['student_password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

class ReadStudentInfo(BaseDTO):
    school_id: int
    student_name: str
    student_email: str
    student_grade: int
    student_class: int
    student_number: int
    teacher_email: str  # 선생님 이메일 추가


class SchoolDTO(BaseDTO):
    school_id: int
    school_name: str