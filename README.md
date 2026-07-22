# 🚀 WebScraper API - Monitor de Preços Automatizado

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![JWT](https://img.shields.io/badge/JWT-Authentication-black)
![APScheduler](https://img.shields.io/badge/APScheduler-Task%20Scheduler-success)

## 📌 Sobre o Projeto

O **WebScraper API** é uma aplicação backend desenvolvida para automatizar o monitoramento de preços de produtos em e-commerces.

O sistema permite que usuários autenticados criem grupos de monitoramento, definam preços-alvo, adicionem links de produtos e acompanhem automaticamente a evolução dos preços ao longo do tempo.

Além do monitoramento contínuo, a aplicação executa verificações agendadas periodicamente, registrando históricos de preço e encerrando monitoramentos automaticamente quando uma meta é atingida ou o prazo definido expira.

O projeto foi desenvolvido seguindo princípios de modularização, separação de responsabilidades e persistência de dados utilizando PostgreSQL, Docker e SQLAlchemy.

---

# ✨ Principais Funcionalidades

### 🔐 Autenticação e Controle de Acesso

* Cadastro de usuários
* Login utilizando JWT (OAuth2 Password Flow)
* Rotas protegidas por autenticação
* Controle de acesso baseado no usuário autenticado

### 📦 Grupos de Produtos Monitorados

* Criação de grupos de monitoramento
* Definição de preço-alvo
* Definição de prazo máximo de monitoramento
* Cancelamento manual de monitoramentos
* Atualização automática de status

### 🔗 Gerenciamento de Links

* Cadastro de links de produtos
* Edição de links monitorados
* Cancelamento individual de links
* Validação de duplicidade de URLs

### 🕷️ Web Scraping

* Coleta automática de:

  * Nome do produto
  * Preço atual
* Captura inicial no momento do cadastro
* Arquitetura preparada para múltiplos scrapers

### 📈 Histórico de Preços

* Registro de todas as coletas realizadas
* Consulta do histórico completo por produto
* Persistência de preços para análise futura

### ⏰ Monitoramento Automatizado

* Scheduler executado em background via APScheduler
* Atualização automática de preços
* Registro de histórico periódico
* Encerramento automático quando:

  * Preço alvo é atingido
  * Prazo de monitoramento expira

### 🐳 Docker

* API containerizada
* Banco PostgreSQL containerizado
* Scheduler containerizado
* Ambiente reproduzível em qualquer máquina

---

# 🏗️ Arquitetura do Projeto

```text
WEBSCRAPPER/
├── alembic/                  # Scripts de migrations do banco
│   └── versions/             # Histórico de alterações do schema
│
├── app/
│   ├── routers/              # Endpoints da API
│   │   ├── auth_routes.py
│   │   ├── monitoredproducts_routes.py
│   │   └── productlinks_routes.py
│   │
│   ├── scheduler/            # Tarefas agendadas
│   │   └── scheduler.py
│   │
│   ├── scrappers/            # Web Scrapers por loja
│   │   └── kabum.py
│   │
│   ├── services/             # Regras de negócio
│   │   └── monitoramento.py
│   │
│   ├── database.py           # Conexão com banco
│   ├── dependencies.py       # Dependências FastAPI
│   ├── main.py               # Entrada da aplicação
│   ├── models.py             # Entidades SQLAlchemy
│   └── schemas.py            # Schemas Pydantic
│
├── .dockerignore
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── requirements.txt
```

---

# 🛠️ Tecnologias Utilizadas

## Backend

* Python 3.12
* FastAPI
* SQLAlchemy
* Pydantic

## Banco de Dados

* PostgreSQL
* SQLite (ambiente de desenvolvimento/testes)

## Migrações

* Alembic

## Web Scraping

* Requests
* BeautifulSoup4

## Segurança

* JWT
* OAuth2 Password Flow

## Agendamento

* APScheduler

## Infraestrutura

* Docker
* Docker Compose

---

# 📊 Fluxo do Monitoramento

```text
Usuário cria grupo
        ↓
Usuário adiciona link
        ↓
Scraper coleta preço inicial
        ↓
Preço salvo no banco
        ↓
Histórico inicial criado
        ↓
Scheduler executa periodicamente
        ↓
Nova coleta realizada
        ↓
Histórico atualizado
        ↓
Verifica regras de negócio
        ↓
Preço atingido?
        ↓
Sim → Encerrar monitoramento

ou

Prazo expirou?
        ↓
Sim → Encerrar monitoramento
```

---

# ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`.

Exemplo:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=webscraperapi

SECRET_KEY=sua_chave_super_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

# 🐳 Executando com Docker

## 1. Clonar o repositório

```bash
git clone https://github.com/LuisJunior0/webscrapper-api.git

cd webscrapper-api
```

---

## 2. Configurar variáveis de ambiente

Crie o arquivo:

```bash
.env
```

Baseando-se no:

```bash
.env.example
```

---

## 3. Subir os containers

```bash
docker compose up -d --build
```

Containers iniciados:

* PostgreSQL
* FastAPI
* Scheduler APScheduler

---

## 4. Verificar containers

```bash
docker ps
```

Exemplo:

```text
postgres_webscrapper_db
fastapi_webscrapper_api
webscrapper_scheduler
```

---

## 5. Acessar a API

```text
http://localhost:8000
```

---

# 📖 Documentação da API

Após iniciar a aplicação:

### Swagger UI

```text
http://localhost:8000/docs
```

Interface interativa para testes de endpoints.

### ReDoc

```text
http://localhost:8000/redoc
```

Documentação alternativa gerada automaticamente pelo FastAPI.

---

# 🧠 Regras de Negócio Implementadas

### Status do Monitoramento

* ATIVO
* PRECO_ATINGIDO
* EXPIRADO
* CANCELADO

### Encerramento Automático

O monitoramento é encerrado automaticamente quando:

* O preço coletado é menor ou igual ao preço-alvo definido.
* A data limite de monitoramento é atingida.

Ao encerrar:

* O grupo é atualizado.
* Todos os links vinculados ao grupo são encerrados.
* O motivo de encerramento é registrado.

---

# 📈 Possíveis Evoluções

* Suporte para múltiplos e-commerces
* Notificações por e-mail
* Notificações via Telegram
* Dashboard administrativo
* Métricas e gráficos de preços
* Cache distribuído com Redis
* Testes automatizados com Pytest
* Deploy em AWS, Railway ou Render
* Integração com Playwright para páginas dinâmicas

---

# 👨‍💻 Autor

Desenvolvido por **Luis Junior** como projeto de estudo focado em:

* Backend com Python
* FastAPI
* SQLAlchemy
* Docker
* Web Scraping
* Automação e Monitoramento de Dados

---

## 📄 Licença

Este projeto está disponível para fins educacionais e de aprendizado.
