"""Ollama LLM 연결"""

import json
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.config import get_config, LLMConfig
from src.core.exceptions import LLMConnectionError, LLMResponseError
from src.core.logger import get_logger

logger = get_logger(__name__)


class LLMManager:
    """LLM 관리자"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or get_config().llm
        self._models: dict[str, ChatOllama] = {}

    def get_model(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> ChatOllama:
        """LLM 모델 가져오기"""
        if model_name is None:
            model_name = self.config.default_model

        cache_key = f"{model_name}_{temperature}"

        if cache_key not in self._models:
            try:
                self._models[cache_key] = ChatOllama(
                    model=model_name,
                    base_url=self.config.base_url,
                    temperature=temperature or self.config.temperature,
                    num_ctx=self.config.num_ctx,
                    **kwargs
                )
                logger.info(f"LLM 모델 로드: {model_name}")
            except Exception as e:
                raise LLMConnectionError(f"LLM 연결 실패: {e}")

        return self._models[cache_key]

    def get_default_model(self) -> ChatOllama:
        """기본 모델 가져오기"""
        return self.get_model(self.config.default_model)

    def get_coding_model(self) -> ChatOllama:
        """코딩 모델 가져오기"""
        return self.get_model(self.config.coding_model)

    def get_fast_model(self) -> ChatOllama:
        """빠른 모델 가져오기"""
        return self.get_model(self.config.fast_model)

    def invoke(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """LLM 호출"""
        model = self.get_model(model_name, **kwargs)

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        try:
            response = model.invoke(messages)
            return response.content
        except Exception as e:
            raise LLMResponseError(f"LLM 응답 오류: {e}")

    def invoke_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> dict:
        """LLM 호출 (JSON 응답)"""
        response = self.invoke(prompt, system_prompt, model_name, **kwargs)

        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패, 원본 응답 반환: {e}")
            return {"raw_response": response, "error": str(e)}


_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """전역 LLM 매니저 가져오기"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


def get_llm(model_name: Optional[str] = None, **kwargs) -> ChatOllama:
    """LLM 모델 가져오기 (편의 함수)"""
    return get_llm_manager().get_model(model_name, **kwargs)


def invoke_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> str:
    """LLM 호출 (편의 함수)"""
    return get_llm_manager().invoke(prompt, system_prompt, model_name, **kwargs)


def invoke_llm_json(
    prompt: str,
    system_prompt: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> dict:
    """LLM JSON 호출 (편의 함수)"""
    return get_llm_manager().invoke_json(prompt, system_prompt, model_name, **kwargs)
