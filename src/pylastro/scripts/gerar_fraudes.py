import random
from datetime import timedelta
import faker
from ..core.config import SETORES, SUPRIMENTOS

class FraudeInjector:
    def __init__(self, factory: DuplicataFactory):
        self.factory = factory
        # Acesso aos dados da factory para manipular
        self.fake = fake 

    def _pegar_empresa_por_setor(self, lista_empresas, setor_alvo):
        """Helper para encontrar uma empresa de um setor específico"""
        candidatos = [e for e in lista_empresas if e['setor'] == setor_alvo]
        if not candidatos:
            # Fallback se não achar: pega qualquer uma e força o setor (sujo, mas funciona pro teste)
            empresa = random.choice(lista_empresas).copy()
            empresa['setor'] = setor_alvo
            return empresa
        return random.choice(candidatos)

    def criar_fraude_valor_excessivo(self):
        """
        CENÁRIO: Lavagem de dinheiro ou erro de digitação.
        Uma transação com valor 50x a 100x maior que a média do mercado.
        """
        base = self.factory.gerar_transacao_normal()
        
        # A Mágica: Multiplica o valor absurdamente
        fator_multiplicacao = random.randint(50, 100)
        base['valor'] = round(base['valor'] * fator_multiplicacao, 2)
        
        # Metadados para gabarito
        base['label_fraude'] = 1
        base['tipo_fraude'] = "VALOR_EXCESSIVO"
        
        return base

    def criar_fraude_incoerencia_lastro(self):
        """
        CENÁRIO: Incoerência Semântica Baseada na Matriz de Suprimentos.
        O script busca o 'Inverso' da matriz de vendas válidas.
        """
        # 1. Tenta achar um vendedor que NÃO venda para todos os setores
        # (Porque se pegarmos Tecnologia, ela vende pra todo mundo, aí não dá pra gerar fraude de lastro fácil)
        while True:
            cedente = random.choice(self.factory.cedentes)
            setor_cedente = cedente['setor']
            
            # Quem pode comprar desse cara?
            setores_permitidos = SUPRIMENTOS.get(setor_cedente, [])
            
            # Quem são TODOS os setores possíveis?
            todos_setores = list(SETORES.keys())
            
            # A diferença entre TODOS e os PERMITIDOS são os PROIBIDOS
            setores_proibidos = [s for s in todos_setores if s not in setores_permitidos]
            
            # Se a lista de proibidos não for vazia, achamos nosso candidato a fraudador
            if setores_proibidos:
                break
        
        # 2. Escolhe um setor proibido aleatório (Ex: Farmacêutico para Construção)
        setor_vitima = random.choice(setores_proibidos)
        
        # 3. Pega uma empresa desse setor proibido
        sacado = self._pegar_empresa_por_setor(self.factory.sacados, setor_vitima)
        
        # 4. Pega um produto do vendedor (Ex: Cimento)
        produto_incoerente = random.choice(SETORES[setor_cedente])
        
        # 5. Monta a transação fraudulenta
        base = self.factory.gerar_transacao_normal()
        
        base['id_cedente'] = cedente['id']
        base['nome_cedente'] = cedente['razao_social']
        base['cnpj_cedente'] = cedente['cnpj']
        base['setor_cedente'] = setor_cedente
        base['estado_cedente'] = cedente['estado']
        
        base['id_sacado'] = sacado['id']
        base['nome_sacado'] = sacado['razao_social']
        base['cnpj_sacado'] = sacado['cnpj']
        base['setor_sacado'] = sacado['setor'] # Ex: Farmácia
        base['estado_sacado'] = sacado['estado']
        
        base['produto'] = produto_incoerente # Ex: Cimento
        
        # Valor aleatório, mas realista
        base['valor'] = round(random.uniform(2000, 15000), 2)
        
        # Regenera a chave para bater com o estado do cedente
        base['chave_nfe'] = self.factory._gerar_chave_nfe(cedente['estado'], base['data_emissao'])
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "INCOERENCIA_LASTRO"
        
        return base

    def criar_fraude_logistica(self):
        """
        CENÁRIO: Nota viajante inviável.
        Produto barato e pesado viajando do AC para SP. O frete custaria mais que o produto.
        """
        base = self.factory.gerar_transacao_normal()
        
        # Força a geografia impossível
        base['estado_cedente'] = 'AC'
        base['estado_sacado'] = 'SP'
        base['produto'] = 'Milheiro de Tijolo'
        base['valor'] = 1200.00 # Valor baixo
        
        # Regenera a chave pois mudamos o estado do emissor
        base['chave_nfe'] = self.factory._gerar_chave_nfe('AC', base['data_emissao'])
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "RISCO_LOGISTICO"
        
        return base

    def criar_fraude_data(self):
        """
        CENÁRIO: Erro cronológico grosseiro.
        Vencimento acontece ANTES da emissão.
        """
        base = self.factory.gerar_transacao_normal()
        
        # Inverte as datas
        base['data_vencimento'] = base['data_emissao'] - timedelta(days=5)
        
        base['label_fraude'] = 1
        base['tipo_fraude'] = "DATA_INCONSISTENTE"
        
        return base

    def contaminar_lote(self, dataset, qtd_fraudes=50):
        """
        Método orquestrador que injeta as fraudes no meio dos dados bons.
        """
        print(f"⚠️ Injetando {qtd_fraudes} registros fraudulentos...")
        
        funcoes_fraude = [
            self.criar_fraude_valor_excessivo,
            self.criar_fraude_incoerencia_lastro,
            self.criar_fraude_logistica,
            self.criar_fraude_data
        ]
        
        for _ in range(qtd_fraudes):
            # Escolhe um tipo de fraude aleatório
            funcao_escolhida = random.choice(funcoes_fraude)
            transacao_suja = funcao_escolhida()
            dataset.append(transacao_suja)
            
        random.shuffle(dataset) # Mistura tudo para ficar difícil
        return dataset