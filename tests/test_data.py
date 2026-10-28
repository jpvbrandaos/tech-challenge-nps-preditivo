from src.config import PROCESSED_DATA_FILE, PROJ_ROOT, RAW_DATA_DIR


def test_data_paths_stay_inside_project():
    assert RAW_DATA_DIR.is_relative_to(PROJ_ROOT)
    assert PROCESSED_DATA_FILE.is_relative_to(PROJ_ROOT)
