"""Knowledge Graph 워크플로우

LangGraph를 사용한 멀티 에이전트 워크플로우 정의.
Research → Analyst → Writer 순서로 실행.
"""

from typing import Optional

from langgraph.graph import StateGraph, END

from src.core.logger import get_logger
from src.graphs.state import WorkflowState, create_initial_state
from src.agents.research_agent import ResearchAgent
from src.agents.analyst_agent import AnalystAgent
from src.agents.writer_agent import WriterAgent

logger = get_logger(__name__)


def create_workflow(model_name: Optional[str] = None) -> StateGraph:
    """워크플로우 생성

    Args:
        model_name: 사용할 LLM 모델명

    Returns:
        컴파일된 StateGraph
    """
    # 에이전트 인스턴스 생성
    research_agent = ResearchAgent(model_name=model_name)
    analyst_agent = AnalystAgent(model_name=model_name)
    writer_agent = WriterAgent(model_name=model_name)

    # 노드 함수 정의 (순수 함수: state → partial state)
    def research_node(state: WorkflowState) -> dict:
        """Research Agent 노드"""
        logger.info("[워크플로우] Research Agent 실행")
        try:
            result = research_agent.run(state)
            return {
                **result,
                "current_step": "research_completed"
            }
        except Exception as e:
            logger.error(f"Research Agent 오류: {e}")
            return {
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "research_failed"
            }

    def analyst_node(state: WorkflowState) -> dict:
        """Analyst Agent 노드"""
        logger.info("[워크플로우] Analyst Agent 실행")
        try:
            result = analyst_agent.run(state)
            return {
                **result,
                "current_step": "analyst_completed"
            }
        except Exception as e:
            logger.error(f"Analyst Agent 오류: {e}")
            return {
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "analyst_failed"
            }

    def writer_node(state: WorkflowState) -> dict:
        """Writer Agent 노드"""
        logger.info("[워크플로우] Writer Agent 실행")
        try:
            result = writer_agent.run(state)
            return {
                **result,
                "current_step": "writer_completed"
            }
        except Exception as e:
            logger.error(f"Writer Agent 오류: {e}")
            return {
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "writer_failed"
            }

    # StateGraph 생성
    workflow = StateGraph(WorkflowState)

    # 노드 추가
    workflow.add_node("research", research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    # 엣지 추가 (순차 실행)
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)

    # 컴파일
    return workflow.compile()


class KnowledgeGraphBuilder:
    """Knowledge Graph Builder

    워크플로우를 실행하여 문서에서 지식 그래프를 구축.

    사용법:
        builder = KnowledgeGraphBuilder(
            input_dir="data/input",
            output_file="data/output/graph.cypher"
        )
        result = builder.run()

        if result["success"]:
            print(f"완료: {result['result']}")
        else:
            print(f"실패: {result['errors']}")
    """

    def __init__(
        self,
        input_dir: str = "data/input",
        output_file: str = "data/output/graph.cypher",
        model_name: Optional[str] = None
    ):
        """초기화

        Args:
            input_dir: 입력 파일 디렉토리
            output_file: 출력 Cypher 파일 경로
            model_name: 사용할 LLM 모델명
        """
        self.input_dir = input_dir
        self.output_file = output_file
        self.model_name = model_name
        self.workflow = create_workflow(model_name)
        self.logger = get_logger("knowledge_graph_builder")

    def run(self) -> dict:
        """워크플로우 실행

        Returns:
            {success, result, errors}
        """
        self.logger.info("=" * 50)
        self.logger.info("Knowledge Graph Builder 시작")
        self.logger.info(f"입력: {self.input_dir}")
        self.logger.info(f"출력: {self.output_file}")
        self.logger.info("=" * 50)

        # 초기 상태
        initial_state = create_initial_state(
            input_dir=self.input_dir,
            output_file=self.output_file
        )

        try:
            # 워크플로우 실행
            final_state = self.workflow.invoke(initial_state)

            # 결과 정리
            errors = final_state.get("errors", [])
            result = final_state.get("result", {})

            if errors:
                self.logger.warning(f"완료 (경고 {len(errors)}개): {errors}")
            else:
                self.logger.info("워크플로우 완료")

            return {
                "success": len(errors) == 0,
                "result": result,
                "errors": errors,
                "final_state": final_state
            }

        except Exception as e:
            self.logger.error(f"워크플로우 실패: {e}")
            return {
                "success": False,
                "result": {},
                "errors": [str(e)],
                "final_state": None
            }

    def run_step(self, step: str, state: WorkflowState) -> WorkflowState:
        """단일 단계만 실행 (디버깅용)

        Args:
            step: 실행할 단계 (research, analyst, writer)
            state: 현재 상태

        Returns:
            업데이트된 상태
        """
        agents = {
            "research": ResearchAgent(model_name=self.model_name),
            "analyst": AnalystAgent(model_name=self.model_name),
            "writer": WriterAgent(model_name=self.model_name),
        }

        if step not in agents:
            raise ValueError(f"알 수 없는 단계: {step}")

        agent = agents[step]
        result = agent.run(state)

        return {**state, **result}
