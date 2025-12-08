from typing import TypedDict, Sequence, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing_extensions import NotRequired


class AgentState(TypedDict):
    """
    ສະຖານະຂອງ LangGraph Agent
    """
    question: NotRequired[str]  # ຄຳຖາມຂອງຜູ້ໃຊ້
    messages: Annotated[Sequence[BaseMessage], add_messages]  # ຂໍ້ຄວາມຂອງຜູ້ໃຊ້ ແລະ LLM
    sql_script: NotRequired[str]  # SQL Query ສຳລັບດຶງຂໍ້ມູນ
    result_schema: NotRequired[str]  # ຜົນລັບ schema ຂອງ tables ທັງໝົດ (text)
    sql_result: NotRequired[dict]  # ຜົນລັບຈາກການ execute SQL (columns, rows)