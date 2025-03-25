from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductSchema(BaseModel):
    id: int
    name: str
    description: str
    price: float

    class Config:
        orm_mode = True
