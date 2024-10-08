"""
메인 서버 모듈
"""
from src.core import DowaDOAPI
from src.core import cors, error, event, router
from fastapi.openapi.utils import get_openapi
import logging


logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

app = DowaDOAPI(**{
    "title" : "Do:WADO API Server",
    "description" : "Do:WADO 청소년 AI 진로 추천 서비스",
    "version" : "0.1",
    "docs_url" : "/docs",
    "redoc_url" : "/redoc",
})

# 확장 모듈 등록
app.use(cors)
app.use(error)
app.use(router, base="./src/api")
app.use(event)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Do:WADO API Server",
        version="0.1",
        description="Do:WADO 청소년 AI 진로 추천 서비스",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {
                        "student": "Access as student",
                        "teacher": "Access as teacher",
                    }
                }
            }
        }
    }
    # openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi



_logger.info('=>> 서버 시작 중...')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8080, reload=True)