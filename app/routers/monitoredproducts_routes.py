from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.models import ProdutoMonitorado, Usuario, StatusMonitoramento, LinkProduto
from app.dependencies import pegar_sessao, get_current_user
from app.schemas import ProdutosMonitoradosCreateSchema, ProdutosMonitoradosUpdateSchema
from datetime import date, datetime, UTC


monitoredProducts_router = APIRouter(tags=["CRUD De Grupos de Produtos"])


@monitoredProducts_router.post("/produtos")
async def criar_produto(produtomonitoradocreateschema: ProdutosMonitoradosCreateSchema, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    
    produto_monitorado = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.nome_produto==produtomonitoradocreateschema.nome_produto, ProdutoMonitorado.user_id==current_user.id, ProdutoMonitorado.status != StatusMonitoramento.CANCELADO).first() 
    
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


@monitoredProducts_router.get("/produtos")
async def listar_produtos(current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    
    meus_produtos = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.user_id == current_user.id, ProdutoMonitorado.status != StatusMonitoramento.CANCELADO).all()

    total_links_ativos = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == current_user.id, LinkProduto.status != StatusMonitoramento.CANCELADO).count()

    return [
        {
        "nome_produto": produto.nome_produto,
        "preco_alvo": produto.preco_alvo,
        "data_limite_monitoramento": produto.data_limite_monitoramento,
        "status": produto.status,
        "links_ativos": total_links_ativos,
        "id": produto.id
        } 
        for produto in meus_produtos
    ]

@monitoredProducts_router.patch("/produtos/{id}/cancelar")
async def cancelar_produtos(id: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    
    produto_cancelado = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.user_id==current_user.id, ProdutoMonitorado.id == id).first() 

    if not produto_cancelado:
        raise HTTPException(
        status_code=404,
        detail="Produto Não Encontrado"
    )

    if produto_cancelado.status == StatusMonitoramento.CANCELADO:
        raise HTTPException(
            status_code=400,
            detail="Produto já está cancelado."
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

@monitoredProducts_router.patch("/produtos/{produto_monitorado_id}")
async def editar_produto(produtosmonitoradosppdateschema: ProdutosMonitoradosUpdateSchema, produto_monitorado_id: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    
    produto = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == produto_monitorado_id, ProdutoMonitorado.user_id == current_user.id).first()
    
    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Nenhum grupo de produto encontrado."
    )

    produto_editado = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == produto_monitorado_id, ProdutoMonitorado.user_id == current_user.id).first()

    if produto_editado.status == StatusMonitoramento.CANCELADO:
        raise HTTPException(
            status_code=404,
            detail="Esse produto ja foi cancelado."
        )
    
    if produtosmonitoradosppdateschema.nome_produto is not None:

        nome_produto_existente = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.user_id == current_user.id, ProdutoMonitorado.nome_produto == produtosmonitoradosppdateschema.nome_produto, ProdutoMonitorado.id != produto_monitorado_id).first()
        
        if nome_produto_existente:
            raise HTTPException(
            status_code=400,
            detail="Ja existe um produto com esse nome cadastrado."
        )

        produto_editado.nome_produto = produtosmonitoradosppdateschema.nome_produto

    if produtosmonitoradosppdateschema.preco_alvo is not None:
        produto_editado.preco_alvo = produtosmonitoradosppdateschema.preco_alvo

    if produtosmonitoradosppdateschema.data_limite_monitoramento is not None:
        
        if produtosmonitoradosppdateschema.data_limite_monitoramento <= date.today():
            raise HTTPException(
            status_code=400,
            detail="A data limite deve ser futura."
        )
 
        produto_editado.data_limite_monitoramento = produtosmonitoradosppdateschema.data_limite_monitoramento

    session.commit()
    session.refresh(produto_editado)

    dados_produto_editado = {
        "nome_produto": produto_editado.nome_produto,
        "preco_alvo": produto_editado.preco_alvo,
        "data_limite_monitoramento": produto_editado.data_limite_monitoramento,
        "status": produto_editado.status,
        "motivo_encerramento": produto_editado.motivo_encerramento,
        "data_encerramento": produto_editado.data_encerramento, 
        "id": produto_editado.id
    }

    return dados_produto_editado

