"""
core : FastAPI 애플리케이션의 구성을 확장, 커스터마이징한 모듈 모음
"""
"""
FastAPI 라우터 확장 모듈
"""
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional
from fastapi import APIRouter, FastAPI
import logging

_logger = logging.getLogger(__name__)


class DowaDOAPI(FastAPI):
    
    def __init__(self, **kwargs):
        ''' kwargs에 'disable_api_doc'이 지정되어 있으면 API 문서 비활성화 '''
        if kwargs.get('disable_api_doc', None):
            kwargs.update({"redoc_url": None, "docs_url": None})
        super().__init__(**kwargs)
        _logger.info("=>> DowaDOAPI 인스턴스 생성")
        
    
    def _get_module_name(self, path: Path) -> str:
        ''' 파일 경로로부터 모듈 이름 생성('src/api/auth/auth_control.py' -> 'src.api.auth.auth_control') '''
        paths = []
        if path.name != '__init__.py':
            paths.append(path.stem)
        while True:
            path = path.parent
            if not path or not path.is_dir():
                break

            inits = [f for f in path.iterdir() if f.name == '__init__.py']
            if not inits:
                break

            paths.append(path.stem)

        module_name = '.'.join(reversed(paths))
        _logger.info(f"=>> 파일 경로로부터 라우터 이름 생성 : {module_name}")
        return module_name
    
    
    def _load_module(self, module_name: str, attr_name: str) -> Optional[APIRouter]:
        ''' 모듈 동적 임포트, 로드 '''
        _logger.info(f"=>> 라우터 로드 중 -> module_name : {module_name}, attr_name : {attr_name}")
        module = __import__(module_name, fromlist=[attr_name])
        return getattr(module, attr_name, None)

    
    def use(self, extend, *args, **kwargs):
        """ 외부 확장 모듈 사용 """
        extend.use(self, *args, **kwargs)
    
        
    def load_controller(self, base: str):
        ''' 특정 패턴을 가진 파일들 안에서 라우터(APIRouter)를 동적으로 로드 '''
        for f in Path(base).glob("**/*_control.py"):
            module_name = self._get_module_name(f)
            _logger.info(f"=>> 발견한 라우터(로드 대상) : {module_name}")
            router = self._load_module(module_name, "router")
            if router:
                yield router
    
    
    def aop(self, fn: Optional[Callable[..., Any]] = None):
        """
        AOP 데코레이터 팩토리
        :param fn:
        """

        def aop_decorator(original_function):
            """AOP Decorator"""

            @wraps(original_function)
            async def wrapper(*args, **kwargs):
                if fn:
                    return await fn(original_function, *args, **kwargs)
                else:
                    return await original_function(*args, **kwargs)
            return wrapper
        
        return aop_decorator

_logger.info("core 모듈 로드 완료")