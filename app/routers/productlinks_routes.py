from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.models import Usuario, StatusMonitoramento, LinkProduto, ProdutoMonitorado, HistoricoPreco
from app.dependencies import pegar_sessao, get_current_user
from app.schemas import LinkProdutoCreateSchema, LinkProdutoUpdateSchema
from datetime import date, datetime, UTC
from app.scrappers.kabum import scrapper_kabum


productlinks_router = APIRouter(tags=["CRUD De Links de Produtos"])

@productlinks_router.post("/produtos/{produto_monitorado_id}/links")
async def criar_link(produto_monitorado_id: int, linkprodutocreateschema: LinkProdutoCreateSchema, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    produto = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == produto_monitorado_id, ProdutoMonitorado.user_id == current_user.id).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Nenhum grupo de produto encontrado."
    )

    if produto.status == StatusMonitoramento.CANCELADO:
        raise HTTPException(
            status_code=400,
            detail="Não é possível adicionar links a um grupo cancelado."
        )
    
    link_existente = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == produto_monitorado_id, LinkProduto.url == linkprodutocreateschema.url, LinkProduto.status == StatusMonitoramento.ATIVO).first() 

    if link_existente:
        # JA existe um link com essa url
        raise HTTPException(
            status_code=400,
            detail="Você já possui um link para esta Loja"
    )

    novo_link = LinkProduto(produto_monitorado_id = produto_monitorado_id, nome_loja = linkprodutocreateschema.nome_loja, url = linkprodutocreateschema.url)

    #Caso falhe, levanta um erro de captura de dados
    try:
        #Roda o scrapper e fornece os dados (MPV possui apenas Kabum)
        nome_produto, preco_produto = scrapper_kabum(novo_link.url)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível capturar os dados da URL."
        )
    novo_link.nome_produto = nome_produto
    novo_link.ultimo_preco = preco_produto
    novo_link.ultima_coleta = datetime.now(UTC)
    
    session.add(novo_link)
    session.flush() #Flush gera um ID no banco antes mesmo de comitar, para ser usado no novo_link.id de historico

    historico_de_precos = HistoricoPreco(link_produto_id = novo_link.id, preco = preco_produto, capturado_em = datetime.now(UTC))
    session.add(historico_de_precos)
    
    session.commit()
    session.refresh(novo_link)

    return {
        "nome_loja": novo_link.nome_loja,
        "url": novo_link.url,
        "link_id": novo_link.id,
        "nome_produto": novo_link.nome_produto,
        "ultimo_preco": novo_link.ultimo_preco,
        "ultima_coleta": novo_link.ultima_coleta,
        "status": novo_link.status
    }

@productlinks_router.get("/produtos/{produto_monitorado_id}/links")
async def listar_link(produto_monitorado_id: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    produto = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == produto_monitorado_id, ProdutoMonitorado.user_id == current_user.id).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Nenhum grupo de produto encontrado."
    )

    links_existentes = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == produto_monitorado_id, LinkProduto.status != StatusMonitoramento.CANCELADO).all()
    return [
        {
        "nome_loja": link.nome_loja,
        "url": link.url,
        "data_inicio": link.data_de_inicio,
        "status": link.status,
        "ultimo_preco": link.ultimo_preco,
        "ultima_coleta": link.ultima_coleta,
        "group_id":link.produto_monitorado_id,
        "id": link.id
        } 
        for link in links_existentes
    ]

@productlinks_router.patch("/produtos/{produto_monitorado_id}/links/{link_id}/cancelar")
async def cancelar_link(produto_monitorado_id: int, link_id: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):
    
    produto = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == produto_monitorado_id, ProdutoMonitorado.user_id == current_user.id).first()
    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Nenhum grupo de produto encontrado."
    )
    
    link_cancelado = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == produto_monitorado_id, LinkProduto.id == link_id, LinkProduto.status != StatusMonitoramento.CANCELADO).first()

    if not link_cancelado:
        raise HTTPException(
            status_code=404,
            detail="Link não encontrado."
        )

    link_cancelado.status = StatusMonitoramento.CANCELADO
    link_cancelado.motivo_encerramento = "Cancelado pelo usuario"
    link_cancelado.data_encerramento = datetime.now(UTC)

    dados_link_cancelado = {
        "nome_loja": link_cancelado.nome_loja,
        "url": link_cancelado.url,
        "data_inicio": link_cancelado.data_de_inicio,
        "status": link_cancelado.status,
        "ultimo_preco": link_cancelado.ultimo_preco,
        "data_encerramento": link_cancelado.data_encerramento, 
        "id": link_cancelado.id
    }
        
    session.commit()
    session.refresh(link_cancelado)

    return dados_link_cancelado

    
@productlinks_router.patch("/produtos/{produto_monitorado_id}/links/{link_id}")
async def editar_link(produto_monitorado_id: int, link_id: int, linkprodutoupdateschema: LinkProdutoUpdateSchema, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    produto = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == produto_monitorado_id, ProdutoMonitorado.user_id == current_user.id).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Nenhum grupo de produto encontrado."
    )
    
    link_editado = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == produto_monitorado_id, LinkProduto.id == link_id, LinkProduto.status != StatusMonitoramento.CANCELADO).first()

    if not link_editado:
        raise HTTPException(
            status_code=404,
            detail="Link não encontrado."
        )

    if linkprodutoupdateschema.nome_loja is not None:
        link_editado.nome_loja = linkprodutoupdateschema.nome_loja
    
    if linkprodutoupdateschema.url is not None:

        url_existente = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == produto_monitorado_id, LinkProduto.url == linkprodutoupdateschema.url, LinkProduto.id != link_id).first()

        if url_existente:
            raise HTTPException(
            status_code=400,
            detail="Já existe um link com essa URL neste grupo."
        )

        link_editado.url = linkprodutoupdateschema.url

    session.commit()
    session.refresh(link_editado)

    dados_link_editado = {
        "nome_loja": link_editado.nome_loja,
        "url": link_editado.url,
        "data_inicio": link_editado.data_de_inicio,
        "status": link_editado.status,
        "ultimo_preco": link_editado.ultimo_preco,
        "data_encerramento": link_editado.data_encerramento, 
        "id": link_editado.id
    }

    return dados_link_editado

@productlinks_router.get("/produtos/{produto_monitorado_id}/links/{link_id}/historico")
async def listar_historico(produto_monitorado_id: int, link_id: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    produto = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == produto_monitorado_id, ProdutoMonitorado.user_id == current_user.id).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Nenhum grupo de produto encontrado."
    )

    links_existentes = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == produto_monitorado_id, LinkProduto.status != StatusMonitoramento.CANCELADO).all()

    if not links_existentes:
        raise HTTPException(
            status_code=404,
            detail="Nenhum link encontrado"
        )
    
    link_do_grupo = session.query(LinkProduto).filter(LinkProduto.produto_monitorado_id == produto_monitorado_id, LinkProduto.id == link_id,  LinkProduto.status != StatusMonitoramento.CANCELADO).first()

    if not link_do_grupo:
        raise HTTPException(
            status_code=404,
            detail="Nenhum link encontrado no grupo atual"
        )
    
    historicos = session.query(HistoricoPreco).filter(HistoricoPreco.link_produto_id == link_id).all()

    if not historicos:
        raise HTTPException(
            status_code=404,
            detail="Nenhum historico disponivel encontrado"
        )
    
    return [
        {
        "preco": historico.preco,
        "capturado_em": historico.capturado_em
        
        }
        for historico in historicos
    ]