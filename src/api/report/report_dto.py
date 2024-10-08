"""
진로 추천 레포트 API
"""
from datetime import datetime, timezone
from typing import Optional, Annotated, List
from fastapi import Depends, Form, Path
from pydantic import Field, EmailStr, validator
from src.config.dto import BaseDTO


class ChatLogDTO(BaseDTO):
    chat_session_id: str
    chat_content: dict
    chat_date: datetime
    chat_status: bool
    student_email: str
