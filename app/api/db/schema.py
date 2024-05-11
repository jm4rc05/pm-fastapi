from pydantic import BaseModel


class Person(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    title: str

class Resource(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    description: str
