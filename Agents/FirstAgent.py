from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain.messages import HumanMessage
from pydantic import BaseModel
from pprint import pprint
from typing import List

load_dotenv()

# Example 1: Agent with structured output


question = HumanMessage(content="Qual é a capital da França?")
agent_structured = create_agent(
    model=ChatAnthropic(model="claude-haiku-4-5", max_tokens=1024),
    system_prompt="Você é um expert em turismo. Responda com as informações sobre a capital solicitada.",
)

response_structured = agent_structured.invoke(
    {"messages": [question]}
)

print("Output do Agente:")
capital_info = response_structured["messages"][-1].text
pprint(capital_info)