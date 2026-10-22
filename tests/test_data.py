import pytest
from src.config import PROJ_ROOT, RAW_DATA_DIR


def test_pasta_de_dados_fica_dentro_do_projeto():
    assert RAW_DATA_DIR.is_relative_to(PROJ_ROOT)
