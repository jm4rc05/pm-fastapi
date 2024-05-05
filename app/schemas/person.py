from pydantic import BaseModel


class Person(Base):
    class Config:
        orm_mode = True

    id: int
    name: str
    title: str
