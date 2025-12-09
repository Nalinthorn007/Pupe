import os
from langchain_groq import ChatGroq
from loguru import logger


def get_router_llm(model_name: str = "moonshotai/kimi-k2-instruct-0905", temperature: float = 0.0):
    """
    ສ້າງ LLM ສຳລັບ Router/Agent ໂດຍໃຊ້ Groq
    
    Args:
        model_name: ຊື່ model (default: moonshotai/kimi-k2-instruct-0905)
        temperature: ຄວາມສຸ່ມຂອງ output (0.0 = deterministic)
    
    Returns:
        ChatGroq: LLM instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        logger.error("❌ GROQ_API_KEY not found in environment variables")
        raise ValueError("GROQ_API_KEY is required")
    
    logger.info(f"🤖 Initializing Groq LLM: {model_name}")
    
    llm = ChatGroq(
        api_key=api_key,
        model=model_name,
        temperature=temperature
    )
    
    return llm
