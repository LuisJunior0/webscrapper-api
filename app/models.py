from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base  
from enum import Enum

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String, nullable=False)
    
    email = Column(String, unique=True, nullable=False)
    
    senha = Column(String, nullable=False)


class StatusMonitoramento(str, Enum):
    ATIVO = "ATIVO"
    PAUSADO = "PAUSADO"
    EXPIRADO = "EXPIRADO"
    PRECO_ATINGIDO = "PRECO_ATINGIDO"
    CANCELADO = "CANCELADO"

class ProdutoMonitorado(Base):
    __tablename__ = "produtos_monitorados"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column (Integer, ForeignKey("usuarios.id"), nullable=False)
    
    nome_produto = Column(String, nullable=False)
    
    preco_alvo = Column(Numeric(10, 2), nullable=False)

    status = Column(SQLEnum(StatusMonitoramento), nullable=False, default=StatusMonitoramento.ATIVO)

    data_de_inicio = Column(DateTime, server_default=func.now())

    motivo_encerramento = Column(String(255), nullable=True)

    data_final = Column(DateTime, nullable=True)

    ultima_execucao = Column(DateTime, nullable=True)

class LinkProduto(Base):
    __tablename__ = "links_produtos"

    id = Column(Integer, primary_key=True, index=True)

    produto_monitorado_id = Column (Integer, ForeignKey("produtos_monitorados.id"), nullable=False)

    nome_loja = Column(String(100), nullable=False)

    url = Column(String, nullable=False)

    status = Column(SQLEnum(StatusMonitoramento), nullable=False, default=StatusMonitoramento.ATIVO)

    data_de_inicio = Column(DateTime, server_default=func.now())

    ultimo_preco = Column(Numeric(10, 2), nullable=True)

    ultima_coleta = Column(DateTime, nullable=True)

class HistoricoPreco(Base):
    __tablename__ = "historicos_precos"

    id = Column(Integer, primary_key=True, index=True)

    link_produto_id = Column(Integer, ForeignKey("links_produtos.id"), nullable=False)

    preco = Column(Numeric(10, 2), nullable=False)

    capturado_em = Column(DateTime, server_default=func.now(), nullable=False)
