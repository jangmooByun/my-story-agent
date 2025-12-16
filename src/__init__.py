"""src 패키지 (레거시 호환성)

새 모듈 구조:
- agents/ : 에이전트 패키지들 (research_agent, analyst_agent, writer_agent)
- core/   : 공유 핵심 모듈
- graphs/ : LangGraph 워크플로우
- tools/  : 공유 도구들 (parsers, cypher)

이 패키지는 레거시 호환성을 위해 유지됩니다.
새 코드는 루트 레벨 모듈을 직접 import하세요.
"""

# 레거시 호환성을 위한 re-export
try:
    from graphs import KnowledgeGraphBuilder, WorkflowState, create_workflow
    from agents import ResearchAgent, AnalystAgent, WriterAgent
    from tools.cypher import CypherManager, GraphState, GraphNode, GraphRelationship
    from core import BaseAgent

    __all__ = [
        "KnowledgeGraphBuilder",
        "WorkflowState",
        "create_workflow",
        "ResearchAgent",
        "AnalystAgent",
        "WriterAgent",
        "CypherManager",
        "GraphState",
        "GraphNode",
        "GraphRelationship",
        "BaseAgent",
    ]
except ImportError:
    # 새 모듈이 없으면 빈 export
    __all__ = []
