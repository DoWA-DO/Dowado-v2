"""
진로 상담 챗봇 API - DTO(데이터 전송 객체 선언)
"""
from datetime import datetime, timezone
from typing import Optional, Annotated
from fastapi import Depends, Form, Path
from pydantic import Field, EmailStr, validator
from src.config.dto import BaseDTO


class ChatRequest(BaseDTO):
    session_id: str
    query: str
    
class ChatResponse(BaseDTO):
    session_id: str
    response: str
    