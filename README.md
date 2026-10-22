# NPS Preditivo
- Resumo a preencher

## Objetivo

## Base de Dados

## Metodologia

## Principais Resultados

## Estrutura do Repositório

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>


```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         src and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes src a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

## Como Reproduzir

Requer Python 3.13 e Git.

1. Clone o repositório:
   `git clone https://github.com/jpvbrandaos/tech-challenge-nps-preditivo.git`
2. Crie e ative o ambiente virtual:
   - Windows (PowerShell): `py -3.13 -m venv .venv` e `.\.venv\Scripts\Activate.ps1`
   - Linux ou macOS: `python3.13 -m venv .venv` e `source .venv/bin/activate`
3. Instale as dependências: `pip install -r requirements.txt`
4. A base já vem em `data/raw/`; a origem está em Base de dados.
5. Execute os notebooks na ordem numérica, do início ao fim.


## Registro de Decisões

## Limitações e Próximos Passos

## Convenções

## Convenções

- Código em inglês e `snake_case`, como as colunas da base; textos em português.
- Notebooks numerados na ordem de execução (`01_`, `02_`, `03_`).
- Todo notebook roda do início ao fim (Restart & Run All) antes do commit e vai com as saídas.
- Caminhos sempre via `src/config.py`; semente sempre `RANDOM_STATE`.
- `data/raw/` é imutável.
- Commits no padrão Conventional Commits, em português.
- Uma branch e uma pull request por etapa.

## Autor

A análise e a modelagem preditiva deste projeto foram desenvolvidas por:

<img src="https://avatars.githubusercontent.com/u/287458588?v=4" width="110px;" style="border-radius: 50%;" alt="Foto do João Pedro Brandão"/>

### João Pedro Brandão
*Cientista de Dados*

Administrador pela UFMG e pós-graduando em IA na FIAP. Trabalho combinando visão de negócios e ciência de dados para transformar análises e modelos preditivos em soluções que geram resultado real.

[LinkedIn](https://linkedin.com) | [GitHub](https://github.com)




--------
