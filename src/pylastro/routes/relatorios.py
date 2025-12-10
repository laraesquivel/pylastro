import requests
import random
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from ..core.dependencies import get_db_connection
from ..service.detector_fraude import DetectorFraudeService
from ..service.simular_alerta import SimularAlertaService
from ..models.duplicatas_fraudes import DuplicatasPayload, DuplicataItem

router = APIRouter(prefix="/relatorios", tags=["Analytics & Fraudes"])

@router.get("/fraudes")
def get_fraudes(n_itens : int = 20):
    conn = get_db_connection()
    try:
        query = """SELECT * FROM duplicatas"""
        resultado = conn.execute(query).df()
        service = DetectorFraudeService(resultado)
        return service.executar(n_itens)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simular_alerta_bi")
def post_simular_alerta_bi(payload : DuplicatasPayload ):
    try:
        service= SimularAlertaService()
        resultado = service.alerta(payload)
        return jsonable_encoder(resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simular_pipeline")
def simular_pipeline():
    try:
        response = requests.get("http://localhost:8000/relatorios/fraudes?n_itens=10")
        data = response.json()

        suspeito = random.choice(data['top_suspeitos'])

        # Remove campos que não devem ir para a LLM
        suspeito.pop("label_fraude", None)
        suspeito.pop("tipo_fraude_real", None)

        duplicata_item = DuplicataItem(**suspeito)

        payload = DuplicatasPayload(duplicatas=[duplicata_item])

        service = SimularAlertaService()
        resultado = service.alerta(payload)

        return jsonable_encoder(resultado)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


