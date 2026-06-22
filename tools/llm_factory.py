from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

def get_llm(tier="cheap"):
    api_key = os.getenv("OPENAI_API_KEY")
    
    if tier == "cheap":
        # Ultra-fast, cost-saving tier for basic text extraction and routing
        return ChatOpenAI(
            model="gpt-4o-mini", 
            api_key=api_key,
            temperature=0
        )
    elif tier == "reasoning":
        # Premium tier using your custom model for complex system design
        return ChatOpenAI(
            model="gpt-5.5", 
            api_key=api_key,
            temperature=0.2
        )
    else:
        # Fallback to premium
        return ChatOpenAI(
            model="gpt-5.5", 
            api_key=api_key,
            temperature=0.2
        )