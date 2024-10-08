"""
레포트 생성 관련 RAG 설정 및 유틸리티
"""
import openai
import redis
import uuid
import pickle
from typing import NewType
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import settings
from src.database.session import DATABASE_URL
# from src.api.report.report_constnats import 
import logging


_logger = logging.getLogger(__name__)
openai.api_key = settings.general.OPENAI_API_KEY


