import hashlib

import pytest

from src.dataset import download_raw_data, sha256_of

CONTENT = b"order_id,nps_score\n50001,6.9\n"


def test_sha256_matches_reference_value(tmp_path):
    file_path = tmp_path / "abc.txt"
    file_path.write_bytes(b"abc")
    # Valor de referência oficial do SHA-256 para o texto "abc"
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert sha256_of(file_path) == expected


def test_download_with_right_hash_creates_file(tmp_path):
    source = tmp_path / "source.csv"
    source.write_bytes(CONTENT)
    destination = tmp_path / "raw" / "base.csv"

    download_raw_data(source.as_uri(), destination, hashlib.sha256(CONTENT).hexdigest())

    assert destination.read_bytes() == CONTENT


def test_download_with_wrong_hash_fails_and_leaves_no_file(tmp_path):
    source = tmp_path / "source.csv"
    source.write_bytes(CONTENT)
    destination = tmp_path / "raw" / "base.csv"

    with pytest.raises(ValueError):
        download_raw_data(source.as_uri(), destination, "0" * 64)

    assert not destination.exists()
    assert not destination.with_name(destination.name + ".part").exists()
