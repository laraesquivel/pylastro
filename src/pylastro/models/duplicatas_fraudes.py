from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class ClassificacaoEnum(str, Enum):
    CRITICO = "CRÍTICO"
    ALTO = "ALTO"
    MEDIO = "MÉDIO"
    BAIXO = "BAIXO"


class TipoFraudeEnum(str, Enum):
    EMISSAO_FALSA = "EMISSAO_FALSA"
    DUPLICIDADE = "DUPLICIDADE"
    ENDOSSO_INDEVIDO = "ENDOSSO_INDEVIDO"
    RELACAO_CIRCULAR = "RELACAO_CIRCULAR"
    VENCIMENTO_ANOMALO = "VENCIMENTO_ANOMALO"
    VALOR_INCOMPATIVEL = "VALOR_INCOMPATIVEL"


class DuplicataItem(BaseModel):
    id_duplicata: UUID
    risk_score: float
    classificacao: ClassificacaoEnum
    valor: float
    cedente: str
    sacado: str
    motivos: List[str]
    # label_real: int = Field(..., description="0 ou 1")
    # tipo_fraude_real: TipoFraudeEnum


# Payload POST (lista de duplicatas)
class DuplicatasPayload(BaseModel):
    duplicatas: List[DuplicataItem]
