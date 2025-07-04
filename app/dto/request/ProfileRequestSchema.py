from pydantic import BaseModel, constr


class NicknameUpdateRequest(BaseModel):
    nickname: constr(min_length=2, max_length=10)