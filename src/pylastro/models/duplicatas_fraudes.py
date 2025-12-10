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

    cnpj_cedente: str
    estado_cedente: str
    setor_cedente: str

    cnpj_sacado: str
    estado_sacado: str
    setor_sacado: str

    aceite_sacado: bool
    endossatario: str | None = None

    data_emissao: str
    data_vencimento: str
    prazo_dias: int

    # label_fraude: int = Field(..., description="0 ou 1 indicando fraude real")
    # tipo_fraude_real: TipoFraudeEnum

# Payload POST (lista de duplicatas)
class DuplicatasPayload(BaseModel):
    duplicatas: List[DuplicataItem]
