# RAG - Project

Exemplos de agentes com **LangChain** e **LangGraph** usando o modelo **Claude Haiku 4.5** da Anthropic.

## Scripts

| Arquivo | O que faz |
|---|---|
| `FirstAgent.py` | Agente simples que responde perguntas de turismo (ex.: "Qual é a capital da França?"). |
| `AgentReceitas.py` | Agente "chef pessoal": busca receitas na web com a Tavily e devolve uma lista estruturada (nome, ingredientes, modo de preparo). |
| `CondicionalEdges.py` | Grafo LangGraph que classifica feedbacks de clientes e usa uma **aresta condicional** para enviá-los à equipe certa (Engenharia, Marketing ou Suporte). |

## Requisitos

- Python 3.10 ou mais recente
- Uma chave da API da Anthropic: https://platform.claude.com/settings/keys
- Uma chave da Tavily, só para o `AgentReceitas.py`: https://tavily.com

## Instalação

```bash
pip install python-dotenv pydantic langchain langgraph langchain-anthropic langchain-tavily
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

O `.env` está no `.gitignore` e não é enviado para o repositório. Nunca faça commit das suas chaves.

## Como rodar

```bash
python FirstAgent.py
python AgentReceitas.py
python CondicionalEdges.py
```

## Custo

Todos os scripts usam o `claude-haiku-4-5`, o modelo mais barato da Anthropic (US$ 1 por milhão de tokens de entrada e US$ 5 por milhão de saída). Cada script define um `max_tokens` para limitar o tamanho das respostas e o gasto.

O `AgentReceitas.py` custa mais por execução que os outros, porque os resultados da busca na web entram no contexto do modelo.
