from langchain.agents import create_agent
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from Retriever import DOCRetriever
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"]=os.getenv("TAVILY_API_KEY")

retriever=DOCRetriever()
#model=ChatGroq(model="qwen/qwen3-32b")
model=ChatOllama(model="llama3.2")



@tool("calculator", description="Performs arithmetic calculations. Use this for any maths operation.")
def calc(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Calculation error: {e}"


@tool("document_search",description=("Search the currently uploaded document for information relevant to a query. "
                                    "Use this whenever the user's question could be answered from an uploaded file. "
                                    "If no document has been uploaded yet, this tool will say so."),)
def document_search(query: str) -> str:
    results= retriever.retrieve(query) 
    return "\n".join(f"{r['content']}" for r in results)


@tool("code_executor",
      description="""Executes Python code and returns output or errors.
      Use this AFTER retrieving code from document_search.
      Input must be complete, runnable Python code as a string.""")
def code_executor(code: str) -> str:
    import subprocess
    result = subprocess.run(["python3", "-c", code],capture_output=True, text=True, timeout=10)
    return result.stdout if result.stdout else result.stderr


websearch_tool = TavilySearch(max_results=5, topic="general")


tools = [websearch_tool, calc, document_search,code_executor]

agent = create_agent(model=model,tools=tools,system_prompt="""
        You are an intelligent AI assistant named Ultron.
        Rules:
        - Use document_search whenever the question could relate to an uploaded document.
        - Use calculator for arithmetic.
        - Use web_search for current information not in any document.
        - If document_search says no document is loaded, tell the user to upload one.
        - When a document is first loaded, give a short overview of it.
    """,)




