import random
from datetime import date, date
import pandas as pd
import numpy as np
import faker

# Configuração
fake = faker.Faker('pt_BR')
faker.Faker.seed(42)
random.seed(42)

QTD_TRANSACOES = 10000
ARQUIVO_SAIDA = "duplicatas_simuladas.csv"

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
            setor = random.choice(list(SETORES_PRODUTOS.keys()))
            self.cedentes.append({
                "id": faker.uuid4(),
                "razao_social": faker.company(),
                "cnpj": faker.cnpj(),
                "estado": random.choice(ESTADOS_BR),
                "setor": setor,
                "tipo": "Cedente"
            })

        for _ in range(qtd_sacados):
            setor = random.choice(list(SETORES_PRODUTOS.keys()))
            self.sacados.append({
                "id": faker.uuid4(),
                "razao_social": faker.company(),
                "cnpj": faker.cnpj(),
                "estado": random.choice(ESTADOS_BR),
                "setor": setor,
                "tipo": "Sacado"
            })

    def gerar_transacao_normal(self):
        """Gera uma duplicata saudável (sem fraude)"""
        cedente = random.choice(self.cedentes)
        
        # Lógica de match: 80% das vezes, setores correlatos compram entre si
        if random.random() < 0.8:
            sacados_compativeis = [s for s in self.sacados if s['setor'] == cedente['setor'] or s['setor'] == 'Varejo Geral']
            if not sacados_compativeis: sacados_compativeis = self.sacados
            sacado = random.choice(sacados_compativeis)
        else:
            sacado = random.choice(self.sacados)

        produto = random.choice(SETORES_PRODUTOS[cedente['setor']])
        
        # Datas
        dt_emissao = faker.date_between(start_date='-6m', end_date='today')
        prazo = random.choice([30, 45, 60, 90])
        dt_vencimento = dt_emissao + timedelta(days=prazo)

        # Valores realistas
        preco_base = random.uniform(1000, 10000)
        valor_nota = round(preco_base * random.uniform(0.9, 1.1), 2)

        return {
            "id_duplicata": faker.uuid4(),
            "chave_nfe": self._gerar_chave_nfe(cedente['estado'], dt_emissao),
            "data_emissao": dt_emissao,
            "data_vencimento": dt_vencimento,
            "prazo_dias": prazo,
            # Cedente
            "id_cedente": cedente['id'],
            "nome_cedente": cedente['razao_social'],
            "cnpj_cedente": cedente['cnpj'],
            "estado_cedente": cedente['estado'],
            "setor_cedente": cedente['setor'],
            # Sacado
            "id_sacado": sacado['id'],
            "nome_sacado": sacado['razao_social'],
            "cnpj_sacado": sacado['cnpj'],
            "estado_sacado": sacado['estado'],
            "setor_sacado": sacado['setor'],
            # Lastro
            "produto": produto,
            "valor": valor_nota,
            # Regulatório
            "aceite_sacado": True, # Normal ter aceite
            "label_fraude": 0,
            "tipo_fraude": "Nenhuma"
        }

    def gerar_fraudes(self, dataset_atual):
        """Injeta casos específicos de fraude para testar o validador"""
        fraudes = []
        
        # --- CASO 1: FRAUDE DE VALOR (Math Check) ---
        # Um vendedor pequeno tenta passar uma nota milionária
        base = dataset_atual[0].copy()
        base['id_duplicata'] = faker.uuid4()
        base['valor'] = 450000.00 # Valor absurdo
        base['chave_nfe'] = self._gerar_chave_nfe(base['estado_cedente'], base['data_emissao'])
        base['label_fraude'] = 1
        base['tipo_fraude'] = "VALOR_EXCESSIVO"
        fraudes.append(base)

        # --- CASO 2: INCOERÊNCIA DE LASTRO (Semantic Check) ---
        # Padaria comprando Cimento
        cedente_cons = next(c for c in self.cedentes if c['setor'] == 'Construção Civil')
        sacado_alim = next(s for s in self.sacados if s['setor'] == 'Alimentos e Bebidas')
        
        fraude_semantica = {
            **self.gerar_transacao_normal(), # Herda estrutura base
            "id_cedente": cedente_cons['id'],
            "nome_cedente": cedente_cons['razao_social'],
            "setor_cedente": "Construção Civil",
            "id_sacado": sacado_alim['id'],
            "nome_sacado": "Padaria do João Ltda", # Forcei um nome óbvio
            "setor_sacado": "Alimentos e Bebidas",
            "produto": "Betoneira", # Padaria comprando Betoneira
            "valor": 5000.00,
            "label_fraude": 1,
            "tipo_fraude": "INCOERENCIA_LASTRO"
        }
        fraudes.append(fraude_semantica)

        # --- CASO 3: RISCO LOGÍSTICO (Geo Check) ---
        # Tijolo viajando do Acre para São Paulo
        cedente_ac = self.cedentes[0].copy()
        cedente_ac['estado'] = 'AC'
        sacado_sp = self.sacados[0].copy()
        sacado_sp['estado'] = 'SP'
        
        fraude_log = {
            **self.gerar_transacao_normal(),
            "estado_cedente": "AC",
            "nome_cedente": "Olaria Rio Branco",
            "estado_sacado": "SP",
            "nome_sacado": "Construtora Paulista",
            "produto": "Milheiro de Tijolo", # Pesado e barato
            "valor": 2000.00,
            "label_fraude": 1,
            "tipo_fraude": "RISCO_LOGISTICO"
        }
        fraudes.append(fraude_log)

        return fraudes
