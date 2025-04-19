from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False, settings_files=["config/settings.yaml"], load_dotenv=True
)

RAW_DIR = Path(settings.raw_data_dir)
RAW_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_DIR = Path(settings.processed_data_dir)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

use_thread = settings.use_thread
