from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str


    class Config:
        from_attributes = True