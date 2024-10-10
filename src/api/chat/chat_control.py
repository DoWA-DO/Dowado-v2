"""
진로 상담 챗봇 채팅 관련 API 라우터
"""
from typing import Annotated
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Request
from src.config.status import Status, SU, ER
from src.api.chat import chat_service
from src.api.chat.chat_dto import ChatRequest, ChatResponse
from src.config.security import JWT
import logging
from fastapi import HTTPException
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/careerchat", tags=["진로 추천 챗봇 관련 API"])


@router.post(
    "/new-session",
    summary     = "새로운 채팅 시작하기 버튼",
    description = "- 새로운 채팅 세션 생성, 채팅을 위한 초기값들 초기화, ChatGenerator 객체 생성",
    dependencies=[Depends(JWT.verify)],
    responses   = Status.docs(SU.SUCCESS)
)
def create_chatbot_session():    
    session_id = chat_service.create_chatbot_session() 
    return {"session_id" : session_id}

@router.post(
    "/chat",
    summary        = "진로 상담 챗봇에게 채팅 메시지 전송하기 버튼",
    description    = "- 채팅 메시지를 기입 후 전송하면, 챗봇의 답장이 반환됨.",
    dependencies=[Depends(JWT.verify)],
    response_model = ChatResponse,
    responses      = Status.docs(SU.SUCCESS, ER.INVALID_TOKEN)
)
async def create_chatbot_message(
    session_id: str,
    input_query: str,
):
    response = await chat_service.get_chatbot_message(session_id, input_query)
    return response

@router.post(
    "/continue-chat",
    summary        = "(상담 이어하기) 미완료된 채팅 session_id 에 채팅을 하기 위한 채팅 객체 주입",
    description    = "- 이전에 시작된 채팅 세션을 이어서 채팅할 수 있도록 초기화합니다. chat_status가 false인 경우에만 가능.",
    dependencies   = [Depends(JWT.verify)],
    responses      = Status.docs(SU.SUCCESS, ER.INVALID_TOKEN, ER.NOT_FOUND)
)
async def update_chatbot_session(
    session_id: str
):
    # 이어서 채팅할 수 있도록 세션 초기화
    new_session_id = await chat_service.update_chatbot_session(session_id)
    return {"new_session_id": new_session_id}

@router.post(
    "/save-chatlog",
    summary     = "미완료된(진행중인) 진로상담 내용 임시 저장",
    description = "- Redis에 임시 저장된 채팅 내용을 RDB에 저장/ 이전 채팅 이력 수정 후 다시 저장 가능\n- 채팅화면에서 뒤로가기 버튼에 적용\n- 레포트 생성 버튼에 적용",
    dependencies=[Depends(JWT.verify)],
    responses   = Status.docs(SU.SUCCESS, ER.INVALID_TOKEN),
)
async def create_chatlog(
    claims: Annotated[Dict[str, Any], Depends(JWT.verify)],
    session_id: str,
):
    user_id = claims["email"]
    await chat_service.create_chatlog(session_id, user_id)
    return SU.CREATED

@router.get(
    "/chat/content",
    summary="데이터베이스에서 채팅 내용 가져오기",
    description="특정 세션 ID에 해당하는 채팅 내용을 가져옵니다.",
    responses=Status.docs(SU.SUCCESS, ER.INVALID_TOKEN, ER.NOT_FOUND)
)
async def get_chat_content(
    session_id: str,
):
    chatlog = await chat_service.get_chat_content_by_session_id(session_id)
    if not chatlog:
        raise HTTPException(status_code=404, detail="채팅 기록을 찾을 수 없습니다.")
    return {"chat_content": chatlog.chat_content}

