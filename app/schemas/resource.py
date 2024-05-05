from pydantic import BaseModel


class Resource(Base):
    class Config:
        orm_mode = True

    id: int
    name: str
    description: str
