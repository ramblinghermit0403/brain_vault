
try:
    import langchain
    print(f"LangChain Version: {langchain.__version__}")
    
    from langchain.agents import AgentExecutor
    print("Success: from langchain.agents import AgentExecutor")
except ImportError as e:
    print(f"Failed: from langchain.agents import AgentExecutor -> {e}")

try:
    from langchain.agents.agent import AgentExecutor
    print("Success: from langchain.agents.agent import AgentExecutor")
except ImportError as e:
    print(f"Failed: from langchain.agents.agent import AgentExecutor -> {e}")

try:
    from langchain.agents.react.agent import create_react_agent
    print("Success: from langchain.agents.react.agent import create_react_agent")
except ImportError as e:
    print(f"Failed: from langchain.agents.react.agent import create_react_agent -> {e}")

try:
    from langchain_community.chat_models import ChatOpenAI
    print("Success: from langchain_community.chat_models import ChatOpenAI")
except ImportError as e:
    print(f"Failed: from langchain_community.chat_models import ChatOpenAI -> {e}")
