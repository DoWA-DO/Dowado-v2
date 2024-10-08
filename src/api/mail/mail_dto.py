from typing import Annotated, Union
from pydantic import BaseModel, EmailStr, Field

class EmailRequest(BaseModel):
    to_email: Annotated[Union[EmailStr, None], Field(description="메일")]
