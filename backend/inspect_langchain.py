
import sys
import os

try:
    import langchain
    import langchain.agents
    
    with open("langchain_debug.txt", "w") as f:
        f.write(f"LangChain Version: {langchain.__version__}\n")
        f.write(f"LangChain File: {langchain.__file__}\n")
        f.write(f"LangChain Agents File: {langchain.agents.__file__}\n")
        f.write(f"Dir(langchain.agents): {dir(langchain.agents)}\n")
        
        has_ae = 'AgentExecutor' in dir(langchain.agents)
        f.write(f"Has AgentExecutor: {has_ae}\n")
        
        if has_ae:
             f.write(f"AgentExecutor module: {langchain.agents.AgentExecutor.__module__}\n")

except Exception as e:
    with open("langchain_debug.txt", "w") as f:
        f.write(f"Error: {e}\n")
