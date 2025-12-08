from fastapi import APIRouter, HTTPException
import duckdb
from datetime import datetime
from ..core.dependencies import get_db_connection

router = APIRouter(prefix="/view", tags=["Analytics & Dashboard"])

@router.get("/kpis-gerais")
def get_kpis_gerais():
    """
    Retorna os indicadores macro: Total valor, Qtd Notas, Ticket Médio e % Fraude.
    Ideal para os 'Cards' no topo do dashboard.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                COUNT(*) as total_duplicatas,
                COALESCE(SUM(valor), 0) as valor_total_movimentado,
                COALESCE(AVG(valor), 0) as ticket_medio,
                ROUND(CAST(SUM(CASE WHEN label_fraude = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as taxa_fraude_percentual
            FROM duplicatas
        """
        result = conn.execute(query).fetchone()
        
        return {
            "total_docs": result[0],
            "valor_total": result[1],
            "ticket_medio": round(result[2], 2),
            "taxa_fraude": result[3]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/top-cedentes")
def get_top_cedentes(limit: int = 5):
    """
    Retorna os Cedentes que mais operam e o risco associado a eles.
    Ideal para Tabela ou Gráfico de Barras Horizontais.
    """
    conn = get_db_connection()
    try:
        query = f"""
            SELECT 
                nome_cedente,
                setor_cedente,
                COUNT(*) as qtd_operacoes,
                SUM(valor) as volume_total,
                SUM(label_fraude) as qtd_alertas_fraude
            FROM duplicatas
            GROUP BY nome_cedente, setor_cedente
            ORDER BY volume_total DESC
            LIMIT {limit}
        """
        result = conn.execute(query).df()
        return result.to_dict(orient="records")
    finally:
        conn.close()

@router.get("/distribuicao-fraude")
def get_distribuicao_fraude():
    """
    Mostra quais tipos de fraude são mais comuns.
    Ideal para Gráfico de Pizza ou Donut.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                tipo_fraude,
                COUNT(*) as ocorrencias
            FROM duplicatas
            WHERE label_fraude = 1
            GROUP BY tipo_fraude
            ORDER BY ocorrencias DESC
        """
        result = conn.execute(query).df()
        return result.to_dict(orient="records")
    finally:
        conn.close()

@router.get("/fluxo-vencimento")
def get_fluxo_vencimento():
    """
    Previsão de fluxo de caixa (Cash Flow) baseado nos vencimentos futuros.
    Importante para saber quanto dinheiro 'deve' entrar por dia.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                data_vencimento,
                SUM(valor) as valor_a_vencer
            FROM duplicatas
            WHERE data_vencimento >= CURRENT_DATE
            GROUP BY data_vencimento
            ORDER BY data_vencimento ASC
            LIMIT 30
        """
        # Nota: Limitado a 30 dias para não pesar o JSON
        df = conn.execute(query).df()
        df['data_vencimento'] = df['data_vencimento'].dt.strftime('%Y-%m-%d')
        return df.to_dict(orient="records")
    finally:
        conn.close()