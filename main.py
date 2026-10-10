from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

YAML_CONFIG = {
    "workers": 3,
    "debug": True,
    "log_level": "warning",
}

DOTENV_CONFIG = {
    "APP_PORT": "8772",
    "NUM_WORKERS": "1",
    "APP_DEBUG": "true",
    "APP_API_KEY": "key-xsukba9aaa",
}

OS_ENV_CONFIG = {
    "APP_PORT": "8639",
}

CONFIG_KEYS = {"port", "workers", "debug", "log_level", "api_key"}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_boolean(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def build_effective_config(overrides: list[str] | None) -> dict[str, int | bool | str]:
    config: dict[str, object] = DEFAULTS.copy()
    config.update(YAML_CONFIG)

    dotenv_aliases = {
        "APP_PORT": "port",
        "NUM_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_API_KEY": "api_key",
    }
    for source_key, value in DOTENV_CONFIG.items():
        config[dotenv_aliases[source_key]] = value

    os_env_aliases = {"APP_PORT": "port"}
    for source_key, value in OS_ENV_CONFIG.items():
        config[os_env_aliases[source_key]] = value

    for override in overrides or []:
        key, separator, value = override.partition("=")
        if separator and key in CONFIG_KEYS:
            config[key] = value

    config["port"] = int(config["port"])
    config["workers"] = int(config["workers"])
    config["debug"] = parse_boolean(config["debug"])
    config["log_level"] = str(config["log_level"])
    config["api_key"] = "****"
    return {key: config[key] for key in ("port", "workers", "debug", "log_level", "api_key")}


@app.get("/effective-config")
def effective_config(
    overrides: Annotated[list[str] | None, Query(alias="set")] = None,
) -> dict[str, int | bool | str]:
    return build_effective_config(overrides)
