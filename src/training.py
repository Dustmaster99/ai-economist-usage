"""Orquestração de experimentos."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def run_experiment(config: dict[str, Any]) -> None:
    """Executa um experimento; substitua pelo pipeline de treino do projeto."""
    project = config.get("project", {}).get("name", "ai-economist")
    logger.info("Experimento '%s' iniciado.", project)
    logger.info("Estrutura base configurada com sucesso.")
