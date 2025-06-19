from typing import Any

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False,
    settings_files=["configs/settings.yaml"],
    load_dotenv=True,
)


def get_scraper_setting(source: str, key: str, default: Any = None) -> Any:
    return settings.sources.get(source, {}).get("scraper", {}).get(key, default)
