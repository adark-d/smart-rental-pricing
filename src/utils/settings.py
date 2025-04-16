from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False, settings_files=["config/settings.yaml"], load_dotenv=True
)
