'''
수정 필요(레포트 API으로 이동 필)
'''
from fastapi import Request
from src.utils.use_model import Model
from src.utils.data_processing import preprocess_text_kiwi, label_decoding
from src.api.chat import chat_dao
from src.api.chat.chat_utils import chatbot_instances
from src.api.report import report_dao
from typing import Optional

import requests
import json
import logging


_logger = logging.getLogger(__name__)
model = Model()


async def save_chatlog_and_get_recommendation(session_id: str, student_email: str):
    ''' 채팅 로그를 저장하고 모델 추론을 수행 '''
    if session_id in chatbot_instances:
        
        ####################################### 채팅 로그 저장 #################################################
        chat_generator = chatbot_instances[session_id]
        chat_content = chat_generator.get_chatlog_from_redis()
        _logger.info(f'=>> 세션 ID : {session_id}, 채팅이력 : {chat_content}')
        
        # 채팅 로그 저장
        await report_dao.create_chatlog(session_id, chat_content, student_email)
        
        ######################################### 진로 추론 ####################################################
        # 채팅 로그에서 query와 response를 합친 텍스트 생성
        combined_text = " ".join([entry["query"] + " " + entry["response"] for entry in chat_content])
        _logger.info(f'로그 텍스트 병합 : {combined_text}')
        
        text = preprocess_text_kiwi(combined_text)
        pred = model.classify_dataframe(text)
        pred_decoded = label_decoding(pred)
        
        ########################################## 레포트 생성 ###################################################
        """
        [ 레포트 내용 ]
        - 직업군(예측 값)
        - 연관 직업 + 직업 상세 정보
        - 연관 전공 + 전공 상세 정보
        """
        
        # 추천 직업군 및 연관 정보 생성 (예시 데이터) -> RAG으로 전환 예정
        related_jobs = [
            {"title": "[테스트용 예시1] 웹 개발자", "info": "[테스트] Develops and maintains websites"},
            {"title": "[테스트용 예시2] 데이터 사이언티스트", "info": "[테스트] Analyzes complex data sets"}
        ]
        related_majors = [
            {"major": "[테스트용 예시1] 컴퓨터공학전공", "info": "[테스트] Study of computation and information"},
            {"major": "[테스트용 예시2] 정보통신전공", "info": "[테스트] Focus on the use of computers and technology"}
        ]
        
        
        # ChatReport 저장
        await report_dao.create_report(session_id, pred_decoded, related_jobs, related_majors)
        
        # 레포트 생성
        return {
            'prediction': pred_decoded,
            'relatedJobs': related_jobs,
            'relatedMajors': related_majors
        }

    else:
        _logger.error(f'입력 받은 session_id 에 chatbot_instance가 없습니다. session_id: {session_id}')
        raise ValueError("챗봇 인스턴스가 없습니다.")


async def get_chatlogs_by_teacher(teacher_email: str):
    ''' 선생님이 담당하는 학생들의 채팅 로그를 조회 '''
    chat_logs = await report_dao.get_chatlogs_by_teacher(teacher_email)
    return chat_logs


async def search_chatlogs_by_teacher(teacher_email: str, search_type: str, search_query: Optional[str]):
    ''' 선생님이 이름 또는 이메일(아이디)로 학생의 채팅 로그를 검색 '''
    if not search_query:
        return []
    chat_logs = await report_dao.search_chatlogs_by_teacher(teacher_email, search_type, search_query)
    return chat_logs


async def get_chatlogs_by_student(student_email: str):
    ''' 학생의 채팅 로그를 조회 '''
    chat_logs = await report_dao.get_chatlogs_by_student(student_email)
    return chat_logs


async def get_report_by_session_id(session_id: str):
    ''' 특정 세션 ID에 대한 레포트 내용 가져오기 '''
    report = await report_dao.get_report_by_session_id(session_id)
    if report:
        return {
            "prediction": report.report_career, 
            "relatedJobs": json.loads(report.report_jobs) if report.report_jobs else [],
            "relatedMajors": json.loads(report.report_majors) if report.report_majors else []
        }
    else:
        _logger.error(f'레포트를 찾을 수 없습니다. session_id: {session_id}')
        return None
