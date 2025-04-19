from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False, settings_files=["config/settings.yaml"], load_dotenv=True
)

RAW_DIR = Path(settings.raw_data_dir)
RAW_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path(settings.logs_dir)
LOG_DIR.mkdir(parents=True, exist_ok=True)

FAILED_DIR = Path(settings.failed_data_dir)
FAILED_DIR.mkdir(parents=True, exist_ok=True)
