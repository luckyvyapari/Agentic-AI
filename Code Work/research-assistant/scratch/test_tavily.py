import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

tool = TavilySearch(max_results=2)
results = tool.invoke({"query": "What is the capital of France?"})
print(f"Type: {type(results)}")
print(f"Results: {results}")
