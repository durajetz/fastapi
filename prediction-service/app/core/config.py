from typing import Any
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    SITE_DOMAIN: str = "myapp.com"
    TORCH_SERVE_URL: str = "http://localhost:8080/predictions/"
    APP_VERSION: str = "1"


settings = Config()

app_configs: dict[str, Any] = {"title": "Predictions API"}
app_configs["openapi_url"] = f"/api/v{settings.APP_VERSION}/predictions/openapi.json"
app_configs["docs_url"] = f"/api/v{settings.APP_VERSION}/predictions/docs"
