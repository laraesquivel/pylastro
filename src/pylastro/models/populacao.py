from pydantic import BaseModel, Field
from typing import Optional, List


class StatusPopulacao(BaseModel):
    """Status da população do banco"""
    tabela_existe: bool
    total_registros: int
    total_fraudes: int
    percentual_fraudes: float
    pode_popular: bool
    mensagem: str

class ConfigPopulacao(BaseModel):
    """Configuração para popular o banco"""
    qtd_cedentes: int = Field(default=50, ge=1, le=500)
    qtd_sacados: int = Field(default=200, ge=1, le=1000)
    qtd_duplicatas: int = Field(default=1000, ge=100, le=50000)
    taxa_fraude: float = Field(default=0.15, ge=0.0, le=0.5)
    forcar_limpeza: bool = Field(default=False)

class ResultadoPopulacao(BaseModel):
    """Resultado da população"""
    status: str
    total_inserido: int
    total_fraudes: int
    tempo_execucao: float
    distribuicao_fraudes: dict
