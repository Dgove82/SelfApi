from fastapi import FastAPI, Request
import atexit
import settings
from src.library.handler import RequestHandler
import warnings

warnings.filterwarnings("ignore")
settings.log.info(f'SERVER PROCESS STARTED')
atexit.register(lambda: settings.log.info(f'SERVER PROCESS FINISHED'))

app = FastAPI()


@app.api_route("/{module}/{resource}/{action}", methods=settings.CORS_ALLOW_METHODS)
async def entrance(request: Request):
    response = await RequestHandler(request).handler()
    return response
