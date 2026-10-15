import asyncio
import pprint
from pathlib import Path
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

# Usando o adaptador oficial Langchain (vem com `pip install "langchain[mcp]"`)
from langchain.mcp import MCPAdapter

load_dotenv()

async def main():
    print("Iniciando o Exemplo 04: MCP como Tool (Cliente)\n")
    print("Usaremos o MCPAdapter para englobar as tools expostas em mcp_server.py.")

    # Path (e não str) indica um servidor local: o adaptador o inicia via stdio
    server_script = Path(__file__).parent / "mcp_server.py"

    print("Conectando ao Travel_MCP Server... (Subprocess)")
    async with MCPAdapter(server_script) as adapter:
        langchain_tools = await adapter.list_tools()
        print(f"[{len(langchain_tools)} Tools Descobertas e Adaptadas]")
        for t in langchain_tools:
            print(f" - {t.name}")

        print("\nCriando o Agente (create_agent)...")
        llm = ChatAnthropic(model="claude-haiku-4-5", temperature=0, max_tokens=1024)
        agent = create_agent(llm, langchain_tools)

        raw_input = """O cliente pediu 7 dias em Paris, visitando a Torre Eiffel, o Arco do Triunfo, a Catedral de Notre-Dame, o Louvre, o Musée d'Orsay, o Jardim de Luxemburgo e o Jardim das Tulherias.
        A viagem será do dia 10 ao dia 17 de Maio. Use a tool create_itinerary para criar o roteiro corporativo."""
        print(f"Usuário Manual: '{raw_input}'\n")

        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=raw_input)]}
        )

    #bloco de debug da resposta completa do LLM
    # print("\n[Resposta Final do LLM RAW]:")   
    # pprint.pprint(response) 

    #bloco limpo de resposta
    print("\n[Resposta Final do LLM]:")
    print(response["messages"][-1].text)

if __name__ == "__main__":
    asyncio.run(main())