# NPS Preditivo

Projeto de ciência de dados que estima, logo após a entrega, o risco de cada cliente de um e-commerce se tornar detrator na pesquisa de NPS. O diagnóstico da base está concluído: os dados são íntegros, mas têm sinais claros de simulação, e as conclusões valem como demonstração de método ([D-10](reports/registro_decisoes.md#d-10-base-tratada-como-simulada)). A análise exploratória e o modelo de risco vêm nas próximas etapas.

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

O dicionário de dados, disponível em [`references/dicionario_de_dados.md`](references/dicionario_de_dados.md), descreve as variáveis da base de dados e suas respectivas definições, as leituras adotadas pelo projeto e os atributos da base tratada.

- **Base tratada**

O notebook 01 gera `data/processed/base_tratada.csv`, com todos os pedidos e colunas originais e os atributos de negócio de `src/features.py`. Como a base bruta, ela fica fora do Git e é recriada a cada execução do notebook.


## Metodologia

O projeto segue as fases do CRISP-DM, cada uma com um documento ou notebook próprio:

1. [Entendimento do negócio](reports/entendimento_negocio.md): problema, metas e critérios de sucesso, premissas e hipóteses.
2. [Definição da variável-alvo](reports/definicao_target.md): escolha da variável, regra de classificação, variáveis permitidas no modelo e riscos de uso.
3. [Qualidade e preparação dos dados](notebooks/01_qualidade_e_tratamento.ipynb): diagnóstico da base, decisões de tratamento e base tratada com os atributos de negócio.

## Principais Resultados

### Qualidade dos dados

- A base tem 2.500 pedidos e 19 colunas, sem valores ausentes, duplicidades ou valores fora de faixa, e cada cliente aparece em um único pedido.
- Três leituras mudaram com o diagnóstico: o tempo de entrega é a previsão informada ao cliente ([D-07](reports/registro_decisoes.md#d-07-tempo-de-entrega-lido-como-previsão)), o valor do pedido já vem com o desconto ([D-08](reports/registro_decisoes.md#d-08-valor-do-pedido-lido-como-líquido-do-desconto)), e contatos, reclamações e tempo de resolução são registros independentes ([D-09](reports/registro_decisoes.md#d-09-registros-de-atendimento-lidos-como-independentes)).
- Distribuições planas e relações esperadas ausentes indicam base simulada, e as conclusões do projeto valem como demonstração de método ([D-10](reports/registro_decisoes.md#d-10-base-tratada-como-simulada)).
- O detrator é a grande maioria: 84,4% dos pedidos pelo corte direto da D-05, com NPS de −80,0. O arredondamento levaria a 79,0% e −72,8, sem mudar a conclusão.

## Estrutura do Repositório

Estrutura baseada no [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/).

```
├── data/                        # fora do Git (D-01)
│   ├── raw/                     # base original, baixada por python -m src.dataset
│   └── processed/               # base tratada, gerada pelo notebook 01
├── models/                      # modelo treinado, na etapa de modelagem
├── notebooks/
│   └── 01_qualidade_e_tratamento.ipynb
├── references/
│   └── dicionario_de_dados.md
├── reports/
│   ├── entendimento_negocio.md
│   ├── definicao_target.md
│   ├── registro_decisoes.md
│   └── figures/
├── src/
│   ├── config.py                # caminhos, semente e fonte da base
│   ├── dataset.py               # download da base e conferência do SHA-256
│   ├── features.py              # atributos de negócio da base tratada
│   ├── plots.py                 # gráficos, na análise exploratória
│   └── modeling/                # treino e predição, na etapa de modelagem
├── tests/                       # download, atributos e qualidade da base tratada
├── LICENSE
├── Makefile
├── pyproject.toml
└── requirements.txt
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
6. Rode os testes: `python -m pytest tests`. Os testes da base tratada pedem o notebook 01 já executado.


## Registro de Decisões

As decisões do projeto, com contexto, alternativas consideradas, justificativa e consequências, ficam em [Registro de decisões](reports/registro_decisoes.md).

## Limitações e Próximos Passos

- **Base simulada.** As conclusões valem como demonstração de método, e não como retrato de uma operação real (D-10).
- **Não resposta.** A base traz só quem respondeu à pesquisa, e o viés de não resposta não pode ser medido.
- **Atendimento.** Reclamações e tempo de resolução não se vinculam com segurança ao pedido avaliado (D-09).
- **Próximos passos.** Análise exploratória das hipóteses H1 a H9 e, depois, o modelo de risco.

As premissas, restrições e riscos completos estão na [seção 7 do entendimento do negócio](reports/entendimento_negocio.md#7-premissas-restrições-e-riscos).

## Convenções

- Código em inglês e `snake_case`, como as colunas da base; textos em português.
- Notebooks numerados na ordem de execução (`01_`, `02_`, `03_`).
- Todo notebook roda do início ao fim (Restart & Run All) antes do commit e vai com as saídas.
- Caminhos sempre via `src/config.py`; semente sempre `RANDOM_SEED`.
- `data/raw/` é imutável.
- Commits no padrão Conventional Commits, em português.
- Uma branch e uma pull request por etapa.

## Autor

A análise e a modelagem preditiva deste projeto foram desenvolvidas por:

<img src="https://avatars.githubusercontent.com/u/287458588?v=4" width="110px;" style="border-radius: 50%;" alt="Foto do João Pedro Brandão"/>

### João Pedro Brandão
*Cientista de Dados*

Administrador pela UFMG e pós-graduando em IA na FIAP. Trabalho combinando visão de negócios e ciência de dados para transformar análises e modelos preditivos em soluções que geram resultado real.

[GitHub](https://github.com/jpvbrandaos)
