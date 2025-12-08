from pathlib import Path
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .scripts.gerar_dados import DuplicataFactory
from .scripts.popular_banco_automatico import popular_banco_automatico
from .models.populacao import ConfigPopulacao
from .core.config import DB_PATH
from .core.dependencies import get_db_manager

Path("data").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("\n🚀 Iniciando API de Duplicatas...")
    print(f"📁 Banco de dados: {DB_PATH}")

    config = ConfigPopulacao(
        qtd_cedentes=50,
        qtd_sacados=200,
        qtd_duplicatas=5000,
        taxa_fraude=0.15,
        forcar_limpeza=False
    )

    # Inicialização assincrona em background
    asyncio.create_task(popular_banco_automatico(config, get_db_manager()))

    # Aqui a API fica ativa
    yield

    # Evento de encerramento (opcional)
    print("🛑 Encerrando aplicação...")

app = FastAPI(
    title="API de Duplicatas com Detecção de Fraude",
    description="Sistema assíncrono para geração e análise de duplicatas",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "API de Geração e Detecção de Fraudes em Duplicatas",
        "version": "2.0.0",
        "endpoints": {
            "/status": "Verifica status do banco de dados",
            "/popular": "Popula o banco com dados sintéticos (manual)",
            "/limpar": "Limpa todos os dados do banco",
            "/estatisticas": "Estatísticas gerais do dataset",
            "/fraudes": "Lista todas as fraudes detectadas",
            "/docs": "Documentação interativa"
        }
    }