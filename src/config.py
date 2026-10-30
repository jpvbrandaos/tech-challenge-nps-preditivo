from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass

RANDOM_SEED = 42


# Base bruta: fonte oficial e impressão digital esperada (fora do Git, decisão D-01)
RAW_DATA_URL = (
    "https://raw.githubusercontent.com/AnaRaquelCafe/POSTECH_AI_SCIENTIST/main/"
    "Base%20de%20dados%20Tech%20Challenge/desafio_nps_fase_1.csv"
)
RAW_DATA_FILE = RAW_DATA_DIR / "desafio_nps_fase_1.csv"
RAW_DATA_SHA256 = "cc97b3ebb94ed7251c2ae37ee813381207023e8ef1b0cd32c339844c4347b42b"

# Base tratada: gerada por python -m src.features e mantida fora do Git, como a base bruta (D-01)
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "base_tratada.csv"

# Fração da base reservada para o teste, separada antes da análise exploratória (D-11)
TEST_SIZE = 0.2

# Modelo de risco e lista do dia: gerados por comando e mantidos fora do Git, como as bases
MODEL_FILE = MODELS_DIR / "modelo_detrator.joblib"
DAILY_LIST_FILE = PROCESSED_DATA_DIR / "lista_do_dia.csv"
