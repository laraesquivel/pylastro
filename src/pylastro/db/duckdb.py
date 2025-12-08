from typing import List
from pathlib import Path
from datetime import datetime
import duckdb
import pandas as pd

class DuckDBManager:
    """Gerenciador de conexão e operações com DuckDB"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    
    def get_connection(self):
        """Retorna conexão com o DuckDB"""
        return duckdb.connect(self.db_path)
    
    def tabela_existe(self) -> bool:
        """Verifica se a tabela duplicatas existe"""
        conn = self.get_connection()
        try:
            result = conn.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = 'duplicatas'
            """).fetchone()
            return result[0] > 0
        finally:
            conn.close()
    
    def contar_registros(self) -> int:
        """Conta total de registros"""
        if not self.tabela_existe():
            return 0
        
        conn = self.get_connection()
        try:
            result = conn.execute("SELECT COUNT(*) FROM duplicatas").fetchone()
            return result[0]
        finally:
            conn.close()
    
    def contar_fraudes(self) -> int:
        """Conta total de fraudes"""
        if not self.tabela_existe():
            return 0
        
        conn = self.get_connection()
        try:
            result = conn.execute("""
                SELECT COUNT(*) 
                FROM duplicatas 
                WHERE label_fraude = 1
            """).fetchone()
            return result[0]
        finally:
            conn.close()
    
    def limpar_tabela(self):
        """Remove a tabela duplicatas"""
        conn = self.get_connection()
        try:
            conn.execute("DROP TABLE IF EXISTS duplicatas")
            conn.commit()
        finally:
            conn.close()
    
    def criar_tabela(self):
        """Cria a estrutura da tabela duplicatas"""
        conn = self.get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS duplicatas (
                    id_duplicata VARCHAR PRIMARY KEY,
                    chave_nfe VARCHAR,
                    data_emissao DATE,
                    data_vencimento DATE,
                    prazo_dias INTEGER,
                    id_cedente VARCHAR,
                    nome_cedente VARCHAR,
                    cnpj_cedente VARCHAR,
                    estado_cedente VARCHAR,
                    setor_cedente VARCHAR,
                    id_sacado VARCHAR,
                    nome_sacado VARCHAR,
                    cnpj_sacado VARCHAR,
                    estado_sacado VARCHAR,
                    setor_sacado VARCHAR,
                    produto VARCHAR,
                    valor DECIMAL(18,2),
                    aceite_sacado BOOLEAN,
                    endossatario VARCHAR,
                    label_fraude INTEGER,
                    tipo_fraude VARCHAR,
                    data_insercao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Cria índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chave_nfe ON duplicatas(chave_nfe)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_label_fraude ON duplicatas(label_fraude)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cedente ON duplicatas(id_cedente)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sacado ON duplicatas(id_sacado)")
            
            conn.commit()
        finally:
            conn.close()
    
    def inserir_lote(self, duplicatas: List[dict]):
        """Insere um lote de duplicatas"""
        if not duplicatas:
            return
        
        df = pd.DataFrame(duplicatas)
        
        # Garante que a coluna endossatario existe
        if 'endossatario' not in df.columns:
            df['endossatario'] = None
        
        df['data_insercao'] = datetime.now()
        
        conn = self.get_connection()
        try:
            conn.register('lote',df)
            conn.execute("INSERT INTO duplicatas BY NAME SELECT * FROM lote")
            conn.commit()
        finally:
            conn.close()
