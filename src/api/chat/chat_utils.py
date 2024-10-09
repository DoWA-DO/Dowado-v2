import openai
import redis
import uuid
import pickle
from typing import NewType
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_huggingface import HuggingFaceEndpoint, HuggingFacePipeline
from langchain_postgres.vectorstores import PGVector
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import settings
from src.database.session import DATABASE_URL
from src.api.chat.chat_constants import contextualize_q_prompt, qa_prompt
# from src.config import chat_tokenizer, chat_model # hf
# from src.config import chat_model, chat_tokenizer
import os
import logging
from langchain_teddynote import logging as lang_logging
_logger = logging.getLogger(__name__)
redis_client = redis.Redis.from_url(settings.Idx.REDIS_URL)
lang_logging.langsmith("dowado-chat")


'''
초기 설정
'''
class ChatBase:
    def __init__(self):
        self._SIMILARITY_THRESHOLD = 0.15
        # self._llm = chat_model
        self._llm = ChatOpenAI(
            model       = settings.Idx.model_name, 
            temperature = settings.Idx.temperature,
        )
        self.vector_store_I = self._init_vector_store("job_info_docs")
        self.retriever_I = self._init_retriever(self.vector_store_I, settings.Idx.retriever_I_search_type)
        self.chain = self._init_jobinfo_chain()
    
    
    # 허깅페이스 임베딩으로 바꿔야함
    def _init_vector_store(self, collection_name: str):
        ''' Vector Store 초기화 '''
        _embeddings = OpenAIEmbeddings(model = settings.Idx.embed_model)
        vector_store = PGVector(
            connection = DATABASE_URL,                        # 벡터 DB 주소
            embeddings = _embeddings,                         # 임베딩 함수
            # embedding_length = settings.Idx.embedding_length, # 임베딩 벡터 길이 제약,
            collection_name = collection_name,                # 벡터스토어 컬렉션 이름(=그룹명)
            distance_strategy = "cosine",                     # 유사도 측정 기준, l2, cosine, inner
            pre_delete_collection = False,                    # 테스트 시 True -> 기존 컬렉션 삭제
            use_jsonb = True,                                 # json보다 성능 좋음     
        )
        return vector_store


    # QI 케이스 구분완료
    def _init_retriever(self, vector_store, search_type: str, search_kwargs: Optional[Dict] = None):
        ''' Retriever 초기화 '''
        
        if search_kwargs is None:
            search_kwargs = {}
        
        if search_type == "similarity":
            return vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
        elif search_type == "mmr":
            search_kwargs.setdefault('lambda_mult', 0.5)
            search_kwargs.setdefault('fetch_k', 20)
            return vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
        elif search_type == "similarity_score_threshold":
            search_kwargs.setdefault('score_threshold', self._SIMILARITY_THRESHOLD)
            return vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
        else:
            raise ValueError(f"Invalid search type: {search_type}")
    
    # job info
    def _init_jobinfo_chain(self):
        ''' chain 초기화
        create_stuff_documents_chain : 문서 목록을 가져와서 모두 프롬프트로 포맷한 다음 해당 프롬프트를 LLM에 전달합니다.
        create_history_aware_retriever : 대화 기록을 가져온 다음 이를 사용하여 검색 쿼리를 생성하고 이를 기본 리트리버에 전달
        create_retrieval_chain : 사용자 문의를 받아 리트리버로 전달하여 관련 문서를 가져옵니다. 그런 다음 해당 문서(및 원본 입력)는 LLM으로 전달되어 응답을 생성
        '''
        
        # 유저 질문 문맥화  
        history_aware_retriever = create_history_aware_retriever(
            self._llm, self.retriever_I, contextualize_q_prompt
        )       
        # 응답 생성 + 프롬프트 엔지니어링
        qa_chain = create_stuff_documents_chain(self._llm, qa_prompt)
        jobinfo_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

        _logger.info("=>> jobinfo chain 초기화 완료")
        return jobinfo_chain        


'''
채팅 생성
'''
class ChatGenerator:
    def __init__(self, chat_base: ChatBase, session_id: str = None):
        self.chat_base = chat_base
        self.session_id = session_id or self.create_session_id()
        
    @classmethod
    def create_session_id(self):
        ''' 새로운 채팅 세션 생성, 객체 생성 없이 호출 가능 '''
        session_id = str(uuid.uuid4())
        _logger.info(f"=>> 새로운 세션 ID 생성 : {session_id}")
        return session_id
    
    def get_session_id(self):
        ''' 현재 객체의 session_id 반환 '''
        return self.session_id

    def generate_query(self, input_query: str) -> str:
        ''' 챗봇에게 쿼리 전송 '''
        def get_session_history(session_id: str) -> RedisChatMessageHistory:
            return RedisChatMessageHistory(session_id=session_id, url=settings.Idx.REDIS_URL)

        conversational_rag_chain = RunnableWithMessageHistory(
            self.chat_base.chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        response = conversational_rag_chain.invoke(
            {"input": input_query},
            config={"configurable": {"session_id": self.session_id}}
        )

        # redis에 채팅기록 저장
        self.create_message_to_redis({"query": input_query, "response": response["answer"]})
        
        _logger.info(f'[응답 생성] 실제 모델 응답: response => \n{response}\n')
        _logger.info(f"[응답 생성] 세션 ID [{self.session_id}]에서 답변을 생성했습니다.")
        return response["answer"]


    # 유틸리티
    def create_message_to_redis(self, message):
        ''' Redis에 메시지 저장 '''
        chat_history_key = f"chat_history:{self.session_id}"
        redis_client.rpush(chat_history_key, pickle.dumps(message))
    
    # 유틸리티
    def get_chatlog_from_redis(self, num_turns: int = 10) -> list:
        ''' Redis에서 현재 객체의 session_id에 해당하는 채팅 로그 가져오기 '''
        chat_history_key = f"chat_history:{self.session_id}"
        chat_log = redis_client.lrange(chat_history_key, -num_turns, -1) # redis에서 최근 10개 기록 가져오기
        _logger.info(f'=>> Redis에서 불러온 채팅기록 : {chat_log}')
        if not chat_log:
            _logger.warning(f'채팅 기록이 비어 있습니다: {self.session_id}')
        return [pickle.loads(log) for log in chat_log]          # 역직렬화된 채팅 로그 항목들의 리스트를 반환
    
                

chatbot_instances: Dict[str, ChatGenerator] = {}
def init_chatbot_instance():
    ''' ChatBase에 기반한 챗봇 객체 생성 '''
    chat_base = ChatBase()
    new_chatbot_instance = ChatGenerator(chat_base)
    session_id = new_chatbot_instance.session_id
    chatbot_instances[session_id] = new_chatbot_instance
    _logger.info(f'=>> ChatBot 객체 생성 : {new_chatbot_instance} for session_id: {session_id}')
    return session_id
