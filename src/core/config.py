"""설정 관리"""

from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

import yaml

from src.core.exceptions import ConfigError


@dataclass
class LLMConfig:
    """LLM 설정"""
    default_model: str = "qwen2.5:7b"
    coding_model: str = "qwen2.5-coder:7b"
    fast_model: str = "phi3:mini"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    num_ctx: int = 4096


@dataclass
class Neo4jConfig:
    """Neo4j 설정"""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"
    export_formats: list[str] = field(default_factory=lambda: ["cypher", "csv", "markdown"])
    output_dir: str = "data/output/neo4j"


@dataclass
class PathsConfig:
    """경로 설정"""
    input_dir: str = "data/input"
    output_dir: str = "data/output"
    temp_dir: str = "data/temp"
    supported_extensions: list[str] = field(
        default_factory=lambda: [".md", ".txt", ".csv", ".docx", ".json"]
    )


@dataclass
class ProcessingConfig:
    """처리 설정"""
    batch_size: int = 10
    max_file_size_mb: int = 50
    max_concurrent: int = 3
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 1


@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/agent.log"


@dataclass
class Config:
    """전체 설정"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def _dict_to_dataclass(data: dict, cls: type) -> Any:
    """딕셔너리를 dataclass로 변환"""
    if data is None:
        return cls()

    field_names = {f.name for f in cls.__dataclass_fields__.values()}
    filtered_data = {k: v for k, v in data.items() if k in field_names}

    return cls(**filtered_data)


def load_config(config_path: Optional[str] = None) -> Config:
    """설정 파일 로드"""
    if config_path is None:
        config_path = "configs/settings.yaml"

    path = Path(config_path)

    if not path.exists():
        return Config()

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"YAML 파싱 오류: {e}")
    except Exception as e:
        raise ConfigError(f"설정 파일 로드 오류: {e}")

    config = Config(
        llm=_dict_to_dataclass(data.get('llm'), LLMConfig),
        neo4j=_dict_to_dataclass(data.get('neo4j'), Neo4jConfig),
        paths=_dict_to_dataclass(data.get('paths'), PathsConfig),
        processing=_dict_to_dataclass(data.get('processing'), ProcessingConfig),
        logging=_dict_to_dataclass(data.get('logging'), LoggingConfig),
    )

    return config


def load_prompts(prompt_file: str) -> dict:
    """프롬프트 파일 로드"""
    path = Path(prompt_file)

    if not path.exists():
        raise ConfigError(f"프롬프트 파일을 찾을 수 없습니다: {prompt_file}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"프롬프트 YAML 파싱 오류: {e}")


def load_agents_config(config_path: Optional[str] = None) -> dict:
    """에이전트 설정 로드"""
    if config_path is None:
        config_path = "configs/agents.yaml"

    path = Path(config_path)

    if not path.exists():
        return {}

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"에이전트 설정 YAML 파싱 오류: {e}")


_config: Optional[Config] = None


def get_config() -> Config:
    """전역 설정 가져오기"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """설정 다시 로드"""
    global _config
    _config = load_config(config_path)
    return _config
