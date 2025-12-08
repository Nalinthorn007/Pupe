"""
builder.py - ສ້າງ LangGraph Workflow

ໂຄງສ້າງ Workflow:
1. get_schema → sql_agent → execute_sql → END
"""

from langgraph.graph import StateGraph, END
from loguru import logger

from src.Agent.state import AgentState
from src.Agent.nodes import get_schema_node, sql_agent_node, execute_sql_node, chart_generation_node


def _build_workflow():
    """
    ສ້າງ workflow graph
    """
    workflow = StateGraph(AgentState)
    
    # ເພີ່ມ Nodes
    workflow.add_node("get_schema", get_schema_node)
    workflow.add_node("sql_agent", sql_agent_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("chart_agent", chart_generation_node)
    
    # ຕັ້ງຄ່າ Entry Point
    workflow.set_entry_point("get_schema")
    
    # Edges
    workflow.add_edge("get_schema", "sql_agent")
    workflow.add_edge("sql_agent", "execute_sql")
    workflow.add_edge("execute_sql", "chart_agent")
    workflow.add_edge("chart_agent", END)
    
    logger.info("✅ Workflow graph built successfully")
    
    return workflow


def get_agent_app():
    """
    ດຶງ agent app
    """
    workflow = _build_workflow()
    app = workflow.compile()
    return app
