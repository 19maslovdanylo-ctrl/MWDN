from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.v1 import bidding_router, stats_router
from core.logging import setup_logging, get_logger
from core.settings import get_settings
from infrastructure.db.session import init_db, close_db

setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting FastAPI application')
    # Database initialization is done in entrypoint.sh before workers start
    yield
    logger.info('Shutting down FastAPI application')
    await close_db()


app = FastAPI(
    title='Bidding API',
    description='API for running auctions and retrieving statistics',
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(bidding_router, prefix='/api/v1')
app.include_router(stats_router, prefix='/api/v1')


@app.get('/health', tags=['health'])
async def health_check():
    return {
        'status': 'healthy',
        'service': 'bidding-api'
    }
