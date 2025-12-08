import asyncio
from datetime import datetime

from .gerar_dados import DuplicataFactory
from .gerar_fraudes import FraudeInjector
from ..models.populacao import ConfigPopulacao


async def popular_banco_automatico(config: ConfigPopulacao, db_manager):
    """
    Popula automaticamente o banco na inicialização.
    Pode ser executado em background (lifespan/startup).
    """

    inicio = datetime.now()
    resultado = {
        "em_andamento": True,
        "concluido": False,
        "erro": None
    }

    try:
        print("\n" + "="*60)
        print("🚀 INICIANDO POPULAÇÃO AUTOMÁTICA DO BANCO DE DADOS")
        print("="*60)

        # Verifica se já existe dados
        total_existente = db_manager.contar_registros()

        if total_existente > 0 and not config.forcar_limpeza:
            print(f"ℹ️  Banco já contém {total_existente} registros - pulando população")
            resultado.update({"concluido": True})
            return resultado

        # Limpa se necessário
        if config.forcar_limpeza and total_existente > 0:
            print(f"🗑️  Limpando {total_existente} registros existentes...")
            db_manager.limpar_tabela()

        # Cria estrutura
        print("🏗️  Criando estrutura do banco...")
        db_manager.criar_tabela()

        # Gera empresas
        print(f"🏭 Gerando {config.qtd_cedentes} cedentes e {config.qtd_sacados} sacados...")
        factory = DuplicataFactory()
        factory.gerar_carteira_empresas(
            qtd_cedentes=config.qtd_cedentes,
            qtd_sacados=config.qtd_sacados
        )

        # Gera duplicatas
        print(f"📝 Gerando {config.qtd_duplicatas} duplicatas...")
        dataset = []

        tamanho_lote = 1000
        for i in range(0, config.qtd_duplicatas, tamanho_lote):
            lote_size = min(tamanho_lote, config.qtd_duplicatas - i)

            for _ in range(lote_size):
                dataset.append(factory.gerar_transacao_normal())

            progresso = (i + lote_size) / config.qtd_duplicatas * 100
            print(f"   📊 Progresso: {progresso:.1f}%")

            await asyncio.sleep(0.01)

        # Injeta fraudes
        print(f"⚠️  Contaminando com fraudes ({config.taxa_fraude*100:.1f}%)...")
        injector = FraudeInjector(factory)
        dataset_final = injector.contaminar_dataset(dataset, taxa_fraude=config.taxa_fraude)

        # Insere no banco
        print("💾 Inserindo no banco...")
        tamanho_lote_insert = 5000
        total_lotes = (len(dataset_final) + tamanho_lote_insert - 1) // tamanho_lote_insert

        for idx, i in enumerate(range(0, len(dataset_final), tamanho_lote_insert), 1):
            lote = dataset_final[i:i + tamanho_lote_insert]
            db_manager.inserir_lote(lote)
            print(f"   💾 Lote {idx}/{total_lotes} inserido")
            await asyncio.sleep(0.01)

        # Estatísticas
        total_inserido = db_manager.contar_registros()
        total_fraudes = db_manager.contar_fraudes()
        tempo_total = (datetime.now() - inicio).total_seconds()

        print("\n" + "="*60)
        print("✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print(f"📊 Total de registros: {total_inserido:,}")
        print(f"⚠️  Total de fraudes: {total_fraudes:,} ({total_fraudes/total_inserido*100:.1f}%)")
        print(f"⏱️  Tempo de execução: {tempo_total:.2f}s")
        print("="*60 + "\n")

        resultado["concluido"] = True
        return resultado

    except Exception as e:
        print(f"\n❌ ERRO na população automática: {str(e)}")
        import traceback
        traceback.print_exc()
        resultado["erro"] = str(e)
        return resultado

    finally:
        resultado["em_andamento"] = False
