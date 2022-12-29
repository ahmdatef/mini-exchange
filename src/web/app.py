import uvicorn
from fastapi import FastAPI

from web.api.routes import router
from web.serializers.response_handlers import register_error_handlers
from common.config.logging import get_logging_config
from common.config.settings import get_settings

app = FastAPI(title="Mini Stock Ex-change Command API",
              description="Mini Stock Ex-change Command API",
              version="1.0.0")

app.include_router(router)

register_error_handlers(app)

settings = get_settings()
logging_config = get_logging_config()


if __name__ == "__main__":
    uvicorn.run("app:app",
                host=settings.host,
                port=settings.port,
                log_config=logging_config)
