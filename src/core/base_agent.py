"""베이스 에이전트 클래스"""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypedDict

from src.core.llm import get_llm_manager
from src.core.logger import get_logger


class BaseAgent(ABC):
    """베이스 에이전트

    모든 에이전트가 상속받는 기본 클래스.
    각 에이전트는 자체 state, tools, prompts를 가진 독립 패키지로 구성됨.
    """

    name: str = "base_agent"
    description: str = "기본 에이전트"

    def __init__(self, model_name: Optional[str] = None):
        """초기화

        Args:
            model_name: 사용할 LLM 모델명
        """
        self.logger = get_logger(self.name)
        self.llm = get_llm_manager()
        self.model_name = model_name

        # 에이전트별 프롬프트 (서브클래스에서 정의)
        self.prompts: dict[str, str] = {}

        # 에이전트별 도구 (서브클래스에서 정의)
        self.tools: dict[str, Any] = {}

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """프롬프트 가져오기 및 포맷팅"""
        template = self.prompts.get(prompt_name, "")
        if not template:
            return ""

        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.warning(f"프롬프트 포맷팅 실패: {e}")
            return template

    def invoke_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """LLM 호출"""
        if system_prompt is None:
            system_prompt = self.prompts.get("system", "")

        return self.llm.invoke(
            prompt=prompt,
            system_prompt=system_prompt,
            model_name=self.model_name
        )

    def invoke_llm_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """LLM JSON 호출"""
        if system_prompt is None:
            system_prompt = self.prompts.get("system", "")

        return self.llm.invoke_json(
            prompt=prompt,
            system_prompt=system_prompt,
            model_name=self.model_name
        )

    @abstractmethod
    def run(self, state: dict) -> dict:
        """에이전트 실행

        순수 함수: 입력 state → 부분 state 업데이트 반환
        상태를 직접 수정하지 않음

        Args:
            state: 워크플로우 상태

        Returns:
            업데이트할 상태 부분 (전체 state가 아님)
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
