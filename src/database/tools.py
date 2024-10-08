"""
데이터베이스 세션 관리 도구 모듈
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
from typing import AsyncIterable, Callable, Any
from contextlib import asynccontextmanager
import logging
from src.database.models import Base


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class RDBTools:
    ''' 데이터베이스 세션 도구 모음 '''
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.session_factory = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        
    async def create_tables(self):
        ''' 테이블 생성 '''
        async with self.engine.begin() as conn:
            _logger.info('모델 메타 데이터에 기반하여 테이블 유무 확인 후, 생성')
            await conn.run_sync(Base.metadata.create_all)
    
    async def dispose_engine(self):
        ''' 엔진 종료 '''
        _logger.info('DB 연결 해제')
        await self.engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncIterable[AsyncSession]:
        ''' 데이터베이스 세션 가져오기 '''
        async with self.session_factory() as session:
            yield session

    @asynccontextmanager
    async def get_transaction_session(self) -> AsyncIterable[AsyncSession]:
        ''' 트랜잭션 세션 가져오기 '''
        async with self.session_factory.begin() as session:
            yield session

    def dao(self, transactional: bool = False, session_var_name: str = "session"):
        '''
        DAO 데코레이터 팩토리

        :param transactional: 트랜잭션 사용 여부
        :param session_var_name: 세션을 주입할 변수 이름
        '''

        def dao_decorator(original_function: Callable[..., Any]):
            ''' DAO 데코레이터 '''

            @wraps(original_function)
            async def wrapper(*args, **kwargs):
                get_session = self.get_transaction_session if transactional else self.get_session
                async with get_session() as session:
                    kwargs[session_var_name] = session
                    result = await original_function(*args, **kwargs)
                return result

            return wrapper

        return dao_decorator

    def inject_async(self) -> AsyncSession:
        ''' 
        비동기 세션 인스턴스 주입 
        :None 반환 후 @dao는 실제 인스턴스 주입
        '''
        pass