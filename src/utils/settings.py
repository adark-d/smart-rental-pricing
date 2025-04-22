from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False, settings_files=["configs/settings.yaml"], load_dotenv=True
)

RAW_DIR = Path(settings.raw_data_dir)
CLEANED_DIR = Path(settings.cleaned_data_dir)
LOG_DIR = Path(settings.logs_dir)
FAILED_DIR = Path(settings.failed_data_dir)
COMPRESSED_DIR = Path(settings.compressed_data_dir)
