"""
학생 계정 관련 API 라우터
"""
from typing import Optional, Annotated, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Security
from src.config.status import Status, SU, ER
from src.api.user_students.student_dto import ReadStudentInfo, CreateStudent, UpdateStudent, SchoolDTO
from src.api.user_students import student_service
from src.config.security import JWT
import logging
from src.api.auth.login_service import get_current_user


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/student", tags=["회원(학생) 계정 관련 API"])

@router.post(
    "/sign-up",
    summary="회원가입",
    description="학생 회원가입",
    responses=Status.docs(SU.CREATED, ER.DUPLICATE_RECORD),
    status_code=201
)
async def create_student(student_info: CreateStudent):
    logger.info("----------신규 학생 생성----------")
    await student_service.create_student_info(student_info)
    return SU.CREATED


@router.post(
    "/read",
    summary="개인 정보 조회",
    description="- 학생 개인 정보 조회",
    # dependencies=[Depends(get_current_user)],
    dependencies=[Depends(JWT.verify)],
    response_model=ReadStudentInfo,
    responses=Status.docs(SU.SUCCESS, ER.NOT_FOUND)
)
async def get_student_info(claims: Annotated[Dict[str, Any], Depends(JWT.verify)]) -> ReadStudentInfo:
    logger.info("----------개인 정보 조회----------")
    user_id = claims["email"]
    try:
        student_info = await student_service.get_student_info(user_id)
        logger.info(student_info)
        return student_info
    except Exception as e:
        logger.error(f"Error getting student info: {e}")
        raise HTTPException(status_code=404, detail="Student not found")


@router.put(
    "/update",
    summary="개인 정보 수정",
    description="- 학생 개인 정보 수정\n값을 모두 입력해야 정상동작함(프론트에서 별도 입력처리 필)",
    dependencies=[Depends(JWT.verify)],
    responses=Status.docs(SU.SUCCESS, ER.NOT_FOUND, ER.UNAUTHORIZED)
)
async def update_student_info(
    claims: Annotated[Dict[str, Any], Depends(JWT.verify)],
    student_info: Annotated[UpdateStudent, Depends()]
):
    logger.info("----------개인 정보 수정----------")
    user_id = claims["email"]
    try:
        await student_service.update_student_info(user_id, student_info)
        return SU.SUCCESS
    except HTTPException as e:
        logger.error(f"Error updating student info: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    



@router.get(
    "/school_list", 
    summary="학교 목록 조회", 
    description="모든 학교의 목록을 조회합니다.(회원가입 시 체크박스 선택 용도)",
    response_model=List[SchoolDTO]
)
async def get_school_list():
    schools = await student_service.get_student_list()
    return schools