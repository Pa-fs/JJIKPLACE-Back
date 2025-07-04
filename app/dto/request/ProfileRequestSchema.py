from pydantic import BaseModel, constr


class NicknameUpdateRequest(BaseModel):
    nickname: constr(min_length=2, max_length=10)


class PasswordChangeRequest(BaseModel):
    new_password: constr(min_length=4)
    new_password_check: str