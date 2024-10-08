from typing import Annotated, Union
from pydantic import EmailStr, Field, validator
from fastapi import Form
from src.config.dto import BaseDTO

class KeyTeacher(BaseDTO):
    teacher_email: Annotated[Union[EmailStr, None], Form(description="교직원 메일")]

class UpdateTeacher(BaseDTO):
    teacher_grade: Annotated[Union[int, None], Form(description="교직원 학년")]
    teacher_class: Annotated[Union[int, None], Form(description="교직원 반")]
    teacher_name: Annotated[Union[str, None], Form(description="교직원 이름")]
    teacher_password: Annotated[Union[str, None], Form(description="교직원 비밀번호")]
    teacher_new_password: Annotated[Union[str, None], Form(description="교직원 신규 비밀번호")]

class CreateTeacher(KeyTeacher):
    school_id: Annotated[Union[int, None], Form(description="학교 ID")]
    teacher_grade: Annotated[Union[int, None], Form(description="교직원 학년")]
    teacher_class: Annotated[Union[int, None], Form(description="교직원 반")]
    teacher_name: Annotated[Union[str, None], Form(description="교직원 이름")]
    teacher_password: Annotated[Union[str, None], Form(description="교직원 비밀번호")]
    teacher_password2: Annotated[Union[str, None], Form(description="교직원 비밀번호 확인")]

    @validator('teacher_email', 'teacher_password', 'teacher_password2', 'teacher_name')
    def not_empty(cls, v):
        if not v or not str(v).strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

    @validator('teacher_grade', 'teacher_class')
    def check_integer(cls, v):
        if v is not None and not isinstance(v, int):
            raise ValueError('정수 값이 필요합니다.')
        return v

    @validator('teacher_password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'teacher_password' in values and v != values['teacher_password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

class ReadTeacherInfo(BaseDTO):
    school_id: int
    teacher_name: str
    teacher_email: str
    teacher_grade: int
    teacher_class: int
    is_verified: bool
