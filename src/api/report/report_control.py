"""
레포트(생성,조회) 관련 API 라우터
"""
from typing import Annotated, Dict, Any
from typing import Optional
from fastapi import APIRouter, Depends, Request
from src.config.status import Status, SU, ER
from src.api.report import report_service
from src.config.security import JWT
from fastapi import HTTPException
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["진로 추천 레포트 관련 API"])


@router.post(
    "/predict",
    summary="채팅 로그 저장 및 진로 추천",
    description="- 채팅 로그를 저장하고 해당 로그를 기반으로 모델 추론을 통해 진로 추천 + 레포트 생성 및 저장",
    dependencies=[Depends(JWT.verify)],
    responses=Status.docs(SU.SUCCESS, ER.INVALID_TOKEN)
)
async def save_chatlog_and_get_recommendation(
    claims: Annotated[Dict[str, Any], Depends(JWT.verify)],
    session_id: str,
):
    user_id = claims["email"]
    recommendation = await report_service.save_chatlog_and_get_recommendation(session_id, user_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="추천 결과를 생성할 수 없습니다.")
    return recommendation
'''
#### /predict 반환 데이터 구조 예시 ###
{
  "prediction": "추천 직업군",
  "relatedJobs": [
    { "title": "연관 직업 1", "info": "연관 직업 1 상세 정보" },
    { "title": "연관 직업 2", "info": "연관 직업 2 상세 정보" }
  ],
  "relatedMajors": [
    { "major": "연관 전공 1", "info": "연관 전공 1 상세 정보" },
    { "major": "연관 전공 2", "info": "연관 전공 2 상세 정보" }
  ]
}
'''


@router.get(
    "/teacher/chatlogs",
    summary="선생님이 담당 학생들의 채팅 로그 조회",
    description="- 선생님 이메일로 해당 선생님이 담당하는 학생들의 채팅 로그를 조회",
    dependencies=[Depends(JWT.verify)],
    responses=Status.docs(SU.SUCCESS, ER.INVALID_TOKEN, ER.NOT_FOUND)
)
async def get_chatlogs_by_teacher(
    claims: Annotated[Dict[str, Any], Depends(JWT.verify)],
):
    teacher_email = claims["email"]
    chatlogs = await report_service.get_chatlogs_by_teacher(teacher_email)
    if not chatlogs:
        raise HTTPException(status_code=404, detail="채팅 기록을 찾을 수 없습니다.")
    return chatlogs


@router.get(
    "/teacher/search-chatlogs",
    summary="이름 또는 이메일로 학생의 채팅 로그 검색",
    description="- 선생님이 이름 또는 이메일(아이디)로 학생의 채팅 로그를 검색",
    dependencies=[Depends(JWT.verify)],
    responses=Status.docs(SU.SUCCESS, ER.INVALID_TOKEN, ER.NOT_FOUND)
)
async def search_chatlogs_by_teacher(
    claims: Annotated[Dict[str, Any], Depends(JWT.verify)],
    search_type: Optional[str] = "name",
    search_query: Optional[str] = None,
):
    teacher_email = claims["email"]
    chatlogs = await report_service.search_chatlogs_by_teacher(teacher_email, search_type, search_query)
    if not chatlogs:
        raise HTTPException(status_code=404, detail="채팅 기록을 찾을 수 없습니다.")
    return chatlogs




@router.get(
    "/student/chatlogs",
    summary="학생이 자신의 채팅 로그 조회",
    description="- 학생 이메일로 해당 학생의 채팅 로그를 조회",
    dependencies=[Depends(JWT.verify)],
    responses=Status.docs(SU.SUCCESS, ER.INVALID_TOKEN, ER.NOT_FOUND)
)
async def get_chatlogs_by_student(
    claims: Annotated[Dict[str, Any], Depends(JWT.verify)],
):
    student_email = claims["email"]
    chatlogs = await report_service.get_chatlogs_by_student(student_email)
    if not chatlogs:
        raise HTTPException(status_code=404, detail="채팅 기록을 찾을 수 없습니다.")
    return chatlogs



@router.get(
    "/content",
    summary="데이터베이스에서 레포트 내용 가져오기",
    description="선생님이 담당 학생의 레포트를 조회",
    dependencies=[Depends(JWT.verify)],
    responses=Status.docs(SU.SUCCESS, ER.INVALID_TOKEN, ER.NOT_FOUND)
)
async def get_teacher_report(
    session_id: str
):
    report = await report_service.get_report_by_session_id(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="레포트를 찾을 수 없습니다.")
    return report