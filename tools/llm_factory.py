from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()


def get_llm(tier="cheap"):

    if st is not None:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            api_key = os.getenv("OPENAI_API_KEY")
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if tier == "cheap":

        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0
        )

    elif tier == "reasoning":

        return ChatOpenAI(
            model="gpt-5.5",
            api_key=api_key,
            temperature=0.2
        )

    else:

        return ChatOpenAI(
            model="gpt-5.5",
            api_key=api_key,
            temperature=0.2
        )