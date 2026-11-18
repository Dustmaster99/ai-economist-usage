# AI Economist

Estrutura base para experimentos e desenvolvimento de um projeto de AI Economist.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Configuração

```bash
uv sync --dev
```

## Execução

```bash
uv run python main.py
```

Para usar outro arquivo de configuração:

```bash
uv run python main.py --config configs/default.yaml
```

## Exemplos oficiais

Listar os exemplos disponíveis:

```bash
uv run python main.py --list-examples
```

Executar a versão Python do tutorial básico oficial do AI Economist:

```bash
uv run python main.py --example economic_simulation_basic
```

O exemplo executa dois episódios de 1000 passos e abre as visualizações em janelas
Matplotlib. Feche as janelas para encerrar o processo.

## Qualidade e testes

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Estrutura

```text
.
|-- configs/          # Configurações dos experimentos
|-- docs/             # Documentação técnica
|-- src/
|   |-- env/          # Ambientes e simulações
|   |-- models/       # Modelos e agentes
|   `-- utils/        # Funções compartilhadas
|-- tests/            # Testes automatizados
|-- main.py           # Ponto de entrada
|-- Makefile          # Atalhos de desenvolvimento
`-- pyproject.toml    # Metadados e dependências
```

Os diretórios `artifacts/`, `checkpoints/`, `logs/` e `mlruns/` são reservados para
saídas geradas localmente e não são versionados.
