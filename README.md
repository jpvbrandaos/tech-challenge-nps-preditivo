# NPS Preditivo
- Resumo a preencher

## Objetivo

Identificar as falhas de entrega e atendimento que mais transformam clientes em detratores e estimar, logo após a entrega, o risco de cada cliente se tornar detrator, a tempo de a empresa agir antes da pesquisa de NPS. O projeto responde ao Tech Challenge da Fase 1 da Pós-Tech AI Scientist (FIAP).

O problema de negócio, as metas e os critérios de sucesso estão em [Entendimento do negócio](reports/entendimento_negocio.md).

## Base de Dados

- **Origem dos dados**

A base de dados utilizada neste projeto é proveniente do repositório público [POSTECH_AI_SCIENTIST](https://github.com/AnaRaquelCafe/POSTECH_AI_SCIENTIST), disponibilizada no arquivo [`desafio_nps_fase_1.csv`](https://github.com/AnaRaquelCafe/POSTECH_AI_SCIENTIST/blob/main/Base%20de%20dados%20Tech%20Challenge/desafio_nps_fase_1.csv).

- **Download da base de dados**

Por decisão de versionamento (D-01), o arquivo original não é armazenado no repositório. Sua obtenção é automatizada pelo módulo src.dataset, responsável por baixar os dados da fonte original e salvá-los no diretório data/raw/.

Para obter a base de dados, execute o seguinte comando na raiz do projeto:

    python -m src.dataset

Após o download, a integridade do arquivo é verificada por meio do cálculo do hash SHA-256 e da comparação com o valor de referência definido em src/config.py. Essa validação permite identificar divergências em relação ao arquivo original esperado.

- **Dicionário de dados**

O dicionário de dados, disponível em [`references/dicionario_de_dados.md`](references/dicionario_de_dados.md), descreve as variáveis da base de dados e suas respectivas definições.


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
4. Baixe a base e confira a integridade: `python -m src.dataset`. Na primeira vez o comando precisa de internet; depois, ele só confere o arquivo.
5. Execute os notebooks na ordem numérica, do início ao fim.


## Registro de Decisões

As decisões do projeto, com contexto, alternativa descartada e motivo, ficam em [Registro de decisões](reports/registro_decisoes.md).

## Limitações e Próximos Passos

Por enquanto, as premissas, restrições e riscos conhecidos estão na [seção 7 do entendimento do negócio](reports/entendimento_negocio.md#7-premissas-restrições-e-riscos).

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
