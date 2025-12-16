"""Research Agent 패키지

문서를 파싱하고 개념을 추출하는 에이전트.
다른 프로젝트에서 독립적으로 재사용 가능.

사용법:
    from agents.research_agent import ResearchAgent

    agent = ResearchAgent()
    result = agent.run({"input_dir": "data/input"})
"""

from agents.research_agent.agent import ResearchAgent
from agents.research_agent.state import ResearchState
from agents.research_agent.tools import ResearchTools
from agents.research_agent.prompts import PROMPTS

__all__ = [
    "ResearchAgent",
    "ResearchState",
    "ResearchTools",
    "PROMPTS",
]
