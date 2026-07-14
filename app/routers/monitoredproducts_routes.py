from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.models import ProdutoMonitorado, Usuario, StatusMonitoramento
from app.dependencies import pegar_sessao, get_current_user
from app.schemas import ProdutosMonitoradosCreateSchema
from datetime import date, datetime, UTC


monitoredProducts_router = APIRouter(tags=["Criação De Grupos de Produtos"])

@monitoredProducts_router.get("/produtos")
async def listar_produtos(current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    meus_produtos = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.user_id == current_user.id, ProdutoMonitorado.status != StatusMonitoramento.CANCELADO).all()

    return [
        {
        "nome_produto": produto.nome_produto,
        "preco_alvo": produto.preco_alvo,
        "data_limite_monitoramento": produto.data_limite_monitoramento,
        "status": produto.status,
        "id": produto.id
        } 
        for produto in meus_produtos
    ]


@monitoredProducts_router.post("/criar_produto")
async def criar_produto(produtomonitoradocreateschema: ProdutosMonitoradosCreateSchema, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    
    produto_monitorado = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.nome_produto==produtomonitoradocreateschema.nome_produto, ProdutoMonitorado.user_id==current_user.id).first() 
    
    if produto_monitorado:
        # JA existe um produto_monitorado com esse nome
        raise HTTPException(
            status_code=400,
            detail="Você já possui um grupo de monitoramento com este nome."
    )

    if produtomonitoradocreateschema.data_limite_monitoramento <=date.today():
        raise HTTPException(
            status_code=400,
            detail="A data limite deve ser futura."
    )

    novo_produto = ProdutoMonitorado(nome_produto = produtomonitoradocreateschema.nome_produto, preco_alvo = produtomonitoradocreateschema.preco_alvo, data_limite_monitoramento = produtomonitoradocreateschema.data_limite_monitoramento, user_id = current_user.id)
    session.add(novo_produto)
    session.commit()
    session.refresh(novo_produto)
    return {
        "nome_produto": novo_produto.nome_produto,
        "preco_alvo": novo_produto.preco_alvo,
        "data_limite_monitoramento": novo_produto.data_limite_monitoramento
    }

@monitoredProducts_router.patch("/produtos/{id}/cancelar")
async def cancelar_produtos(id: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    
    produto_cancelado = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.user_id==current_user.id, ProdutoMonitorado.id == id).first() 

    if not produto_cancelado:
        raise HTTPException(
        status_code=404,
        detail="Produto Não Encontrado"
    )
    produto_cancelado.status = StatusMonitoramento.CANCELADO
    produto_cancelado.motivo_encerramento = "Cancelado pelo usuario"
    produto_cancelado.data_encerramento = datetime.now(UTC)
    
    dados_produto_cancelado = {
        "nome_produto": produto_cancelado.nome_produto,
        "preco_alvo": produto_cancelado.preco_alvo,
        "data_limite_monitoramento": produto_cancelado.data_limite_monitoramento,
        "status": produto_cancelado.status,
        "motivo_encerramento": produto_cancelado.motivo_encerramento,
        "data_encerramento": produto_cancelado.data_encerramento, 
        "id": produto_cancelado.id
    }
        
    session.commit()
    session.refresh(produto_cancelado)

    return dados_produto_cancelado