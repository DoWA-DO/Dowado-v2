"""
교직원 계정 관련 API 라우터
"""
from typing import Optional, Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Security
from src.config.status import Status, SU, ER
from src.api.user_teachers.teacher_dto import ReadTeacherInfo, CreateTeacher, UpdateTeacher
from src.api.user_teachers import teacher_service
from src.config.security import JWT
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/teacher", tags=["회원(교직원) 계정 관련 API"])

@router.post(
    "/sign-up",
    summary="회원가입",
    description="교직원 회원가입",
    responses=Status.docs(SU.CREATED, ER.DUPLICATE_RECORD),
    status_code=201
)
async def create_teacher(teacher_info: CreateTeacher): # Annotated[CreateTeacher, Depends()]
    logger.info("----------신규 교직원 생성----------")
    await teacher_service.create_teacher_info(teacher_info)
    return SU.CREATED

@router.post(
    "/read",
    summary="개인 정보 조회",
    description="- 교직원 개인 정보 조회",
    # dependencies=[Depends(JWT.verify)],
    response_model=ReadTeacherInfo,
    responses=Status.docs(SU.SUCCESS, ER.NOT_FOUND)
)
async def get_teacher_info(claims: Annotated[Dict[str, Any], Depends(JWT.verify)],) -> ReadTeacherInfo:
    logger.info("----------개인 정보 조회----------")
    user_id = claims["email"]
    try:
        teacher_info = await teacher_service.get_teacher_info(user_id)
        logger.info(teacher_info)
        return teacher_info
    except Exception as e:
        logger.error(f"Error getting teacher info: {e}")
        raise HTTPException(status_code=404, detail="Teacher not found")

@router.put(
    "/update",
    summary="개인 정보 수정",
    description="- 교직원 개인 정보 수정",
    dependencies=[Depends(JWT.verify)],
    responses=Status.docs(SU.SUCCESS, ER.NOT_FOUND, ER.UNAUTHORIZED)
)
async def update_teacher_info(
    claims: Annotated[Dict[str, Any], Depends(JWT.verify)],
    teacher_info: Annotated[UpdateTeacher, Depends()]
):
    logger.info("----------개인 정보 수정----------")
    user_id = claims["email"]
    try:
        await teacher_service.update_teacher_info(user_id, teacher_info)
        return SU.SUCCESS
    except HTTPException as e:
        logger.error(f"Error updating teacher info: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post(
    "/verify-email",
    summary="이메일 인증",
    description="이메일로 전송된 인증 코드를 확인하여 계정 인증",
    responses=Status.docs(SU.SUCCESS)
)
async def verify_teacher_email(email: str, code: str):
    logger.info("----------이메일 인증----------")
    try:
        await teacher_service.verify_email(email, code)
        return SU.SUCCESS
    except HTTPException as e:
        logger.error(f"Error verifying email: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
