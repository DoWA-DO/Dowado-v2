"""
애플리케이션 환경 설정 및 로깅 설정 모듈
"""
from typing import Optional, Tuple, TypeVar, Type
from pathlib import Path
import json
import logging
import logging.config
import os
import sys
from dataclasses import dataclass
import dacite
from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from typing import ClassVar
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, LlamaTokenizer, LlamaForCausalLM # BitsAndBytesConfig
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
import torch


# .env 파일에서 환경 변수 로드
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class GeneralSettings(BaseSettings):
    OPENAI_API_KEY: SecretStr = SecretStr(os.getenv("OPENAI_API_KEY"))
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    HUGGINGFACE_CHATMODEL_REPO_ID: str = "ormor/dowado_chat_model"
    DEBUG: bool = True
    API_DOC_VIEW: bool = True

class RDBSettings(BaseSettings):
    DB_PROTOCAL: str = os.getenv("DB_PROTOCAL")  # asyncpg | psycopg 이지만 psycopg3 사용(비동기가능/벡터DB+RDB) 
    DB_USERNAME: str = os.getenv("DB_USERNAME")
    DB_PASSWORD: SecretStr = SecretStr(os.getenv("DB_PASSWORD")) 
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")

    @property # 메서드를 클래스 속성처럼 사용 가능
    def DATABASE_URL(self) -> str:
        return f"{self.DB_PROTOCAL}://{self.DB_USERNAME}:{self.DB_PASSWORD.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

class JWTSettings(BaseSettings):
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") # secret key 생성 : openssl rand -hex 32
    JWT_ACCESS_TOKEN_EXPIRE_MIN: float = float(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MIN"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    # JWT_INV_ACCESS_EXPIRE_MIN: int = 1440
    # JWT_SESSION_EXPIRE_MIN: int = 30
    
class SMTPSettings(BaseSettings):
    NAVER_EMAIL_ADDRESS: str = os.getenv("NAVER_EMAIL_ADDRESS")
    NAVER_EMAIL_PASSWORD: str = os.getenv("NAVER_EMAIL_PASSWORD")
    
class IdxSettings(BaseSettings):
    model_name: str = "gpt-3.5-turbo-1106" # gpt-3.5-turbo gpt-4-turbo
    temperature: int = 0
    context_window: int = 4096 # 16385(3.5) 128000(4)
    output_token: int = 1024 # 4096
    chunk_overlap: int = 0
    chunk_size: int = 512
    embed_model: str = "text-embedding-ada-002" # "intfloat/e5-small"
    
    # 추가 옵션
    embedding_length: int = 512 # 768, 임베딩 벡터 길이 제약
    
    # search type : similarity(코사인유사도), mmr(mmr알고리즘, 다양성에 집중), similarity_score_threshold(유사도 기준값 지정 버전)
    retriever_Q_search_type: str = "mmr"
    retriever_I_search_type: str = "similarity"
    
    # Chat DB
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    

class Settings(BaseSettings):
    general: GeneralSettings = GeneralSettings()
    rdb: RDBSettings = RDBSettings()
    jwt: JWTSettings = JWTSettings()
    mail: SMTPSettings = SMTPSettings()
    Idx: IdxSettings = IdxSettings()
    
settings = Settings()

"""
로깅 설정
"""
def setup_logging():
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s:%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p", 
        level=logging.DEBUG if settings.general.DEBUG else logging.INFO
    )

    _logger = logging.getLogger(__name__)
    _logger.info("Config 로드 완료")



############
# 테스트용 임시
# hf = None
chat_model = None
chat_tokenizer = None
login(token=settings.general.HUGGINGFACEHUB_API_TOKEN)
os.environ["TRANSFORMERS_CACHE"] = "./cache/"
os.environ["HF_HOME"] = "./cache/"


def load_model():
    global chat_model, chat_tokenizer
    model_id = settings.general.HUGGINGFACE_CHATMODEL_REPO_ID
    
    # # 4bit 양자화를 사용하여 모델 로드
    # quantization_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_compute_dtype=torch.bfloat16
    # )
    
    
    device = torch.device('cpu')
    chat_tokenizer = LlamaTokenizer.from_pretrained(model_id)
    chat_model = LlamaForCausalLM.from_pretrained(model_id).to(device)
    
    # chat_model = AutoModelForCausalLM.from_pretrained(
    #     model_id, device_map="cpu",
    # )
    # chat_tokenizer = AutoTokenizer.from_pretrained(model_id)
    torch.set_default_tensor_type('torch.Float16Tensor')
    # quantization_config=quantization_config
    
    # pipe = pipeline(
    #     "text-generation", 
    #     model=chat_model, 
    #     tokenizer=chat_tokenizer,
    # )
    
    # hf = HuggingFacePipeline(pipeline=pipe)
    
    # hf = HuggingFacePipeline.from_model_id(
    #     model_id="ormor/dowado_chat_model",  
    #     task="text-generation",  
    #     pipeline_kwargs={"max_new_tokens": 512},
    # )
      
    logging.info(f"{model_id} 모델이 로드되었습니다.")