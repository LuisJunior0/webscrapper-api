from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from datetime import date, datetime

class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str


    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProdutosMonitoradosCreateSchema(BaseModel):
    nome_produto: str
    preco_alvo: Decimal
    data_limite_monitoramento: date

    class Config:
        from_attributes = True
