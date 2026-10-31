"""Reprodução do projeto de ponta a ponta, da base bruta à lista do dia."""

from pathlib import Path
from typing import Annotated

from loguru import logger
from nbclient import NotebookClient
import nbformat
import typer

from src import features
from src.config import PROCESSED_DATA_FILE, PROJ_ROOT
from src.modeling import predict, train

app = typer.Typer()

NOTEBOOKS_DIR = PROJ_ROOT / "notebooks"

# Na ordem do projeto: qualidade dos dados, análise exploratória e modelagem
NOTEBOOKS = ["01_qualidade_e_tratamento.ipynb", "02_eda.ipynb", "03_modelagem.ipynb"]

# Limite por célula, com folga: a mais lenta, a busca de hiperparâmetros, leva cerca de um minuto
CELL_TIMEOUT_SECONDS = 600


def run_notebook(path: Path, timeout: int = CELL_TIMEOUT_SECONDS) -> None:
    """Roda o notebook do início ao fim num kernel novo, como Restart e Run All, e salva as saídas.

    O horário de execução de cada célula fica fora dos metadados: no mesmo ambiente, rodar de novo
    não muda o arquivo, e uma diferença no git status indica um resultado que não se repetiu.
    """
    notebook = nbformat.read(path, as_version=4)
    NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        record_timing=False,
        resources={"metadata": {"path": str(path.parent)}},
    ).execute()
    nbformat.write(notebook, path)


@app.command()
def main(
    notebooks: Annotated[
        bool, typer.Option(help="Roda também os notebooks, do início ao fim.")
    ] = True,
) -> None:
    """Refaz o projeto na ordem: base bruta e base tratada, notebooks, modelo e lista do dia."""
    # A base tratada baixa a base bruta, se faltar, e confere o SHA-256 antes de tratar
    features.main()
    if notebooks:
        for name in NOTEBOOKS:
            logger.info(f"Rodando {name}")
            run_notebook(NOTEBOOKS_DIR / name)
    train.main()
    predict.main(PROCESSED_DATA_FILE)
    logger.success("Projeto refeito do zero")


if __name__ == "__main__":
    app()
