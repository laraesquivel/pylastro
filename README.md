# 📄 Sistema de Detecção e Análise de Fraudes em Duplicatas

## 📌 Visão Geral do Projeto
Este projeto implementa um **pipeline completo de detecção de fraude em duplicatas**, combinando:

- **Modelagem heurística/estatística** (ratios financeiros)
- **RAG com LLM (Gemini 2.5 Flash)**
- **Agente inteligente com LangGraph**
- **Ferramentas externas (API simulada + DuckDB)**
- **FastAPI para exposição dos serviços**
- **Scripts automáticos para geração e população do banco**

O sistema é capaz de:
- Analisar duplicatas em lote  
- Classificar risco (Baixo → Crítico)  
- Gerar relatórios e métricas  
- Investigar casos suspeitos com ferramentas automáticas  
- Confirmar operações via simulação de contato com o cliente  
- Emitir veredito final estruturado  

---

# 🗂 Estrutura de Pastas
```text
src/
│
├── data/
│ └── duplicatas.duckdb
│
└── pylastro/
├── main.py
├── core/
│ ├── config.py
│ └── dependencies.py
│
├── db/
│ └── duckdb.py
│
├── domain/
│ ├── agente.py
│ ├── mock_api_empresa.py
│ └── detector_fraudes.py
│
├── models/
│ ├── populacao.py
│ └── duplicatas_fraudes.py
│
├── routes/
│ ├── relatorios.py
│ ├── mocks.py
│ └── simulacao.py
│
├── script/
│ ├── gerar_dados.py
│ ├── gerar_fraudes.py
│ └── popular_banco_automatico.py
│
└── service/
├── detectar_fraude.py
└── simular_alerta.py
```

---

# 🧠 Descrição dos Módulos e Responsabilidades

## 📂 service

### `detectar_fraude.py`
Responsável por executar todo o pipeline de detecção de fraudes:
- Calcula ratios financeiros
- Calcula risk score
- Classifica cada duplicata
- Retorna métricas e ranking de suspeitos

### `simular_alerta.py`
- Encapsula o uso do **AntiFraudeAgente**
- Recebe um payload de duplicatas
- Analisa cada duplicata individualmente
- Usado pela rota `/simular_pipeline`

---

## 📂 domain

### `detector_fraudes.py`
Núcleo estatístico que:
- Analisa liquidez e circularidade  
- Detecta emissões anômalas  
- Calcula pontuação de risco  
- Gera relatório técnico  

### `mock_api_empresa.py`
API fake para consulta de:
- Instituições financeiras
- Empresas suspeitas
- Classificação automática de entidades

### `agente.py` — **AntiFraudeAgente**
Componente avançado que combina:
- LangGraph  
- Gemini 2.5 Flash  
- Ferramentas externas (Tools)  
- DuckDB  

Fluxo:
1. Analisa evento de duplicata  
2. Consulta entidade (opcional)  
3. Contata o cliente (tool)  
4. Segue protocolo antifraude  
5. Retorna JSON estrutural com:
   - veredito final  
   - causa raiz  
   - justificativa técnica  
   - passo a passo da investigação  

É um **auditor virtual** totalmente automatizado.

---

## 📂 models

### `duplicatas_fraudes.py`
Contém:
- `ClassificacaoEnum`
- `TipoFraudeEnum`
- `DuplicataItem`
- `DuplicatasPayload`

Define o padrão dos dados de entrada e saída.

### `populacao.py`
Modelos para controle da geração/população do banco:
- `StatusPopulacao`
- `ConfigPopulacao`
- `ResultadoPopulacao`

---

## 📂 db

### `duckdb.py`
- Manipula `duplicatas.duckdb`
- Permite consultas de duplicatas para validação real do cliente
- Usado pela tool `verificar_com_cliente`

---

## 📂 core
- `config.py`: configurações gerais da aplicação  
- `dependencies.py`: gerencia conexões e injeções  

---

## 📂 script
- `gerar_dados.py`: gera duplicatas legítimas  
- `gerar_fraudes.py`: cria padrões fraudulentos  
- `popular_banco_automatico.py`: carrega tudo para o DuckDB  

---

## 📂 routes
Rotas FastAPI:
- `/relatorios`  
- `/simular_pipeline`  
- `/mocks/instituicoes`  

---

# 🚀 Fluxo Completo da Solução

1. Dados são gerados via scripts  
2. O banco DuckDB é populado  
3. O serviço `detectar_fraude` executa o pipeline  
4. O usuário chama `/simular_pipeline`  
5. O AntiFraudeAgente investiga cada duplicata:
   - usa ferramentas para confirmar dados  
   - consulta API simulada  
   - verifica com cliente via DuckDB  
6. Retorna veredito final completamente estruturado  

---

# 🎯 O Problema Que o Projeto Resolve

O sistema resolve a necessidade de **investigação rápida, padronizada e confiável** de duplicatas suspeitas.

Antes:
- Analistas avaliavam manualmente  
- Consultavam bases externas  
- Ligavam para clientes  
- Documentavam investigações  
- Risco alto de erro ou inconsistência  

Agora:
- A análise é automática, padronizada e auditável  
- O agente segue sempre o mesmo protocolo  
- Dados externos são consultados pelas tools  
- A decisão é mais rápida e mais precisa  

---

# 📈 Ganhos de Eficiência

### ⏱ 1. Redução de tempo de análise
- Manual: **10–20 minutos por duplicata**
- Agente: **< 2 segundos**

Para 500 duplicatas/dia:
- Antes: ~166 horas  
- Agora: ~17 minutos  
→ **Economia de ~99% do tempo**

### 🧪 2. Redução de falsos positivos
O modelo estatístico identifica suspeitos,  
mas o agente confirma usando:
- consulta externa  
- verificação com cliente  

### 🔄 3. Padronização total do processo
Todos os casos seguem o mesmo fluxo antifraude.

### 📝 4. Rastreabilidade e documentação automática
O retorno inclui:
- causa raiz  
- passo a passo  
- justificativa técnica  
- ações recomendadas  

### 👥 5. Libera o time para atividades estratégicas
Analistas focam nos casos realmente críticos.
