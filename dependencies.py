from app.database import SessionLocal
from sqlalchemy.orm import Session

# Criando uma dependencia para as rotas terem acesso ao DB.
def pegar_sessao():
    session = SessionLocal()
    try:
        # Yield permite entregar a sesão para a rota.
        # Após a rota terminar, o FastAPI retorna para esta função e executa o finally
        yield session
    
    finally:
        session.close()