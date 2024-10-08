"""
라우터 확장 모듈
"""
from fastapi import APIRouter
from src.core import DowaDOAPI
import logging


_logger = logging.getLogger(__name__)

def use(app: DowaDOAPI, base: str):
    ''' 라우터 확장 모듈 추가 '''
    api_router = APIRouter()
    for router in app.load_controller(base):
        _logger.info(f"=>> 모든 라우터가 추가되었습니다: {router.prefix}")
        api_router.include_router(router)
    app.include_router(api_router)