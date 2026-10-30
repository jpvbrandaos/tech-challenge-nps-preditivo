# NPS Preditivo

Projeto de ciência de dados que estima, logo após a entrega, o risco de cada cliente de um e-commerce se tornar detrator na pesquisa de NPS. O diagnóstico da base está concluído: os dados são íntegros, mas têm sinais claros de simulação, e as conclusões valem como demonstração de método ([D-10](reports/registro_decisoes.md#d-10-base-tratada-como-simulada)). Na análise exploratória, o atraso aparece como a falha que mais pesa: metade dos clientes que recebem no prazo é detratora, contra quase todos a partir de três dias de atraso. O modelo de risco, uma regressão logística, supera no teste a regra de dias de atraso, com ROC-AUC de 0,869 contra 0,784, e o ganho é maior nos pedidos com até 2 dias de atraso, que ele ordena na lista diária de contato.

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

O comando `python -m src.features` gera `data/processed/base_tratada.csv`, com todos os pedidos e colunas originais e os atributos de negócio de `src/features.py`. Como a base bruta, ela fica fora do Git.

Antes da análise exploratória, `src/split.py` reserva 20% dos pedidos para o teste final, sorteados com semente fixa e com a mesma proporção de detratores do treino ([D-11](reports/registro_decisoes.md#d-11-teste-separado-antes-da-análise-exploratória)).


## Metodologia

O projeto segue as fases do CRISP-DM, cada uma com um documento ou notebook próprio:

1. [Entendimento do negócio](reports/entendimento_negocio.md): problema, metas e critérios de sucesso, premissas e hipóteses.
2. [Definição da variável-alvo](reports/definicao_target.md): escolha da variável, regra de classificação, variáveis permitidas no modelo e riscos de uso.
3. [Qualidade e preparação dos dados](notebooks/01_qualidade_e_tratamento.ipynb): diagnóstico da base, decisões de tratamento e base tratada com os atributos de negócio.
4. [Análise exploratória](notebooks/02_eda.ipynb): fatores associados aos detratores, pontos de ruptura, interações, perfis de cliente, veredito das hipóteses e referências para o modelo, só com os pedidos de treino (D-11).
5. [Estratégia preditiva](reports/estrategia_preditiva.md): pergunta do modelo, momento da predição, escolha entre regressão e classificação, plano de avaliação, uso do score pela empresa e piloto com grupo de controle.
6. [Modelagem](notebooks/03_modelagem.ipynb): candidatos comparados por validação cruzada no treino, regressão da nota como comparação, robustez, calibração, erro por grupo e uma única avaliação no teste contra a regra de dias de atraso, resumidos no [model card](reports/model_card.md).

## Principais Resultados

### Qualidade dos dados

- A base tem 2.500 pedidos e 19 colunas, sem valores ausentes, duplicidades ou valores fora de faixa, e cada cliente aparece em um único pedido.
- Três leituras mudaram com o diagnóstico: o tempo de entrega é a previsão informada ao cliente ([D-07](reports/registro_decisoes.md#d-07-tempo-de-entrega-lido-como-previsão)), o valor do pedido já vem com o desconto ([D-08](reports/registro_decisoes.md#d-08-valor-do-pedido-lido-como-líquido-do-desconto)), e contatos, reclamações e tempo de resolução são registros independentes ([D-09](reports/registro_decisoes.md#d-09-registros-de-atendimento-lidos-como-independentes)).
- Distribuições planas e relações esperadas ausentes indicam base simulada, e as conclusões do projeto valem como demonstração de método ([D-10](reports/registro_decisoes.md#d-10-base-tratada-como-simulada)).
- O detrator é a grande maioria: 84,4% dos pedidos pelo corte direto da D-05, com NPS de −80,0. O arredondamento levaria a 79,0% e −72,8, sem mudar a conclusão.

### Análise exploratória

Números do treino, com 2.000 pedidos, na [análise exploratória](notebooks/02_eda.ipynb):

- **Fatores críticos:** só fatores de entrega e atendimento se associam aos detratores, com reclamações (V de Cramér de 0,42) e atraso (0,39) à frente; perfil do cliente e condições do pedido não mostram associação depois da correção de Holm (seção 4).
- **O que mais gera detratores:** o atraso alcança 93% dos detratores e leva a proporção de detratores de 51% nos pedidos no prazo para 89% nos atrasados; mesmo sem atraso, o contato com o atendimento soma 39 pontos de detratores (seção 5).
- **Ponto de ruptura:** não há um limite tolerado. O modelo em que o risco cresce a cada dia de atraso vence o de um corte único por 102 pontos de AIC, e quase todos os clientes são detratores a partir de três dias (seção 6).
- **Perfis de cliente:** região, idade, tempo de relacionamento, valor do pedido e parcelamento ficam todos entre 81% e 89% de detratores, sem diferença que resista à correção (seções 4 e 8).
- **Hipóteses:** H1 confirmada no crescimento do risco com o atraso e refutada no salto; H6 confirmada; H3, H4, H5, H8 e H9 refutadas; H2 e H7 inconclusivas (seção 9).
- **Tamanho da oportunidade:** se os pedidos atrasados tivessem a mistura de notas dos pedidos no prazo, o NPS iria de −79,8 para −32,4, um ganho de 47 pontos com intervalo de 38 a 57, como teto otimista (seção 10).

### Modelo

Números da [modelagem](notebooks/03_modelagem.ipynb), com validação cruzada nos 2.000 pedidos de treino e uma única avaliação nos 500 de teste; a ficha do modelo está no [model card](reports/model_card.md):

- **Escolha:** a regressão logística vence o gradient boosting por 0,015 de ROC-AUC na validação cruzada, acima da margem de 0,01 que levaria ao desempate pelo mais simples, e a regressão da nota, medida como comparação, empata com a classificação (seções 2 e 3).
- **Teste:** ROC-AUC de 0,869, contra 0,784 da regra de dias de atraso e 0,500 do modelo ingênuo. A diferença para a regra é de 0,085, com intervalo de 0,044 a 0,129, e, com a PR-AUC também acima, o modelo atende aos três critérios da [D-15](reports/registro_decisoes.md#d-15-alvos-do-modelo-e-da-meta-de-negócio) (seção 10).
- **Onde está o ganho:** nos pedidos com até 2 dias de atraso, seis em cada dez, em que a regra só separa zero, um e dois dias, a diferença sobe para 0,120 no teste. É nesse segmento que o modelo ordena a lista do dia (seções 4 e 10).
- **Sinais:** dias de atraso, reclamações e, bem atrás, tempo de resolução. Sem as reclamações, o modelo conserva cerca de três quartos da vantagem sobre a regra; só com cadastro e pedido, no checkout, fica perto do sorteio (seções 5 e 6).
- **Calibração e grupos:** a probabilidade prevista acompanha a proporção observada em nove das dez faixas de risco, e o erro fica a menos de meio ponto nas regiões e a até quatro pontos nas faixas de idade (seções 7 e 8).
- **Lista do dia:** 20% dos pedidos entregues, metade com 3 dias de atraso ou mais, na ordem do atraso, e metade com até 2 dias, na ordem do risco do modelo, cada um com a ação definida pela falha registrada ([D-19](reports/registro_decisoes.md#d-19-uso-do-score-por-segmento-de-atraso-com-a-ação-definida-pela-falha-do-pedido)).

## Estrutura do Repositório

Estrutura baseada no [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/).

```
├── data/                        # fora do Git (D-01)
│   ├── raw/                     # base original, baixada por python -m src.dataset
│   └── processed/               # base tratada e lista do dia, geradas por comando
├── models/                      # modelo treinado por python -m src.modeling.train, fora do Git
├── notebooks/
│   ├── 01_qualidade_e_tratamento.ipynb
│   ├── 02_eda.ipynb
│   └── 03_modelagem.ipynb
├── references/
│   └── dicionario_de_dados.md
├── reports/
│   ├── entendimento_negocio.md
│   ├── definicao_target.md
│   ├── estrategia_preditiva.md
│   ├── model_card.md
│   ├── registro_decisoes.md
│   └── figures/                 # figuras da análise exploratória e da modelagem, usadas nos slides
├── src/
│   ├── config.py                # caminhos, semente, fonte da base e tamanho do teste
│   ├── dataset.py               # download da base e conferência do SHA-256
│   ├── features.py              # atributos de negócio e geração da base tratada
│   ├── split.py                 # separação de treino e teste (D-11)
│   ├── analysis.py              # proporções, efeitos e vereditos da análise exploratória
│   ├── plots.py                 # gráficos da análise exploratória e da modelagem
│   └── modeling/
│       ├── models.py            # variáveis, preparação, candidatos e busca (D-06 e D-18)
│       ├── evaluation.py        # validação cruzada, comparação com a regra e diagnósticos
│       ├── train.py             # treino e gravação do modelo
│       └── predict.py           # risco dos pedidos e lista do dia (D-19)
├── tests/                       # download, atributos, base tratada, separação, análise e modelagem
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
5. Gere a base tratada: `python -m src.features`.
6. Execute os notebooks na ordem numérica, do início ao fim.
7. Treine o modelo: `python -m src.modeling.train`. Ele vai para `models/`, fora do Git, com um JSON de rastreio ao lado.
8. Gere a lista do dia: `python -m src.modeling.predict data/processed/base_tratada.csv`. A entrada pode ser qualquer CSV com `order_id` e as colunas de cadastro, pedido, entrega e atendimento; a lista sai em `data/processed/lista_do_dia.csv`.
9. Rode os testes: `python -m pytest tests`. Os testes da base tratada pedem o passo 5.


## Registro de Decisões

As decisões do projeto, com contexto, alternativas consideradas, justificativa e consequências, ficam em [Registro de decisões](reports/registro_decisoes.md).

## Limitações e Próximos Passos

- **Base simulada.** As conclusões valem como demonstração de método, e não como retrato de uma operação real (D-10).
- **Não resposta.** A base traz só quem respondeu à pesquisa, e o viés de não resposta não pode ser medido.
- **Atendimento.** Reclamações e tempo de resolução não se vinculam com segurança ao pedido avaliado (D-09).
- **Associação.** Os achados da análise exploratória descrevem associação, e não causa; o efeito de cada ação só se confirma em piloto com grupo de controle.
- **Próximos passos.** Validar com o atendimento a capacidade de 20% e as ações por tipo de falha e rodar, por dois trimestres, o piloto com grupo de controle da [D-20](reports/registro_decisoes.md#d-20-piloto-com-grupo-de-controle-para-medir-o-efeito-das-ações), contra a meta de reduzir os detratores em 10 pontos. Na operação, o modelo é comparado todo mês com a regra de dias de atraso e retreinado com os clientes do grupo de controle permanente, como descreve o [model card](reports/model_card.md#8-monitoramento-e-retreino).

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
