"""Ponto de entrada do projeto AI Economist."""

from __future__ import annotations

import argparse
import importlib
import logging
from pathlib import Path
from typing import Any

import yaml

from src.official_examples import EXAMPLES
from src.training import run_experiment
from src.utils.logger import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa um experimento do AI Economist.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/default.yaml"),
        help="Caminho do arquivo YAML de configuração.",
    )
    parser.add_argument("--log-level", default="INFO", help="Nível de logging.")
    parser.add_argument(
        "--example",
        choices=sorted(EXAMPLES),
        help="Executa um exemplo oficial pelo nome em vez do experimento padrão.",
    )
    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="Lista os exemplos oficiais disponíveis e encerra.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    if args.list_examples:
        print("Exemplos oficiais disponíveis:")
        for example_name in sorted(EXAMPLES):
            print(f"  - {example_name}")
        return

    if args.example:
        example_module = importlib.import_module(EXAMPLES[args.example])
        example_module.run()
        return

    logging.getLogger(__name__).info("Carregando configuração de %s", args.config)
    run_experiment(load_config(args.config))


if __name__ == "__main__":
    main()
