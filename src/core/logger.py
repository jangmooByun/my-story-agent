"""로깅 설정"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "agent_system",
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """로거 설정

    Args:
        name: 로거 이름
        level: 로깅 레벨 (DEBUG, INFO, WARNING, ERROR)
        log_file: 로그 파일 경로 (None이면 콘솔만)
        format_string: 로그 포맷

    Returns:
        설정된 Logger
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


_default_logger: Optional[logging.Logger] = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """로거 가져오기"""
    global _default_logger

    if name:
        return logging.getLogger(name)

    if _default_logger is None:
        _default_logger = setup_logger()

    return _default_logger


def set_log_level(level: str, name: Optional[str] = None):
    """로그 레벨 변경"""
    logger = get_logger(name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    for handler in logger.handlers:
        handler.setLevel(log_level)
