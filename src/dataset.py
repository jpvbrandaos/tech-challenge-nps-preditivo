"""Obtenção da base bruta: baixa da fonte oficial e confere a integridade."""

import hashlib
from pathlib import Path
import shutil
import urllib.request

from loguru import logger
import typer

from src.config import RAW_DATA_FILE, RAW_DATA_SHA256, RAW_DATA_URL

app = typer.Typer()


def sha256_of(path: Path) -> str:
    """Calcula o SHA-256 do arquivo: a impressão digital do conteúdo."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        # Lê em blocos de 64 KB para não carregar arquivos grandes de uma vez
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_sha256(path: Path, expected: str) -> None:
    """Para com erro se o SHA-256 do arquivo for diferente do esperado."""
    actual = sha256_of(path)
    if actual != expected:
        raise ValueError(
            f"O SHA-256 de {path} é {actual}, mas o esperado é {expected}. "
            "O arquivo está corrompido ou a fonte mudou."
        )


def download_raw_data(
    url: str = RAW_DATA_URL,
    destination: Path = RAW_DATA_FILE,
    expected_sha256: str = RAW_DATA_SHA256,
) -> Path:
    """Garante a base bruta em data/raw, íntegra.

    Se o arquivo já existe, só confere o SHA-256. Se não existe, baixa para um
    arquivo temporário e só dá o nome final depois de conferir: assim um
    download interrompido ou corrompido nunca vira a base do projeto.
    """
    if destination.exists():
        check_sha256(destination, expected_sha256)
        logger.info(f"Base já presente e íntegra: {destination}")
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".part")
    logger.info(f"Baixando a base de {url}")
    try:
        with urllib.request.urlopen(url, timeout=60) as response, temporary.open("wb") as file:
            shutil.copyfileobj(response, file)
        check_sha256(temporary, expected_sha256)
        temporary.replace(destination)
    finally:
        # Se algo falhou no caminho, não deixa arquivo pela metade
        temporary.unlink(missing_ok=True)

    logger.success(f"Base baixada e conferida: {destination}")
    return destination


@app.command()
def main() -> None:
    """Baixa a base bruta, se faltar, e confere a integridade."""
    download_raw_data()


if __name__ == "__main__":
    app()
