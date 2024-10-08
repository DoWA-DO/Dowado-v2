"""
커스텀 예외처리 확장 모듈
"""
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from src.config.status import ER
import logging


_logger = logging.getLogger(__name__)


def _error(err: Exception):
    ''' 입력된 예외 객체를 처리하여 로깅 정보를 반환 '''
    _logger.exception(err)
    return {"error": traceback.format_exc()}


def use(app: FastAPI):
    ''' 커스텀 예외 모듈 사용 '''
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        ''' HTTPException 예외에 대한 처리 '''
        status_code = exc.status_code
        result = {"message": exc.detail}
        result["detail"] = _error(exc)
        return JSONResponse(status_code=status_code, content=result)
                            

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        ''' 모든 예외에 대한 전역 처리 '''
        status_code = ER.INTERNAL_ERROR[0]
        result = {
            "message": ER.INTERNAL_ERROR[1]
        }
        result["detail"] = _error(exc)
        return JSONResponse(status_code=status_code, content=result)
