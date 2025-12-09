import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

class DetectorFraudeRatios:
    """
    Sistema de detecção de fraudes em duplicatas usando ratios financeiros.
    Simula a tarefa O*NET #3: Gerar ratios financeiros para avaliar status.
    
    IMPORTANTE: Este código NÃO usa o campo 'label_fraude' para detecção!
    Usa apenas análise estatística e ratios financeiros.
    """
    
    def __init__(self, df_duplicatas: pd.DataFrame):
        """
        Args:
            df_duplicatas: DataFrame com as duplicatas (COM ou SEM label_fraude)
        """
        self.df = df_duplicatas.copy()
        self.resultados = None

        
    def calcular_ratios_financeiros(self):
        """
        RATIO 1: Liquidez Implícita (Valor/Prazo)
        - Indica a "velocidade" do dinheiro
        - Valores muito altos = urgência suspeita
        - Valores muito baixos = alongamento suspeito
        """
        self.df['ratio_liquidez'] = self.df['valor'] / np.maximum(self.df['prazo_dias'], 1)
        
        """
        RATIO 2: Score de Valor Redondo
        - Fraudes tendem a usar valores "bonitos" (10k, 50k, 100k)
        - Score = 1 se termina em .00, caso contrário 0
        """
        self.df['is_valor_redondo'] = (self.df['valor'] % 1000 == 0).astype(int)
        
        """
        RATIO 3: Desvio de Valor por Setor
        - Compara valor com média do setor
        - Z-score alto = valor anômalo
        """
        sector_stats = self.df.groupby('setor_cedente')['valor'].agg(['mean', 'std'])
        self.df['valor_medio_setor'] = self.df['setor_cedente'].map(sector_stats['mean'])
        self.df['valor_std_setor'] = self.df['setor_cedente'].map(sector_stats['std'])
        self.df['zscore_valor'] = (
            (self.df['valor'] - self.df['valor_medio_setor']) / 
            np.maximum(self.df['valor_std_setor'], 1)
        )
        
        """
        RATIO 4: Frequência de Duplicidade (mesma chave_nfe)
        - Se chave_nfe aparece > 1 vez = possível double spending
        """
        chave_counts = self.df['chave_nfe'].value_counts()
        self.df['freq_chave_nfe'] = self.df['chave_nfe'].map(chave_counts)
        
        """
        RATIO 5: Relacionamento Circular (CNPJ similar)
        - Compara raiz do CNPJ (8 primeiros dígitos)
        """
        self.df['cnpj_cedente_raiz'] = self.df['cnpj_cedente'].str.replace(r'\D', '', regex=True).str[:8]
        self.df['cnpj_sacado_raiz'] = self.df['cnpj_sacado'].str.replace(r'\D', '', regex=True).str[:8]
        self.df['mesma_raiz_cnpj'] = (
            self.df['cnpj_cedente_raiz'] == self.df['cnpj_sacado_raiz']
        ).astype(int)

        """
        RATIO 5.5: Mesmo Estado (Cedente e Sacado)
        - Necessário para o RATIO 10
        """
        self.df['mesmo_estado'] = (
            self.df['estado_cedente'] == self.df['estado_sacado']
        ).astype(int)
        
        """
        RATIO 6: Prazo Anômalo
        - Muito curto (< 7 dias) ou muito longo (> 180 dias)
        """
        self.df['prazo_anomalo'] = (
            (self.df['prazo_dias'] < 7) | (self.df['prazo_dias'] > 180)
        ).astype(int)
        
        """
        RATIO 7: Taxa de Aceite
        - Sem aceite do sacado = red flag
        """
        self.df['sem_aceite'] = (~self.df['aceite_sacado']).astype(int)
        
        """
        RATIO 8: Endosso Não-Bancário
        - Se endossatário não é nulo e não é banco
        """
        bancos_keywords = ['Banco', 'S.A.', 'Unibanco', 'Bradesco', 'Itaú', 'Santander', 'BTG']
        self.df['endosso_suspeito'] = self.df['endossatario'].notna()
        # Remove bancos legítimos
        for keyword in bancos_keywords:
            self.df.loc[
                self.df['endossatario'].str.contains(keyword, case=False, na=False),
                'endosso_suspeito'
            ] = False
        self.df['endosso_suspeito'] = self.df['endosso_suspeito'].astype(int)
        
        """
        RATIO 9: Vencimento Expirado
        - Duplicata ainda ativa mas já vencida
        """
        self.df['data_vencimento'] = pd.to_datetime(self.df['data_vencimento'])
        hoje = pd.Timestamp.now()
        self.df['vencida'] = (self.df['data_vencimento'] < hoje).astype(int)
        
        """
        RATIO 10: Mesmo Estado Cedente/Sacado + Valor Alto
        - Pode indicar operação circular
        """
        threshold_alto = self.df['valor'].quantile(0.75)

        self.df['mesmo_estado_valor_alto'] = (
            (self.df['mesmo_estado'] == 1) & 
            (self.df['valor'] > threshold_alto)
        ).astype(int)
        return self.df
    
    def calcular_risk_score(self):
        """
        Risk Score Final: Soma ponderada dos ratios
        
        Cada indicador tem um peso baseado em severidade típica:
        - Duplicidade de chave (peso 3.0) = gravíssimo
        - Endosso suspeito (peso 2.5) = muito grave
        - CNPJ circular (peso 2.0) = grave
        - Valor anômalo (peso 1.5) = médio-grave
        - Demais (peso 1.0) = moderado
        """
        pesos = {
            'freq_chave_nfe': 3.0,      # Duplicidade
            'endosso_suspeito': 2.5,    # Endosso indevido
            'mesma_raiz_cnpj': 2.0,     # Relação circular
            'zscore_valor': 1.5,        # Valor anômalo
            'is_valor_redondo': 1.0,    # Valor redondo
            'prazo_anomalo': 1.0,       # Prazo suspeito
            'sem_aceite': 1.0,          # Sem aceite
            'vencida': 1.0,             # Vencimento
            'mesmo_estado_valor_alto': 1.0
        }
        
        # Normaliza z-score para [0,1]
        self.df['zscore_norm'] = np.clip(np.abs(self.df['zscore_valor']) / 3, 0, 1)
        
        # Normaliza frequência de chave (> 1 = suspeito)
        self.df['freq_norm'] = np.clip((self.df['freq_chave_nfe'] - 1), 0, 3)
        
        # Calcula score
        self.df['risk_score'] = (
            pesos['freq_chave_nfe'] * self.df['freq_norm'] +
            pesos['endosso_suspeito'] * self.df['endosso_suspeito'] +
            pesos['mesma_raiz_cnpj'] * self.df['mesma_raiz_cnpj'] +
            pesos['zscore_valor'] * self.df['zscore_norm'] +
            pesos['is_valor_redondo'] * self.df['is_valor_redondo'] +
            pesos['prazo_anomalo'] * self.df['prazo_anomalo'] +
            pesos['sem_aceite'] * self.df['sem_aceite'] +
            pesos['vencida'] * self.df['vencida'] +
            pesos['mesmo_estado_valor_alto'] * self.df['mesmo_estado_valor_alto']
        )
        
        # Classifica risco
        self.df['classificacao_risco'] = pd.cut(
            self.df['risk_score'],
            bins=[-np.inf, 1.0, 3.0, 5.0, np.inf],
            labels=['BAIXO', 'MODERADO', 'ALTO', 'CRÍTICO']
        )
        
        return self.df
    
    def gerar_relatorio(self, top_n=20):
        """
        Gera relatório dos casos mais suspeitos
        """
        # Ordena por risk_score
        suspeitos = self.df.nlargest(top_n, 'risk_score')
        
        relatorio = []
        for idx, row in suspeitos.iterrows():
            motivos = []
            
            if row['freq_chave_nfe'] > 1:
                motivos.append(f"⚠️ DUPLICIDADE: Chave NF-e aparece {int(row['freq_chave_nfe'])}x no sistema")
            
            if row['endosso_suspeito']:
                motivos.append(f"🚨 Endosso para entidade não-bancária: {row['endossatario']}")
            
            if row['mesma_raiz_cnpj']:
                motivos.append("🔄 Cedente e Sacado têm CNPJ com mesma raiz (grupo econômico?)")
            
            if abs(row['zscore_valor']) > 2:
                motivos.append(f"💰 Valor {abs(row['zscore_valor']):.1f} desvios-padrão acima da média do setor")
            
            if row['is_valor_redondo']:
                motivos.append(f"🎯 Valor redondo suspeito: R$ {row['valor']:,.2f}")
            
            if row['prazo_anomalo']:
                motivos.append(f"📅 Prazo anômalo: {int(row['prazo_dias'])} dias")
            
            if row['sem_aceite']:
                motivos.append("❌ Sacado não aceitou a duplicata")
            
            if row['vencida']:
                motivos.append("⏰ Duplicata vencida mas ainda ativa")
            
            if row['mesmo_estado_valor_alto']:
                motivos.append(f"🔄 Mesma UF ({row['estado_cedente']}) com valor alto: R$ {row['valor']:,.2f}")
            
            relatorio.append({
                'id_duplicata': row['id_duplicata'],
                'risk_score': row['risk_score'],
                'classificacao': row['classificacao_risco'],
                'valor': row['valor'],
                'cedente': row['nome_cedente'],
                'sacado': row['nome_sacado'],
                'motivos': motivos,
                'valor': row['valor'],
                'cedente': row['nome_cedente'],
                'cnpj_cedente': row['cnpj_cedente'],          
                'estado_cedente': row['estado_cedente'],
                'setor_cedente': row['setor_cedente'],
                
                'sacado': row['nome_sacado'],
                'cnpj_sacado': row['cnpj_sacado'],
                'estado_sacado': row['estado_sacado'],
                'setor_sacado': row['setor_sacado'],

                "aceite_sacado": row['aceite_sacado'],
                "endossatario": row['endossatario'],
                
                'data_emissao': row['data_emissao'],
                'data_vencimento': row['data_vencimento'],
                'prazo_dias': row['prazo_dias'],

                # Para validação (remover em produção)
                'label_fraude': row.get('label_fraude', 'N/A'),
                'tipo_fraude_real': row.get('tipo_fraude', 'N/A')
            })
        
        return pd.DataFrame(relatorio)
    
    def metricas_desempenho(self):
        """
        Calcula métricas de detecção (SE houver label_fraude)
        """
        if 'label_fraude' not in self.df.columns:
            return "⚠️ Dataset não possui labels de fraude para validação"
        
        # Threshold: risk_score > 3.0 = fraude
        self.df['pred_fraude'] = (self.df['risk_score'] > 3.0).astype(int)
        
        tp = ((self.df['pred_fraude'] == 1) & (self.df['label_fraude'] == 1)).sum()
        fp = ((self.df['pred_fraude'] == 1) & (self.df['label_fraude'] == 0)).sum()
        tn = ((self.df['pred_fraude'] == 0) & (self.df['label_fraude'] == 0)).sum()
        fn = ((self.df['pred_fraude'] == 0) & (self.df['label_fraude'] == 1)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'Total Duplicatas': len(self.df),
            'Fraudes Reais': int(self.df['label_fraude'].sum()),
            'Fraudes Detectadas': int(self.df['pred_fraude'].sum()),
            'True Positives': int(tp),
            'False Positives': int(fp),
            'True Negatives': int(tn),
            'False Negatives': int(fn),
            'Precision': f"{precision:.2%}",
            'Recall': f"{recall:.2%}",
            'F1-Score': f"{f1:.2%}"
        }
    