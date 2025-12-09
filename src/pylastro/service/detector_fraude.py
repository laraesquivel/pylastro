import pandas as pd
from ..domain.detector_fraudes import DetectorFraudeRatios

class DetectorFraudeService:

    def __init__(self, df: pd.DataFrame):
        self.detector = DetectorFraudeRatios(df)

    def executar(self, top_n:int = 20) -> dict:
        """
        Executa pipeline completo sem prints, 
        retorna estrutura JSON serializável
        """
        # 1) features
        self.detector.calcular_ratios_financeiros()

        # 2) score
        self.detector.calcular_risk_score()

        # 3) relatório (df)
        relatorio_df = self.detector.gerar_relatorio(top_n=top_n)

        # 4) métricas (se existir label)
        metricas = None
        if 'label_fraude' in self.detector.df.columns:
            metricas = self.detector.metricas_desempenho()

        # montar resposta final JSON friendly
        return {
            "resumo_risco": (
                self.detector.df['classificacao_risco']
                .value_counts()
                .sort_index()
                .to_dict()
            ),
            "top_suspeitos": relatorio_df.to_dict(orient="records"),
            "metricas": metricas
        }
