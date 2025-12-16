"""커스텀 예외 클래스"""


class AgentSystemError(Exception):
    """에이전트 시스템 기본 예외"""
    pass


class ConfigError(AgentSystemError):
    """설정 관련 오류"""
    pass


class LLMError(AgentSystemError):
    """LLM 관련 오류"""
    pass


class LLMConnectionError(LLMError):
    """LLM 연결 오류"""
    pass


class LLMResponseError(LLMError):
    """LLM 응답 오류"""
    pass


class ParserError(AgentSystemError):
    """파서 관련 오류"""
    pass


class FileParseError(ParserError):
    """파일 파싱 오류"""
    pass


class AgentError(AgentSystemError):
    """에이전트 실행 오류"""
    pass


class WorkflowError(AgentSystemError):
    """워크플로우 오류"""
    pass


class ExportError(AgentSystemError):
    """내보내기 오류"""
    pass
