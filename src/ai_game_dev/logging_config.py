"""Structured logging configuration for the MCP server."""

import logging
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

from ai_game_dev.config import ServerSettings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add custom fields to log record
        if not hasattr(record, 'component'):
            record.component = 'server'
        if not hasattr(record, 'operation'):
            record.operation = 'unknown'
        
        return super().format(record)


def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured logging with Rich formatting."""
    # Install rich traceback handler
    install(show_locals=True)
    
    # Create console handler with Rich
    console = Console(stderr=True)
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )
    
    # Create file handler for persistent logs
    settings = ServerSettings()
    log_dir = settings.data_base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / "openai_mcp_server.log",
        encoding="utf-8"
    )
    
    # Set formatters
    file_formatter = StructuredFormatter(
        fmt="%(asctime)s | %(levelname)8s | %(component)s | %(operation)s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our handlers
    root_logger.addHandler(rich_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str, component: str = "server", operation: str = "general") -> logging.Logger:
    """Get a logger with structured context."""
    logger = logging.getLogger(name)
    
    # Add context attributes directly to logger
    logger.component = component  # type: ignore[attr-defined]
    logger.operation = operation  # type: ignore[attr-defined]
    
    return logger