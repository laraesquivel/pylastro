import random
from datetime import date, timedelta
import pandas as pd
import numpy as np
import faker
from ..core.config import SETORES, ESTADOS, SUPRIMENTOS


# Configuração
fake = faker.Faker('pt_BR')
faker.Faker.seed(42)
random.seed(42)

class DuplicataFactory:
    def __init__(self):
        self.cedentes = []
        self.sacados = []
        self.data_hoje = date.today()

    def _gerar_chave_nfe(self, uf, data_emissao):
        """Simula uma chave de acesso de NF-e válida (44 dígitos)"""
        # Formato: UF(2) + AAMM(4) + CNPJ(14) + Mod(2) + Serie(3) + Num(9) + Random(9) + DV(1)
        aamm = data_emissao.strftime("%y%m")
        cod_uf = "35" # Simplificação
        random_part = str(random.randint(10000000000000000000, 99999999999999999999))
        chave = f"{cod_uf}{aamm}{random_part}"
        return chave[:44].ljust(44, '0')

    def gerar_carteira_empresas(self, qtd_cedentes=50, qtd_sacados=200):
        """Cria as empresas que farão parte do ecossistema"""
        print(f"🏭 Criando {qtd_cedentes} Cedentes e {qtd_sacados} Sacados...")
        
        for _ in range(qtd_cedentes):
            setor = random.choice(list(SETORES.keys()))
            self.cedentes.append({
                "id": faker.uuid4(),
                "razao_social": faker.company(),
                "cnpj": faker.cnpj(),
                "estado": random.choice(ESTADOS),
                "setor": setor,
                "tipo": "Cedente"
            })

        for _ in range(qtd_sacados):
            setor = random.choice(list(SETORES.keys()))
            self.sacados.append({
                "id": faker.uuid4(),
                "razao_social": faker.company(),
                "cnpj": faker.cnpj(),
                "estado": random.choice(ESTADOS),
                "setor": setor,
                "tipo": "Sacado"
            })

    def gerar_transacao_normal(self):
        """Gera uma duplicata saudável baseada na Matriz de Suprimentos"""
        cedente = random.choice(self.cedentes)
        setor_cedente = cedente['setor']
        
        # 1. Olha na matriz quem são os compradores válidos para esse vendedor
        setores_compradores_validos = self.MATRIZ_SUPRIMENTOS.get(setor_cedente, [])
        
        # 2. Filtra a lista de sacados para achar empresas desses setores
        sacados_candidatos = [
            s for s in self.sacados 
            if s['setor'] in setores_compradores_validos
        ]
        
        # Fallback: Se não achar ninguém específico (raro), pega qualquer um (exceção do mundo real)
        if not sacados_candidatos:
            sacado = random.choice(self.sacados)
        else:
            sacado = random.choice(sacados_candidatos)

        produto = random.choice(SETORES_PRODUTOS[cedente['setor']])
        
        # --- O RESTO DO CÓDIGO PERMANECE IGUAL ---
        dt_emissao = faker.date_between(start_date='-6m', end_date='today')
        prazo = random.choice([30, 45, 60, 90])
        dt_vencimento = dt_emissao + timedelta(days=prazo)
        
        preco_base = random.uniform(1000, 10000)
        valor_nota = round(preco_base * random.uniform(0.9, 1.1), 2)

        return {
            "id_duplicata": faker.uuid4(),
            "chave_nfe": self._gerar_chave_nfe(cedente['estado'], dt_emissao),
            "data_emissao": dt_emissao,
            "data_vencimento": dt_vencimento,
            "prazo_dias": prazo,
            "id_cedente": cedente['id'],
            "nome_cedente": cedente['razao_social'],
            "cnpj_cedente": cedente['cnpj'],
            "estado_cedente": cedente['estado'],
            "setor_cedente": cedente['setor'],
            "id_sacado": sacado['id'],
            "nome_sacado": sacado['razao_social'],
            "cnpj_sacado": sacado['cnpj'],
            "estado_sacado": sacado['estado'],
            "setor_sacado": sacado['setor'],
            "produto": produto,
            "valor": valor_nota,
            "aceite_sacado": True,
            "label_fraude": 0,
            "tipo_fraude": "Nenhuma"
        }
