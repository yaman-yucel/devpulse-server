"""Logger configuration using loguru for DevPulse server."""

import sys
from pathlib import Path

from loguru import logger


def setup_logger(log_level: str = "INFO", log_to_file: bool = True, log_dir: str = "logs", rotation: str = "100 MB", retention: str = "7 days", compression: str = "gz") -> None:
    # Remove default logger
    logger.remove()

    # Console logger with colored output
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        colorize=True,
    )

    if log_to_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # File logger for all logs
        logger.add(
            log_path / "devpulse_{time:YYYY-MM-DD}.log",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation=rotation,
            retention=retention,
            compression=compression,
            serialize=False,
        )

        # Separate error log file
        logger.add(
            log_path / "devpulse_errors_{time:YYYY-MM-DD}.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation=rotation,
            retention=retention,
            compression=compression,
            serialize=False,
        )
