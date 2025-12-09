
from typing import Optional, List, Dict
from fastapi.encoders import jsonable_encoder
from ..service.detector_fraude import DetectorFraudeRatios
from ..domain.agente import AntiFraudeAgente
from ..models.duplicatas_fraudes import DuplicatasPayload

class SimularAlertaService:
    def __init__(self):
        self.antifraude = AntiFraudeAgente()
        self.resultados = []

    def alerta(self, payload: DuplicatasPayload):
        resultados = []
        
        for item in payload.duplicatas:
            # item é um DuplicataItem
            resultados.append(
                self.antifraude.analisar_caso(jsonable_encoder(item))
            )
        
        return resultados

