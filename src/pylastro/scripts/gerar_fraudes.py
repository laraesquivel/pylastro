import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import date, timedelta

# --- CONFIGURAÇÕES ---
fake = Faker('pt_BR')
Faker.seed(42)
random.seed(42)

class FraudeInjector:
    def __init__(self, factory):
        self.factory = factory
        
        # Lista de entidades suspeitas para receber endosso (Fraude C)
        self.laranjas = [
            "Consultoria e Gestão Empresarial Ltda",
            "M.S. Apoio Administrativo",
            "João da Silva - CPF 123.456.789-00",
            "Padaria e Confeitaria do Bairro",
            "Holding Patrimonial X",
            "Associação de Moradores da Vila",
            "Lava Jato Rápido ME",
            "Maria Oliveira - CPF 987.654.321-00",
            "J.P. Consultoria Individual",
            "Bar e Mercearia Central"
        ]
        
        # Bancos legítimos para evitar em duplicidades
        self.bancos_legitimos = [
            "Banco do Brasil S.A.",
            "Itaú Unibanco S.A.",
            "Bradesco S.A.",
            "Santander Brasil S.A.",
            "Caixa Econômica Federal",
            "BTG Pactual S.A.",
            "Safra S.A.",
            "Banco Inter S.A."
        ]

    def criar_emissao_falsa(self):
        """
        FRAUDE A: Emissão de Duplicatas Falsas (Ghost Notes)
        Cenário: A empresa inventa uma venda para inflar números ou obter crédito.
        
        Sinais de Detecção:
        1. Valor Redondo: Números inventados tendem a ser redondos (10k, 50k, 100k)
        2. Sem Aceite do Sacado: O "comprador" não reconhece a dívida
        3. Produto genérico ou vago
        4. Data de emissão muito recente (urgência suspeita)
        """
        base = self.factory.gerar_transacao_normal()
        
        # Valores redondos e suspeitos
        valores_suspeitos = [10000.00, 20000.00, 25000.00, 50000.00, 
                            75000.00, 100000.00, 150000.00, 200000.00]
        base['valor'] = random.choice(valores_suspeitos)
        
        # Sacado não reconhece (sem aceite)
        base['aceite_sacado'] = False
        
        # Produto vago
        base['produto'] = random.choice([
            "Serviços Diversos",
            "Consultoria Geral",
            "Materiais Diversos",
            "Produtos Variados"
        ])
        
        # Emissão muito recente (0-7 dias)
        base['data_emissao'] = fake.date_between(start_date='-7d', end_date='today')
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "EMISSAO_FALSA"
        
        return base

    def criar_duplicidade(self, dataset_existente):
        """
        FRAUDE B: Duplicatas Duplicadas (Double Spending)
        Cenário: Mesma NF-e descontada em múltiplas instituições financeiras.
        
        Sinais de Detecção:
        1. MESMA chave de NF-e em múltiplos registros
        2. IDs de duplicata diferentes (tentativa de mascarar)
        3. Endossatários diferentes (bancos concorrentes)
        4. Datas de emissão/vencimento idênticas ou muito próximas
        """
        if not dataset_existente or len(dataset_existente) < 10:
            # Fallback: cria uma transação normal se não houver dados
            return self.factory.gerar_transacao_normal()
        
        # Escolhe uma vítima (duplicata legítima para clonar)
        vitima = random.choice(dataset_existente)
        
        # Cria um clone
        copia_fraude = vitima.copy()
        
        # Muda apenas o ID (para parecer documento novo)
        copia_fraude['id_duplicata'] = fake.uuid4()
        
        # MANTÉM a mesma chave_nfe (AQUI ESTÁ A FRAUDE!)
        # copia_fraude['chave_nfe'] já é igual ao original
        
        # Marca como fraude
        copia_fraude['label_fraude'] = 1
        copia_fraude['tipo_fraude'] = "DUPLICIDADE"
        
        return copia_fraude

    def criar_endosso_indevido(self):
        """
        FRAUDE C: Endosso Indevido / Desvio de Recursos
        Cenário: Duplicata endossada para entidade não-financeira (laranja).
        
        Sinais de Detecção:
        1. Endossatário é pessoa física ou empresa não-financeira
        2. Nome do endossatário não consta em lista de instituições reguladas
        3. Empresa pequena/informal recebendo duplicatas de grande valor
        """
        base = self.factory.gerar_transacao_normal()
        
        # Adiciona campo endossatário (se não existir na base)
        base['endossatario'] = random.choice(self.laranjas)
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "ENDOSSO_INDEVIDO"
        
        return base
    
    def criar_relacao_suspeita(self):
        """
        FRAUDE D: Relacionamento Circular / Empresas Coligadas
        Cenário: Cedente e sacado são do mesmo grupo econômico (inflação artificial).
        
        Sinais de Detecção:
        1. CNPJ com mesma raiz (8 primeiros dígitos)
        2. Endereço/Estado idêntico
        3. Mesmo setor de atuação (incomum em B2B)
        4. Volume/frequência anormal entre as mesmas empresas
        """
        base = self.factory.gerar_transacao_normal()
        
        # Força CNPJ similar (mesma raiz)
        cnpj_cedente = base['cnpj_cedente']
        raiz_cnpj = cnpj_cedente[:10]  # Pega os 8 dígitos + separadores
        novo_sufixo = f"{random.randint(1000, 9999)}-{random.randint(10, 99)}"
        base['cnpj_sacado'] = raiz_cnpj + novo_sufixo
        
        # Força mesmo estado
        base['estado_sacado'] = base['estado_cedente']
        
        # Valor alto (inflação artificial)
        base['valor'] = round(random.uniform(50000, 200000), 2)
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "RELACAO_CIRCULAR"
        
        return base
    
    def criar_vencimento_suspeito(self):
        """
        FRAUDE E: Vencimento Anômalo
        Cenário: Prazos muito curtos (urgência) ou muito longos (protelar).
        
        Sinais de Detecção:
        1. Prazo < 7 dias (urgência atípica)
        2. Prazo > 180 dias (alongamento suspeito)
        3. Vencimento já passou mas duplicata ainda está ativa
        """
        base = self.factory.gerar_transacao_normal()
        
        tipo_anomalia = random.choice(['curto', 'longo', 'vencida'])
        
        if tipo_anomalia == 'curto':
            # Prazo urgente (1-5 dias)
            prazo = random.randint(1, 5)
            base['data_vencimento'] = base['data_emissao'] + timedelta(days=prazo)
            base['prazo_dias'] = prazo
            
        elif tipo_anomalia == 'longo':
            # Prazo excessivo (200-365 dias)
            prazo = random.randint(200, 365)
            base['data_vencimento'] = base['data_emissao'] + timedelta(days=prazo)
            base['prazo_dias'] = prazo
            
        else:  # vencida
            # Vencimento no passado (já expirou)
            prazo = random.randint(30, 90)
            base['data_emissao'] = fake.date_between(start_date='-6m', end_date='-3m')
            base['data_vencimento'] = base['data_emissao'] + timedelta(days=prazo)
            base['prazo_dias'] = prazo
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "VENCIMENTO_ANOMALO"
        
        return base
    
    def criar_valor_incompativel(self):
        """
        FRAUDE F: Valor Incompatível com o Setor
        Cenário: Operação com valor muito acima/abaixo do padrão do setor.
        
        Sinais de Detecção:
        1. Valor extremamente alto para o tipo de negócio
        2. Setor incompatível (ex: padaria vendendo milhões)
        3. Produto não condiz com capacidade operacional
        """
        base = self.factory.gerar_transacao_normal()
        
        # Setores pequenos com valores gigantes
        setores_pequenos = ['Varejo', 'Serviços', 'Alimentos']
        if base['setor_cedente'] not in setores_pequenos:
            base['setor_cedente'] = random.choice(setores_pequenos)
        
        # Valor absurdamente alto
        base['valor'] = round(random.uniform(500000, 2000000), 2)
        
        # Produto incompatível
        base['produto'] = random.choice([
            "Equipamentos Hospitalares de Alta Complexidade",
            "Turbinas Aeronáuticas",
            "Usina de Energia Solar Industrial"
        ])
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "VALOR_INCOMPATIVEL"
        
        return base

    def contaminar_dataset(self, dataset, taxa_fraude=0.15):
        """
        Método orquestrador para injetar fraudes de forma balanceada.
        
        Args:
            dataset: Lista de duplicatas normais
            taxa_fraude: Percentual de fraudes (default 15%)
        
        Returns:
            Dataset contaminado com fraudes distribuídas
        """
        qtd_total = len(dataset)
        qtd_fraudes = int(qtd_total * taxa_fraude)
        
        print(f"📊 Dataset original: {qtd_total} registros")
        print(f"⚠️  Injetando {qtd_fraudes} fraudes ({taxa_fraude*100:.1f}%)")
        
        # Distribuição balanceada dos tipos de fraude
        tipos_fraude = ['A', 'B', 'C', 'D', 'E', 'F']
        fraudes_por_tipo = qtd_fraudes // len(tipos_fraude)
        resto = qtd_fraudes % len(tipos_fraude)
        
        contadores = {tipo: 0 for tipo in tipos_fraude}
        
        for _ in range(qtd_fraudes):
            tipo = random.choice(tipos_fraude)
            
            if tipo == 'A':
                dataset.append(self.criar_emissao_falsa())
                contadores['A'] += 1
            elif tipo == 'B':
                dataset.append(self.criar_duplicidade(dataset))
                contadores['B'] += 1
            elif tipo == 'C':
                dataset.append(self.criar_endosso_indevido())
                contadores['C'] += 1
            elif tipo == 'D':
                dataset.append(self.criar_relacao_suspeita())
                contadores['D'] += 1
            elif tipo == 'E':
                dataset.append(self.criar_vencimento_suspeito())
                contadores['E'] += 1
            elif tipo == 'F':
                dataset.append(self.criar_valor_incompativel())
                contadores['F'] += 1
        
        # Embaralha tudo
        random.shuffle(dataset)
        
        print(f"✅ Dataset final: {len(dataset)} registros")
        print(f"📈 Distribuição de fraudes:")
        print(f"   A - Emissão Falsa: {contadores['A']}")
        print(f"   B - Duplicidade: {contadores['B']}")
        print(f"   C - Endosso Indevido: {contadores['C']}")
        print(f"   D - Relação Circular: {contadores['D']}")
        print(f"   E - Vencimento Anômalo: {contadores['E']}")
        print(f"   F - Valor Incompatível: {contadores['F']}")
        
        return dataset