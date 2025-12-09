import json
import requests
from typing import Dict, Any, List, TypedDict, Annotated
import duckdb
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from ..core.dependencies import get_db_connection

# Estado do agente
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


class AntiFraudeAgente:
    def __init__(
        self, 
        api_url="http://localhost:8000/mocks/instituicoes", 
        google_model="gemini-2.5-flash" 
    ):
        self.api_url = api_url
        self.conn = get_db_connection()
        
        # LLM
        self.llm = ChatGoogleGenerativeAI(
            model=google_model,
            temperature=0.2,
        )
        
        # Tools
        self.tools = self._build_tools()
        
        # Bind tools ao LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Cria o grafo do agente
        self.graph = self._create_graph()

    # --------------------------------------
    # TOOLS
    # --------------------------------------
    def _consulta_instituicao(self, nome: str):
        try:
            url = f"{self.api_url}?nome={nome.strip()}"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return r.json()
        except requests.exceptions.RequestException:
            return None
        return None

    def _build_tools(self) -> List[Tool]:
        def consultar_entidade(nome: str) -> str:
            """
            Consulta uma API pública para validar dados cadastrais de uma instituição financeira ou empresa.
            Use esta tool quando tiver dúvidas sobre a classificação da entidade (ex: se é Banco, Factoring, etc).
            Retorna JSON string ou 'NO_DATA'.
            """
            data = self._consulta_instituicao(nome)
            if not data:
                return "NO_DATA"
            return json.dumps(data, ensure_ascii=False)
            
        def verificar_com_cliente(id_duplicata: str) -> str:
            try:
                query = """
                SELECT label_fraude, nome_cedente 
                FROM duplicatas WHERE id_duplicata = ?
                """

                resultado = self.conn.execute(query, [id_duplicata]).fetchone()

                if not resultado:
                    return "ERRO: Cliente não encontrado para este ID de duplicata."

                is_fraude_real = resultado[0] == 1
                nome_cliente = resultado[1]

                if is_fraude_real:
                    return """
                    [CANAL: E-mail]
                    Olá, desconhecemos essa operação...
                    """
                else:
                    return """
                    [CANAL: WhatsApp]
                    Confirmamos a emissão...
                    """

            except Exception as e:
                return f"Erro ao contatar cliente: {str(e)}"

        
        return [
            Tool(
                name="consultar_entidade",
                func=consultar_entidade,
                description="Consulta uma API pública para validar dados cadastrais de uma instituição financeira ou empresa. Use esta tool quando tiver dúvidas sobre a classificação da entidade (ex: se é Banco, Factoring, etc). Retorna JSON string ou 'NO_DATA'."
            ),
            Tool(
                name="verificar_com_cliente",
                func=verificar_com_cliente,
                description="Simula o contato com o cliente para confirmar a veracidade da duplicata. Consulta a base de fatos (DuckDB) para simular a resposta correta do cliente. Retorna a mensagem do cliente. Input: id_duplicata (string)"
            )
        ]

    # --------------------------------------
    # GRAFO DO AGENTE (LangGraph)
    # --------------------------------------
    def _create_graph(self):
        """Cria o grafo de execução do agente usando LangGraph"""
        
        # Define a função que chama o LLM
        def call_model(state: AgentState):
            messages = state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        # Define quando continuar ou parar
        def should_continue(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            
            # Se a última mensagem tem tool_calls, continua para executar as tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            
            # Caso contrário, termina
            return END
        
        # Cria o grafo
        workflow = StateGraph(AgentState)
        
        # Adiciona os nós
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Define o ponto de entrada
        workflow.set_entry_point("agent")
        
        # Adiciona as edges condicionais
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Após executar as tools, volta para o agente
        workflow.add_edge("tools", "agent")
        
        # Compila o grafo
        return workflow.compile()

    # --------------------------------------
    # ANALISAR CASO (COM VERIFICAÇÃO ATIVA)
    # --------------------------------------
    def analisar_caso(self, evento_bi: Dict) -> Dict:
        evento_str = json.dumps(evento_bi, indent=2, ensure_ascii=False)

        prompt_sistema = f"""
        Você é um Auditor Sênior de Riscos e Agente Antifraude.

        OBJETIVO:
        Analisar o evento de duplicata abaixo, verificar a veracidade da transação com o cliente (simulado) e emitir um veredito.

        DADOS DO EVENTO:
        {evento_str}

        SEU PROTOCOLO DE AÇÃO (Rigoroso):

        1. ANÁLISE INICIAL: 
        Analise os dados. O erro parece ser cadastral (Entidade) ou operacional?

        2. CONSULTA DE ENTIDADE (Opcional):
        Se houver dúvida sobre quem é o sacado/cedente (ex: CNAE incompatível), use a tool `consultar_entidade`.

        3. VERIFICAÇÃO COM CLIENTE (OBRIGATÓRIO SE HOUVER SUSPEITA - O*NET Req 7):
        Se a duplicata for classificada como POSSÍVEL_FRAUDE ou SUSPEITA:
        - CHAME a tool `verificar_com_cliente` passando o `id_duplicata`.
        - A tool irá consultar a "base de verdade" (DuckDB) e retornar a resposta do cliente.

        4. VEREDITO FINAL:
        - Se o cliente responder confirmando a emissão -> Classifique como "FALSO_POSITIVO".
        - Se o cliente responder desconhecendo a dívida -> Classifique como "FRAUDE_CONFIRMADA".
        - Se não houve necessidade de contato -> Classifique conforme análise técnica.

        FORMATO DE RESPOSTA ESPERADO (Retorne APENAS este JSON válido, sem markdown):
        {{
            "id_duplicata": "copie do evento",
            "veredito_final": "FRAUDE_CONFIRMADA" | "FALSO_POSITIVO" | "LEGITIMO" | "EM_ANALISE",
            "causa_raiz": "ENTIDADE" | "OPERACIONAL" | "GOLPE_EXTERNO",
            "passo_a_passo": {{
                "analise_entidade": "O que você analisou sobre a empresa...",
                "contato_cliente_realizado": true | false,
                "resposta_cliente": "Resumo do que a tool retornou (se houve contato)"
            }},
            "acao_recomendada": "BLOQUEAR" | "LIBERAR" | "AGUARDAR",
            "justificativa_tecnica": "Explicação completa baseada nas tools chamadas."
        }}
        """

        try:
            # Executa o grafo
            initial_state = {
                "messages": [HumanMessage(content=prompt_sistema)]
            }
            
            result = self.graph.invoke(initial_state)
            
            # Pega a última mensagem do agente
            final_message = result["messages"][-1]
            content = final_message.content

            if isinstance(content, list):
                content = "\n".join(
                    x.get("text", str(x)) if isinstance(x, dict) else str(x)
                    for x in content
                )

            output_text = (
                content.replace("```json", "")
                    .replace("```", "")
                    .strip()
            )

            
            # Limpeza robusta para garantir que Markdown não quebre o parser
            output_text = output_text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(output_text)
            
        except json.JSONDecodeError as e:
            return {
                "detail": "Falha no parse do JSON gerado pelo Agente", 
                "conteudo_bruto": output_text if 'output_text' in locals() else "",
                "status": "ERRO_INTERNO",
                "detalhes": str(e)
            }
        except Exception as e:
            return {
                "detail": f"Erro crítico na execução do agente: {str(e)}",
                "status": "ERRO_INTERNO"
            }