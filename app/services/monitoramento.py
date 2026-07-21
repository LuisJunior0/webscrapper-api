import logging
from app.models import ProdutoMonitorado, LinkProduto, StatusMonitoramento, HistoricoPreco
from app.database import SessionLocal
from app.scrappers.kabum import scrapper_kabum
from datetime import datetime, UTC

# Devolver log do erro
logger = logging.getLogger(__name__)

def atualizar_precos():
    print("Monitoramento em execução")
    # Abre e gerencia a sessão do DB manualmente para o scheduler, como não é uma rota FastAPI não é possivel usar o Depends
    with SessionLocal() as session:
        
        links_ativos = session.query(LinkProduto).filter(LinkProduto.status == StatusMonitoramento.ATIVO).all()

        for link in links_ativos:

            agora = datetime.now(UTC)
            
            # Caso o grupo seja alterado para PRECO_ATINGIDO os demais links ainda em memoria tambem serão, o if valida buscas desnecessárias.
            if link.status == StatusMonitoramento.ATIVO:
                try:
                    # "_" é usado para ignorar o nome_produto que é retornado da função scrapper_kabum
                    _, preco_produto = scrapper_kabum(link.url)
                except Exception as e:
                    logger.error(f"Erro ao capturar dados do link ID {link.id} ({link.url}): {e}")
                    continue
                
                link.ultimo_preco = preco_produto
                
                # Query para buscar o produto amarrado ao link percorrendo no for
                produto_monitorado = session.query(ProdutoMonitorado).filter(ProdutoMonitorado.id == link.produto_monitorado_id, ProdutoMonitorado.status == StatusMonitoramento.ATIVO).first()
                
                # Caso o preco_produto encontrado agora seja menor ou igual ao preco_alvo definido no grupo. Ele é atualizado para PRECO_ATINGIDO
                # validação de segurança com "and" para entrar apenas se ambas forem True
                if produto_monitorado and preco_produto <= produto_monitorado.preco_alvo:
                    produto_monitorado.status = StatusMonitoramento.PRECO_ATINGIDO
                    produto_monitorado.motivo_encerramento = "Preco alvo do atingido"
                    produto_monitorado.data_encerramento = agora
                    
                    # Query para buscar os links ativos pertencentes ao grupo com status alterado
                    # Utiliza update para salvar os dados todos de uma vez direto no banco de dados, alterando diretamente em forma de lote (bulk). Otimização 
                    # A variavel links_ativos_do_grupo retorna agora o numero de links encontrados, podendo ser manipulado posteriormente. Ficou aqui apenas por padronização
                    links_ativos_do_grupo = session.query(LinkProduto).filter(
                    LinkProduto.status == StatusMonitoramento.ATIVO, 
                    LinkProduto.produto_monitorado_id == produto_monitorado.id).update(
                    {LinkProduto.status: StatusMonitoramento.PRECO_ATINGIDO, LinkProduto.motivo_encerramento: "Preco alvo do grupo atingido", LinkProduto.data_encerramento: agora})
                
                link.ultima_coleta = agora

                historico = HistoricoPreco(link_produto_id = link.id, preco = preco_produto, capturado_em = agora)

                session.add(historico)
        
        session.commit()
    print("Monitoramento finalizado com sucesso")