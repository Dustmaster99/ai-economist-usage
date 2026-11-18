# Arquitetura

O projeto segue uma separação simples de responsabilidades:

- `src/env`: ambientes, regras e dinâmica da simulação;
- `src/models`: modelos, políticas e agentes;
- `src/training.py`: orquestração de treino e avaliação;
- `src/utils`: infraestrutura compartilhada, como logging;
- `configs`: parâmetros de experimentos em YAML.

Atualize este documento conforme os componentes do domínio forem definidos.
