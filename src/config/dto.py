""" 
애플리케이션의 모든 DTO(데이터 전송 객체)에 대한 부모 DTO
"""
from pydantic import BaseModel # 데이터 검증 및 직렬화 처리 관련 모듈


class BaseDTO(BaseModel):   
    class Config:
        from_attributes = True # ORM 객체의 속성들이 pydantic 모델의 필드로 자동 매핑됨.
        use_enum_values = True # pydantic 모델이 Enum 클래스의 값을 사용할 때, Enum의 이름 대신 실제 값을 사용
        protected_namespaces = ('model_',)