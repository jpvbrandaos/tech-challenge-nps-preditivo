import hashlib

import pytest

from src.dataset import download_raw_data, sha256_of

CONTEUDO = b"order_id,nps_score\n50001,6.9\n"


def test_sha256_bate_com_o_valor_de_referencia(tmp_path):
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")
    # Valor de referência oficial do SHA-256 para o texto "abc"
    esperado = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert sha256_of(arquivo) == esperado


def test_download_com_hash_certo_cria_a_base(tmp_path):
    origem = tmp_path / "origem.csv"
    origem.write_bytes(CONTEUDO)
    destino = tmp_path / "raw" / "base.csv"

    download_raw_data(origem.as_uri(), destino, hashlib.sha256(CONTEUDO).hexdigest())

    assert destino.read_bytes() == CONTEUDO


def test_download_com_hash_errado_falha_e_nao_deixa_arquivo(tmp_path):
    origem = tmp_path / "origem.csv"
    origem.write_bytes(CONTEUDO)
    destino = tmp_path / "raw" / "base.csv"

    with pytest.raises(ValueError):
        download_raw_data(origem.as_uri(), destino, "0" * 64)

    assert not destino.exists()
    assert not destino.with_name(destino.name + ".part").exists()
