
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from ..core.dependencies import get_db_connection
from ..service.detector_fraude import DetectorFraudeService
from ..service.simular_alerta import SimularAlertaService
from ..models.duplicatas_fraudes import DuplicatasPayload

router = APIRouter(prefix="/relatorios", tags=["Analytics & Fraudes"])

@router.get("/fraudes")
def get_fraudes(n_itens : int = 20):
    conn = get_db_connection()
    try:
        query = """SELECT * FROM duplicatas"""
        resultado = conn.execute(query).df()
        service = DetectorFraudeService(resultado)
        return service.executar()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simular_alerta_bi")
def get_simular_alerta_bi(payload : DuplicatasPayload ):
    try:
        service= SimularAlertaService()
        print("oi")
        resultado = service.alerta(payload)
        print('oioi')
        return jsonable_encoder(resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))