from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF", settings_files=["config/settings.toml"], load_dotenv=True
)
