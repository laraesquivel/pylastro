import pandas as pd
import duckdb


class Analises:
    def __init__(self,conn, table_name="duplicatas"):
        self.conn = conn
        self.table_name = table_name

    def estatistica_basicas(self):
        df = self.conn.execute("""
            SELECT 
                COUNT(*) AS n,
                AVG(valor) AS avg_valor,
                STDDEV(valor) AS std_valor,
                MIN(valor) AS min_valor,
                MAX(valor) AS max_valor
            FROM duplicatas
        """).df()
        return df

    def outliers_zscore(self):
        df = self.conn.execute("""
                SELECT *,
                    (valor - AVG(valor) OVER()) / STDDEV(valor) OVER() AS zscore
                FROM duplicatas
                ORDER BY zscore DESC
                LIMIT 10
            """).df()
        return df
        
    def prazos_curtos(self):
        df = self.conn.execute("""
                SELECT *
                FROM duplicatas
                WHERE prazo_dias < 7 OR prazo_dias > 180
                LIMIT 10
            """).df()
        
        return df
        
    def duplicidade_chavenfe(self):
        df = self.conn.execute("""
                SELECT chave_nfe, COUNT(*) qtd
                FROM duplicatas
                GROUP BY chave_nfe
                HAVING COUNT(*) > 1
                ORDER BY qtd DESC
                LIMIT 10
            """).df()
        
        return df
        
    def raiz_cnpj(self):
        df = self.conn.execute("""
                SELECT *
                FROM duplicatas
                WHERE substr(cnpj_cedente, 1, 8) = substr(cnpj_sacado, 1, 8)
                LIMIT 10
            """).df()
        
        return df
    