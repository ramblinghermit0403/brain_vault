
import importlib
import pkgutil
import langchain
import langchain.agents

print(f"LangChain Version: {langchain.__version__}")
print(f"LangChain Path: {langchain.__file__}")

try:
    from langchain.agents import AgentExecutor
    print("Found: from langchain.agents import AgentExecutor")
except ImportError:
    print("Failed: from langchain.agents import AgentExecutor")

# Inspect submodules
print("\nSubmodules in langchain.agents:")
for loader, name, is_pkg in pkgutil.walk_packages(langchain.agents.__path__):
    print(f" - {name}")
    try:
        module = importlib.import_module(f"langchain.agents.{name}")
        if hasattr(module, "AgentExecutor"):
             print(f"   *** FOUND AgentExecutor in langchain.agents.{name} ***")
    except Exception as e:
        print(f"   (Error importing {name}: {e})")
