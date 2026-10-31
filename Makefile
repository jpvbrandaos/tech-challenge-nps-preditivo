#################################################################################
# VARIÁVEIS                                                                     #
#################################################################################

PYTHON_INTERPRETER = python

#################################################################################
# AMBIENTE E QUALIDADE                                                          #
#################################################################################

## Instala as versões fixas do requirements.txt
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Apaga os arquivos compilados do Python
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Confere o estilo com o ruff, sem alterar nada
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Formata o código e corrige o que o ruff corrige sozinho
.PHONY: format
format:
	ruff check --fix
	ruff format

## Roda os testes
.PHONY: test
test:
	$(PYTHON_INTERPRETER) -m pytest tests

#################################################################################
# ETAPAS DO PROJETO                                                             #
#################################################################################

## Baixa a base bruta e confere o SHA-256
.PHONY: data
data:
	$(PYTHON_INTERPRETER) -m src.dataset

## Gera a base tratada
.PHONY: features
features:
	$(PYTHON_INTERPRETER) -m src.features

## Treina o modelo e grava em models/
.PHONY: train
train:
	$(PYTHON_INTERPRETER) -m src.modeling.train

## Gera a lista do dia a partir da base tratada
.PHONY: predict
predict:
	$(PYTHON_INTERPRETER) -m src.modeling.predict data/processed/base_tratada.csv

## Refaz o projeto inteiro, da base bruta à lista do dia, com os notebooks
.PHONY: pipeline
pipeline:
	$(PYTHON_INTERPRETER) -m src.pipeline

#################################################################################
# AJUDA                                                                         #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Comandos disponíveis:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

## Lista os comandos
help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
