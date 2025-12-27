from pydantic import BaseModel

class RequestCreate(BaseModel):
    applianceType: str
    applianceModel: str
    problemDescryption: str

    class Config:
        orm_mode = True