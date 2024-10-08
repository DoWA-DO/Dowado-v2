"""
진로 추천 레포트 API
"""
import json
import logging
from fastapi import Depends
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Result, ScalarResult, select, update, insert, delete
from sqlalchemy.orm import Session, joinedload, query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import ChatLog, UserStudent, ChatReport
from src.database.session import AsyncSession, rdb


_logger = logging.getLogger(__name__)

@rdb.dao(transactional=True)
async def create_chatlog(session_id: str, chat_content: list, student_email: str, session: AsyncSession = rdb.inject_async()) -> None:
    ''' ChatLOG 테이블에 완료된(레포트를 생성완료한) 채팅 내역 저장하기 '''
    
    # 먼저 해당 세션 ID가 존재하는지 확인
    existing_chatlog = await session.execute(select(ChatLog).where(ChatLog.chat_session_id == session_id))
    existing_chatlog = existing_chatlog.scalars().first()

    if existing_chatlog:
        # 세션 ID가 존재하면 업데이트
        await session.execute(update(ChatLog).where(ChatLog.chat_session_id == session_id).values(
            chat_content=json.dumps(chat_content),
            chat_date=datetime.now(timezone.utc),
            chat_status=True,
            student_email=student_email
        ))
        _logger.info(f'기존 채팅 로그 업데이트: {session_id}')
    else:
        # 세션 ID가 존재하지 않으면 새로 삽입
        chatlog = ChatLog(
            chat_session_id=session_id,
            chat_content=json.dumps(chat_content),
            chat_date=datetime.now(timezone.utc),
            chat_status=True,
            student_email=student_email
        )
        await session.execute(insert(ChatLog).values({
            "chat_session_id": chatlog.chat_session_id,
            "chat_content": chatlog.chat_content,
            "chat_date": chatlog.chat_date,
            "chat_status": chatlog.chat_status,
            "student_email": chatlog.student_email
        }))
        _logger.info(f'새로운 채팅 로그 삽입: {session_id}')


@rdb.dao(transactional=True)
async def create_report(session_id: str, prediction: str, related_jobs: list, related_majors: list, session: AsyncSession = rdb.inject_async()) -> None:
    ''' ChatReport 테이블에 추천된 직업군 및 관련 정보를 저장 '''
    report = ChatReport(
        chat_session_id=session_id,
        report_career=prediction,
        report_jobs=json.dumps(related_jobs),
        report_majors=json.dumps(related_majors)
    )
    await session.execute(insert(ChatReport).values({
        "chat_session_id": report.chat_session_id,
        "report_career": report.report_career,
        "report_jobs": report.report_jobs,
        "report_majors": report.report_majors
    }))
    _logger.info(f'새로운 레포트 생성: {session_id}')



@rdb.dao()
async def get_chatlogs_by_teacher(teacher_email: str, session: AsyncSession = rdb.inject_async()):
    ''' 선생님 이메일로 해당 선생님이 담당하는 학생들의 채팅 로그 조회 (chat_status가 True인 항목만) '''
    result = await session.execute(
        select(ChatLog, UserStudent.student_name)  # student_name도 선택
        .join(UserStudent, ChatLog.student_email == UserStudent.student_email)
        .where(UserStudent.teacher_email == teacher_email)
        .where(ChatLog.chat_status == True)  # chat_status가 True인 항목만 필터링
    )
    return [{'chat': chat, 'student_name': student_name} for chat, student_name in result]


@rdb.dao()
async def search_chatlogs_by_teacher(teacher_email: str, search_type: str, search_query: str, session: AsyncSession = rdb.inject_async()):
    ''' 이름 또는 이메일로 학생의 채팅 로그 검색 '''
    query = select(ChatLog, UserStudent.student_name)  # student_name도 선택
    query = query.join(UserStudent, ChatLog.student_email == UserStudent.student_email)
    
    if search_type == "name":
        query = query.where(UserStudent.student_name.ilike(f"%{search_query}%"))
    elif search_type == "email":
        query = query.where(UserStudent.student_email.ilike(f"%{search_query}%"))

    query = query.where(UserStudent.teacher_email == teacher_email)  # 담당 학생 필터
    query = query.where(ChatLog.chat_status == True)  # chat_status가 True인 항목만
    
    result = await session.execute(query)
    return [{'chat': chat, 'student_name': student_name} for chat, student_name in result]



@rdb.dao()
async def get_chatlogs_by_student(student_email: str, session: AsyncSession = rdb.inject_async()):
    ''' 학생 이메일로 해당 학생의 채팅 로그 조회 '''
    result = await session.execute(
        select(ChatLog, UserStudent.student_name)  # student_name도 선택
        .join(UserStudent, ChatLog.student_email == UserStudent.student_email)
        .where(ChatLog.student_email == student_email)
    )
    return [{'chat': chat, 'student_name': student_name} for chat, student_name in result]


@rdb.dao(transactional=True)
async def get_report_by_session_id(session_id: str, session: AsyncSession = rdb.inject_async()) -> Optional[ChatReport]:
    ''' 특정 세션 ID에 대한 레포트 내용 가져오기 '''
    result = await session.execute(select(ChatReport).where(ChatReport.chat_session_id == session_id))
    report = result.scalars().first()
    return report