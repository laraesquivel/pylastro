import requests
import pandas as pd

class MockAPIEmpresas:
    def __init__(self):
        self.api_url = "http://localhost:8000/mocks/intituicoes"

    def _carregar_entidades(self, cache=None):
            """
            Carrega lista de entidades autorizadas (bancos e instituições financeiras).
            
            Prioridade:
            1. Cache local (se fornecido)
            2. API externa (se api_url configurada)
            3. Lista vazia (modo degradado)
            """
            if cache:
                print("📦 Usando cache local de entidades")
                return self._processar_entidades(cache)
            
            if self.api_url:
                try:
                    print(f"🌐 Buscando entidades autorizadas em: {self.api_url}")
                    response = requests.get(self.api_url, timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    return self._processar_entidades(data)
                except Exception as e:
                    print(f"⚠️ Erro ao buscar API: {e}")
                    print("   Modo degradado: usando detecção por keywords")
                    return {'instituicoes_financeiras': set(), 'modo': 'fallback'}
            
            print("⚠️ Sem API configurada. Detecção por keywords ativa.")
            return {'instituicoes_financeiras': set(), 'modo': 'fallback'}
    

    def _processar_entidades(self, data):
            """
            Processa JSON da API e separa instituições financeiras das demais.
            
            Returns:
                Dict com sets de nomes autorizados por tipo
            """
            if 'entidades' not in data:
                return {'instituicoes_financeiras': set(), 'modo': 'fallback'}
            
            instituicoes_financeiras = set()
            entidades_suspeitas = set()
            
            for entidade in data['entidades']:
                nome = entidade['nome_exato']
                tipo = entidade['tipo_instituicao'].lower()
                
                # Classifica como instituição financeira
                if any(keyword in tipo for keyword in [
                    'instituição financeira', 
                    'banco', 
                    'financeira'
                ]):
                    instituicoes_financeiras.add(nome)
                else:
                    entidades_suspeitas.add(nome)
            
            print(f"   ✅ {len(instituicoes_financeiras)} instituições financeiras registradas")
            print(f"   ⚠️  {len(entidades_suspeitas)} entidades não-financeiras detectadas")
            
            return {
                'instituicoes_financeiras': instituicoes_financeiras,
                'entidades_suspeitas': entidades_suspeitas,
                'modo': 'api'
            }
